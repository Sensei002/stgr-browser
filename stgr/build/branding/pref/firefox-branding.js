/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

// This file contains branding-specific preferences for STGR Browser.
// It is installed to bin/browser/defaults/preferences/firefox-branding.js
// via JS_PREFERENCE_FILES in the staging moz.build (see branding-common
// template). All URLs point at the STGR project, not Mozilla.

pref("startup.homepage_override_url", "https://steigerdojo.mvp.bd/");
pref("startup.homepage_welcome_url", "https://steigerdojo.mvp.bd/");
pref("startup.homepage_welcome_url.additional", "");
// The time interval between checks for a new version (in seconds)
pref("app.update.interval", 7200); // 2 hours
// Give the user x seconds to react before showing the big UI. default=12 hours
pref("app.update.promptWaitTime", 43200);
// URL user can browse to manually if for some reason all update installation
// attempts fail.
pref("app.update.url.manual", "https://github.com/Sensei002/stgr-browser/releases");
// A default value for the "More information about this update" link
// supplied in the "An update is available" page of the update wizard.
pref("app.update.url.details", "https://github.com/Sensei002/stgr-browser/releases");

pref("app.releaseNotesURL", "https://github.com/Sensei002/stgr-browser/releases");
pref("app.releaseNotesURL.aboutDialog", "https://github.com/Sensei002/stgr-browser/releases");
pref("app.releaseNotesURL.prompt", "https://github.com/Sensei002/stgr-browser/releases");

// The number of days a binary is permitted to be old
// without checking for an update.  This assumes that
// app.update.checkInstallTime is true.
pref("app.update.checkInstallTime.days", 2);

// Give the user x seconds to reboot before showing a badge on the hamburger
// button. default=immediately
pref("app.update.badgeWaitTime", 0);

// Number of usages of the web console.
// If this is less than 5, then pasting code into the web console is disabled
pref("devtools.selfxss.count", 5);
