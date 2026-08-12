#!/bin/sh
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# STGR Browser branding identity (mirrors browser/branding/official/configure.sh).
#
# NOTE: MOZ_APP_ID intentionally keeps the upstream Firefox application id so
# that WebExtensions declaring applications.gecko.id = {ec8030f7-…} remain
# compatible — full Firefox extension compatibility is a hard requirement.
# The profile directory is intentionally DIFFERENT from Mozilla Firefox's:
# %APPDATA%\STGR\STGR Browser\Profiles (never touches Firefox user data).

MOZ_APP_DISPLAYNAME="STGR Browser"
MOZ_APP_VENDOR="STGR"
MOZ_APP_NAME=stgr
MOZ_APP_BASENAME="STGR Browser"
MOZ_APP_PROFILE="STGR Browser"
MOZ_APP_ID="{ec8030f7-c20a-464f-9b0e-13a3a9e97384}"
MOZ_APP_UA_NAME=STGR
