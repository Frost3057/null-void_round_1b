#!/bin/bash

# Adobe Hackathon Docker Build Script
# Provides optimized build options for different use cases

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Adobe Hackathon Docker Build Script${NC}"
echo "=========================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Parse command line arguments
BUILD_TYPE=${1:-"dev"}
CACHE=${2:-"--no-cache"}

case $BUILD_TYPE in
    "dev"|"development")
        echo -e "${BLUE}Building development image (fast, minimal dependencies)...${NC}"
        docker build $CACHE -f dockerfile.dev -t adobe-hackathon:dev .
        print_status "Development image built successfully!"
        echo -e "${YELLOW}Run with: docker run -v \$(pwd)/output_1A:/app/output_1A adobe-hackathon:dev${NC}"
        ;;
        
    "prod"|"production")
        echo -e "${BLUE}Building production image (full functionality)...${NC}"
        docker build $CACHE -f dockerfile -t adobe-hackathon:prod .
        print_status "Production image built successfully!"
        echo -e "${YELLOW}Run with: docker run -v \$(pwd)/input_1A:/app/input_1A -v \$(pwd)/output_1A:/app/output_1A adobe-hackathon:prod${NC}"
        ;;
        
    "both")
        echo -e "${BLUE}Building both development and production images...${NC}"
        docker build $CACHE -f dockerfile.dev -t adobe-hackathon:dev .
        print_status "Development image built!"
        docker build $CACHE -f dockerfile -t adobe-hackathon:prod .
        print_status "Production image built!"
        ;;
        
    "compose")
        echo -e "${BLUE}Building with docker-compose...${NC}"
        docker-compose build $CACHE
        print_status "All services built with docker-compose!"
        echo -e "${YELLOW}Run with: docker-compose up [service-name]${NC}"
        ;;
        
    "clean")
        echo -e "${BLUE}Cleaning up Docker images and cache...${NC}"
        docker system prune -f
        docker image prune -f
        print_status "Docker cleanup completed!"
        ;;
        
    *)
        print_error "Unknown build type: $BUILD_TYPE"
        echo "Usage: $0 [dev|prod|both|compose|clean] [--no-cache|--cache]"
        echo ""
        echo "Build types:"
        echo "  dev        - Fast development build (minimal dependencies)"
        echo "  prod       - Full production build (all features)"
        echo "  both       - Build both dev and prod images"
        echo "  compose    - Build using docker-compose"
        echo "  clean      - Clean up Docker cache and unused images"
        echo ""
        echo "Cache options:"
        echo "  --no-cache - Force rebuild (default)"
        echo "  --cache    - Use cached layers"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Build completed successfully!${NC}"
echo ""
echo "Available commands:"
echo "  🔍 Test validation:    docker run --rm -v \$(pwd)/output_1A:/app/output_1A adobe-hackathon:dev"
echo "  🚀 Run full pipeline:  docker run --rm -v \$(pwd)/input_1A:/app/input_1A -v \$(pwd)/output_1A:/app/output_1A adobe-hackathon:prod"
echo "  📊 Run with compose:   docker-compose up validation"
