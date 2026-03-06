---
name: struct-offset-analyzer
description: Statically analyze C struct member offsets through code reading to calculate memory layouts
---

# struct-offset-analyzer

Statically analyze the memory offsets of C language struct members without needing to run code.

## Use Cases

- Locating struct members during reverse engineering
- Confirming memory layouts during debugging
- Analyzing data structures in security research
- Understanding struct field positions in binary analysis

## Workflow

### 1. Locate Struct Definition

```bash
# Search for struct definition
grep -n "struct xxx_st {" **/*.h
grep -n "typedef struct" **/*.h
```

### 2. Collect Type Information

Find definitions for all member types:
- Nested structs
- Enum types
- typedef aliases
- Constant definitions (e.g., `#define EVP_MAX_MD_SIZE 64`)

### 3. Calculate Alignment Rules

| Type | Size (64-bit) | Alignment Requirement |
|------|---------------|----------------------|
| char/unsigned char | 1 | 1 |
| short | 2 | 2 |
| int/uint32_t | 4 | 4 |
| long/size_t/pointer | 8 | 8 |
| unsigned char[N] | N | 1 (no padding needed) |
| enum | usually 4 | 4 |
| struct | depends on members | aligned to largest member |

**Key Rules**:
- Member offset must be a multiple of its size
- `unsigned char` arrays are 1-byte aligned, **no padding required**
- Overall struct size is aligned to the size of its largest member
- Padding bytes count toward offsets

### 4. Output Offset Table

Use hexadecimal representation for offsets, format:

```
| Offset(0x) | Member | Type | Size |
|------------|--------|------|------|
| 0x00 | field1 | int | 4 |
| 0x04 | *(padding)* | - | 4 |
| 0x08 | field2 | void * | 8 |
```

## Common Search Patterns

```bash
# Find struct member definition
grep -n "struct xxx_st" **/*.h

# Find type definition
grep -n "typedef.*XXX" **/*.h

# Find constant definition
grep -n "#define.*SIZE" **/*.h

# Find enum definition
grep -n "typedef enum" **/*.h
```

## Example: OpenSSL ssl_st Analysis

Analyzing `client_app_traffic_secret` member offset:

1. Locate struct: `ssl/ssl_local.h:1068`
2. Find constant: `EVP_MAX_MD_SIZE = 64` (`include/openssl/evp.h:19`)
3. Calculate layout, note that `unsigned char` arrays need no padding
4. Result: offset 0x33c (828 bytes)

## Notes

- Confirm target platform (32-bit vs 64-bit)
- Note that conditional compilation (#ifdef) may affect struct layout
- Check for #pragma pack directives that may change alignment
- Union members share the same offset