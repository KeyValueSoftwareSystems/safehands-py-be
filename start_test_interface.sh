#!/bin/bash

# SafeHands Test Interface Startup Script
# This script starts the web-based test interface for the SafeHands AI Assistant

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    print_step "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_status "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name is not responding after $max_attempts attempts"
    return 1
}

# Main startup function
main() {
    print_header "🤖 SafeHands Senior AI Assistant - Test Interface Startup"
    echo "=================================================================="
    
    # Check if we're in the right directory
    if [ ! -f "web_interface/index.html" ]; then
        print_error "Test interface files not found. Please run this script from the project root directory."
        exit 1
    fi
    
    # Check Python installation
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_step "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f "venv/pyvenv.cfg" ] || ! pip show fastapi >/dev/null 2>&1; then
        print_step "Installing dependencies..."
        pip install fastapi uvicorn python-multipart
    fi
    
    # Check if backend is running
    print_step "Checking if SafeHands backend is running..."
    if port_in_use 8000; then
        print_status "Backend appears to be running on port 8000"
        
        # Test backend health
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_status "Backend is healthy and responding"
        else
            print_warning "Backend is running but not responding to health checks"
        fi
    else
        print_warning "Backend is not running on port 8000"
        print_warning "Please start the backend first with: ./start.sh"
        print_warning "Or run: python run.py"
        echo ""
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Exiting. Please start the backend first."
            exit 1
        fi
    fi
    
    # Check if test interface port is available
    if port_in_use 3000; then
        print_error "Port 3000 is already in use. Please stop the service using port 3000 or modify the script."
        exit 1
    fi
    
    # Start the test interface
    print_step "Starting SafeHands Test Interface..."
    echo ""
    print_header "🚀 Test Interface Starting..."
    print_status "Interface will be available at: http://localhost:3000"
    print_status "Backend should be running at: http://localhost:8000"
    print_status "WebSocket endpoint: ws://localhost:8000/ws"
    echo ""
    print_header "📱 Test Interface Features:"
    echo "  • Real-time chat with AI assistant"
    echo "  • Voice message simulation"
    echo "  • Screen upload and analysis"
    echo "  • Step-by-step guidance display"
    echo "  • Error detection and recovery"
    echo "  • Context-aware assistance"
    echo ""
    print_header "🎯 Quick Test Scenarios:"
    echo "  1. Try: 'I want to order food'"
    echo "  2. Try: 'Send a message to my daughter'"
    echo "  3. Try: 'Pay my electricity bill'"
    echo "  4. Upload a screenshot of any app"
    echo "  5. Try: 'Help me with my phone'"
    echo ""
    print_header "⚡ Performance Testing:"
    echo "  • Monitor response times"
    echo "  • Test WebSocket connection stability"
    echo "  • Verify AI response quality"
    echo "  • Check error handling"
    echo ""
    print_warning "Press Ctrl+C to stop the test interface"
    echo "=================================================================="
    
    # Change to web_interface directory and start server
    cd web_interface
    python server.py
}

# Handle script interruption
trap 'echo -e "\n${YELLOW}[INFO]${NC} Test interface stopped by user"; exit 0' INT

# Run main function
main "$@"
