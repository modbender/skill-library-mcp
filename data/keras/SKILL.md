---
name: Keras
slug: keras
version: 1.0.0
homepage: https://clawic.com/skills/keras
description: Build, train, and debug deep learning models with Keras patterns, layer recipes, and training diagnostics.
metadata: {"clawdbot":{"emoji":"🧠","requires":{"bins":["python3"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, check `setup.md` for integration guidelines. The skill stores preferences in `~/keras/` when the user confirms.

## When to Use

User builds neural networks with Keras or TensorFlow. Agent handles model architecture, layer configuration, training loops, callbacks, debugging loss issues, and deployment preparation.

## Architecture

Memory lives in `~/keras/`. See `memory-template.md` for setup.

```
~/keras/
├── memory.md          # Preferred architectures, hyperparams
└── models/            # Saved model configs (optional)
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Layer patterns | `layers.md` |
| Training diagnostics | `training.md` |
| Common architectures | `architectures.md` |

## Core Rules

### 1. Sequential vs Functional API
- Sequential: simple stacks, no branching
- Functional: multi-input/output, skip connections, shared layers
- Subclassing: custom forward pass, dynamic architectures

```python
# Sequential - simple stack
model = keras.Sequential([
    layers.Dense(64, activation='relu'),
    layers.Dense(10, activation='softmax')
])

# Functional - flexible graphs
inputs = keras.Input(shape=(784,))
x = layers.Dense(64, activation='relu')(inputs)
outputs = layers.Dense(10, activation='softmax')(x)
model = keras.Model(inputs, outputs)
```

### 2. Input Shape Patterns
- First layer needs `input_shape` (exclude batch)
- Images: `(height, width, channels)` for channels_last
- Sequences: `(timesteps, features)`
- Tabular: `(features,)`

```python
# Image input
layers.Conv2D(32, 3, input_shape=(224, 224, 3))

# Sequence input
layers.LSTM(64, input_shape=(100, 50))  # 100 timesteps, 50 features

# Tabular input
layers.Dense(64, input_shape=(20,))  # 20 features
```

### 3. Activation Functions
| Task | Output Activation | Loss |
|------|-------------------|------|
| Binary classification | `sigmoid` | `binary_crossentropy` |
| Multi-class | `softmax` | `categorical_crossentropy` |
| Multi-label | `sigmoid` | `binary_crossentropy` |
| Regression | `linear` (none) | `mse` or `mae` |

### 4. Regularization Stack
Apply in this order for overfitting:
1. **Dropout** - after dense/conv layers (0.2-0.5)
2. **BatchNorm** - before or after activation
3. **L2 regularization** - in layer (0.01-0.001)
4. **Early stopping** - callback with patience

```python
layers.Dense(64, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01))
layers.Dropout(0.3)
layers.BatchNormalization()
```

### 5. Callbacks Essentials
```python
callbacks = [
    keras.callbacks.EarlyStopping(
        monitor='val_loss', patience=5, restore_best_weights=True
    ),
    keras.callbacks.ModelCheckpoint(
        'best_model.keras', save_best_only=True
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.5, patience=3
    ),
    keras.callbacks.TensorBoard(log_dir='./logs')
]
```

### 6. Data Pipeline
```python
# tf.data for performance
dataset = tf.data.Dataset.from_tensor_slices((x, y))
dataset = dataset.shuffle(10000).batch(32).prefetch(tf.data.AUTOTUNE)

# ImageDataGenerator for augmentation
datagen = keras.preprocessing.image.ImageDataGenerator(
    rotation_range=20,
    horizontal_flip=True,
    validation_split=0.2
)
```

### 7. Compile Checklist
```python
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)
```
- Learning rate: start 0.001, reduce on plateau
- Batch size: 32-128 typical, larger = smoother gradients

## Common Traps

- `Input shape mismatch` → check data shape vs model input_shape, exclude batch dim
- `Loss is NaN` → reduce learning rate, check for inf/nan in data, add gradient clipping
- `Validation loss diverges` → add regularization, reduce model capacity, more data
- `Model not learning` → check labels are correct, verify loss function matches task
- `GPU OOM` → reduce batch size, use mixed precision, gradient checkpointing
- `Slow training` → use tf.data pipeline with prefetch, enable XLA compilation

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| TensorFlow model hub | None (download only) | Pretrained weights when using `weights='imagenet'` |

**Note:** Transfer learning examples download pretrained weights on first use. Use `weights=None` for fully offline operation.

## Security & Privacy

**Data that stays local:**
- Model architectures and configs in `~/keras/`
- Training preferences and hyperparameters

**This skill does NOT:**
- Upload models or data anywhere
- Access files outside `~/keras/` and working directory
- Store training data

## Related Skills
Install with `clawhub install <slug>` if user confirms:

- `tensorflow` — TensorFlow operations and deployment
- `pytorch` — Alternative deep learning framework
- `ai` — General AI and ML patterns
- `models` — Model architecture design

## Feedback

- If useful: `clawhub star keras`
- Stay updated: `clawhub sync`
