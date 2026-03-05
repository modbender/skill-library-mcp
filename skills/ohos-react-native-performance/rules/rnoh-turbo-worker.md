---
title: Run heavy TurboModule work on a worker thread
impact: MEDIUM
source: ohos_react_native performance optimization - TurboModule on worker
---

# rnoh-turbo-worker

By default, React Native on OpenHarmony runs TurboModules on the main thread, competing with UI. **Heavy work** should run on a worker thread to avoid blocking the main thread; modules that **often interact with the UI thread** should not be moved to a worker.

## Good candidates for worker thread

- Heavy data: JSON parsing, crypto, image processing
- Math / algorithms
- Audio / video processing
- Network request/response handling
- File I/O

## Poor candidates for worker thread

- Modules that frequently switch threads or send lots of data to the UI thread (e.g. **ImageLoaderTurboModule** is driven from the UI thread; running it on a worker causes many thread hops and can hurt performance)

## Implementation

- Use ArkTS **worker** to run the TurboModule thread (long-running).
- Start the worker **at app startup** (JS loading the bundle will call system TurboModules like Networking, UIManager).
- In `ArkTSTurboModule` `callSync` / `callAsync`, switch to the worker or main thread per config.
- If extending RNAbility, override `getRNOHWorkerScriptUrl()` and return the worker path (e.g. `"entry/ets/workers/RNOHWorker.ets"`).

See the official doc "TurboModule - Run custom TurboModule on worker thread" for steps.

## Static check

- For custom TurboModules that do heavy work above, confirm they are configured to run on the worker.
- Ensure ImageLoader and other UI-bound TurboModules are not mistakenly moved to the worker.
