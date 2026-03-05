# Cabal Project Guide

## Cabal File Format

### Basic Package Structure
```cabal
cabal-version: 3.0  -- Use latest cabal format
name: myproject
version: 0.1.0.0
synopsis: A short description
description: 
    A longer description of the project.
    .
    This can span multiple paragraphs and include formatting.

license: MIT
license-file: LICENSE
author: Your Name
maintainer: you@example.com
homepage: https://github.com/yourusername/myproject
bug-reports: https://github.com/yourusername/myproject/issues
copyright: 2024 Your Name
category: Development
build-type: Simple

-- Additional metadata
extra-source-files: 
    README.md
    CHANGELOG.md
extra-doc-files:
    docs/*.md

source-repository head
  type: git
  location: https://github.com/yourusername/myproject
```

### Library Section
```cabal
library
  -- Expose modules for library users
  exposed-modules:
      MyProject
      MyProject.Core
      MyProject.Utils
  
  -- Internal modules not exposed to users
  other-modules:
      MyProject.Internal
      MyProject.Types
  
  -- Re-export modules from dependencies
  reexported-modules:
      Data.Text as MyProject.Text,
      Control.Monad as MyProject.Monad
  
  -- Source directories
  hs-source-dirs: src
  
  -- Language and extensions
  default-language: Haskell2010
  default-extensions:
      DerivingStrategies  
      LambdaCase
  
  -- GHC options for all modules
  ghc-options: 
      -Wall
      -Wcompat
      -Widentities
      -Wincomplete-record-updates
      -Wincomplete-uni-patterns
      -Wmissing-home-modules
      -Wpartial-fields
      -Wredundant-constraints
  
  -- Dependencies with version bounds
  build-depends:
      base >= 4.7 && < 5,
      text >= 1.2 && < 3,
      aeson >= 2.0 && < 3,
      containers >= 0.6 && < 0.8
```

### Executable Section
```cabal
executable myproject-exe
  -- Main module
  main-is: Main.hs
  
  -- Source directory
  hs-source-dirs: app
  
  -- Language settings (inherit from common)
  default-language: Haskell2010
  default-extensions:
      OverloadedStrings
  
  -- Optimization for executables
  ghc-options:
      -Wall
      -threaded
      -rtsopts
      -with-rtsopts=-N
      -O2
  
  -- Dependencies (including our own library)
  build-depends:
      base,
      myproject,
      optparse-applicative >= 0.16,
      text
```

### Test Suites
```cabal
test-suite myproject-test
  type: exitcode-stdio-1.0
  main-is: Spec.hs
  hs-source-dirs: test
  
  default-language: Haskell2010
  default-extensions:
      OverloadedStrings
  
  ghc-options:
      -Wall
      -threaded
      -rtsopts
      -with-rtsopts=-N
  
  build-depends:
      base,
      myproject,
      hspec >= 2.7,
      QuickCheck >= 2.14,
      text
  
  -- Discover test modules automatically
  build-tool-depends:
      hspec-discover:hspec-discover

-- Property-based test suite
test-suite myproject-properties
  type: exitcode-stdio-1.0
  main-is: Properties.hs
  hs-source-dirs: test-properties
  
  default-language: Haskell2010
  
  build-depends:
      base,
      myproject,
      QuickCheck,
      quickcheck-instances
```

### Benchmarks
```cabal
benchmark myproject-bench
  type: exitcode-stdio-1.0
  main-is: Main.hs  
  hs-source-dirs: bench
  
  default-language: Haskell2010
  
  ghc-options:
      -Wall
      -O2
      -threaded
      -rtsopts
      -with-rtsopts=-N
  
  build-depends:
      base,
      myproject,
      criterion >= 1.5,
      deepseq
```

## Common Stanzas

### Sharing Configuration
```cabal
cabal-version: 3.0
name: myproject

-- Define common options
common shared-properties
  default-language: Haskell2010
  default-extensions:
      OverloadedStrings
      DerivingStrategies
      LambdaCase
      MultiWayIf
      TypeApplications
  
  ghc-options:
      -Wall
      -Wcompat
      -Widentities
      -Wincomplete-record-updates
      -Wincomplete-uni-patterns
      -Wmissing-home-modules
      -Wpartial-fields
      -Wredundant-constraints
  
  build-depends:
      base >= 4.7 && < 5

common executable-properties
  import: shared-properties
  ghc-options:
      -threaded
      -rtsopts
      -with-rtsopts=-N
      -O2

-- Use in components
library
  import: shared-properties
  exposed-modules: MyProject
  hs-source-dirs: src
  
executable myproject-exe
  import: executable-properties
  main-is: Main.hs
  hs-source-dirs: app
  build-depends: myproject
```

