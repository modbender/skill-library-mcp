---
name: error-codes
description: "Error code reference for ZK Compression. Codes 6000-16034. Search hex value (0x1770-0x3EB2) or error name."
---

# Error Codes Reference

> Activate: "error code", "0x", hex code, error name, debugging errors

Complete error code reference for ZK Compression programs.

## How to Use

Search for your error code or hex value with `Cmd+F` / `Ctrl+F`.

## 6000 - 6053 / SystemProgramError Variants

> **Source:** [errors.rs](https://github.com/Lightprotocol/light-protocol/blob/604892ff3902292dd0b0b047cb0bfacc469ea0d4/programs/system/src/errors.rs#L133)

| Code | Hex    | Error                                           | Message                                                                                                                           |
| :--- | :----- | :---------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| 6000 | 0x1770 | `SumCheckFailed`                                | "Sum check failed"                                                                                                                |
| 6001 | 0x1771 | `SignerCheckFailed`                             | "Signer check failed"                                                                                                             |
| 6002 | 0x1772 | `CpiSignerCheckFailed`                          | "Cpi signer check failed"                                                                                                         |
| 6003 | 0x1773 | `ComputeInputSumFailed`                         | "Computing input sum failed."                                                                                                     |
| 6004 | 0x1774 | `ComputeOutputSumFailed`                        | "Computing output sum failed."                                                                                                    |
| 6005 | 0x1775 | `ComputeRpcSumFailed`                           | "Computing rpc sum failed."                                                                                                       |
| 6006 | 0x1776 | `InvalidAddress`                                | "InvalidAddress"                                                                                                                  |
| 6007 | 0x1777 | `DeriveAddressError`                            | "DeriveAddressError"                                                                                                              |
| 6008 | 0x1778 | `CompressedSolPdaUndefinedForCompressSol`       | "CompressedSolPdaUndefinedForCompressSol"                                                                                         |
| 6009 | 0x1779 | `DecompressLamportsUndefinedForCompressSol`     | "DecompressLamportsUndefinedForCompressSol"                                                                                       |
| 6010 | 0x177A | `CompressedSolPdaUndefinedForDecompressSol`     | "CompressedSolPdaUndefinedForDecompressSol"                                                                                       |
| 6011 | 0x177B | `DeCompressLamportsUndefinedForDecompressSol`   | "DeCompressLamportsUndefinedForDecompressSol"                                                                                     |
| 6012 | 0x177C | `DecompressRecipientUndefinedForDecompressSol`  | "DecompressRecipientUndefinedForDecompressSol"                                                                                    |
| 6013 | 0x177D | `WriteAccessCheckFailed`                        | "WriteAccessCheckFailed"                                                                                                          |
| 6014 | 0x177E | `InvokingProgramNotProvided`                    | "InvokingProgramNotProvided"                                                                                                      |
| 6015 | 0x177F | `InvalidCapacity`                               | "InvalidCapacity"                                                                                                                 |
| 6016 | 0x1780 | `InvalidMerkleTreeOwner`                        | "InvalidMerkleTreeOwner"                                                                                                          |
| 6017 | 0x1781 | `ProofIsNone`                                   | "ProofIsNone"                                                                                                                     |
| 6018 | 0x1782 | `ProofIsSome`                                   | "Proof is some but no input compressed accounts or new addresses provided."                                                       |
| 6019 | 0x1783 | `EmptyInputs`                                   | "EmptyInputs"                                                                                                                     |
| 6020 | 0x1784 | `CpiContextAccountUndefined`                    | "CpiContextAccountUndefined"                                                                                                      |
| 6021 | 0x1785 | `CpiContextEmpty`                               | "CpiContextEmpty"                                                                                                                 |
| 6022 | 0x1786 | `CpiContextMissing`                             | "CpiContextMissing"                                                                                                               |
| 6023 | 0x1787 | `DecompressionRecipientDefined`                 | "DecompressionRecipientDefined"                                                                                                   |
| 6024 | 0x1788 | `SolPoolPdaDefined`                             | "SolPoolPdaDefined"                                                                                                               |
| 6025 | 0x1789 | `AppendStateFailed`                             | "AppendStateFailed"                                                                                                               |
| 6026 | 0x178A | `InstructionNotCallable`                        | "The instruction is not callable"                                                                                                 |
| 6027 | 0x178B | `CpiContextFeePayerMismatch`                    | "CpiContextFeePayerMismatch"                                                                                                      |
| 6028 | 0x178C | `CpiContextAssociatedMerkleTreeMismatch`        | "CpiContextAssociatedMerkleTreeMismatch"                                                                                          |
| 6029 | 0x178D | `NoInputs`                                      | "NoInputs"                                                                                                                        |
| 6030 | 0x178E | `InputMerkleTreeIndicesNotInOrder`              | "Input merkle tree indices are not in ascending order."                                                                           |
| 6031 | 0x178F | `OutputMerkleTreeIndicesNotInOrder`             | "Output merkle tree indices are not in ascending order."                                                                          |
| 6032 | 0x1790 | `OutputMerkleTreeNotUnique`                     | "OutputMerkleTreeNotUnique"                                                                                                       |
| 6033 | 0x1791 | `DataFieldUndefined`                            | "DataFieldUndefined"                                                                                                              |
| 6034 | 0x1792 | `ReadOnlyAddressAlreadyExists`                  | "ReadOnlyAddressAlreadyExists"                                                                                                    |
| 6035 | 0x1793 | `ReadOnlyAccountDoesNotExist`                   | "ReadOnlyAccountDoesNotExist"                                                                                                     |
| 6036 | 0x1794 | `HashChainInputsLenghtInconsistent`             | "HashChainInputsLenghtInconsistent"                                                                                               |
| 6037 | 0x1795 | `InvalidAddressTreeHeight`                      | "InvalidAddressTreeHeight"                                                                                                        |
| 6038 | 0x1796 | `InvalidStateTreeHeight`                        | "InvalidStateTreeHeight"                                                                                                          |
| 6039 | 0x1797 | `InvalidArgument`                               | "InvalidArgument"                                                                                                                 |
| 6040 | 0x1798 | `InvalidAccount`                                | "InvalidAccount"                                                                                                                  |
| 6041 | 0x1799 | `AddressMerkleTreeAccountDiscriminatorMismatch` | "AddressMerkleTreeAccountDiscriminatorMismatch"                                                                                   |
| 6042 | 0x179A | `StateMerkleTreeAccountDiscriminatorMismatch`   | "StateMerkleTreeAccountDiscriminatorMismatch"                                                                                     |
| 6043 | 0x179B | `ProofVerificationFailed`                       | "Proof verification failed." [How to debug this error](/resources/error-cheatsheet/debug-0x179b-6043-proofverificationfailed) |
| 6044 | 0x179C | `InvalidAccountMode`                            | "Invalid account mode."                                                                                                           |
| 6045 | 0x179D | `InvalidInstructionDataDiscriminator`           | "InvalidInstructionDataDiscriminator"                                                                                             |
| 6046 | 0x179E | `NewAddressAssignedIndexOutOfBounds`            | "NewAddressAssignedIndexOutOfBounds"                                                                                              |
| 6047 | 0x179F | `AddressIsNone`                                 | "AddressIsNone"                                                                                                                   |
| 6048 | 0x17A0 | `AddressDoesNotMatch`                           | "AddressDoesNotMatch"                                                                                                             |
| 6049 | 0x17A1 | `CpiContextAlreadySet`                          | "CpiContextAlreadySet"                                                                                                            |
| 6050 | 0x17A2 | `InvalidTreeHeight`                             | "InvalidTreeHeight"                                                                                                               |
| 6051 | 0x17A3 | `TooManyOutputAccounts`                         | "TooManyOutputAccounts"                                                                                                           |
| 6052 | 0x17A4 | `BorrowingDataFailed`                           | "Borrowing data failed"                                                                                                           |
| 6053 | 0x17A5 | `DuplicateAccountInInputsAndReadOnly`           | "DuplicateAccountInInputsAndReadOnly"                                                                                             |

## 7001 - 7009 / HasherError Variants

> **Source:** [errors.rs](https://github.com/Lightprotocol/light-protocol/blob/604892ff3902292dd0b0b047cb0bfacc469ea0d4/program-libs/hasher/src/errors.rs)

| Code | Hex    | Error                                   | Message                                                                                  |
| :--- | :----- | :-------------------------------------- | :--------------------------------------------------------------------------------------- |
| 7001 | 0x1B59 | `IntegerOverflow`                       | "Integer overflow, value too large"                                                      |
| 7003 | 0x1B5B | `PoseidonSyscall(PoseidonSyscallError)` | "Poseidon syscall error: {0}"                                                            |
| 7005 | 0x1B5D | `InvalidInputLength(usize, usize)`      | "Allowed input length {0} provided {1}"                                                  |
| 7006 | 0x1B5E | `InvalidNumFields`                      | "Invalid number of fields"                                                               |
| 7007 | 0x1B5F | `EmptyInput`                            | "Empty input"                                                                            |
| 7008 | 0x1B60 | `BorshError`                            | "Borsh serialization failed."                                                            |
| 7009 | 0x1B61 | `OptionHashToFieldSizeZero`             | "Option hash to field size returned [0u8;32], a collision with None for an Option type." |

## 10001 - 10014 / ConcurrentMerkleTreeError Variants

> **Source:** [errors.rs](https://github.com/Lightprotocol/light-protocol/blob/604892ff3902292dd0b0b047cb0bfacc469ea0d4/program-libs/concurrent-merkle-tree/src/errors.rs)

| Code  | Hex    | Error                                     | Message                                                                                                           |
| :---- | :----- | :---------------------------------------- | :---------------------------------------------------------------------------------------------------------------- |
| 10001 | 0x2711 | `IntegerOverflow`                         | "Integer overflow"                                                                                                |
| 10002 | 0x2712 | `HeightZero`                              | "Invalid height, it has to be greater than 0"                                                                     |
| 10003 | 0x2713 | `InvalidHeight(usize)`                    | "Invalid height, expected {0}"                                                                                    |
| 10004 | 0x2714 | `ChangelogZero`                           | "Invalid changelog size, it has to be greater than 0. Changelog is used for storing Merkle paths during appends." |
| 10005 | 0x2715 | `RootsZero`                               | "Invalid number of roots, it has to be greater than 0"                                                            |
| 10006 | 0x2716 | `CanopyGeThanHeight`                      | "Canopy depth has to be lower than height"                                                                        |
| 10007 | 0x2717 | `TreeIsFull`                              | "Merkle tree is full, cannot append more leaves."                                                                 |
| 10008 | 0x2718 | `BatchGreaterThanChangelog(usize, usize)` | "Number of leaves ({0}) exceeds the changelog capacity ({1})."                                                    |
| 10009 | 0x2719 | `InvalidProofLength(usize, usize)`        | "Invalid proof length, expected {0}, got {1}."                                                                    |
| 10010 | 0x271A | `InvalidProof([u8; 32], [u8; 32])`        | "Invalid Merkle proof, expected root: `{0:?}`, the provided proof produces root: `{1:?}`"                         |
| 10011 | 0x271B | `CannotUpdateLeaf`                        | "Attempting to update the leaf which was updated by an another newest change."                                    |
| 10012 | 0x271C | `CannotUpdateEmpty`                       | "Cannot update the empty leaf"                                                                                    |
| 10013 | 0x271D | `EmptyLeaves`                             | "The batch of leaves is empty"                                                                                    |
| 10014 | 0x271E | `BufferSize(usize, usize)`                | "Invalid buffer size, expected {0}, got {1}"                                                                      |

## 11001 - 11009 / IndexedMerkleTreeError Variants

> **Source:** [errors.rs](https://github.com/Lightprotocol/light-protocol/blob/604892ff3902292dd0b0b047cb0bfacc469ea0d4/program-libs/indexed-merkle-tree/src/errors.rs)

| Code  | Hex    | Error                                   | Message                                                             |
| :---- | :----- | :-------------------------------------- | :------------------------------------------------------------------ |
| 11001 | 0x2AF9 | `IntegerOverflow`                       | "Integer overflow"                                                  |
| 11002 | 0x2AFA | `IndexHigherThanMax`                    | "Invalid index, it exceeds the number of elements."                 |
| 11003 | 0x2AFB | `LowElementNotFound`                    | "Could not find the low element."                                   |
| 11004 | 0x2AFC | `LowElementGreaterOrEqualToNewElement`  | "Low element is greater or equal to the provided new element."      |
| 11005 | 0x2AFD | `NewElementGreaterOrEqualToNextElement` | "The provided new element is greater or equal to the next element." |
| 11006 | 0x2AFE | `ElementAlreadyExists`                  | "The element already exists, but was expected to be absent."        |
| 11007 | 0x2AFF | `ElementDoesNotExist`                   | "The element does not exist, but was expected to be present."       |
| 11008 | 0x2B00 | `ChangelogBufferSize(usize, usize)`     | "Invalid changelog buffer size, expected {0}, got {1}"              |
| 11009 | 0x2B01 | `ArrayFull`                             | "Indexed array is full, cannot append more elements"                |

## 12006 - 12019 / AccountError Variants

> **Source:** [error.rs](https://github.com/Lightprotocol/light-protocol/blob/604892ff3902292dd0b0b047cb0bfacc469ea0d4/program-libs/account-checks/src/error.rs)

| Code  | Hex    | Error                        | Message                           |
| :---- | :----- | :--------------------------- | :-------------------------------- |
| 12006 | 0x2EE6 | `InvalidDiscriminator`       | "Invalid Discriminator."          |
| 12007 | 0x2EE7 | `AccountOwnedByWrongProgram` | "Account owned by wrong program." |
| 12008 | 0x2EE8 | `AccountNotMutable`          | "Account not mutable."            |
| 12009 | 0x2EE9 | `BorrowAccountDataFailed`    | "Borrow account data failed."     |
| 12010 | 0x2EEA | `InvalidAccountSize`         | "Invalid Account size."           |
| 12011 | 0x2EEB | `AccountMutable`             | "Account is mutable."             |
| 12012 | 0x2EEC | `AlreadyInitialized`         | "Account is already initialized." |
| 12013 | 0x2EED | `InvalidAccountBalance`      | "Invalid account balance."        |
| 12014 | 0x2EEE | `FailedBorrowRentSysvar`     | "Failed to borrow rent sysvar."   |
| 12015 | 0x2EEF | `InvalidSigner`              | "Invalid Signer"                  |
| 12016 | 0x2EF0 | `InvalidSeeds`               | "Invalid Seeds"                   |
| 12017 | 0x2EF1 | `InvalidProgramId`           | "Invalid Program Id"              |
| 12018 | 0x2EF2 | `ProgramNotExecutable`       | "Program not executable."         |
| 12019 | 0x2EF3 | `AccountNotZeroed`           | "Account not zeroed."             |

## 14001 - 14009 / MerkleTreeMetadataError Variants

> **Source:** [errors.rs](https://github.com/Lightprotocol/light-protocol/blob/604892ff3902292dd0b0b047cb0bfacc469ea0d4/program-libs/merkle-tree-metadata/src/errors.rs)

| Code  | Hex    | Error                             | Message                                     |
| :---- | :----- | :-------------------------------- | :------------------------------------------ |
| 14001 | 0x36B1 | `MerkleTreeAndQueueNotAssociated` | "Merkle tree and queue are not associated." |
| 14002 | 0x36B2 | `RolloverNotConfigured`           | "Rollover not configured."                  |
| 14003 | 0x36B3 | `MerkleTreeAlreadyRolledOver`     | "Merkle tree already rolled over."          |
| 14004 | 0x36B4 | `InvalidQueueType`                | "Invalid queue type."                       |
| 14005 | 0x36B5 | `InsufficientRolloverFee`         | "Insufficient rollover fee."                |
| 14006 | 0x36B6 | `NotReadyForRollover`             | "Merkle tree not ready for rollover."       |
| 14007 | 0x36B7 | `InvalidTreeType`                 | "Invalid tree type."                        |
| 14008 | 0x36B8 | `InvalidRolloverThreshold`        | "Invalid Rollover Threshold."               |
| 14009 | 0x36B9 | `InvalidHeight`                   | "Invalid Height."                           |

## 14017 - 14034 / LightSdkTypesError Variants

> **Source:** [error.rs](https://github.com/Lightprotocol/light-protocol/blob/604892ff3902292dd0b0b047cb0bfacc469ea0d4/sdk-libs/sdk-types/src/error.rs#L4)

| Code  | Hex    | Error                                | Message                                                                                                                                           |
| :---- | :----- | :----------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| 14017 | 0x36C1 | `FewerAccountsThanSystemAccounts`    | "Fewer accounts than system accounts"                                                                                                             |
| 14021 | 0x36C5 | `InitAddressIsNone`                  | "Address is none during initialization"                                                                                                           |
| 14022 | 0x36C6 | `InitWithAddressIsNone`              | "Address is none during initialization with address"                                                                                              |
| 14023 | 0x36C7 | `InitWithAddressOutputIsNone`        | "Output is none during initialization with address"                                                                                               |
| 14024 | 0x36C8 | `MetaMutAddressIsNone`               | "Address is none during meta mutation"                                                                                                            |
| 14025 | 0x36C9 | `MetaMutInputIsNone`                 | "Input is none during meta mutation"                                                                                                              |
| 14026 | 0x36CA | `MetaMutOutputLamportsIsNone`        | "Output lamports is none during meta mutation"                                                                                                    |
| 14027 | 0x36CB | `MetaMutOutputIsNone`                | "Output is none during meta mutation"                                                                                                             |
| 14028 | 0x36CC | `MetaCloseAddressIsNone`             | "Address is none during meta close"                                                                                                               |
| 14029 | 0x36CD | `MetaCloseInputIsNone`               | "Input is none during meta close"                                                                                                                 |
| 14031 | 0x36CF | `CpiAccountsIndexOutOfBounds(usize)` | "CPI accounts index out of bounds: {0}"                                                                                                           |
| 14032 | 0x36D0 | `InvalidCpiContextAccount`           | "Invalid CPI context account"                                                                                                                     |
| 14033 | 0x36D1 | `InvalidSolPoolPdaAccount`           | "Invalid sol pool pda account"                                                                                                                    |
| 14034 | 0x36D2 | `InvalidCpiAccountsOffset`           | "CpiAccounts accounts slice starts with an invalid account. It should start with LightSystemProgram SySTEM1eSU2p4BGQfQpimFEWWSC1XDFeun3Nqzz3rT7." |

## 14301 - 14312 / BatchedMerkleTreeError Variants

> **Source:** [errors.rs](https://github.com/Lightprotocol/light-protocol/blob/604892ff3902292dd0b0b047cb0bfacc469ea0d4/program-libs/batched-merkle-tree/src/errors.rs)

| Code  | Hex    | Error                                 | Message                                                 |
| :---- | :----- | :------------------------------------ | :------------------------------------------------------ |
| 14301 | 0x37DD | `BatchNotReady`                       | "Batch is not ready to be inserted"                     |
| 14302 | 0x37DE | `BatchAlreadyInserted`                | "Batch is already inserted"                             |
| 14303 | 0x37DF | `BatchInsertFailed`                   | "Batch insert failed"                                   |
| 14304 | 0x37E0 | `LeafIndexNotInBatch`                 | "Leaf index not in batch."                              |
| 14305 | 0x37E1 | `InvalidNetworkFee`                   | "Invalid network fee."                                  |
| 14306 | 0x37E2 | `BatchSizeNotDivisibleByZkpBatchSize` | "Batch size not divisible by ZKP batch size."           |
| 14307 | 0x37E3 | `InclusionProofByIndexFailed`         | "Inclusion proof by index failed."                      |
| 14308 | 0x37E4 | `InvalidBatchIndex`                   | "Invalid batch index"                                   |
| 14309 | 0x37E5 | `InvalidIndex`                        | "Invalid index"                                         |
| 14310 | 0x37E6 | `TreeIsFull`                          | "Batched Merkle tree is full."                          |
| 14311 | 0x37E7 | `NonInclusionCheckFailed`             | "Value already exists in bloom filter."                 |
| 14312 | 0x37E8 | `BloomFilterNotZeroed`                | "Bloom filter must be zeroed prior to reusing a batch." |

## 15001 - 15017 / ZeroCopyError Variants

> **Source:** [errors.rs](https://github.com/Lightprotocol/light-protocol/blob/604892ff3902292dd0b0b047cb0bfacc469ea0d4/program-libs/zero-copy/src/errors.rs)

| Code  | Hex    | Error                                       | Message                                                      |
| :---- | :----- | :------------------------------------------ | :----------------------------------------------------------- |
| 15001 | 0x3A99 | `Full`                                      | "The vector is full, cannot push any new elements"           |
| 15002 | 0x3A9A | `ArraySize(usize, usize)`                   | "Requested array of size {}, but the vector has {} elements" |
| 15003 | 0x3A9B | `IterFromOutOfBounds`                       | "The requested start index is out of bounds"                 |
| 15004 | 0x3A9C | `InsufficientMemoryAllocated(usize, usize)` | "Memory allocated {}, Memory required {}"                    |
| 15006 | 0x3A9E | `UnalignedPointer`                          | "Unaligned pointer"                                          |
| 15007 | 0x3A9F | `MemoryNotZeroed`                           | "Memory not zeroed"                                          |
| 15008 | 0x3AA0 | `InvalidConversion`                         | "Invalid conversion"                                         |
| 15009 | 0x3AA1 | `InvalidData(Infallible)`                   | "Invalid data"                                               |
| 15010 | 0x3AA2 | `Size`                                      | "Invalid size"                                               |
| 15011 | 0x3AA3 | `InvalidOptionByte(u8)`                     | "Invalid option byte {} must be 0 (None) or 1 (Some)"        |
| 15012 | 0x3AA4 | `InvalidCapacity`                           | "Invalid capacity. Capacity must be greater than 0"          |
| 15013 | 0x3AA5 | `LengthGreaterThanCapacity`                 | "Length is greater than capacity"                            |
| 15014 | 0x3AA6 | `CurrentIndexGreaterThanLength`             | "Current index is greater than length"                       |
| 15015 | 0x3AA7 | `InvalidEnumValue`                          | "Invalid enum value"                                         |
| 15016 | 0x3AA8 | `InsufficientCapacity`                      | "Insufficient capacity for operation"                        |
| 15017 | 0x3AA9 | `PlatformSizeOverflow`                      | "Value too large for platform usize"                         |

## 16001 - 16034 / LightSdkError Variants

> **Source:** [error.rs](https://github.com/Lightprotocol/light-protocol/blob/main/sdk-libs/sdk/src/error.rs#L126)

| Code  | Hex    | Error                                | Message                                                                                                                                           |
| :---- | :----- | :----------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| 16001 | 0x3E81 | `ConstraintViolation`                | "Constraint violation"                                                                                                                            |
| 16002 | 0x3E82 | `InvalidLightSystemProgram`          | "Invalid light-system-program ID"                                                                                                                 |
| 16003 | 0x3E83 | `ExpectedAccounts`                   | "Expected accounts in the instruction"                                                                                                            |
| 16004 | 0x3E84 | `ExpectedAddressTreeInfo`            | "Expected address Merkle context to be provided"                                                                                                  |
| 16005 | 0x3E85 | `ExpectedAddressRootIndex`           | "Expected address root index to be provided"                                                                                                      |
| 16006 | 0x3E86 | `ExpectedData`                       | "Accounts with a specified input are expected to have data"                                                                                       |
| 16007 | 0x3E87 | `ExpectedDiscriminator`              | "Accounts with specified data are expected to have a discriminator"                                                                               |
| 16008 | 0x3E88 | `ExpectedHash`                       | "Accounts with specified data are expected to have a hash"                                                                                        |
| 16009 | 0x3E89 | `ExpectedLightSystemAccount(String)` | "Expected the `{0}` light account to be provided"                                                                                                 |
| 16010 | 0x3E8A | `ExpectedMerkleContext`              | "`mut` and `close` accounts are expected to have a Merkle context"                                                                                |
| 16011 | 0x3E8B | `ExpectedRootIndex`                  | "Expected root index to be provided"                                                                                                              |
| 16012 | 0x3E8C | `TransferFromNoInput`                | "Cannot transfer lamports from an account without input"                                                                                          |
| 16013 | 0x3E8D | `TransferFromNoLamports`             | "Cannot transfer from an account without lamports"                                                                                                |
| 16014 | 0x3E8E | `TransferFromInsufficientLamports`   | "Account, from which a transfer was attempted, has insufficient amount of lamports"                                                               |
| 16015 | 0x3E8F | `TransferIntegerOverflow`            | "Integer overflow resulting from too large resulting amount"                                                                                      |
| 16016 | 0x3E90 | `Borsh`                              | "Borsh error."                                                                                                                                    |
| 16017 | 0x3E91 | `FewerAccountsThanSystemAccounts`    | "Fewer accounts than number of system accounts."                                                                                                  |
| 16018 | 0x3E92 | `InvalidCpiSignerAccount`            | "InvalidCpiSignerAccount"                                                                                                                         |
| 16019 | 0x3E93 | `MissingField(String)`               | "Missing meta field: {0}"                                                                                                                         |
| 16020 | 0x3E94 | `OutputStateTreeIndexIsNone`         | "Output state tree index is none. Use an CompressedAccountMeta type with output tree index to initialize or update accounts."                     |
| 16021 | 0x3E95 | `InitAddressIsNone`                  | "Address is none during initialization"                                                                                                           |
| 16022 | 0x3E96 | `InitWithAddressIsNone`              | "Address is none during initialization with address"                                                                                              |
| 16023 | 0x3E97 | `InitWithAddressOutputIsNone`        | "Output is none during initialization with address"                                                                                               |
| 16024 | 0x3E98 | `MetaMutAddressIsNone`               | "Address is none during meta mutation"                                                                                                            |
| 16025 | 0x3E99 | `MetaMutInputIsNone`                 | "Input is none during meta mutation"                                                                                                              |
| 16026 | 0x3E9A | `MetaMutOutputLamportsIsNone`        | "Output lamports is none during meta mutation"                                                                                                    |
| 16027 | 0x3E9B | `MetaMutOutputIsNone`                | "Output is none during meta mutation"                                                                                                             |
| 16028 | 0x3E9C | `MetaCloseAddressIsNone`             | "Address is none during meta close"                                                                                                               |
| 16029 | 0x3E9D | `MetaCloseInputIsNone`               | "Input is none during meta close"                                                                                                                 |
| 16031 | 0x3E9F | `CpiAccountsIndexOutOfBounds(usize)` | "CPI accounts index out of bounds: {0}"                                                                                                           |
| 16032 | 0x3EA0 | `InvalidCpiContextAccount`           | "Invalid CPI context account"                                                                                                                     |
| 16033 | 0x3EA1 | `InvalidSolPoolPdaAccount`           | "Invalid SolPool PDA account"                                                                                                                     |
| 16034 | 0x3EA2 | `InvalidCpiAccountsOffset`           | "CpiAccounts accounts slice starts with an invalid account. It should start with LightSystemProgram SySTEM1eSU2p4BGQfQpimFEWWSC1XDFeun3Nqzz3rT7." |
