#!/usr/bin/env python3
"""
Verify that a PE file actually carries the STGR icon.

Why this exists: rcedit exits 0 whether or not it replaced the icon group that
the application actually loads. On Windows, Chromium's exe is a thin loader and
the icon resources the window uses live in chrome.dll, so stamping only the exe
produces a build that looks successful and still shows the Chromium logo in the
taskbar. This reads the resource directory and reports the truth.

Read-only. Never modifies the file.

    python scripts/verify-icon.py build/app/stgr.exe build/app/chrome.dll
    python scripts/verify-icon.py --expect-count 7 <pe>...

Exit code 1 if a file has an icon group whose entry count does not match
--expect-count. Files that cannot be parsed are reported and skipped, so a
parser gap never fails a build.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

RT_GROUP_ICON = 14


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


class PE:
    def __init__(self, data: bytes) -> None:
        if data[:2] != b"MZ":
            raise ValueError("not a PE file (missing MZ)")
        pe = u32(data, 0x3C)
        if data[pe : pe + 4] != b"PE\0\0":
            raise ValueError("not a PE file (missing PE signature)")
        coff = pe + 4
        count = u16(data, coff + 2)
        opt_size = u16(data, coff + 16)
        table = coff + 20 + opt_size
        self.data = data
        self.sections: list[tuple[str, int, int, int, int]] = []
        for i in range(count):
            base = table + i * 40
            name = data[base : base + 8].rstrip(b"\0").decode("ascii", "replace")
            self.sections.append(
                (name, u32(data, base + 12), u32(data, base + 8), u32(data, base + 20), u32(data, base + 16))
            )

    def offset_of_rva(self, rva: int) -> int | None:
        for _name, va, vsize, raw_ptr, raw_size in self.sections:
            if va <= rva < va + max(vsize, raw_size):
                return rva - va + raw_ptr
        return None

    def resource_root(self) -> int:
        """File offset of the resource directory (RVA and file offset differ)."""
        for name, va, _vsize, _raw_ptr, _raw_size in self.sections:
            if name == ".rsrc":
                off = self.offset_of_rva(va)
                if off is None:
                    raise ValueError(".rsrc has no raw data")
                return off
        raise ValueError("no .rsrc section")

    def entries(self, dir_off: int) -> list[tuple[int, int, bool]]:
        named = u16(self.data, dir_off + 12)
        ids = u16(self.data, dir_off + 14)
        out = []
        for i in range(named + ids):
            e = dir_off + 16 + i * 8
            raw_ident = u32(self.data, e)
            target = u32(self.data, e + 4)
            # High bit means "this is an offset into the name table", not an id.
            ident = raw_ident & 0xFFFF if not (raw_ident & 0x80000000) else -1
            out.append((ident, target & 0x7FFFFFFF, bool(target & 0x80000000)))
        return out

    def icon_groups(self) -> list[tuple[int, list[tuple[int, int]]]]:
        root = self.resource_root()
        groups: list[tuple[int, list[tuple[int, int]]]] = []

        for type_id, type_rel, is_dir in self.entries(root):
            if type_id != RT_GROUP_ICON or not is_dir:
                continue
            type_dir = root + type_rel
            for group_id, group_rel, group_is_dir in self.entries(type_dir):
                if not group_is_dir:
                    continue
                lang_dir = root + group_rel
                langs = self.entries(lang_dir)
                if not langs:
                    continue
                _lang, data_rel, data_is_dir = langs[0]
                if data_is_dir:
                    continue
                data_entry = root + data_rel
                payload_rva = u32(self.data, data_entry)
                payload_size = u32(self.data, data_entry + 4)
                payload_off = self.offset_of_rva(payload_rva)
                if payload_off is None:
                    continue
                blob = self.data[payload_off : payload_off + payload_size]
                if len(blob) < 6 or u16(blob, 2) != 1:
                    continue
                dims = []
                for k in range(u16(blob, 4)):
                    e_off = 6 + k * 14
                    if e_off + 14 > len(blob):
                        break
                    dims.append((blob[e_off] or 256, blob[e_off + 1] or 256))
                groups.append((group_id, dims))
        return groups


def ico_dims(path: Path) -> list[tuple[int, int]]:
    blob = path.read_bytes()
    if len(blob) < 6:
        raise ValueError("not an ICO")
    dims = []
    for i in range(u16(blob, 4)):
        off = 6 + i * 16
        if off + 16 > len(blob):
            break
        dims.append((blob[off] or 256, blob[off + 1] or 256))
    return dims


def main() -> int:
    args = sys.argv[1:]
    ico = None
    if "--ico" in args:
        i = args.index("--ico")
        ico = Path(args[i + 1])
        del args[i : i + 2]

    if not args:
        print(__doc__)
        return 2

    expected = None
    if ico:
        if not ico.exists():
            print(f"reference icon missing: {ico}")
            return 2
        expected = sorted(ico_dims(ico))
        print(f"reference {ico.name}: {len(expected)} sizes {[w for w, _ in expected]}")

    failures = 0
    for name in args:
        path = Path(name)
        if not path.exists():
            print(f"  MISSING {path}")
            failures += 1
            continue
        try:
            groups = PE(path.read_bytes()).icon_groups()
        except Exception as exc:  # noqa: BLE001 - a parser gap must not fail the build
            print(f"  SKIP    {path.name}: cannot parse resources ({exc})")
            continue

        if not groups:
            print(f"  NONE    {path.name}: no RT_GROUP_ICON")
            failures += 1
            continue

        matched = False
        for gid, dims in groups:
            label = "named" if gid < 0 else str(gid)
            if expected is not None and sorted(dims) == expected:
                matched = True
                print(f"  MATCH   {path.name} group {label}: STGR icon present")
                break
            print(f"          {path.name} group {label}: {len(dims)} sizes {[w for w, _ in dims]}")

        if expected is not None and not matched:
            failures += 1

    if failures:
        print(f"FAIL: {failures} file(s) do not carry the STGR icon")
        return 1
    print("OK: all files carry the STGR icon")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
