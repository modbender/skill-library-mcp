# Common Architectures — Keras

## Image Classification

```python
def simple_cnn(input_shape, num_classes):
    """Basic CNN for image classification."""
    inputs = keras.Input(shape=input_shape)
    
    x = layers.Conv2D(32, 3, padding='same')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D()(x)
    
    x = layers.Conv2D(64, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D()(x)
    
    x = layers.Conv2D(128, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.GlobalAveragePooling2D()(x)
    
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    return keras.Model(inputs, outputs)
```

## Transfer Learning

```python
def transfer_model(input_shape, num_classes, trainable_layers=20):
    """Fine-tune pretrained model."""
    base = keras.applications.EfficientNetB0(
        include_top=False,
        weights='imagenet',
        input_shape=input_shape
    )
    
    # Freeze early layers
    for layer in base.layers[:-trainable_layers]:
        layer.trainable = False
    
    inputs = keras.Input(shape=input_shape)
    x = base(inputs)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    return keras.Model(inputs, outputs)
```

## Text Classification

```python
def text_cnn(vocab_size, embedding_dim, max_length, num_classes):
    """1D CNN for text classification."""
    inputs = keras.Input(shape=(max_length,))
    
    x = layers.Embedding(vocab_size, embedding_dim)(inputs)
    
    # Parallel convolutions with different kernel sizes
    conv_outputs = []
    for kernel_size in [3, 4, 5]:
        conv = layers.Conv1D(128, kernel_size, activation='relu')(x)
        conv = layers.GlobalMaxPooling1D()(conv)
        conv_outputs.append(conv)
    
    x = layers.Concatenate()(conv_outputs)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    return keras.Model(inputs, outputs)


def lstm_classifier(vocab_size, embedding_dim, max_length, num_classes):
    """Bidirectional LSTM for text."""
    inputs = keras.Input(shape=(max_length,))
    
    x = layers.Embedding(vocab_size, embedding_dim, mask_zero=True)(inputs)
    x = layers.Bidirectional(layers.LSTM(64, return_sequences=True))(x)
    x = layers.Bidirectional(layers.LSTM(32))(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    return keras.Model(inputs, outputs)
```

## Time Series

```python
def lstm_forecaster(timesteps, features, forecast_horizon):
    """LSTM for time series forecasting."""
    inputs = keras.Input(shape=(timesteps, features))
    
    x = layers.LSTM(64, return_sequences=True)(inputs)
    x = layers.Dropout(0.2)(x)
    x = layers.LSTM(32)(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(forecast_horizon)(x)
    
    return keras.Model(inputs, outputs)


def tcn_model(timesteps, features, num_classes):
    """Temporal Convolutional Network."""
    inputs = keras.Input(shape=(timesteps, features))
    
    x = inputs
    for dilation_rate in [1, 2, 4, 8]:
        x = layers.Conv1D(64, 3, padding='causal', dilation_rate=dilation_rate)(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.Dropout(0.2)(x)
    
    x = layers.GlobalAveragePooling1D()(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    return keras.Model(inputs, outputs)
```

## Autoencoder

```python
def autoencoder(input_dim, encoding_dim):
    """Simple autoencoder for dimensionality reduction."""
    # Encoder
    inputs = keras.Input(shape=(input_dim,))
    x = layers.Dense(256, activation='relu')(inputs)
    x = layers.Dense(128, activation='relu')(x)
    encoded = layers.Dense(encoding_dim, activation='relu')(x)
    
    # Decoder
    x = layers.Dense(128, activation='relu')(encoded)
    x = layers.Dense(256, activation='relu')(x)
    decoded = layers.Dense(input_dim, activation='sigmoid')(x)
    
    autoencoder = keras.Model(inputs, decoded)
    encoder = keras.Model(inputs, encoded)
    
    return autoencoder, encoder


def conv_autoencoder(input_shape):
    """Convolutional autoencoder for images."""
    inputs = keras.Input(shape=input_shape)
    
    # Encoder
    x = layers.Conv2D(32, 3, activation='relu', padding='same')(inputs)
    x = layers.MaxPooling2D()(x)
    x = layers.Conv2D(64, 3, activation='relu', padding='same')(x)
    encoded = layers.MaxPooling2D()(x)
    
    # Decoder
    x = layers.Conv2D(64, 3, activation='relu', padding='same')(encoded)
    x = layers.UpSampling2D()(x)
    x = layers.Conv2D(32, 3, activation='relu', padding='same')(x)
    x = layers.UpSampling2D()(x)
    decoded = layers.Conv2D(input_shape[-1], 3, activation='sigmoid', padding='same')(x)
    
    return keras.Model(inputs, decoded)
```

## Residual Block

```python
def residual_block(x, filters, downsample=False):
    """ResNet-style residual block."""
    shortcut = x
    stride = 2 if downsample else 1
    
    x = layers.Conv2D(filters, 3, strides=stride, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    
    x = layers.Conv2D(filters, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    
    if downsample or shortcut.shape[-1] != filters:
        shortcut = layers.Conv2D(filters, 1, strides=stride)(shortcut)
        shortcut = layers.BatchNormalization()(shortcut)
    
    x = layers.Add()([x, shortcut])
    x = layers.Activation('relu')(x)
    return x
```

## U-Net for Segmentation

```python
def unet(input_shape, num_classes):
    """U-Net for image segmentation."""
    inputs = keras.Input(shape=input_shape)
    
    # Encoder
    c1 = layers.Conv2D(64, 3, activation='relu', padding='same')(inputs)
    c1 = layers.Conv2D(64, 3, activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D()(c1)
    
    c2 = layers.Conv2D(128, 3, activation='relu', padding='same')(p1)
    c2 = layers.Conv2D(128, 3, activation='relu', padding='same')(c2)
    p2 = layers.MaxPooling2D()(c2)
    
    # Bottleneck
    c3 = layers.Conv2D(256, 3, activation='relu', padding='same')(p2)
    c3 = layers.Conv2D(256, 3, activation='relu', padding='same')(c3)
    
    # Decoder
    u1 = layers.UpSampling2D()(c3)
    u1 = layers.Concatenate()([u1, c2])
    c4 = layers.Conv2D(128, 3, activation='relu', padding='same')(u1)
    c4 = layers.Conv2D(128, 3, activation='relu', padding='same')(c4)
    
    u2 = layers.UpSampling2D()(c4)
    u2 = layers.Concatenate()([u2, c1])
    c5 = layers.Conv2D(64, 3, activation='relu', padding='same')(u2)
    c5 = layers.Conv2D(64, 3, activation='relu', padding='same')(c5)
    
    outputs = layers.Conv2D(num_classes, 1, activation='softmax')(c5)
    
    return keras.Model(inputs, outputs)
```
