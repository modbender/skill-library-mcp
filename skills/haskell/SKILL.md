---
name: haskell
description: Expert Haskell development skill. Covers type-driven design, GHC extensions, Cabal/Stack/Nix builds, performance optimization, testing, and the modern Haskell library ecosystem. Activate for any Haskell programming, debugging, or architecture tasks.
---

# Haskell Development Guide

## Core Philosophy

1. **Types are the design** — Make illegal states unrepresentable. If the type checker accepts it, we would like it to be correct.
2. **Purity by default** — Side effects are explicit in the type system. `IO` is a feature, not a burden.
3. **Composition over inheritance** — Small, composable functions. Typeclasses for ad-hoc polymorphism.
4. **Laziness as a tool** — Enables elegant abstractions but demands awareness of space leaks.
5. **Correctness first, then performance** — Get it right, then profile, then optimize.
5. **Keep it Simple** — Purity and strong types (i.e. roughly Haskell2010) gives you the majority of Haskell's value.  Avoid more advanced language features unless absolutely necessary.

## Project Setup

### Cabal (preferred with Nix)

```bash
mkdir my-project && cd my-project
cabal init --interactive
```

Minimal `my-project.cabal`:
```cabal
cabal-version: 3.0
name:          my-project
version:       0.1.0.0
build-type:    Simple

common warnings
    ghc-options: -Wall -Werror -Wcompat -Widentities
                 -Wincomplete-record-updates
                 -Wincomplete-uni-patterns
                 -Wpartial-fields
                 -Wredundant-constraints

library
    import:           warnings
    exposed-modules:  MyProject
    build-depends:    base >= 4.17 && < 5
                    , text
                    , containers
                    , aeson
    hs-source-dirs:   src
    default-language:  Haskell2010
    default-extensions:
        DeriveGeneric
        DerivingStrategies
        LambdaCase
        ScopedTypeVariables

executable my-project
    import:           warnings
    main-is:          Main.hs
    build-depends:    base, my-project
    hs-source-dirs:   app
    default-language: Haskell2010

test-suite tests
    import:           warnings
    type:             exitcode-stdio-1.0
    main-is:          Main.hs
    build-depends:    base, my-project, hspec, QuickCheck
    hs-source-dirs:   test
    default-language: Haskell2010
```

## Project Structure

```
my-project/
├── exe/
│   └── Main.hs              # Executable entry point (thin — delegates to library)
├── src/
│   ├── MyProject.hs          # Public API (re-exports)
│   ├── MyProject/
│   │   ├── Types.hs          # Core domain types
│   │   ├── App.hs            # Application monad, config
│   │   ├── DB.hs             # Database layer
│   │   ├── API.hs            # HTTP/API layer
│   │   └── Internal/         # Not exported — implementation details
│   │       └── Utils.hs
├── test/
│   ├── Main.hs
│   └── MyProject/
│       ├── TypesSpec.hs
│       └── DBSpec.hs
├── my-project.cabal
├── cabal.project             # Multi-package config, source-repository-packages
```

## Essential GHC Extensions

### Always Enable (via `default-extensions` in .cabal)
```haskell
DeriveGeneric           -- Derives Generic
DerivingStrategies      -- Explicit: deriving stock, newtype, anyclass, via
LambdaCase              -- \case { ... } instead of \x -> case x of ...
ScopedTypeVariables     -- forall a. ... lets you reference 'a' in where clauses
```

### Use Freely When Needed
```haskell
BangPatterns
DeriveDataTypeable
DeriveFunctor
DeriveGeneric               -- Generic instances for aeson, etc.
DerivingVia                 -- Derive via newtype coercion
DuplicateRecordFields       -- Same field name in different records
ExistentialQuantification   -- Hide type variables
FlexibleContexts            -- Relax context restrictions
FlexibleInstances           -- Relax instance head restrictions
FunctionalDependencies      -- fundeps for MPTC
GeneralizedNewtypeDeriving  -- Derive through newtypes
MultiParamTypeClasses       -- Typeclasses with multiple params
NumericUnderscores          -- More readable number syntax
OverloadedRecordDot         -- record.field syntax (GHC 9.2+)
OverloadedStrings           -- String literals as Text/ByteString
RankNTypes                  -- Higher-rank polymorphism (forall inside arrows)
RecordWildCards             -- Controversial but can be used effectively
```

### Avoid unless there's a significant clear value
```haskell
TemplateHaskell         -- Metaprogramming (aeson TH, lens TH). Slows compilation.
GADTs                   -- Generalized algebraic data types
TypeFamilies            -- Type-level functions
DataKinds               -- Promote data constructors to types
ConstraintKinds         -- Alias constraint sets
UndecidableInstances    -- Sometimes needed for MTL/type families. Understand why.
TypeOperators           -- type a :+: b. Servant uses heavily.
AllowAmbiguousTypes     -- Pair with TypeApplications for type-level dispatch.
```

