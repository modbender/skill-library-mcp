---
name: pywayne-crypto
description: Encryption and decryption toolkit for string and byte data. Supports Fernet (AES-128) symmetric encryption, fallback XOR encryption, custom password protection, code obfuscation, and batch processing. Use when users need to encrypt/decrypt sensitive data, protect algorithms, or obfuscate Python code.
---

# Pywayne Crypto

加密解密工具集，支持对称加密、自定义密码和代码混淆保护。

## Quick Start

```python
from pywayne.crypto import encrypt, decrypt

# 基础加密/解密
encrypted = encrypt("Hello World")
decrypted = decrypt(encrypted)
print(decrypted)  # 输出: Hello World

# 使用自定义密码加密
encrypted = encrypt("Secret message", "my_password")
decrypted = decrypt(encrypted, "my_password")
print(decrypted)  # 输出: Secret message
```

## encrypt - 加密函数

加密字符串或字节数据。

```python
# 文本加密
encrypted = encrypt("机密信息", "password")
# 字节加密
byte_data = b"binary data"
encrypted = encrypt(byte_data, "password")
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `text` | str or bytes | 要加密的文本数据或字节数据 |
| `password` | str | 可选，自定义密码。不提供时使用默认密钥 |

**返回值**：`str` - base64 编码的加密字符串

**参数类型错误处理**：
- 当输入不是 `str` 或 `bytes` 时抛出 `ValueError`

## decrypt - 解密函数

解密之前加密的字符串。

```python
# 解密（使用默认密钥）
decrypted = decrypt(encrypted_text)

# 解密（使用自定义密码）
decrypted = decrypt(encrypted_text, "my_password")
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `encrypted_text` | str | 要解密的 base64 编码字符串 |
| `password` | str | 可选，解密密码。必须与加密时使用的密码相同 |

**返回值**：`str` - 解密后的原始字符串

## 批量操作

支持批量加密和解密操作。

```python
from pywayne.crypto import encrypt, decrypt

data = ["数据1", "数据2", "数据3"]
password = "batch_password"

# 批量加密
encrypted_list = encrypt_batch(data, password)

# 批量解密
decrypted_list = decrypt_batch(encrypted_list, password)
```

**参数**：

| 函数 | 参数 | 说明 |
|------|------|------|
| `encrypt_batch(data_list, password)` | data_list: 数据列表 | password: 密码 |
| `decrypt_batch(encrypted_list, password)` | encrypted_list: 加密数据列表 | password: 密码 |

**返回值**：`list[str]` - 解密结果列表（失败项目为 None）

## 配置文件管理

保存和加载加密配置文件（JSON 格式）。

```python
from pywayne.crypto import encrypt, decrypt

# 保存配置
config = {"database": {"host": "localhost", "username": "admin", "password": "secret"}}
save_config(config, "master_password", "config.enc")

# 加载配置
loaded_config = load_config("master_password", "config.enc")
print(loaded_config)  # 输出: {'database': {...}}
```

**参数**：

| 函数 | 参数 | 说明 |
|------|------|------|
| `save_config(config_dict, password, filename)` | config_dict: 配置字典 | password: 加密密码 | filename: 输出文件名 |
| `load_config(password, filename)` | password: 解密密码 | filename: 配置文件名 |

**异常**：
- `ValueError`：配置文件解密失败（密码错误或数据损坏）

## 加密策略

模块采用分层加密策略，优先使用 Fernet，回退到 XOR。

| 策略 | 说明 |
|------|------|------|
| **Fernet 加密**（推荐） | AES-128 对称加密，带消息完整性验证 |
| **XOR 加密**（回退） | 简单异或加密，无依赖，基本功能 |
| **代码混淆保护** | Base64 编码隐藏、动态函数生成、命名空间清理 |

## 错误处理

完善的异常处理机制，支持密码错误、数据格式错误、解密失败等情况。

```python
# 密码错误
try:
    decrypted = decrypt(encrypted_text, "wrong_password")
except ValueError:
    print("错误: 解密失败，密码不正确")

# 数据格式错误
try:
    encrypted = encrypt(123)
except ValueError:
    print("错误: 输入类型必须是字符串或字节")
```

## 最佳实践

- 密码妥善保管，避免硬编码在源码中
- 高安全性要求的应用使用专业加密库
- 密钥通过环境变量传递，避免写入日志
