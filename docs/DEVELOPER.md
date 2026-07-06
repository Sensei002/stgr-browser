# STGR Browser Developer Guide

## Development Workflow

### 1. Setup Development Environment

```bash
git clone https://github.com/stgr-browser/stgr-browser.git
cd stgr-browser
./scripts/setup.sh
```

### 2. Make Changes

STGR Browser consists of two codebases:

1. **STGR-specific code** (`branding/`, `config/`, `scripts/`, `docs/`, `patches/`)
   - These are in the main `stgr-browser` repo
   - Edit directly and commit

2. **Firefox source code** (`gecko-dev/`)
   - Cloned by `setup.sh`
   - Contains the actual browser engine
   - Make changes and create patches:
     ```bash
     cd gecko-dev
     # Make changes
     git diff > ../patches/XXXX-description.patch
     ```

### 3. Testing Changes

```bash
# Run full test suite (takes hours)
./scripts/build.sh test

# Run specific tests
cd gecko-dev
./mach test browser/components/gaming/test
./mach test toolkit/components/telemetry

# Run linting
./mach lint
./mach clang-format
```

### 4. Create a Build

```bash
# Incremental build (5-30 min)
./scripts/build.sh build

# Run after build
./scripts/build.sh run
```

## Coding Standards

### C++

- Follow [Mozilla C++ Coding Standards](https://firefox-source-docs.mozilla.org/code-quality/coding-style/index.html)
- Use modern C++17/20 features where appropriate
- No raw pointers where smart pointers suffice
- Use `nsCOMPtr` for XPCOM objects
- RAII for resource management
- No memory leaks (use ASAN builds to verify)

### Rust

- Follow [Rust Style Guide](https://doc.rust-lang.org/nightly/style-guide/)
- Use `cargo clippy` for linting
- Prefer safe Rust over `unsafe`
- Document `unsafe` blocks with SAFETY comments
- Use `moz_assert` for debug assertions

### JavaScript

- Follow Mozilla JS coding conventions
- Use `ChromeUtils.importESModule` for module imports
- Use `Services.*` for XPCOM services
- Lazy initialization for all components
- No telemetry calls in STGR-specific code

### Python (Build System)

- Follow PEP 8
- Use `moz.build` files for build configuration
- Document build targets

## STGR Component Development

### Creating a New Component

1. Create component directory:
   ```bash
   mkdir -p gecko-dev/browser/components/stgr-<name>
   ```

2. Create `moz.build`:
   ```python
   DIRS += ['stgr-<name>']
   ```

3. Create main JS module:
   ```javascript
   // gecko-dev/browser/components/stgr-<name>/StgrName.jsm
   var EXPORTED_SYMBOLS = ["StgrName"];
   
   class StgrName {
     constructor() {
       // Initialize
     }
   }
   ```

4. Register in `browser/components/moz.build`

### Working with Preferences

STGR preferences live in `config/stgr-prefs.js`. For runtime preference access:

```javascript
// Reading
Services.prefs.getBoolPref("stgr.feature.enabled");
Services.prefs.getIntPref("stgr.feature.limit");
Services.prefs.getCharPref("stgr.feature.url");

// Writing
Services.prefs.setBoolPref("stgr.feature.enabled", true);
Services.prefs.setIntPref("stgr.feature.limit", 42);
```

### Adding Strings for Localization

STGR uses Fluent (FTL) for localization:

```
# gecko-dev/stgr/locales/en-US/stgr/stgr.ftl
stgr-gaming-mode-activated = Gaming Mode Activated
stgr-gaming-mode-deactivated = Gaming Mode Deactivated
```

## Patch Management

### Creating Patches

```bash
# After making changes in gecko-dev/
cd gecko-dev
git add <files>
git diff --cached > ../patches/XXXX-description.patch
```

### Updating Patches

```bash
# When Firefox source updates
cd gecko-dev
git checkout new-firefox-version
git am ../patches/0001-*.patch
# Fix conflicts if any
git diff --cached > ../patches/0001-updated.patch
```

## Debugging

### Debug Build

```bash
./scripts/build.sh build-debug
```

### Debugging Tools

- **ASAN**: `./mach build --enable-address-sanitizer`
- **TSAN**: `./mach build --enable-thread-sanitizer`
- **Valgrind**: `valgrind ./mach run`
- **Profiling**: `./mach run --enable-profiling`
- **Logging**: `./mach run -console`

### STGR-Specific Logging

```javascript
// In STGR components
Services.console.logStringMessage("STGR: message");
```

## Performance Profiling

### Built-in Profiler

```bash
# Start with profiler
./mach run --start-debugger

# In the browser
# Shift+F5 to open profiler
# Record and analyze performance
```

### Custom Profiling Markers

```javascript
ChromeUtils.addProfilerMarker("STGR: ComponentName: Operation");
```

## Architecture Decisions

### Why STGR uses Firefox's build system

- Full web standards compatibility
- Mature extension ecosystem
- Battle-tested rendering engine
- Active security patching
- Strong privacy foundations

### What STGR changes

- Strips all Mozilla services and telemetry
- Adds Gaming Mode
- Optimizes for memory and startup
- Custom UI theme
- Privacy-by-default configuration

### What STGR keeps

- Full Gecko rendering engine
- SpiderMonkey JavaScript engine
- WebRender GPU rendering
- Extension API compatibility
- Security sandboxing
- Standards compliance
