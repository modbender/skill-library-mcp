---
name: TensorFlow
description: Avoid common TensorFlow mistakes — tf.function retracing, GPU memory, data pipeline bottlenecks, and gradient traps.
metadata: {"clawdbot":{"emoji":"🧠","requires":{"bins":["python3"]},"os":["linux","darwin","win32"]}}
---

## tf.function Retracing
- New input shape/dtype causes retrace — expensive, prints warning
- Use `input_signature` for fixed shapes — `@tf.function(input_signature=[tf.TensorSpec(...)])`
- Python values retrace — pass as tensors, not Python ints/floats
- Avoid Python side effects in tf.function — only runs once during tracing

## GPU Memory
- TensorFlow grabs all GPU memory by default — set `memory_growth=True` before any ops
- `tf.config.experimental.set_memory_growth(gpu, True)` — must be called before GPU init
- OOM with large models — reduce batch size or use gradient checkpointing
- `CUDA_VISIBLE_DEVICES=""` to force CPU — for testing without GPU

## Data Pipeline
- `tf.data.Dataset` without `.prefetch()` — CPU/GPU idle time between batches
- `.cache()` after expensive ops — but before random augmentation
- `.batch()` before `.map()` for vectorized ops — faster than per-element
- `num_parallel_calls=tf.data.AUTOTUNE` — parallel preprocessing
- Dataset iteration in eager mode is slow — use in tf.function or model.fit

## Shape Issues
- First dimension is batch — `None` for variable batch size in Input layer
- `model.build(input_shape)` if not using Input layer — or first call errors
- Reshape errors unclear — `tf.debugging.assert_shapes()` for debugging
- Broadcasting silently succeeds — may hide shape bugs

## Gradient Tape
- Variables watched by default — tensors need `tape.watch(tensor)`
- `persistent=True` for multiple gradients — otherwise tape consumed after first use
- `tape.gradient` returns None if no path — check for disconnected graph
- `@tf.custom_gradient` for custom backward — not all ops have gradients

## Training Gotchas
- `model.trainable = False` after compile does nothing — set before compile
- BatchNorm behaves differently in training vs inference — `training=True/False` matters
- `model.fit` shuffles by default — `shuffle=False` for time series
- `validation_split` takes from end — shuffle data first if order matters

## Saving Models
- `model.save()` saves everything — architecture, weights, optimizer state
- `model.save_weights()` only weights — need model code to restore
- SavedModel format for serving — `tf.saved_model.save(model, path)`
- H5 format limited — doesn't save custom objects well, use SavedModel

## Common Mistakes
- Mixing Keras and raw tf ops incorrectly — use `layers.Lambda` to wrap tf ops in Sequential
- `tf.print` vs Python print — Python print only runs at trace time in tf.function
- NumPy ops in graph — use tf ops, numpy executes eagerly only
- Loss returns scalar per sample — Keras averages, custom loops may need `tf.reduce_mean`
