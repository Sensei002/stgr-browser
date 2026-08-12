# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# STGR Browser NSIS branding. This file intentionally contains no Mozilla
# product, URL, or code-signing identity claims.
!define BrandFullNameInternal "STGR Browser"
!define BrandFullName "STGR Browser"
!define CompanyName "STEiGER Dojo"
!define URLInfoAbout "https://steigerdojo.mvp.bd"
!define URLUpdateInfo "https://github.com/Sensei002/stgr-browser/releases"
!define HelpLink "https://github.com/Sensei002/stgr-browser/security"
!define URLStubDownloadX86 "https://github.com/Sensei002/stgr-browser/releases/latest"
!define URLStubDownloadAMD64 "https://github.com/Sensei002/stgr-browser/releases/latest"
!define URLStubDownloadAArch64 "https://github.com/Sensei002/stgr-browser/releases/latest"
!define URLManualDownload "https://github.com/Sensei002/stgr-browser/releases/latest"
!define URLSystemRequirements "https://github.com/Sensei002/stgr-browser#building"
!define Channel "stable"

# STGR releases are not Mozilla-signed. Certificate identity defines are
# intentionally omitted; they are only needed by the optional stub installer.

# Dialog units and colors for the STGR dark-red/black installer theme.
!define PROFILE_CLEANUP_LABEL_TOP "50u"
!define PROFILE_CLEANUP_LABEL_LEFT "22u"
!define PROFILE_CLEANUP_LABEL_WIDTH "175u"
!define PROFILE_CLEANUP_LABEL_HEIGHT "100u"
!define PROFILE_CLEANUP_LABEL_ALIGN "left"
!define PROFILE_CLEANUP_CHECKBOX_LEFT "22u"
!define PROFILE_CLEANUP_CHECKBOX_WIDTH "175u"
!define PROFILE_CLEANUP_BUTTON_LEFT "22u"
!define INSTALL_HEADER_TOP "70u"
!define INSTALL_HEADER_LEFT "22u"
!define INSTALL_HEADER_WIDTH "180u"
!define INSTALL_HEADER_HEIGHT "100u"
!define INSTALL_BODY_LEFT "22u"
!define INSTALL_BODY_WIDTH "180u"
!define INSTALL_INSTALLING_TOP "115u"
!define INSTALL_INSTALLING_LEFT "270u"
!define INSTALL_INSTALLING_WIDTH "150u"
!define INSTALL_PROGRESS_BAR_TOP "100u"
!define INSTALL_PROGRESS_BAR_LEFT "270u"
!define INSTALL_PROGRESS_BAR_WIDTH "150u"
!define INSTALL_PROGRESS_BAR_HEIGHT "12u"
!define PROFILE_CLEANUP_CHECKBOX_TOP_MARGIN "12u"
!define PROFILE_CLEANUP_BUTTON_TOP_MARGIN "12u"
!define PROFILE_CLEANUP_BUTTON_X_PADDING "80u"
!define PROFILE_CLEANUP_BUTTON_Y_PADDING "8u"
!define INSTALL_BODY_TOP_MARGIN "20u"
!define INSTALL_HEADER_FONT_SIZE 20
!define INSTALL_HEADER_FONT_WEIGHT 600
!define INSTALL_INSTALLING_FONT_SIZE 15
!define INSTALL_INSTALLING_FONT_WEIGHT 600
!define COMMON_TEXT_COLOR 0xFFFFFF
!define COMMON_BACKGROUND_COLOR 0x080808
!define INSTALL_INSTALLING_TEXT_COLOR 0xFFFFFF
!define PROGRESS_BAR_BACKGROUND_COLOR 0x2A2020
