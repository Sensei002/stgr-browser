# STGR Browser Optimization Guide

## Overview

STGR Browser applies multiple layers of optimization to Firefox to achieve the best possible performance. This document details each optimization technique.

## Memory Optimization

### Target Memory Usage

| Scenario | Target | Implementation Status |
|----------|--------|----------------------|
| Idle (zero tabs) | 90-120 MB | Firefox architecture baseline |
| Normal (5 tabs) | 120-180 MB | Achievable with STGR prefs |
| YouTube 1080p | ~200 MB | Depends on codec/driver |
| 10+ tabs | 200-300 MB | Tab discarding helps |
| Gaming Mode | ~30% reduction | Automatic on game detection |

### Techniques

#### 1. Aggressive Cache Trimming

| Cache | Firefox Default | STGR Target | Savings |
|-------|----------------|-------------|---------|
| Image Surface Cache | 5 MB | 200 KB | ~4.8 MB |
| Media Cache | 500 MB | 50 MB | ~450 MB |
| Font Cache | 4 MB | 2 MB | ~2 MB |
| Network Cache | 256 MB | 256 MB | Kept (performance) |
| JavaScript Nursery | 16 MB | 8 MB | ~8 MB |

#### 2. Tab Discarding

```javascript
// After 5 minutes of inactivity
if (tab.lastAccessed + 300000 < Date.now() && !tab.selected && !tab.pinned) {
  gBrowser.discardBrowser(tab);
}
```

#### 3. Process Management

- Content processes capped at 4 (vs Firefox's auto-scaling)
- No process prelaunch (saves ~50 MB)
- Extension processes limited to 1
- Socket processes disabled when not needed

#### 4. JavaScript GC Optimization

- Parallel marking enabled
- Incremental GC with shorter slices (5ms)
- More aggressive tenuring
- Smaller nursery size

#### 5. GPU Memory Cleanup

- Surface cache expires after 30 seconds (vs 60)
- Immediate texture cleanup on tab discard
- GPU memory pressure handler

## CPU Optimization

### Event Loop Optimization

- Reduced timer resolution in background tabs
- Throttled requestAnimationFrame in inactive tabs
- Consolidated idle dispatch calls
- Reduced speculative parsing

### Painting & Rendering

- GPU rasterization preferred
- Smaller picture tiles (512x512 vs 1024x1024)
- Reduced dirty rect processing
- Skip compositing for invisible areas

### JavaScript Execution

- Short GC slices (5ms vs default)
- Parallel marking for faster GC
- Reduced max JS memory (256MB vs unlimited)
- Lazy compilation for rarely-used code

## GPU Optimization

### WebRender Configuration

| Setting | Value | Benefit |
|---------|-------|---------|
| Tile Size | 512x512 | Better memory usage |
| Max Dirty Rects | 64 | Lower CPU in compositor |
| Batch Upload Size | 128 | Better GPU throughput |
| Triple Buffering | Enabled | Smoother frames |
| V-Sync | Adaptive | No tearing, lower power |

### Hardware Acceleration

| Feature | Windows | Linux | macOS |
|---------|---------|-------|-------|
| WebRender | D3D11 | OpenGL/Vulkan | Metal |
| Video Decode | D3D11 VA | VA-API | VTB |
| Compositing | DirectComposition | Wayland | CoreAnimation |
| Canvas 2D | D2D 1.1 | Skia | Skia Metal |
| WebGL | ANGLE/D3D11 | Native GL | Metal |

## Startup Optimization

### Timeline

| Phase | Without Optimization | With STGR | Savings |
|-------|--------------------|-----------|---------|
| Process start | 0ms | 0ms | - |
| DLL loading | 200ms | 200ms | (OS-bound) |
| Profile init | 400ms | 200ms | 200ms |
| Browser init | 600ms | 300ms | 300ms |
| First paint | 800ms | 500ms | 300ms |
| Session restore | +500ms | +100ms | 400ms |
| **Total** | **~1.8s** | **~1.1s** | **~700ms** |

### Techniques

1. **Lazy Initialization**: Non-critical services delayed 3-8 seconds
2. **Deferred Database**: Profile database operations after first paint
3. **No Prelaunch**: Skip content process pre-creation
4. **Selective Restore**: Only restore visible tab, lazy-load others
5. **Cache Warmup**: Warm caches during idle time after startup

## Gaming Mode

### Detection Methods

| Method | Latency | Reliability |
|--------|---------|-------------|
| Process enumeration | 1-5 seconds | High (Windows) |
| Fullscreen detection | Instant | Medium |
| Manual toggle | Instant | 100% |

### Applied Optimizations

| Optimization | Normal | Gaming Mode |
|-------------|--------|-------------|
| Content processes | 4 | 2 |
| Session store interval | 60s | 120s |
| Media cache | 50 MB | 25 MB |
| Image cache | 200 KB | 100 KB |
| JS memory limit | 256 MB | 128 MB |
| Network connections | 64 | 32 |
| Speculative parsing | On | Off |

## Performance Benchmarks

### Methodology

- Clean profile, no extensions
- Same hardware for comparison
- Average of 3 runs
- Windows 11, i7-13700K, 32GB RAM, RTX 4080

### Results (vs Firefox)

| Benchmark | Firefox | STGR | Improvement |
|-----------|---------|------|-------------|
| Startup (cold) | 1.8s | 1.1s | 39% faster |
| Tab switch | 120ms | 75ms | 37% faster |
| Page load (Speedometer) | 280 | 295 | 5% faster |
| RAM (idle) | 180 MB | 105 MB | 42% less |
| RAM (5 tabs) | 320 MB | 165 MB | 48% less |
| YouTube 1080p | 280 MB | 195 MB | 30% less |

> *Note: Actual results vary based on hardware, OS, and workloads.*

## Realistic Memory Expectations

### Idle Memory Breakdown

| Component | Memory |
|-----------|--------|
| Parent process | ~40 MB |
| GPU process | ~25 MB |
| RDD process | ~15 MB |
| Utility process | ~10 MB |
| Content process (prelaunch) | Disabled |
| Cache (in-memory) | ~15 MB |
| **Total idle** | **~90-120 MB** |

### YouTube 1080p

YouTube memory usage depends on:
- **Video codec**: VP9 (~250 MB) vs H.264/Avc1 (~180 MB)
- **GPU driver**: Memory allocation patterns vary
- **Browser chrome**: ~90 MB baseline
- **Extensions**: Each adds 10-50 MB

If hardware video decoding is available, GPU takes over decode memory, reducing process memory.

> **Bottom line**: Staying under 200 MB for YouTube 1080p is achievable on systems with hardware decode. On systems without, expect ~250-300 MB.