## Type-Driven Development

### Scope accessors with type name to avoid name clashes

```
data User = User
  { _user_firstName :: String
  , _user_email :: String
  } deriving (Eq,Ord,Show,Read,Generic)
```

### Make Illegal States Unrepresentable
```haskell
-- BAD: stringly-typed
data User = User { _user_role :: String, _user_email :: String }

-- GOOD: types encode constraints
data Role = Admin | Editor | Viewer
  deriving stock (Show, Eq, Ord)

newtype Email = Email { _unEmail :: Text }  -- smart constructor validates

mkEmail :: Text -> Either EmailError Email
mkEmail t
  | "@" `T.isInfixOf` t = Right (Email t)
  | otherwise = Left InvalidEmail

data User = User
  { _user_role  :: !Role
  , _user_email :: !Email
  }
```

### Phantom Types for State Machines
```haskell
data Draft
data Published

data Article (s :: Type) = Article
  { articleTitle   :: !Text
  , articleContent :: !Text
  }

publish :: Article Draft -> Article Published
publish (Article t c) = Article t c

-- Only published articles can be shared
share :: Article Published -> IO ()
share = ...
```

### Newtypes for Safety
```haskell
newtype UserId    = UserId    { unUserId    :: Int64 } deriving newtype (Eq, Ord, Show, FromJSON, ToJSON)
newtype ProductId = ProductId { unProductId :: Int64 } deriving newtype (Eq, Ord, Show, FromJSON, ToJSON)

-- Now you can't accidentally pass a ProductId where UserId is expected
getUser :: UserId -> IO User
```

## Error Handling

```haskell
-- Pure errors: Either
parseConfig :: Text -> Either ConfigError Config

-- App-level errors: ExceptT or MonadError
class Monad m => MonadError e m where
  throwError :: e -> m a
  catchError :: m a -> (e -> m a) -> m a

-- The ReaderT pattern (simple, composable)
newtype App a = App { unApp :: ReaderT AppEnv IO a }
  deriving newtype (Functor, Applicative, Monad, MonadIO, MonadReader AppEnv)

data AppError
  = NotFound Text
  | Unauthorized
  | ValidationError [Text]
  deriving stock (Show)

-- Throw with exceptions in IO, catch at boundaries
throwIO :: Exception e => e -> IO a
catch   :: Exception e => IO a -> (e -> IO a) -> IO a

-- RULE: Use Either for expected failures, exceptions for unexpected/IO failures.
-- Never use error/undefined in library code.
```

## Common Patterns

### The ReaderT Pattern
```haskell
data AppEnv = AppEnv
  { appDbPool   :: !Pool Connection
  , appLogger   :: !Logger
  , appConfig   :: !Config
  }

newtype App a = App (ReaderT AppEnv IO a)
  deriving newtype (Functor, Applicative, Monad, MonadIO, MonadReader AppEnv)

runApp :: AppEnv -> App a -> IO a
runApp env (App m) = runReaderT m env

-- Use Has-pattern for granular access:
class Has field env where
  obtain :: env -> field

instance Has (Pool Connection) AppEnv where
  obtain = appDbPool

grabPool :: (MonadReader env m, Has (Pool Connection) env) => m (Pool Connection)
grabPool = asks obtain
```

### Optics (lens/optics)
```haskell
-- With OverloadedRecordDot (GHC 9.2+), often you don't need lens for simple access.
-- Use lens/optics for: nested updates, traversals, prisms for sum types.

-- lens: view, set, over
view _1 (1, 2)       -- 1
set _1 10 (1, 2)     -- (10, 2)
over _1 (+1) (1, 2)  -- (2, 2)

-- Compose with (.)
view (config . database . host) appEnv
over (users . each . name) T.toUpper myData
```

## Testing

### HSpec - Testing Framework
```haskell
-- test/MyProject/TypesSpec.hs
module MyProject.TypesSpec (spec) where

import Test.Hspec
import MyProject.Types

spec :: Spec
spec = do
  describe "mkEmail" $ do
    it "accepts valid emails" $
      mkEmail "user@example.com" `shouldBe` Right (Email "user@example.com")

    it "rejects invalid emails" $
      mkEmail "invalid" `shouldSatisfy` isLeft
```

### QuickCheck - Property Testing
```haskell
import Test.QuickCheck

prop_reverseReverse :: [Int] -> Bool
prop_reverseReverse xs = reverse (reverse xs) == xs

-- Generate domain types:
instance Arbitrary Email where
  arbitrary = do
    user   <- listOf1 (elements ['a'..'z'])
    domain <- listOf1 (elements ['a'..'z'])
    pure $ Email $ T.pack $ user <> "@" <> domain <> ".com"
```

## Performance Essentials

