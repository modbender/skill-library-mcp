# Nix-Based Haskell Development

## Why Nix for Haskell

1. **Reproducible builds** - Same dependencies everywhere, no version conflicts
2. **Isolated environments** - Different projects can use different GHC/package versions  
3. **System integration** - Easy to add C libraries, databases, tools
4. **Binary caches** - Avoid rebuilding everything from source
5. **Cross-compilation** - Build for different architectures

## Modern Approach: haskell-flake

### Basic Project Setup
```nix
# flake.nix
{
  description = "My Haskell project";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    haskell-flake.url = "github:srid/haskell-flake";
  };
  
  outputs = inputs@{ self, nixpkgs, haskell-flake, ... }:
    haskell-flake.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-darwin" ];
      
      haskellProjects.default = {
        basePackages = nixpkgs.haskellPackages;  
        
        packages.myproject.root = ./.;  # Local package
        
        devShell.tools = hp: {
          inherit (hp) 
            haskell-language-server
            hlint  
            ormolu
            haskell-ci;
          inherit (nixpkgs) 
            ghcid
            cabal-install;
        };
      };
    };
}
```

### Multi-Package Projects
```nix
# flake.nix for workspace with multiple packages
{
  outputs = inputs@{ self, nixpkgs, haskell-flake, ... }:
    haskell-flake.lib.mkFlake { inherit inputs; } {
      haskellProjects.default = {
        basePackages = nixpkgs.haskellPackages;
        
        # Local packages
        packages = {
          myproject-core.root = ./core;
          myproject-web.root = ./web;  
          myproject-cli.root = ./cli;
        };
        
        # Package-specific settings
        settings = {
          myproject-core = {
            jailbreak = true;      # Ignore version bounds
            check = false;         # Disable tests for this package
          };
          myproject-web = {
            buildFromSdist = true; # Test packaging
          };
        };
      };
    };
}
```

### Using Different GHC Versions
```nix
{
  outputs = inputs@{ self, nixpkgs, haskell-flake, ... }:
    haskell-flake.lib.mkFlake { inherit inputs; } {
      haskellProjects = {
        # Default project with latest GHC
        default = {
          basePackages = nixpkgs.haskellPackages;
          packages.myproject.root = ./.;
        };
        
        # Legacy project with older GHC  
        ghc96 = {
          basePackages = nixpkgs.haskell.packages.ghc96;
          packages.myproject.root = ./.;
        };
        
        # Bleeding edge with latest GHC
        ghc98 = {
          basePackages = nixpkgs.haskell.packages.ghc98;
          packages.myproject.root = ./.;
        };
      };
    };
}
```

## Traditional Approach: nixpkgs haskellPackages

### Basic shell.nix
```nix
{ pkgs ? import <nixpkgs> {} }:
let
  ghc = pkgs.haskell.packages.ghc9121;  # Choose GHC version
in
ghc.shellFor {
  packages = p: [ (p.callCabal2nix "myproject" ./. {}) ];
  
  buildInputs = with pkgs; [
    ghc.haskell-language-server  
    ghc.hlint
    ghc.ormolu
    ghc.cabal-install
    ghcid
    
    # System tools
    zlib.dev
    pkg-config
  ];
  
  withHoogle = true;  # Local documentation
  
  shellHook = ''
    echo "Haskell development environment"
    echo "GHC version: $(ghc --version)"
    export PS1="[haskell] $PS1"
  '';
}
```

### Overriding Dependencies
```nix
{ pkgs ? import <nixpkgs> {} }:
let
  hpkgs = pkgs.haskell.packages.ghc9121.override {
    overrides = hself: hsuper: {
      # Use newer version of a package
      aeson = hself.callHackage "aeson" "2.2.1.0" {};
      
      # Use git version
      servant = hself.callCabal2nix "servant" (pkgs.fetchFromGitHub {
        owner = "haskell-servant";
        repo = "servant";
        rev = "main";
        sha256 = "...";
      }) {};
      
      # Local dependency
      mylib = hself.callCabal2nix "mylib" ../mylib {};
      
      # Disable tests for problematic packages
      some-package = pkgs.haskell.lib.dontCheck hsuper.some-package;
      
      # Jailbreak version bounds
      old-package = pkgs.haskell.lib.doJailbreak hsuper.old-package;
    };
  };
in
hpkgs.shellFor {
  packages = p: [ (p.callCabal2nix "myproject" ./. {}) ];
  # ... rest of shell configuration
}
```

