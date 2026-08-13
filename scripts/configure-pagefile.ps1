<#
.SYNOPSIS
Add an extra large pagefile without rebooting (GitHub Windows runner).

.NOTES
Why this exists: the windows-2022 runner image already ships a small
system-managed pagefile on D: (the temp drive, ~3 GB). The ThinLTO Firefox
build (clang-cl frontends + rustc LTO link of gkrust) needs a much bigger
commit limit than RAM + that pagefile: with ~7 GB RAM it aborts with
"LLVM ERROR: out of memory" / 0xC000001D at the two peak-memory compile
units (see docs/release-process.md).

Windows cannot create a second pagefile on a drive that already has one, so
the extra pagefile goes on C: (the system drive has no pagefile on this
image and has room). Creating pagefiles through WMI (Win32_PageFileSetting)
requires a reboot to take effect; the native NtCreatePagingFile API (the
same technique battle-tested in al-cheb/configure-pagefile-action) activates
the pagefile immediately, without touching the existing D: pagefile.

The script is defensive on purpose: it pre-checks for an existing pagefile on
the target drive and for free disk space (the two ways NtCreatePagingFile can
fail on a freshly provisioned runner), retries the native call once (it can
fail transiently while the image's own pagefile is still initializing), and
reports the raw NTSTATUS in hex when creation does fail so CI failures are
self-explanatory.

Usage:
  pwsh -File scripts/configure-pagefile.ps1 -MinimumSize 8GB -MaximumSize 16GB -DiskRoot "C:"
#>
param(
    [System.UInt64] $MinimumSize = 8GB,
    [System.UInt64] $MaximumSize = 16GB,
    [System.String] $DiskRoot = "C:"
)
$ErrorActionPreference = "Stop"

# Native paging-file API. Adapted from al-cheb/configure-pagefile-action
# (MIT) - enables SeCreatePagefilePrivilege and calls NtCreatePagingFile,
# which activates the pagefile immediately without a reboot.
$source = @'
using System;
using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Principal;
using System.Text;
using Microsoft.Win32;
using Microsoft.Win32.SafeHandles;
namespace StgrUtil
{
class NativeMethods
{
[StructLayout(LayoutKind.Sequential)]
internal struct LUID
{
internal uint LowPart;
internal uint HighPart;
}
[StructLayout(LayoutKind.Sequential)]
internal struct LUID_AND_ATTRIBUTES
{
internal LUID Luid;
internal uint Attributes;
}
[StructLayout(LayoutKind.Sequential)]
internal struct TOKEN_PRIVILEGE
{
internal uint PrivilegeCount;
internal LUID_AND_ATTRIBUTES Privilege;
internal static readonly uint Size = (uint)Marshal.SizeOf(typeof(TOKEN_PRIVILEGE));
}
[StructLayoutAttribute(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
internal struct UNICODE_STRING
{
internal UInt16 length;
internal UInt16 maximumLength;
internal string buffer;
}
[DllImport("kernel32.dll", SetLastError=true)]
internal static extern IntPtr LocalFree(IntPtr handle);
[DllImport("advapi32.dll", ExactSpelling = true, CharSet = CharSet.Unicode, SetLastError = true, PreserveSig = false)]
internal static extern bool LookupPrivilegeValueW(
[In] string lpSystemName,
[In] string lpName,
[Out] out LUID luid
);
[DllImport("advapi32.dll", SetLastError = true, PreserveSig = false)]
internal static extern bool AdjustTokenPrivileges(
[In] SafeCloseHandle tokenHandle,
[In] bool disableAllPrivileges,
[In] ref TOKEN_PRIVILEGE newState,
[In] uint bufferLength,
[Out] out TOKEN_PRIVILEGE previousState,
[Out] out uint returnLength
);
[DllImport("advapi32.dll", CharSet = CharSet.Auto, SetLastError = true, PreserveSig = false)]
internal static extern bool OpenProcessToken(
[In] IntPtr processToken,
[In] int desiredAccess,
[Out] out SafeCloseHandle tokenHandle
);
[DllImport("ntdll.dll", CharSet = CharSet.Unicode, SetLastError = true, CallingConvention = CallingConvention.StdCall)]
internal static extern Int32 NtCreatePagingFile(
[In] ref UNICODE_STRING pageFileName,
[In] ref Int64 minimumSize,
[In] ref Int64 maximumSize,
[In] UInt32 flags
);
[DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
internal static extern uint QueryDosDeviceW(
string lpDeviceName,
StringBuilder lpTargetPath,
int ucchMax
);
}
public sealed class SafeCloseHandle : SafeHandleZeroOrMinusOneIsInvalid
{
[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
internal extern static bool CloseHandle(IntPtr handle);
private SafeCloseHandle() : base(true)
{
}
public SafeCloseHandle(IntPtr preexistingHandle, bool ownsHandle) : base(ownsHandle)
{
SetHandle(preexistingHandle);
}
override protected bool ReleaseHandle()
{
return CloseHandle(handle);
}
}
public class PageFile
{
public static void SetPageFileSize(long minimumValue, long maximumValue, string lpDeviceName)
{
SetPageFilePrivilege();
StringBuilder lpTargetPath = new StringBuilder(260);
UInt32 resultQueryDosDevice = NativeMethods.QueryDosDeviceW(lpDeviceName, lpTargetPath, lpTargetPath.Capacity);
if (resultQueryDosDevice == 0)
{
throw new Win32Exception(Marshal.GetLastWin32Error(), "QueryDosDeviceW failed for " + lpDeviceName);
}
string pageFilePath = lpTargetPath.ToString() + "\\pagefile.sys";
NativeMethods.UNICODE_STRING pageFileName = new NativeMethods.UNICODE_STRING
{
length = (ushort)(pageFilePath.Length * 2),
maximumLength = (ushort)(2 * (pageFilePath.Length + 1)),
buffer = pageFilePath
};
Int32 resultNtCreatePagingFile = NativeMethods.NtCreatePagingFile(ref pageFileName, ref minimumValue, ref maximumValue, 0);
if (resultNtCreatePagingFile != 0)
{
// NtCreatePagingFile returns an NTSTATUS; surface it in hex so CI logs
// are self-explanatory (e.g. 0xC0000035 STATUS_OBJECT_NAME_COLLISION,
// 0xC000007F STATUS_DISK_FULL).
throw new Win32Exception(
unchecked((int)resultNtCreatePagingFile),
string.Format(
"NtCreatePagingFile failed for {0} (NTSTATUS 0x{1:X8})",
pageFilePath, unchecked((uint)resultNtCreatePagingFile)));
}
Console.WriteLine("PageFile created: {0} / {1} bytes at {2}", minimumValue, maximumValue, pageFilePath);
}
static void SetPageFilePrivilege()
{
const int SE_PRIVILEGE_ENABLED = 0x00000002;
const int AdjustPrivileges = 0x00000020;
const int Query = 0x00000008;
NativeMethods.LUID luid;
NativeMethods.LookupPrivilegeValueW(null, "SeCreatePagefilePrivilege", out luid);
SafeCloseHandle hToken;
NativeMethods.OpenProcessToken(
Process.GetCurrentProcess().Handle,
AdjustPrivileges | Query,
out hToken
);
NativeMethods.TOKEN_PRIVILEGE previousState;
NativeMethods.TOKEN_PRIVILEGE newState;
uint previousSize = 0;
newState.PrivilegeCount = 1;
newState.Privilege.Luid = luid;
newState.Privilege.Attributes = SE_PRIVILEGE_ENABLED;
NativeMethods.AdjustTokenPrivileges(hToken, false, ref newState, NativeMethods.TOKEN_PRIVILEGE.Size, out previousState, out previousSize);
}
}
}
'@

Add-Type -TypeDefinition $source

Write-Host "Adding pagefile on ${DiskRoot} (min $MinimumSize / max $MaximumSize)..."

# Pre-flight 1: is there already an adequate pagefile on the target drive?
# (NtCreatePagingFile fails with STATUS_OBJECT_NAME_COLLISION if one exists.)
$driveLetter = $DiskRoot.TrimEnd(':')
$existing = Get-CimInstance Win32_PageFileUsage | Where-Object {
    $_.Name -match "^$([regex]::Escape($driveLetter))" -and $_.AllocatedBaseSize -gt 0
}
$active = $null
if ($existing) {
    if ($existing.AllocatedBaseSize -ge [long]($MinimumSize / 1MB)) {
        Write-Host "Adequate pagefile already exists on $DiskRoot ($($existing.AllocatedBaseSize) MB allocated) - skipping creation"
        $active = $existing
    } else {
        throw "Existing pagefile on $DiskRoot is only $($existing.AllocatedBaseSize) MB (< $MinimumSize). Remove it or choose another drive."
    }
}

# Pre-flight 2: enough free space for the minimum pagefile size?
if (-not $active) {
    $vol = Get-Volume -DriveLetter $driveLetter
    if (-not $vol -or $vol.SizeRemaining -lt ($MinimumSize + 1GB)) {
        $free = if ($vol) { $vol.SizeRemaining } else { 0 }
        throw "Not enough free space on $DiskRoot for a $MinimumSize pagefile (free: $free bytes)."
    }
    Write-Host "Free space on $DiskRoot: $([math]::Round($vol.SizeRemaining / 1GB, 1)) GB"

    # Create with one retry: on a freshly provisioned runner the native call
    # can transiently fail (image pagefile still initializing).
    $created = $false
    for ($attempt = 1; $attempt -le 2 -and -not $created; $attempt++) {
        try {
            [StgrUtil.PageFile]::SetPageFileSize([long]$MinimumSize, [long]$MaximumSize, $DiskRoot)
            $created = $true
        } catch {
            $ex = $_.Exception
            if ($ex.InnerException) { $ex = $ex.InnerException }
            Write-Host "NtCreatePagingFile attempt $attempt/2 failed: $($ex.Message)"
            if ($attempt -lt 2) {
                Write-Host "Retrying in 15 s..."
                Start-Sleep -Seconds 15
            } else {
                throw
            }
        }
    }
}

# Give the OS a moment to register the new pagefile, then report.
for ($i = 0; $i -lt 12; $i++) {
    Start-Sleep -Seconds 5
    $active = Get-CimInstance Win32_PageFileUsage | Where-Object {
        $_.Name -match "^$([regex]::Escape($driveLetter))" -and $_.AllocatedBaseSize -gt 0
    }
    if ($active) { break }
    Write-Host "Probe $($i + 1): pagefile on $DiskRoot not visible yet, waiting..."
}
Get-CimInstance Win32_PageFileUsage | Format-Table -AutoSize
if (-not $active) {
    throw "Pagefile on $DiskRoot did not activate after creation - the ThinLTO build would run out of memory."
}
Write-Host "$DiskRoot pagefile active ($($active.AllocatedBaseSize) MB allocated)"
