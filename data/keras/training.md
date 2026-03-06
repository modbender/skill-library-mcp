# Training Diagnostics — Keras

## Loss Not Decreasing

| Symptom | Cause | Fix |
|---------|-------|-----|
| Loss stuck high | Learning rate too low | Increase LR 10x |
| Loss oscillates wildly | Learning rate too high | Decrease LR 10x |
| Loss decreases then plateaus | Local minimum | Add LR scheduler, try different optimizer |
| Loss is 0 from start | Labels leaked into features | Check data pipeline |

## Overfitting Diagnostics

```
Training loss keeps decreasing
Validation loss increases after epoch N
Gap between train/val grows
```

**Fixes in order:**
1. More training data / data augmentation
2. Add Dropout (0.2-0.5)
3. Add L2 regularization
4. Reduce model capacity
5. Early stopping

## Underfitting Diagnostics

```
Both training and validation loss stay high
Model performs at random chance level
```

**Fixes in order:**
1. Train longer
2. Increase model capacity (more layers/units)
3. Reduce regularization
4. Check data quality and labels
5. Try different architecture

## NaN Loss Debugging

```python
# Check for NaN in data
print(f"NaN in X: {np.isnan(X).any()}")
print(f"Inf in X: {np.isinf(X).any()}")

# Gradient clipping
optimizer = keras.optimizers.Adam(clipnorm=1.0)
# or
optimizer = keras.optimizers.Adam(clipvalue=0.5)

# Mixed precision can cause NaN
# Try disabling: tf.keras.mixed_precision.set_global_policy('float32')
```

## Learning Rate Finder

```python
# Simple LR range test
import numpy as np

class LRFinder(keras.callbacks.Callback):
    def __init__(self, min_lr=1e-7, max_lr=1, steps=100):
        self.min_lr = min_lr
        self.max_lr = max_lr
        self.steps = steps
        self.lrs = []
        self.losses = []
        
    def on_train_begin(self, logs=None):
        self.lr_mult = (self.max_lr / self.min_lr) ** (1 / self.steps)
        keras.backend.set_value(self.model.optimizer.lr, self.min_lr)
        
    def on_batch_end(self, batch, logs=None):
        lr = float(keras.backend.get_value(self.model.optimizer.lr))
        self.lrs.append(lr)
        self.losses.append(logs['loss'])
        keras.backend.set_value(self.model.optimizer.lr, lr * self.lr_mult)
        if logs['loss'] > 10 * self.losses[0]:
            self.model.stop_training = True

# Usage
lr_finder = LRFinder()
model.fit(X, y, epochs=1, callbacks=[lr_finder])
# Plot lrs vs losses, pick LR where loss decreases fastest
```

## Training Monitoring

```python
# Custom callback for detailed monitoring
class TrainingMonitor(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        train_loss = logs.get('loss')
        val_loss = logs.get('val_loss')
        
        if val_loss and train_loss:
            gap = val_loss - train_loss
            if gap > 0.1:
                print(f"Warning: Overfitting detected (gap: {gap:.4f})")
        
        # Check for exploding gradients
        for layer in self.model.layers:
            if hasattr(layer, 'kernel'):
                weights = layer.kernel.numpy()
                if np.isnan(weights).any():
                    print(f"NaN weights in {layer.name}")
```

## Debugging Checklist

1. **Data issues**
   - [ ] Normalized inputs (mean ~0, std ~1)
   - [ ] Labels are correct format (one-hot vs integer)
   - [ ] No data leakage between train/val
   - [ ] Shuffled training data

2. **Architecture issues**
   - [ ] Output activation matches task
   - [ ] Loss function matches output
   - [ ] Gradients can flow (check for dead ReLUs)

3. **Training issues**
   - [ ] Learning rate appropriate
   - [ ] Batch size reasonable (32-256)
   - [ ] Enough epochs to converge

## Performance Optimization

```python
# Mixed precision training (2x speedup on modern GPUs)
tf.keras.mixed_precision.set_global_policy('mixed_float16')

# XLA compilation
tf.config.optimizer.set_jit(True)

# Efficient data pipeline
dataset = tf.data.Dataset.from_tensor_slices((x, y))
dataset = (dataset
    .cache()
    .shuffle(10000)
    .batch(32)
    .prefetch(tf.data.AUTOTUNE))

# Multi-GPU training
strategy = tf.distribute.MirroredStrategy()
with strategy.scope():
    model = build_model()
    model.compile(...)
```