### Building Executables
```nix
{ pkgs ? import <nixpkgs> {} }:
let
  hpkgs = pkgs.haskell.packages.ghc9121;
  myproject = hpkgs.callCabal2nix "myproject" ./. {};
in
{
  # The package itself
  inherit myproject;
  
  # Development shell
  shell = hpkgs.shellFor {
    packages = p: [ myproject ];
    buildInputs = with pkgs; [
      hpkgs.haskell-language-server
      ghcid
    ];
  };
  
  # Static binary (if possible)
  static = (hpkgs.extend (hself: hsuper: {
    myproject = pkgs.haskell.lib.justStaticExecutables 
                  (hsuper.callCabal2nix "myproject" ./. {});
  })).myproject;
}
```

## Advanced haskell.nix Setup

### Using IOHK's haskell.nix
```nix
{
  description = "Project using haskell.nix";
  
  inputs = {
    nixpkgs.follows = "haskellNix/nixpkgs-unstable";
    haskellNix.url = "github:input-output-hk/haskell.nix";
  };
  
  outputs = { self, nixpkgs, haskellNix }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        inherit (haskellNix) config;
        overlays = [ haskellNix.overlay ];
      };
      
      project = pkgs.haskell-nix.cabalProject' {
        src = ./.;
        compiler-nix-name = "ghc9121";
        
        # Package customization
        modules = [
          {
            packages.myproject = {
              doHaddock = false;  # Disable docs for faster builds
              configureFlags = [ "--disable-optimization" ];
            };
          }
        ];
      };
    in
    {
      packages.${system}.default = project.myproject.components.exes.myproject;
      
      devShells.${system}.default = project.shellFor {
        tools = {
          cabal = {};
          hlint = {};
          haskell-language-server = {};
        };
        
        buildInputs = with pkgs; [
          ghcid
          nixpkgs-fmt
        ];
      };
    };
}
```

## Adding System Dependencies

### C Libraries and Tools
```nix
{ pkgs ? import <nixpkgs> {} }:
let
  hpkgs = pkgs.haskell.packages.ghc9121;
in
hpkgs.shellFor {
  packages = p: [ (p.callCabal2nix "myproject" ./. {}) ];
  
  buildInputs = with pkgs; [
    # Haskell tools
    hpkgs.haskell-language-server
    ghcid
    
    # C libraries (for FFI)
    zlib.dev
    openssl.dev
    postgresql.lib
    
    # Development tools
    pkg-config  # For finding C libraries
    docker
    docker-compose
    
    # Database  
    postgresql
    redis
  ];
  
  # Set up environment for C libraries
  shellHook = ''
    export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig:${pkgs.zlib.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [pkgs.openssl pkgs.zlib]}"
  '';
}
```

### Database Setup
```nix
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    # Haskell environment
    (haskell.packages.ghc9121.ghcWithPackages (ps: with ps; [
      postgresql-simple
      persistent-postgresql
    ]))
    
    # Database
    postgresql
    
    # Development tools
    haskell-language-server
  ];
  
  shellHook = ''
    # Set up local PostgreSQL
    export PGDATA="$PWD/.pgdata"
    export PGHOST="$PWD/.pgdata"
    export PGPORT="5432"
    export PGDATABASE="myapp"
    
    if [ ! -d "$PGDATA" ]; then
      echo "Initializing PostgreSQL..."
      initdb --auth=trust
      echo "unix_socket_directories = '$PGDATA'" >> $PGDATA/postgresql.conf
      echo "listen_addresses = ''" >> $PGDATA/postgresql.conf
      echo "port = $PGPORT" >> $PGDATA/postgresql.conf
    fi
    
    pg_ctl start -l $PGDATA/postgres.log
    createdb "$PGDATABASE" 2>/dev/null || true
    
    # Clean up function
    cleanup() {
      pg_ctl stop
    }
    trap cleanup EXIT
  '';
}
```

## Cross-Compilation

