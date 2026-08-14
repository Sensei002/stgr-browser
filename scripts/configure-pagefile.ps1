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

The runner image ships a small pagefile on the target drive (e.g. 2944 MB on
C: with the current windows-2022 image). The image's own WMI-based resize
(Win32_PageFileSetting) requires a reboot, so we use the native
NtCreatePagingFile API (the same technique battle-tested in
al-cheb/configure-pagefile-action) which takes effect immediately. One
important subtlety: NtCreatePagingFile can never DELETE a pagefile - passing
0 for the minimum is below the kernel's 1 MB floor and fails with
STATUS_INVALID_PARAMETER_2 (0xC00000F0). Instead, calling it with the SAME
file path and larger sizes puts the kernel into its "paging file extension"
mode, which resizes an in-use pagefile live (it only extends: a proposed
minimum below the current minimum fails with STATUS_INVALID_PARAMETER_2, and
a proposed maximum below the current maximum fails with
STATUS_INVALID_PARAMETER_3). See:
geoffchappell.com/studies/windows/km/ntoskrnl/api/mm/modwrite/create.htm

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
$targetMB = [long]($MinimumSize / 1MB)

function Get-TargetPagefile {
    Get-CimInstance Win32_PageFileUsage | Where-Object {
        $_.Name -match "^$([regex]::Escape($driveLetter))" -and $_.AllocatedBaseSize -gt 0
    }
}

# Pre-flight 1: is there already a pagefile on the target drive?
$existing = Get-TargetPagefile
$active = $null
if ($existing) {
    if ($existing.AllocatedBaseSize -ge $targetMB) {
        Write-Host "Adequate pagefile already exists on $DiskRoot ($($existing.AllocatedBaseSize) MB allocated) - nothing to do"
        $active = $existing
    } else {
        # The runner image ships a small pagefile on this drive (e.g. 2944 MB
        # on the current windows-2022 image). NtCreatePagingFile cannot DELETE
        # a pagefile - a 0 minimum is below the kernel's 1 MB floor and fails
        # with STATUS_INVALID_PARAMETER_2 (0xC00000F0). Calling it with the
        # SAME path and larger sizes instead triggers the kernel's "paging
        # file extension" mode, which resizes the in-use pagefile live. The
        # extension only grows: a 0xC00000F0 there means the pagefile already
        # meets our minimum, which we treat as success.
        Write-Host "Existing pagefile on $DiskRoot is only $($existing.AllocatedBaseSize) MB - extending it to $MinimumSize / $MaximumSize..."
    }
}

# Pre-flight 2: enough free space for the minimum pagefile size?
if (-not $active) {
    $vol = Get-Volume -DriveLetter $driveLetter
    if (-not $vol -or $vol.SizeRemaining -lt ($MinimumSize + 1GB)) {
        $free = if ($vol) { $vol.SizeRemaining } else { 0 }
        throw "Not enough free space on $DiskRoot for a $MinimumSize pagefile (free: $free bytes)."
    }
    Write-Host "Free space on ${DiskRoot}: $([math]::Round($vol.SizeRemaining / 1GB, 1)) GB"

    # Create (no pagefile yet) or extend (small image pagefile) with retries:
    # on a freshly provisioned runner the native call can transiently fail
    # while the image's own pagefile is still initializing. Extension mode
    # rejects a proposed maximum below the file's current maximum with
    # STATUS_INVALID_PARAMETER_3 (0xC00000F1), so on that error raise the
    # ceiling and try again.
    $sized = $false
    $maxCandidates = @([long]$MaximumSize, 32GB, 64GB, 128GB)
    foreach ($maxCandidate in $maxCandidates) {
        if ($sized) { break }
        for ($attempt = 1; $attempt -le 2; $attempt++) {
            try {
                [StgrUtil.PageFile]::SetPageFileSize([long]$MinimumSize, [long]$maxCandidate, $DiskRoot)
                $sized = $true
                if ([long]$maxCandidate -ne [long]$MaximumSize) {
                    Write-Host "Pagefile sized with a $maxCandidate ceiling (requested $MaximumSize was below the file's current maximum)"
                }
                break
            } catch {
                $ex = $_.Exception
                if ($ex.InnerException) { $ex = $ex.InnerException }
                if ($ex.Message -match '0xC00000F0') {
                    # Proposed minimum < current minimum => the pagefile already
                    # satisfies our requirement.
                    Write-Host "Existing pagefile minimum already meets $MinimumSize - treating as sized"
                    $sized = $true
                    break
                }
                if ($ex.Message -match '0xC00000F1') {
                    # Proposed maximum < current maximum: raise the ceiling.
                    Write-Host "NtCreatePagingFile: ceiling $maxCandidate below the file's current maximum - raising it"
                    break
                }
                Write-Host "NtCreatePagingFile attempt $attempt/2 failed: $($ex.Message)"
                if ($attempt -lt 2) {
                    Write-Host "Retrying in 15 s..."
                    Start-Sleep -Seconds 15
                }
            }
        }
    }
    if (-not $sized) {
        throw "Could not size the pagefile on ${DiskRoot} to $MinimumSize - the ThinLTO build would run out of memory."
    }
}

# Give the OS a moment to register the new size, then report.
for ($i = 0; $i -lt 12; $i++) {
    Start-Sleep -Seconds 5
    $active = Get-TargetPagefile
    if ($active -and $active.AllocatedBaseSize -ge $targetMB) { break }
    $cur = if ($active) { "$($active.AllocatedBaseSize) MB" } else { "absent" }
    Write-Host "Probe $($i + 1): pagefile on $DiskRoot not at ${targetMB} MB yet ($cur), waiting..."
}
Get-CimInstance Win32_PageFileUsage | Format-Table -AutoSize
if (-not $active -or $active.AllocatedBaseSize -lt $targetMB) {
    $got = if ($active) { "$($active.AllocatedBaseSize) MB" } else { "absent" }
    throw "Pagefile on $DiskRoot did not reach $targetMB MB (got $got) - the ThinLTO build would run out of memory."
}
Write-Host "$DiskRoot pagefile active ($($active.AllocatedBaseSize) MB allocated)"