## Multi-Package Projects

### cabal.project Structure
```
myproject/
├── cabal.project          -- Project configuration
├── myproject-core/
│   ├── myproject-core.cabal
│   └── src/
├── myproject-web/  
│   ├── myproject-web.cabal
│   └── src/
├── myproject-cli/
│   ├── myproject-cli.cabal
│   └── src/
└── test-utils/
    ├── test-utils.cabal
    └── src/
```

### cabal.project Configuration
```cabal
-- cabal.project
packages: 
  myproject-core
  myproject-web
  myproject-cli
  test-utils

-- Global flags
tests: True
benchmarks: False
documentation: False

-- Package-specific configuration
package myproject-core
  tests: True
  benchmarks: True
  documentation: True

package myproject-web  
  flags: +development

-- Dependency overrides
constraints: 
  aeson >= 2.0,
  text >= 2.0

-- Allow newer versions
allow-newer: 
  base,
  *:base

-- Source repositories for unreleased packages
source-repository-package
  type: git
  location: https://github.com/example/some-library
  tag: main

-- Local source overrides  
source-repository-package
  type: git
  location: file:///path/to/local/repo
```

### Cross-Package Dependencies
```cabal
-- myproject-web.cabal
library
  build-depends:
      base,
      myproject-core,  -- Local dependency
      servant >= 0.18

-- myproject-cli.cabal  
executable myproject-cli
  build-depends:
      base,
      myproject-core,  -- Shared core
      optparse-applicative

-- test-utils.cabal (shared test utilities)
library
  exposed-modules:
      Test.MyProject.Utils
      Test.MyProject.Generators
  build-depends:
      base,
      myproject-core,
      QuickCheck,
      hspec
```

## Conditional Compilation

### Flags
```cabal
-- Define flags
flag development
  description: Enable development features
  default: False
  manual: True

flag static
  description: Build static executables
  default: False
  manual: True

library
  -- Conditional modules
  if flag(development)
    exposed-modules: MyProject.Debug
    build-depends: debug >= 0.1
  else
    build-depends: 
  
  -- Conditional compilation
  if flag(static)
    ghc-options: -static -optl-static
    cc-options: -static

-- Conditional dependencies based on OS
if os(windows)
  build-depends: Win32 >= 2.3
if os(linux) || os(darwin)  
  build-depends: unix >= 2.7

-- GHC version conditionals
if impl(ghc >= 9.2)
  default-extensions: OverloadedRecordDot
if impl(ghc < 9.0)
  build-depends: semigroups
```

### Build Configuration
```cabal
-- Architecture-specific options
if arch(x86_64)
  cpp-options: -DARCH_X86_64
  cc-options: -march=native

-- Custom preprocessor  
if flag(use-template-haskell)
  build-depends: template-haskell >= 2.16
  other-extensions: TemplateHaskell
```

## Advanced Features

### Custom Setup
```cabal
-- myproject.cabal
build-type: Custom
custom-setup
  setup-depends:
      base >= 4.7,
      Cabal >= 3.0,
      directory
```

```haskell
-- Setup.hs
import Distribution.Simple
import Distribution.Simple.Setup
import Distribution.Simple.LocalBuildInfo  
import System.Directory

main = defaultMainWithHooks simpleUserHooks
  { preBuild = \args flags -> do
      putStrLn "Running custom pre-build step"
      createDirectoryIfMissing True "generated"
      writeFile "generated/BuildInfo.hs" buildInfoModule
      preBuild simpleUserHooks args flags
  }

buildInfoModule :: String
buildInfoModule = unlines
  [ "module BuildInfo where"
  , "buildTime :: String"  
  , "buildTime = " ++ show "2024-01-01"
  ]
```

### Foreign Libraries
```cabal
foreign-library myproject-c
  type: native-shared
  lib-version-info: 1:0:0
  
  if os(Windows)
    type: native-static
    lib-version-info: 1
  
  other-modules: MyProject.Foreign
  build-depends: base, myproject
  hs-source-dirs: cbits
  c-sources: cbits/wrapper.c
  include-dirs: cbits
  install-includes: myproject.h
```

