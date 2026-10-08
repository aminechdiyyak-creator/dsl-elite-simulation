import os from 'os';
import path from 'path';
import fs from 'fs';
import { get } from '../utils/config.js';

const HOME = os.homedir();

const DEFAULT_CHROME_PATHS = {
  darwin: [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    path.join(HOME, 'Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
  ],
  linux: ['/opt/google/chrome/chrome', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable'],
  win32: [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  ],
};

// Dedicated profile: you sign in to Google once in it. Recent Chrome (136+) ignores
// --remote-debugging-port on the default user-data-dir, so this is also the reliable path.
const DEDICATED_USER_DATA_DIR = path.join(HOME, '.google-flow-mcp', 'chrome-profile');

const expandHome = (p) => (p && p.startsWith('~') ? path.join(HOME, p.slice(1)) : p);

function findChrome() {
  const configured = expandHome(get('chromePath'));
  if (configured) return configured;
  const candidates = DEFAULT_CHROME_PATHS[process.platform] || [];
  return candidates.find((p) => fs.existsSync(p)) || candidates[0];
}

/**
 * Chrome launch settings, from config/flow.config.json with per-OS defaults.
 *
 * - chromeUserDataDir / chromeProfile: the profile Chrome runs with
 *   (default: a dedicated ~/.google-flow-mcp/chrome-profile, profile "Default").
 * - extraChromeArgs: additional Chrome switches (array of strings).
 * - copyProfile: true copies that profile into a temp dir first (needed when pointing
 *   at your everyday Chrome profile). The copy holds your Google session cookies and is
 *   deleted when the browser closes or the server exits.
 */
export function chromeSettings() {
  const userDataDir = expandHome(get('chromeUserDataDir')) || DEDICATED_USER_DATA_DIR;
  return {
    chromePath: findChrome(),
    userDataDir,
    profile: get('chromeProfile', 'Default'),
    copyProfile: get('copyProfile', false),
    extraArgs: get('extraChromeArgs', []),
    tempRoot: os.tmpdir(),
  };
}
