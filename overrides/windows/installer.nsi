; =============================================================================
; STGR Browser - Windows installer (NSIS 3 / Modern UI 2)
; =============================================================================
; Driven entirely by /D defines from scripts/build.py. Do not hardcode product
; strings here; if a value is missing add it to branding/brand.json and pass it
; through build.py.
;
; Install model: per-user, no UAC. A browser that needs admin to update is a
; browser that stops getting updated. Policies therefore go to HKCU, which
; Chromium reads with the same precedence as HKLM for a per-user install.
; =============================================================================

Unicode true

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; ── defaults (overridden by build.py) ────────────────────────────────────────
!ifndef VERSION
  !define VERSION "0.1.0"
!endif
!ifndef VI_VERSION
  !define VI_VERSION "0.1.0.0"
!endif
!ifndef PRODUCT_NAME
  !define PRODUCT_NAME "STGR Browser"
!endif
!ifndef PRODUCT_SHORT
  !define PRODUCT_SHORT "STGR"
!endif
!ifndef PUBLISHER
  !define PUBLISHER "STGR"
!endif
!ifndef PRODUCT_URL
  !define PRODUCT_URL "https://github.com/stgr-browser/stgr-browser"
!endif
!ifndef APP_ID
  !define APP_ID "com.stgr.browser"
!endif
!ifndef PROTOCOL
  !define PROTOCOL "stgr"
!endif
!ifndef SRCDIR
  !error "SRCDIR must be defined"
!endif
!ifndef OUTFILE
  !error "OUTFILE must be defined"
!endif
!ifndef ICONFILE
  !define ICONFILE ""
!endif
!ifndef POLICYSCRIPT
  !define POLICYSCRIPT ""
!endif
!ifndef WIZARDIMAGE
  !define WIZARDIMAGE ""
!endif
!ifndef HEADERIMAGE
  !define HEADERIMAGE ""
!endif

; ── metadata ────────────────────────────────────────────────────────────────
Name "${PRODUCT_NAME} ${VERSION}"
OutFile "${OUTFILE}"
InstallDir "$LOCALAPPDATA\Programs\${PRODUCT_SHORT}"
InstallDirRegKey HKCU "Software\${PRODUCT_SHORT}\Browser" "InstallDir"
RequestExecutionLevel user
SetCompressor /SOLID lzma
SetCompressorDictSize 64
SetDatablockOptimize on
CRCCheck on
XPStyle on
BrandingText "${PRODUCT_NAME} ${VERSION}"

VIProductVersion "${VI_VERSION}"
VIAddVersionKey "ProductName"     "${PRODUCT_NAME}"
VIAddVersionKey "ProductVersion"  "${VERSION}"
VIAddVersionKey "FileVersion"     "${VERSION}"
VIAddVersionKey "CompanyName"     "${PUBLISHER}"
VIAddVersionKey "FileDescription" "${PRODUCT_NAME} Setup"
VIAddVersionKey "LegalCopyright"  "Copyright (c) 2026 ${PUBLISHER}"

!if "${ICONFILE}" != ""
  Icon "${ICONFILE}"
  UninstallIcon "${ICONFILE}"
  !define MUI_ICON "${ICONFILE}"
  !define MUI_UNICON "${ICONFILE}"
!endif

!if "${WIZARDIMAGE}" != ""
  !define MUI_WELCOMEFINISHPAGE_BITMAP "${WIZARDIMAGE}"
!endif
!if "${HEADERIMAGE}" != ""
  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "${HEADERIMAGE}"
  !define MUI_HEADERIMAGE_RIGHT
!endif

