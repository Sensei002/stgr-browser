#!/usr/bin/env python3
"""Windows helpers for the STGR test/benchmark tooling.

Stdlib + ctypes only. Every function degrades gracefully (returns None/[] on
non-Windows or on permission failures) so scripts also run on CI.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import time

try:
    _user32 = ctypes.windll.user32
    _kernel32 = ctypes.windll.kernel32
    _psapi = ctypes.windll.psapi
    _IS_WINDOWS = True
except AttributeError:
    _IS_WINDOWS = False

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
TH32CS_SNAPPROCESS = 0x00000002


def is_windows() -> bool:
    return _IS_WINDOWS


def find_window_for_pid(pid: int, title_substr: str | None = None,
                        timeout: float = 30.0):
    """Find a visible top-level window belonging to pid (optionally matching
    part of its title). Returns (hwnd, title) or None."""
    if not _IS_WINDOWS:
        return None
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        found = []

        @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
        def _cb(hwnd, lparam):
            wpid = wt.DWORD()
            _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
            if wpid.value == pid:
                buf = ctypes.create_unicode_buffer(512)
                _user32.GetWindowTextW(hwnd, buf, 512)
                title = buf.value.strip()
                if not title_substr or title_substr.lower() in title.lower():
                    if _user32.IsWindowVisible(hwnd):
                        found.append((hwnd, title))
            return True

        _user32.EnumWindows(_cb, 0)
        if found:
            return found[0]
        time.sleep(0.5)
    return None


def get_window_title(pid: int, timeout: float = 30.0) -> str | None:
    win = find_window_for_pid(pid, None, timeout)
    return win[1] if win else None


def process_memory_bytes(pid: int) -> int | None:
    """Working set size of one process, in bytes."""
    if not _IS_WINDOWS:
        return None
    h = _kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return None
    try:
        class _PMC(ctypes.Structure):
            _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)]
        pmc = _PMC()
        pmc.cb = ctypes.sizeof(_PMC)
        if _psapi.GetProcessMemoryInfo(h, ctypes.byref(pmc), pmc.cb):
            return int(pmc.WorkingSetSize)
        return None
    finally:
        _kernel32.CloseHandle(h)


def process_cpu_seconds(pid: int) -> tuple | None:
    """(kernel_seconds, user_seconds) cumulative for one process."""
    if not _IS_WINDOWS:
        return None
    h = _kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return None
    try:
        def _ft():
            return wt.FILETIME()
        creation, exit_t, kernel, user = _ft(), _ft(), _ft(), _ft()
        if _kernel32.GetProcessTimes(h, ctypes.byref(creation),
                                     ctypes.byref(exit_t),
                                     ctypes.byref(kernel),
                                     ctypes.byref(user)):
            def _sec(ft):
                return (ft.dwHighDateTime << 32 | ft.dwLowDateTime) / 1e7
            return (_sec(kernel), _sec(user))
        return None
    finally:
        _kernel32.CloseHandle(h)


def child_pids(root_pid: int) -> list:
    """All descendant process ids of root_pid (Windows toolhelp snapshot)."""
    if not _IS_WINDOWS:
        return [root_pid]
    children = {root_pid: []}

    class _PE(ctypes.Structure):
        _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD),
                    ("th32ProcessID", wt.DWORD),
                    ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", wt.DWORD), ("cntThreads", wt.DWORD),
                    ("th32ParentProcessID", wt.DWORD),
                    ("pcPriClassBase", wt.LONG), ("dwFlags", wt.DWORD)]

    snapshot = _kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == -1:
        return [root_pid]
    try:
        entry = _PE()
        entry.dwSize = ctypes.sizeof(_PE)
        ok = _kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        procs = []
        while ok:
            procs.append((entry.th32ProcessID, entry.th32ParentProcessID))
            ok = _kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        _kernel32.CloseHandle(snapshot)

    # Build the descendant closure.
    by_parent = {}
    for pid, ppid in procs:
        by_parent.setdefault(ppid, []).append(pid)
    out = []
    stack = [root_pid]
    while stack:
        cur = stack.pop()
        for child in by_parent.get(cur, []):
            out.append(child)
            stack.append(child)
    return [root_pid] + out


def tree_memory_bytes(root_pid: int) -> int | None:
    total, seen = 0, 0
    for pid in child_pids(root_pid):
        mem = process_memory_bytes(pid)
        if mem is not None:
            total += mem
            seen += 1
    return total if seen else None


def tree_cpu_delta_seconds(root_pid: int, sample_seconds: float = 5.0) -> float:
    """CPU seconds consumed by the whole process tree over a sample window."""
    if not _IS_WINDOWS:
        return 0.0
    before = {}
    for pid in child_pids(root_pid):
        t = process_cpu_seconds(pid)
        if t:
            before[pid] = sum(t)
    time.sleep(sample_seconds)
    after = {}
    for pid in child_pids(root_pid):
        t = process_cpu_seconds(pid)
        if t:
            after[pid] = sum(t)
    return sum(after.get(pid, 0) - b for pid, b in before.items())
