---
name: rose-container-tools
version: 0.1.0
description: Build and run ROSE compiler tools using ROSE installed in a Docker container. Use when developing source-to-source translators, call graph analyzers, AST processors, or any tool that links against librose.so. Triggers on "ROSE tool", "callgraph", "AST traversal", "source-to-source", "build with ROSE", "librose".
---

# ROSE Container Tools

Build and run ROSE-based source code analysis tools using ROSE installed in a container.

## ⚠️ ALWAYS Use Makefile

**Never use ad-hoc scripts or command-line compilation for ROSE tools.**

- Use `Makefile` for all builds
- Enables `make -j` parallelism
- Ensures consistent flags
- Supports `make check` for testing

## Why Container?

ROSE requires GCC 7-10 and specific Boost versions. Most modern hosts don't have these. The container provides:
- Pre-installed ROSE at `/rose/install`
- Correct compiler toolchain
- All dependencies configured

## Quick Start

### 1. Start the Container

```bash
# If container exists
docker start rose-tools-dev
docker exec -it rose-tools-dev bash

# Or create new container
docker run -it --name rose-tools-dev \
  -v /home/liao/rose-install:/rose/install:ro \
  -v $(pwd):/work \
  -w /work \
  rose-dev:latest bash
```

### 2. Build with Makefile

**Always use Makefile to build ROSE tools. Never use ad-hoc scripts.**

```bash
# Inside container
make        # Build all tools
make check  # Build and test
```

### 3. Run the Tool

```bash
./build/my_tool -c input.c
```

## Makefile (Required)

Create `Makefile` for your tool:

```makefile
ROSE_INSTALL = /rose/install

CXX      = g++
CXXFLAGS = -std=c++14 -Wall -g -I$(ROSE_INSTALL)/include/rose
LDFLAGS  = -L$(ROSE_INSTALL)/lib -Wl,-rpath,$(ROSE_INSTALL)/lib
LIBS     = -lrose

BUILDDIR = build
SOURCES  = $(wildcard tools/*.cpp)
TOOLS    = $(patsubst tools/%.cpp,$(BUILDDIR)/%,$(SOURCES))

.PHONY: all clean check

all: $(TOOLS)

$(BUILDDIR)/%: tools/%.cpp
	@mkdir -p $(BUILDDIR)
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS) $(LIBS)

check: all
	@for tool in $(TOOLS); do \
		echo "Testing $$tool..."; \
		LD_LIBRARY_PATH=$(ROSE_INSTALL)/lib $$tool -c tests/hello.c; \
	done

clean:
	rm -rf $(BUILDDIR)
```

## Example: Identity Translator

Minimal ROSE tool that parses and unparses code:

```cpp
// tools/identity.cpp
#include "rose.h"

int main(int argc, char* argv[]) {
    SgProject* project = frontend(argc, argv);
    if (!project) return 1;
    
    AstTests::runAllTests(project);
    return backend(project);
}
```

Build and run:
```bash
make
./build/identity -c tests/hello.c
# Output: rose_hello.c (unparsed)
```

## Example: Call Graph Generator

```cpp
// tools/callgraph.cpp
#include "rose.h"
#include <CallGraph.h>

int main(int argc, char* argv[]) {
    ROSE_INITIALIZE;
    SgProject* project = new SgProject(argc, argv);
    
    CallGraphBuilder builder(project);
    builder.buildCallGraph();
    
    AstDOTGeneration dotgen;
    dotgen.writeIncidenceGraphToDOTFile(
        builder.getGraph(), "callgraph.dot");
    
    return 0;
}
```

## Example: AST Node Counter

```cpp
// tools/ast_stats.cpp
#include "rose.h"
#include <map>

class NodeCounter : public AstSimpleProcessing {
public:
    std::map<std::string, int> counts;
    
    void visit(SgNode* node) override {
        if (node) counts[node->class_name()]++;
    }
};

int main(int argc, char* argv[]) {
    SgProject* project = frontend(argc, argv);
    
    NodeCounter counter;
    counter.traverseInputFiles(project, preorder);
    
    for (auto& [name, count] : counter.counts)
        std::cout << name << ": " << count << "\n";
    
    return 0;
}
```

## Common ROSE Headers

| Header | Purpose |
|--------|---------|
| `rose.h` | Main header (includes most things) |
| `CallGraph.h` | Call graph construction |
| `AstDOTGeneration.h` | DOT output for AST/graphs |
| `sageInterface.h` | AST manipulation utilities |

## AST Traversal Patterns

### Simple Traversal (preorder/postorder)
```cpp
class MyTraversal : public AstSimpleProcessing {
    void visit(SgNode* node) override {
        // Process each node
    }
};

MyTraversal t;
t.traverseInputFiles(project, preorder);
```

### Top-Down with Inherited Attributes
```cpp
class MyTraversal : public AstTopDownProcessing<int> {
    int evaluateInheritedAttribute(SgNode* node, int depth) override {
        return depth + 1;  // Pass to children
    }
};
```

### Bottom-Up with Synthesized Attributes
```cpp
class MyTraversal : public AstBottomUpProcessing<int> {
    int evaluateSynthesizedAttribute(SgNode* node, 
        SynthesizedAttributesList childAttrs) override {
        int sum = 0;
        for (auto& attr : childAttrs) sum += attr;
        return sum + 1;  // Return to parent
    }
};
```

## Testing in Container

```bash
# Run from host
docker exec -w /work rose-tools-dev make check

# Or interactively
docker exec -it rose-tools-dev bash
cd /work
make && make check
```

## Troubleshooting

### "rose.h not found"
```bash
# Check include path
echo $ROSE/include/rose
ls $ROSE/include/rose/rose.h
```

### "cannot find -lrose"
```bash
# Check library path
ls $ROSE/lib/librose.so
```

### Runtime: "librose.so not found"
```bash
# Set library path
export LD_LIBRARY_PATH=$ROSE/lib:$LD_LIBRARY_PATH
```

### Segfault on large files
```bash
# Increase stack size
ulimit -s unlimited
```

## Container Reference

| Path | Contents |
|------|----------|
| `/rose/install` | ROSE installation (headers, libs, bins) |
| `/rose/install/include/rose` | Header files |
| `/rose/install/lib` | librose.so and dependencies |
| `/rose/install/bin` | ROSE tools (identityTranslator, etc.) |
| `/work` | Mounted workspace (your code) |