!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN "$INSTDIR\STGRBrowser.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${PRODUCT_NAME}"
!define MUI_FINISHPAGE_LINK "Project homepage"
!define MUI_FINISHPAGE_LINK_LOCATION "${PRODUCT_URL}"
!define MUI_WELCOMEPAGE_TITLE "${PRODUCT_NAME} ${VERSION}"
!define MUI_WELCOMEPAGE_TEXT "Host. Compete. Broadcast.$\r$\n$\r$\nThis will install ${PRODUCT_NAME}, a Chromium-based browser built for speed, low memory use and zero telemetry.$\r$\n$\r$\nYour existing browsers and profiles are not touched."

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ── install ─────────────────────────────────────────────────────────────────
Section "!${PRODUCT_NAME}" SEC_MAIN
  SectionIn RO
  SetOutPath "$INSTDIR"
  SetOverwrite on

  ; The staged tree already contains the engine, launcher, extensions and prefs.
  File /r "${SRCDIR}\*.*"

  ; Per-user policies: telemetry off, DDG as default engine, autoplay blocked.
  !if "${POLICYSCRIPT}" != ""
    !include "${POLICYSCRIPT}"
  !endif

  WriteRegStr HKCU "Software\${PRODUCT_SHORT}\Browser" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "Software\${PRODUCT_SHORT}\Browser" "Version" "${VERSION}"
SectionEnd

Section "Shortcuts" SEC_SHORTCUTS
  SetOutPath "$INSTDIR"

  CreateDirectory "$SMPROGRAMS\${PRODUCT_SHORT}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_SHORT}\${PRODUCT_NAME}.lnk" \
    "$INSTDIR\STGRBrowser.exe" "" "$INSTDIR\STGRBrowser.exe" 0
  CreateShortCut "$SMPROGRAMS\${PRODUCT_SHORT}\${PRODUCT_NAME} (Low RAM).lnk" \
    "$INSTDIR\STGRBrowser.exe" "--stgr-lowmem" "$INSTDIR\STGRBrowser.exe" 0
  CreateShortCut "$SMPROGRAMS\${PRODUCT_SHORT}\Uninstall ${PRODUCT_NAME}.lnk" \
    "$INSTDIR\Uninstall.exe"

  CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" \
    "$INSTDIR\STGRBrowser.exe" "" "$INSTDIR\STGRBrowser.exe" 0
SectionEnd

Section "Integration" SEC_INTEGRATION
  ; stgr:// protocol so links and the NTP can hand work to the browser.
  WriteRegStr HKCU "Software\Classes\${PROTOCOL}" "" "URL:${PRODUCT_NAME} Protocol"
  WriteRegStr HKCU "Software\Classes\${PROTOCOL}" "URL Protocol" ""
  WriteRegStr HKCU "Software\Classes\${PROTOCOL}\DefaultIcon" "" "$INSTDIR\STGRBrowser.exe,0"
  WriteRegStr HKCU "Software\Classes\${PROTOCOL}\shell\open\command" "" '"$INSTDIR\STGRBrowser.exe" "%1"'

  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\App Paths\stgr.exe" "" "$INSTDIR\STGRBrowser.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\App Paths\stgr.exe" "Path" "$INSTDIR"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0

  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "Publisher" "${PUBLISHER}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "DisplayIcon" "$INSTDIR\STGRBrowser.exe,0"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "URLInfoAbout" "${PRODUCT_URL}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "QuietUninstallString" '"$INSTDIR\Uninstall.exe" /S'
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "NoRepair" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "EstimatedSize" $0
SectionEnd

; ── uninstall ───────────────────────────────────────────────────────────────
Section "Uninstall"
  ; Kill a running instance so files are not locked.
  ExecWait '"$INSTDIR\STGRBrowser.exe" --stgr-quit' $0
  Sleep 400

  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_SHORT}\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_SHORT}\${PRODUCT_NAME} (Low RAM).lnk"
  Delete "$SMPROGRAMS\${PRODUCT_SHORT}\Uninstall ${PRODUCT_NAME}.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_SHORT}"

  RMDir /r "$INSTDIR"

  DeleteRegKey HKCU "Software\Classes\${PROTOCOL}"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\App Paths\stgr.exe"
  DeleteRegKey HKCU "Software\Policies\Chromium"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}"
  DeleteRegKey HKCU "Software\${PRODUCT_SHORT}\Browser"

  ; The user profile is deliberately preserved: bookmarks and passwords are
  ; user data, not install artefacts. Removing it is an explicit manual step.
SectionEnd