## Dependency Management

### Version Bounds Best Practices
```cabal
build-depends:
  -- Core dependencies - conservative bounds
  base >= 4.14 && < 4.20,
  text >= 1.2 && < 2.2,
  containers >= 0.6 && < 0.8,
  
  -- Stable packages - wider bounds OK
  aeson >= 1.5 && < 3,
  
  -- Unstable packages - tight bounds
  new-experimental-lib >= 0.1.2 && < 0.2,
  
  -- Internal packages - any version
  myproject-core
```

### Dependency Categories
```cabal
library
  -- Public API dependencies (affect downstream)
  build-depends:
      base,
      text,
      aeson
  
  -- Private implementation dependencies
  build-depends:
      containers,
      unordered-containers,
      hashable
  
  -- Development-only dependencies
  build-depends:
      -- None in library!

executable myproject-exe  
  -- Can have looser bounds
  build-depends:
      base,
      myproject,
      optparse-applicative >= 0.15

test-suite tests
  -- Test-specific dependencies
  build-depends:
      base,
      myproject,
      hspec >= 2.7,
      QuickCheck >= 2.13,
      temporary,
      directory
```

## Publishing to Hackage

### Package Preparation
```cabal
cabal-version: 3.0
name: myproject
version: 1.0.0.0

-- Complete metadata required
synopsis: One-line description (< 80 chars)
description:
    Longer description explaining what the package does.
    .
    * Feature 1
    * Feature 2
    .
    Example usage:
    .
    > import MyProject
    > result = doSomething "input"

license: MIT
license-file: LICENSE
author: Your Name <you@example.com>
maintainer: you@example.com
copyright: 2024 Your Name  
homepage: https://github.com/yourusername/myproject
bug-reports: https://github.com/yourusername/myproject/issues
category: Development

-- Version bounds for Hackage
tested-with: 
    GHC == 8.10.7,
    GHC == 9.0.2,
    GHC == 9.2.8,
    GHC == 9.4.8,
    GHC == 9.6.3

extra-source-files:
    README.md
    CHANGELOG.md
    examples/*.hs
```

### Release Checklist
```bash
# 1. Update version and changelog
# 2. Test with multiple GHC versions
cabal test --enable-tests

# 3. Generate documentation
cabal haddock --haddock-all

# 4. Check package
cabal check

# 5. Build source distribution
cabal sdist

# 6. Test the sdist
cd dist-newstyle/sdist
tar -xf myproject-1.0.0.0.tar.gz
cd myproject-1.0.0.0
cabal build

# 7. Upload to Hackage
cabal upload myproject-1.0.0.0.tar.gz

# 8. Upload documentation (optional)
cabal upload --documentation myproject-1.0.0.0.tar.gz
```

### Hackage Metadata
```cabal
-- Hackage categories (choose appropriate ones)
category: 
    Data,
    Development,
    Web,
    System,
    Network

-- Package stability
stability: experimental  -- or alpha, provisional, stable

-- Hackage tags (in description)
description:
    Tags: json, web, api, cli
```

## Continuous Integration

### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macOS-latest, windows-latest]
        ghc: ['8.10', '9.0', '9.2', '9.4', '9.6']
        
    steps:
    - uses: actions/checkout@v3
    
    - uses: haskell/actions/setup@v2
      with:
        ghc-version: ${{ matrix.ghc }}
        cabal-version: 'latest'
        
    - name: Cache dependencies  
      uses: actions/cache@v3
      with:
        path: ~/.cabal
        key: ${{ runner.os }}-${{ matrix.ghc }}-cabal
        
    - name: Build dependencies
      run: cabal build --dependencies-only --enable-tests
      
    - name: Build
      run: cabal build --enable-tests
      
    - name: Test
      run: cabal test --enable-tests
      
    - name: Documentation
      run: cabal haddock --haddock-all
```

### Nix CI Integration
```yaml
# .github/workflows/nix.yml
name: Nix CI
on: [push, pull_request]

jobs:
  nix-build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: cachix/install-nix-action@v18
    - uses: cachix/cachix-action@v12
      with:
        name: myproject
        authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
        
    - name: Build with Nix
      run: nix build
      
    - name: Run tests
      run: nix run .#test
```

This comprehensive guide covers modern Cabal usage patterns, from simple packages to complex multi-package projects with proper dependency management and CI/CD integration.
