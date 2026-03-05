#!/bin/bash
# Comprehensive Newman test runner with security best practices
# Usage: ./run-tests.sh <collection> <environment> [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
COLLECTION=""
ENVIRONMENT=""
REPORTERS="cli,htmlextra"
OUTPUT_DIR="./test-results"
BAIL=false
VERBOSE=false
ITERATIONS=1
TIMEOUT=30000

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Usage function
usage() {
    cat << EOF
Usage: $0 <collection> <environment> [options]

Arguments:
  collection              Path to Postman collection JSON file
  environment             Path to environment JSON file

Options:
  -o, --output DIR        Output directory for reports (default: ./test-results)
  -r, --reporters LIST    Comma-separated reporters (default: cli,htmlextra)
  -b, --bail              Stop on first test failure
  -v, --verbose           Verbose output
  -n, --iterations NUM    Number of iterations (default: 1)
  -t, --timeout MS        Request timeout in milliseconds (default: 30000)
  -h, --help              Show this help message

Examples:
  $0 api-tests.json staging.json
  $0 api-tests.json staging.json --bail --verbose
  $0 api-tests.json prod.json -o ./reports -r cli,json,junit

Environment Variables:
  API_KEY                 API authentication key
  DB_PASSWORD             Database password
  ENCRYPTION_KEY          Encryption key for secure variables
  
EOF
    exit 1
}

# Parse arguments
if [ $# -lt 2 ]; then
    usage
fi

COLLECTION="$1"
ENVIRONMENT="$2"
shift 2

while [ $# -gt 0 ]; do
    case "$1" in
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -r|--reporters)
            REPORTERS="$2"
            shift 2
            ;;
        -b|--bail)
            BAIL=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -n|--iterations)
            ITERATIONS="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validation
if [ ! -f "$COLLECTION" ]; then
    print_error "Collection file not found: $COLLECTION"
    exit 1
fi

if [ ! -f "$ENVIRONMENT" ]; then
    print_error "Environment file not found: $ENVIRONMENT"
    exit 1
fi

# Check if Newman is installed
if ! command -v newman &> /dev/null; then
    print_error "Newman is not installed!"
    echo "Install with: npm install -g newman"
    exit 1
fi

# Security checks
print_info "Running security checks..."

# Check for hardcoded secrets in collection
if grep -qiE '(password|secret|apikey|token).*:.*["\047][a-zA-Z0-9]{8,}' "$COLLECTION"; then
    print_warning "Possible hardcoded secrets detected in collection!"
    print_warning "Please use environment variables instead."
fi

# Check for required environment variables
REQUIRED_VARS=()
if grep -q "{{API_KEY}}" "$COLLECTION" 2>/dev/null; then
    REQUIRED_VARS+=("API_KEY")
fi
if grep -q "{{DB_PASSWORD}}" "$COLLECTION" 2>/dev/null; then
    REQUIRED_VARS+=("DB_PASSWORD")
fi

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        print_warning "Environment variable $var is not set!"
        print_warning "Tests may fail if this variable is required."
    fi
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Build Newman command
NEWMAN_CMD="newman run \"$COLLECTION\" -e \"$ENVIRONMENT\""

if [ "$BAIL" = true ]; then
    NEWMAN_CMD="$NEWMAN_CMD --bail"
fi

if [ "$VERBOSE" = true ]; then
    NEWMAN_CMD="$NEWMAN_CMD --verbose"
fi

NEWMAN_CMD="$NEWMAN_CMD -n $ITERATIONS"
NEWMAN_CMD="$NEWMAN_CMD --timeout-request $TIMEOUT"
NEWMAN_CMD="$NEWMAN_CMD --reporters $REPORTERS"

# Add reporter outputs
if [[ "$REPORTERS" == *"html"* ]]; then
    NEWMAN_CMD="$NEWMAN_CMD --reporter-htmlextra-export \"$OUTPUT_DIR/newman-report.html\""
fi

if [[ "$REPORTERS" == *"json"* ]]; then
    NEWMAN_CMD="$NEWMAN_CMD --reporter-json-export \"$OUTPUT_DIR/newman-report.json\""
fi

if [[ "$REPORTERS" == *"junit"* ]]; then
    NEWMAN_CMD="$NEWMAN_CMD --reporter-junit-export \"$OUTPUT_DIR/newman-junit.xml\""
fi

# Color output
NEWMAN_CMD="$NEWMAN_CMD --color on"

# Print configuration
print_info "Configuration:"
echo "  Collection:   $COLLECTION"
echo "  Environment:  $ENVIRONMENT"
echo "  Output Dir:   $OUTPUT_DIR"
echo "  Reporters:    $REPORTERS"
echo "  Bail:         $BAIL"
echo "  Verbose:      $VERBOSE"
echo "  Iterations:   $ITERATIONS"
echo "  Timeout:      ${TIMEOUT}ms"
echo ""

# Run Newman
print_info "Running tests..."
echo ""

eval $NEWMAN_CMD
EXIT_CODE=$?

echo ""

# Report results
if [ $EXIT_CODE -eq 0 ]; then
    print_success "All tests passed! ✓"
else
    print_error "Tests failed with exit code: $EXIT_CODE"
fi

# Show report locations
if [ -f "$OUTPUT_DIR/newman-report.html" ]; then
    print_info "HTML report: $OUTPUT_DIR/newman-report.html"
fi

if [ -f "$OUTPUT_DIR/newman-report.json" ]; then
    print_info "JSON report: $OUTPUT_DIR/newman-report.json"
fi

if [ -f "$OUTPUT_DIR/newman-junit.xml" ]; then
    print_info "JUnit report: $OUTPUT_DIR/newman-junit.xml"
fi

exit $EXIT_CODE
