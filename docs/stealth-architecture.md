# Stealth Architecture & Anti-Bot Evasion

Modern web applications protect content using sophisticated client-side anti-bot systems such as **Cloudflare Turnstile**, **DataDome**, **PerimeterX**, and **Akamai**.

Standard browser automation frameworks (e.g. vanilla Playwright, Puppeteer, Selenium) fail on these challenges due to low-level runtime leakages.

---

## 🔍 How Bot Detectors Identify Automation

1. **Chrome DevTools Protocol (CDP) Telemetry**:
   Vanilla Playwright calls `Runtime.enable` to control the page. Anti-bot scripts intercept this and detect active CDP bindings immediately.
2. **`navigator.webdriver` Property**:
   Headless Chromium sets `navigator.webdriver = true` by default.
3. **Missing `window.chrome.runtime` Objects**:
   Standard Chromium headless does not properly populate `window.chrome` sub-objects.
4. **Permissions Mocks**:
   Queries to `navigator.permissions.query({ name: 'notifications' })` return automated states.

---

## 🛡️ The Patchtroy Solution

Patchtroy implements a four-tiered stealth defense:

### 1. C++ Patchright Engine
Patchtroy replaces standard Playwright with **Patchright**, an undetected Chromium driver that removes CDP hooks and internal debugging flags at the C++ source level before the binary executes.

### 2. Runtime Stealth Injections
Before navigation starts, Patchtroy injects stealth emulation scripts:
- Deletes or sets `navigator.webdriver` to `undefined`.
- Mocks realistic `window.chrome` with `runtime`, `loadTimes`, `csi`, and `app`.
- Emulates realistic plugin arrays and standard language lists.
- Overrides `navigator.permissions.query` to return realistic `'default'` states.

### 3. Realistic Fingerprint Rotation
- Viewport size defaults to standard 1280x800 desktop.
- Modern desktop User-Agent headers are randomized per session.

### 4. Automatic Fault-Tolerant HTTP Fallback
If headless Chromium times out or is blocked, Patchtroy automatically falls back to an asynchronous HTTP request using `httpx` with realistic browser headers, ensuring uninterrupted pipeline execution.
