#!/bin/bash
# A simple script to set up, build and run the chezmoi project environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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

# Check if uv is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "uv is not installed"
        print_info "Install from: https://docs.astral.sh/uv/"
        exit 1
    fi
    print_success "uv is installed"
}

# Check if chezmoi is installed
check_chezmoi() {
    if ! command -v chezmoi &> /dev/null; then
        print_warning "chezmoi is not installed"
        print_info "The app will run but some features won't work"
        print_info "Install from: https://www.chezmoi.io/install/"
    else
        local version=$(chezmoi --version | head -n1)
        print_success "chezmoi is installed: $version"
    fi
}

# Setup function
setup() {
    print_info "Setting up development environment..."

    check_uv
    check_chezmoi

    print_info "Syncing dependencies..."
    uv sync

    print_success "Setup complete!"
    print_info "Virtual environment is at: .venv"
}

# Build function (for future use - currently just checks code)
build() {
    print_info "Building project..."

    check_uv

    print_info "Running linter..."
    uv run ruff check .

    print_info "Formatting code..."
    uv run ruff format --check .

    print_success "Build complete - code quality checks passed!"
}

# Run function
run() {
    print_info "Running Chezmoi Manager..."

    check_uv

    uv run python main.py
}

# Clean function
clean() {
    print_info "Cleaning build artifacts..."

    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

    print_success "Cleaned up cache files"
}

# Lint and fix function
lint() {
    print_info "Running linter with auto-fix..."

    check_uv

    print_info "Checking and fixing issues..."
    uv run ruff check --fix .

    print_info "Formatting code..."
    uv run ruff format .

    print_success "Linting and formatting complete!"
}

# Show help
show_help() {
    cat << EOF
Chezmoi Manager - Project Management Script

Usage: ./project.sh [COMMAND]

Commands:
    setup       Set up the development environment and install dependencies
    build       Run code quality checks (linting and formatting)
    run         Run the Chezmoi Manager application
    clean       Remove build artifacts and cache files
    lint        Run linter with auto-fix and format code
    help        Show this help message

Examples:
    ./project.sh setup          # First-time setup
    ./project.sh run            # Run the app
    ./project.sh lint           # Fix code style issues
    ./project.sh clean          # Clean cache files

EOF
}

# Main script logic
main() {
    case "${1:-help}" in
        setup|--setup|-s)
            setup
            ;;
        build|--build|-b)
            build
            ;;
        run|--run|-r)
            run
            ;;
        clean|--clean|-c)
            clean
            ;;
        lint|--lint|-l)
            lint
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
