# Layer Patterns — Keras

## Dense Layers

```python
# Basic dense block
layers.Dense(units, activation='relu')
layers.Dropout(0.3)

# With regularization
layers.Dense(64, 
    activation='relu',
    kernel_regularizer=keras.regularizers.l2(0.01),
    kernel_initializer='he_normal'
)
```

## Convolutional Layers

```python
# Conv block for images
layers.Conv2D(filters, kernel_size, activation='relu', padding='same')
layers.BatchNormalization()
layers.MaxPooling2D(pool_size=(2, 2))

# Typical CNN pattern
def conv_block(x, filters):
    x = layers.Conv2D(filters, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D()(x)
    return x
```

## Recurrent Layers

```python
# LSTM for sequences
layers.LSTM(units, return_sequences=True)  # stack LSTMs
layers.LSTM(units, return_sequences=False)  # final LSTM

# Bidirectional wrapper
layers.Bidirectional(layers.LSTM(64, return_sequences=True))

# GRU alternative (faster)
layers.GRU(units, return_sequences=True)
```

## Attention Layers

```python
# Multi-head attention
layers.MultiHeadAttention(
    num_heads=8,
    key_dim=64,
    dropout=0.1
)

# Self-attention pattern
attention_output = layers.MultiHeadAttention(
    num_heads=8, key_dim=64
)(query=x, value=x, key=x)
x = layers.Add()([x, attention_output])
x = layers.LayerNormalization()(x)
```

## Normalization Layers

```python
# Batch normalization - after conv/dense, before or after activation
layers.BatchNormalization()

# Layer normalization - for transformers, RNNs
layers.LayerNormalization()

# Group normalization - small batch sizes
layers.GroupNormalization(groups=32)
```

## Regularization Layers

```python
# Dropout - randomly zero outputs
layers.Dropout(rate=0.3)

# Spatial dropout - for conv layers (drops entire feature maps)
layers.SpatialDropout2D(rate=0.2)

# Gaussian noise - training only
layers.GaussianNoise(stddev=0.1)
```

## Reshaping Layers

```python
# Flatten for dense after conv
layers.Flatten()

# Global pooling (better than flatten for conv)
layers.GlobalAveragePooling2D()
layers.GlobalMaxPooling2D()

# Reshape
layers.Reshape((7, 7, 256))

# Permute dimensions
layers.Permute((2, 1))  # swap axes
```

## Embedding Layer

```python
# For NLP - integer tokens to dense vectors
layers.Embedding(
    input_dim=vocab_size,
    output_dim=embedding_dim,
    input_length=max_length,
    mask_zero=True  # for variable length
)
```

## Custom Layer Template

```python
class MyLayer(keras.layers.Layer):
    def __init__(self, units, **kwargs):
        super().__init__(**kwargs)
        self.units = units
    
    def build(self, input_shape):
        self.w = self.add_weight(
            shape=(input_shape[-1], self.units),
            initializer='glorot_uniform',
            trainable=True
        )
        self.b = self.add_weight(
            shape=(self.units,),
            initializer='zeros',
            trainable=True
        )
    
    def call(self, inputs, training=None):
        return tf.matmul(inputs, self.w) + self.b
    
    def get_config(self):
        config = super().get_config()
        config.update({'units': self.units})
        return config
```
