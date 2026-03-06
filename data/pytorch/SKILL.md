---
name: PyTorch
description: Avoid common PyTorch mistakes — train/eval mode, gradient leaks, device mismatches, and checkpoint gotchas.
metadata: {"clawdbot":{"emoji":"🔥","requires":{"bins":["python3"]},"os":["linux","darwin","win32"]}}
---

## Train vs Eval Mode
- `model.train()` enables dropout, BatchNorm updates — default after init
- `model.eval()` disables dropout, uses running stats — MUST call for inference
- Mode is sticky — train/eval persists until explicitly changed
- `model.eval()` doesn't disable gradients — still need `torch.no_grad()`

## Gradient Control
- `torch.no_grad()` for inference — reduces memory, speeds up computation
- `loss.backward()` accumulates gradients — call `optimizer.zero_grad()` before backward
- `zero_grad()` placement matters — before forward pass, not after backward
- `.detach()` to stop gradient flow — prevents memory leak in logging

## Device Management
- Model AND data must be on same device — `model.to(device)` and `tensor.to(device)`
- `.cuda()` vs `.to('cuda')` — both work, `.to(device)` more flexible
- CUDA tensors can't convert to numpy directly — `.cpu().numpy()` required
- `torch.device('cuda' if torch.cuda.is_available() else 'cpu')` — portable code

## DataLoader
- `num_workers > 0` uses multiprocessing — Windows needs `if __name__ == '__main__':`
- `pin_memory=True` with CUDA — faster transfer to GPU
- Workers don't share state — random seeds differ per worker, set in `worker_init_fn`
- Large `num_workers` can cause memory issues — start with 2-4, increase if CPU-bound

## Saving and Loading
- `torch.save(model.state_dict(), path)` — recommended, saves only weights
- Loading: create model first, then `model.load_state_dict(torch.load(path))`
- `map_location` for cross-device — `torch.load(path, map_location='cpu')` if saved on GPU
- Saving whole model pickles code path — breaks if code changes

## In-place Operations
- In-place ops end with `_` — `tensor.add_(1)` vs `tensor.add(1)`
- In-place on leaf variable breaks autograd — error about modified leaf
- In-place on intermediate can corrupt gradient — avoid in computation graph
- `tensor.data` bypasses autograd — legacy, prefer `.detach()` for safety

## Memory Management
- Accumulated tensors leak memory — `.detach()` logged metrics
- `torch.cuda.empty_cache()` releases cached memory — but doesn't fix leaks
- Delete references and call `gc.collect()` — before empty_cache if needed
- `with torch.no_grad():` prevents graph storage — crucial for validation loop

## Common Mistakes
- BatchNorm with `batch_size=1` fails in train mode — use eval mode or `track_running_stats=False`
- Loss function reduction default is 'mean' — may want 'sum' for gradient accumulation
- `cross_entropy` expects logits — not softmax output
- `.item()` to get Python scalar — `.numpy()` or `[0]` deprecated/error
