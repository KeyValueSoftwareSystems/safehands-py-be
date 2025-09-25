#!/bin/bash

# SafeHands Senior AI Assistant Backend Startup Script
# Professional production-ready startup script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_warning "Running as root is not recommended for production"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [ "$(printf '%s\n' "3.11" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.11" ]; then
        log_error "Python 3.11+ is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    log_success "Python $PYTHON_VERSION detected"
    
    # Check Redis
    if ! command -v redis-cli &> /dev/null; then
        log_error "Redis CLI is not installed"
        exit 1
    fi
    
    if ! redis-cli ping > /dev/null 2>&1; then
        log_error "Redis is not running. Please start Redis first:"
        echo "  sudo systemctl start redis"
        echo "  or"
        echo "  redis-server"
        exit 1
    fi
    log_success "Redis is running"
    
    # Check PostgreSQL (optional)
    if command -v pg_isready &> /dev/null; then
        if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
            log_warning "PostgreSQL is not running. Some features may not work"
        else
            log_success "PostgreSQL is running"
        fi
    else
        log_warning "PostgreSQL not found. Some features may not work"
    fi
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        log_info "Creating .env file from template..."
        cp env.example .env
        log_warning "Please edit .env file with your configuration before running again"
        log_info "Required: OPENAI_API_KEY and ANTHROPIC_API_KEY"
        exit 1
    fi
    
    # Create uploads directory
    mkdir -p uploads
    log_success "Environment setup complete"
}

# Setup virtual environment
setup_venv() {
    log_info "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    log_info "Activating virtual environment..."
    source venv/bin/activate
    
    log_info "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_success "Virtual environment setup complete"
}

# Validate configuration
validate_config() {
    log_info "Validating configuration..."
    
    # Check for required API keys
    if ! grep -q "OPENAI_API_KEY=sk-" .env; then
        log_error "OPENAI_API_KEY not configured in .env"
        log_error "Please set your OpenAI API key in the .env file"
        exit 1
    fi
    
    # Check for production settings
    if grep -q "DEBUG=true" .env; then
        log_warning "Debug mode is enabled. Not recommended for production"
    fi
    
    if grep -q "SECRET_KEY=your-secret-key-change-in-production" .env; then
        log_warning "Default secret key detected. Please change it for production"
    fi
    
    log_success "Configuration validation complete"
}

# Start the application
start_application() {
    log_info "Starting SafeHands Senior AI Assistant Backend..."
    
    # Set environment variables
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    
    # Start with appropriate settings
    if grep -q "ENVIRONMENT=production" .env; then
        log_info "Starting in production mode..."
        python run.py
    else
        log_info "Starting in development mode..."
        python run.py
    fi
}

# Main execution
main() {
    echo "🚀 SafeHands Senior AI Assistant Backend"
    echo "========================================"
    
    check_root
    check_requirements
    setup_environment
    setup_venv
    validate_config
    start_application
}

# Handle script interruption
trap 'log_error "Startup interrupted"; exit 1' INT TERM

# Run main function
main "$@"