### Building for Different Architectures
```nix
{
  description = "Cross-compilation example";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    haskell-flake.url = "github:srid/haskell-flake";
  };
  
  outputs = inputs@{ self, nixpkgs, haskell-flake, ... }:
    haskell-flake.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ];
      
      haskellProjects.default = {
        basePackages = nixpkgs.pkgsCross.aarch64-multiplatform.haskellPackages;
        packages.myproject.root = ./.;
      };
    };
}
```

### Static Binaries
```nix
{
  outputs = inputs@{ self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      
      # Static build configuration
      hpkgs = pkgs.pkgsStatic.haskell.packages.ghc9121.override {
        overrides = hself: hsuper: {
          # Disable shared libraries
          myproject = pkgs.haskell.lib.disableSharedExecutables 
                        (hsuper.callCabal2nix "myproject" ./. {});
        };
      };
    in
    {
      packages.${system}.default = hpkgs.myproject;
      
      # Docker image with static binary
      packages.${system}.docker = pkgs.dockerTools.buildImage {
        name = "myproject";
        contents = [ hpkgs.myproject ];
        config.Cmd = [ "/bin/myproject" ];
      };
    };
}
```

## IDE Integration

### VS Code with Nix
```json
// .vscode/settings.json
{
  "nix.enableLanguageServer": true,
  "nix.serverPath": "nil",
  
  "haskell.manageHLS": "PATH",
  "haskell.serverEnvironment": {
    "PATH": "${workspaceFolder}/.nix-shell-env/bin:${env:PATH}"
  }
}
```

```nix
# Generate .vscode/settings.json automatically
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    haskell-language-server
    nil  # Nix language server
  ];
  
  shellHook = ''
    mkdir -p .vscode .nix-shell-env/bin
    
    # Create symlinks for tools
    ln -sf $(which haskell-language-server) .nix-shell-env/bin/
    ln -sf $(which nil) .nix-shell-env/bin/
    
    # Generate VS Code settings
    cat > .vscode/settings.json << EOF
    {
      "nix.enableLanguageServer": true,
      "nix.serverPath": "nil",
      "haskell.manageHLS": "PATH"
    }
    EOF
  '';
}
```

### direnv Integration
```bash
# .envrc
use flake

# Or with impure evaluation for unfree packages
# use flake --impure
```

```nix
# .envrc for shell.nix
use nix
```

## Package Publishing with Nix

### Cachix for Binary Caches
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: cachix/install-nix-action@v18
      - uses: cachix/cachix-action@v12
        with:
          name: myproject
          authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
      
      - name: Build
        run: |
          nix build
          nix flake check
```

### Nix Package Repository
```nix
# Generate a package set
{
  description = "My Haskell packages";
  
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  
  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      hpkgs = pkgs.haskell.packages.ghc9121;
    in
    {
      packages.${system} = {
        mypackage1 = hpkgs.callCabal2nix "mypackage1" ./packages/mypackage1 {};
        mypackage2 = hpkgs.callCabal2nix "mypackage2" ./packages/mypackage2 {};
      };
      
      # Overlay for use in other projects  
      overlays.default = final: prev: {
        haskellPackages = prev.haskellPackages.override {
          overrides = hself: hsuper: {
            mypackage1 = self.packages.${system}.mypackage1;
            mypackage2 = self.packages.${system}.mypackage2;
          };
        };
      };
    };
}
```

## Troubleshooting

### Common Issues
```bash
# Missing C library errors
# Add to shell.nix buildInputs: pkgs.zlib.dev pkgs.openssl.dev

# Package conflicts
# Use overrides to pin specific versions

# Build failures with latest nixpkgs
# Pin to specific nixpkgs commit:
# nixpkgs.url = "github:NixOS/nixpkgs/a1b2c3d4..."

# GHC version mismatches
# Ensure all packages use same GHC:
# basePackages = nixpkgs.haskell.packages.ghc9121

# Out of memory during compilation
# Add to flake: settings.myproject = { enableSeparateDataOutput = true; };
```

### Debugging Builds
```bash
# Build with more verbose output
nix build --print-build-logs --show-trace

# Drop into build environment
nix develop .#default

# Check what's in the build
nix-store -q --tree $(nix build --print-out-paths)

# See why packages are being rebuilt
nix why-depends /nix/store/... /nix/store/...
```

This covers the modern approaches to Haskell development with Nix, emphasizing reproducibility and ease of development while avoiding traditional Haskell toolchain issues.
