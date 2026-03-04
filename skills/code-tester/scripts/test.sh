#!/bin/bash
# Code Tester Script
# Supports: Rust, Go, Java
# Usage: test.sh <directory>

set -e

DIR="$1"
if [ -z "$DIR" ]; then
    echo "Error: Directory not provided"
    echo "Usage: test.sh <directory>"
    exit 1
fi

cd "$DIR"

# Detect project type
PROJECT_TYPE="unknown"

if [ -f "Cargo.toml" ] && [ -d "src" ]; then
    PROJECT_TYPE="rust"
elif [ -f "go.mod" ] || [ -f "go.sum" ] || [ -f "main.go" ]; then
    PROJECT_TYPE="go"
elif [ -f "pom.xml" ] || [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    PROJECT_TYPE="java"
fi

echo "Detected project type: $PROJECT_TYPE"

if [ "$PROJECT_TYPE" = "unknown" ]; then
    echo "Error: Could not detect supported project type"
    echo "Supported types: Rust (Cargo.toml), Go (go.mod, main.go), Java (pom.xml, build.gradle)"
    exit 1
fi

# Run tests based on project type
case "$PROJECT_TYPE" in
    rust)
        echo "--- Rust Project ---"
        echo "Running: cargo test"

        # Check if tests exist
        if grep -r "#\[test\]" src/ 2>/dev/null > /dev/null; then
            cargo test 2>&1 | tee /tmp/code-tester-tests.log
            TEST_RESULT=${PIPESTATUS[0]}
            echo "Test result: $TEST_RESULT"
        else
            echo "No tests found, skipping tests"
            TEST_RESULT=0
        fi

        # Try to build and run
        echo ""
        echo "Running: cargo build"
        cargo build 2>&1 | tee /tmp/code-tester-build.log
        BUILD_RESULT=${PIPESTATUS[0]}

        echo ""
        echo "Build result: $BUILD_RESULT"
        ;;
    go)
        echo "--- Go Project ---"

        # Check if tests exist
        if find . -name "*_test.go" -type f | grep -q .; then
            echo "Running: go test ./..."
            go test ./... 2>&1 | tee /tmp/code-tester-tests.log
            TEST_RESULT=${PIPESTATUS[0]}
            echo "Test result: $TEST_RESULT"
        else
            echo "No tests found, skipping tests"
            TEST_RESULT=0
        fi

        echo ""
        echo "Running: go build"
        go build 2>&1 | tee /tmp/code-tester-build.log
        BUILD_RESULT=${PIPESTATUS[0]}

        echo ""
        echo "Build result: $BUILD_RESULT"
        ;;
    java)
        echo "--- Java Project ---"

        if [ -f "pom.xml" ]; then
            echo "Detected: Maven project"

            # Check if tests exist
            if [ -d "src/test" ] && [ "$(find src/test -name "*.java" 2>/dev/null | wc -l)" -gt 0 ]; then
                echo "Running: mvn test"
                mvn test 2>&1 | tee /tmp/code-tester-tests.log
                TEST_RESULT=${PIPESTATUS[0]}
                echo "Test result: $TEST_RESULT"
            else
                echo "No tests found, skipping tests"
                TEST_RESULT=0
            fi

            echo ""
            echo "Running: mvn compile"
            mvn compile 2>&1 | tee /tmp/code-tester-build.log
            BUILD_RESULT=${PIPESTATUS[0]}
        elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
            echo "Detected: Gradle project"

            # Check if tests exist
            if [ -d "src/test" ] && [ "$(find src/test -name "*.java" 2>/dev/null | wc -l)" -gt 0 ]; then
                echo "Running: ./gradlew test"
                ./gradlew test 2>&1 | tee /tmp/code-tester-tests.log
                TEST_RESULT=${PIPESTATUS[0]}
                echo "Test result: $TEST_RESULT"
            else
                echo "No tests found, skipping tests"
                TEST_RESULT=0
            fi

            echo ""
            echo "Running: ./gradlew build -x test"
            ./gradlew build -x test 2>&1 | tee /tmp/code-tester-build.log
            BUILD_RESULT=${PIPESTATUS[0]}
        fi

        echo ""
        echo "Build result: $BUILD_RESULT"
        ;;
esac

# Overall result
echo ""
echo "=== SUMMARY ==="
echo "Project type: $PROJECT_TYPE"
echo "Tests: $TEST_RESULT"
echo "Build: $BUILD_RESULT"

if [ "$TEST_RESULT" -eq 0 ] && [ "$BUILD_RESULT" -eq 0 ]; then
    echo "✓ All checks passed"
    exit 0
else
    echo "✗ Some checks failed"
    exit 1
fi