### Strictness
```haskell
-- Strict fields in data types (almost always want this):
data Config = Config
  { configHost :: !Text       -- strict (bang pattern in field)
  , configPort :: !Int
  }

-- BangPatterns in let bindings:
{-# LANGUAGE BangPatterns #-}
let !result = expensiveComputation

-- Use Text, not String. Always.
-- Use ByteString for binary data.
-- Use Vector for indexed access, [] for sequential processing.
-- Use HashMap/HashSet for large unordered collections.
-- Use Map/Set for ordered collections or when Ord is available.
```

### Profiling
```bash
# Build with profiling
cabal build --enable-profiling

# Run with heap profiling
./my-project +RTS -hc -p -RTS

# Time profiling report
./my-project +RTS -p -RTS
# Generates my-project.prof

# Heap profile visualization
hp2ps -c my-project.hp
```

### Common Space Leaks
```haskell
-- BAD: lazy accumulator
foldl (+) 0 [1..1000000]  -- builds giant thunk chain

-- GOOD: strict left fold
foldl' (+) 0 [1..1000000]  -- evaluates as it goes

-- BAD: lazy state
modify (\s -> s { count = count s + 1 })  -- thunk builds up

-- GOOD: strict state
modify' (\s -> s { count = count s + 1 })
-- Or: use strict fields + evaluate
```

## Commands Reference

| Task | Command |
|------|---------|
| Build | `cabal build` |
| Run | `cabal run my-project` |
| Test | `cabal test --test-show-details=direct` |
| REPL | `cabal repl` |
| Docs | `cabal haddock` |
| Lint | `hlint src/` |
| File watch | `ghcid --command="cabal repl"` |
| Deps outdated | `cabal outdated` |
| Clean | `cabal clean` |
| Nix build | `nix build` |
| Nix dev shell | `nix develop` |

## Common Gotchas

1. **String is [Char]** — Use `Text` (from `text` package) everywhere. Enable `OverloadedStrings` for Text string literals.
2. **Lazy IO** — `readFile` from Prelude is lazy. Use `Data.Text.IO.readFile` or `ByteString.readFile` instead.
3. **Orphan instances** — Don't define typeclass instances outside the module that defines the type or the class. Use newtypes to wrap.
4. **Cabal hell** — Use Nix or cabal's built-in solver (v2-build). Don't use `cabal-install` v1 commands.
5. **Records** — Field names are global. Prefix field names with a uniform and readable scheme: `_employee_familyName`.
6. **Partial functions** — Never use `head`, `tail`, `fromJust`, `read` in production code. Use pattern matching or safe alternatives.
7. **Unsafe operations** - Never use `accursedUnutterablePerformIO`. Only use `unsafePerformIO` when you can prove its use correct.
8. **Undefined** - `undefined` is a fantastic tool for stubbing things out for incremental development and type checking.  It should never exist in production code.
9. **foldl vs foldl'** — Always use `foldl'` (strict). The lazy `foldl` from Prelude is almost never what you want.
10. **Show for serialization** — `Show` is for debugging. Use `aeson` for JSON, `binary`/`cereal` for binary serialization.
11. **MonadFail** — Pattern match failures in `do` blocks require `MonadFail`. Avoid partial patterns in `do`.
12. **Template Haskell ordering** — TH splices create declaration groups. All TH splices must come after the declarations they reference and before declarations that reference the generated code.

## Key Libraries

| Library | Purpose |
|---------|---------|
| `text` | Unicode text (strict & lazy) |
| `bytestring` | Binary data |
| `aeson` | JSON encoding/decoding |
| `postgresql-simple`, `mysql-simple` | Low-level database library |
| `lens` / `optics` | Composable getters/setters |
| `mtl` | Monad transformer classes |
| `containers` | Map, Set, Seq (ordered) |
| `unordered-containers` | HashMap, HashSet (fast) |
| `vector` | Efficient arrays |
| `conduit` / `streaming` | Streaming data processing |
| `warp` | Fast HTTP server |
| `http-client` | Library for making http requests |
| `stm` | Software transactional memory |
| `QuickCheck` | Property-based testing |
| `hspec` | BDD-style test framework |
| `tasty` | Test framework (composable) |
| `criterion` | Benchmarking |
| `optparse-applicative` | CLI argument parsing |
| `katip` | Structured logging |
| `fake` | Generating realistic mock data |

## References

For detailed information, see:
- `references/type-system.md` — ADTs, GADTs, type families, type classes, DataKinds, phantom types
- `references/common-patterns.md` — MTL, ReaderT, effect systems, optics, free monads, type-level programming
- `references/libraries.md` — Essential library ecosystem with examples
- `references/performance.md` — Strictness, profiling, space leaks, concurrency, benchmarking
- `references/ghc-extensions.md` — Comprehensive GHC extension guide by category
- `references/nix-haskell.md` — Nix-based Haskell development (nixpkgs + haskell.nix)
- `references/cabal-guide.md` — Cabal format, multi-package projects, Hackage publishing
- `references/best-practices.md` — Code organization, Haddock, CI, style guide
