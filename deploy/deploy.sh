#!/bin/bash
# =============================================================================
# Marketing Multi-Agent System - Deployment Script
# Usage: ./deploy.sh
# =============================================================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Config
PROJECT_DIR="/opt/marketing-multi-agent"
REQUIRED_PORTS=(8501)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║     🚀 Marketing Multi-Agent System - Deploy            ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info()  { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_step()  { echo -e "\n${BLUE}[→]${NC} $1"; }

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
check_docker() {
    log_step "Step 1/6: Checking Docker environment..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        echo "  CentOS 7: yum install -y docker"
        echo "  CentOS 8: dnf install -y docker"
        exit 1
    fi
    log_info "Docker version: $(docker --version)"

    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose plugin is not installed."
        echo "  Install: yum install -y docker-compose-plugin"
        exit 1
    fi
    log_info "Docker Compose version: $(docker compose version)"

    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running."
        echo "  Start it: systemctl start docker"
        exit 1
    fi
    log_info "Docker daemon is running"
}

check_env() {
    log_step "Step 2/6: Checking environment configuration..."

    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            log_warn ".env file not found. Creating from .env.example..."
            cp .env.example .env
            log_warn "Please edit .env and fill in your API keys, then re-run this script."
            echo ""
            echo "  Required keys:"
            echo "    ZHIPU_API_KEY    - Get from https://open.bigmodel.cn/"
            echo "    DASHSCOPE_API_KEY - Get from https://dashscope.aliyuncs.com/"
            echo "    BOCHA_API_KEY    - Get from https://open.bochaai.com/"
            exit 1
        else
            log_error ".env.example not found. Cannot continue."
            exit 1
        fi
    fi

    # Check if API keys are set (not default placeholders)
    UNCONFIGURED_KEYS=()
    for key in ZHIPU_API_KEY DASHSCOPE_API_KEY BOCHA_API_KEY; do
        value=$(grep "^${key}=" .env | cut -d'=' -f2)
        if [ -z "$value" ] || [[ "$value" == *"your_"* ]] || [[ "$value" == *"here"* ]]; then
            UNCONFIGURED_KEYS+=("$key")
        fi
    done

    if [ ${#UNCONFIGURED_KEYS[@]} -gt 0 ]; then
        log_error "The following API keys are not configured in .env:"
        for key in "${UNCONFIGURED_KEYS[@]}"; do
            echo "    - $key"
        done
        echo ""
        log_warn "Please edit .env and fill in valid API keys, then re-run this script."
        exit 1
    fi
    log_info "All API keys are configured"
}

check_port() {
    log_step "Step 3/6: Checking port availability..."

    for port in "${REQUIRED_PORTS[@]}"; do
        if ss -tlnp | grep -q ":${port} "; then
            log_warn "Port ${port} is already in use. The service may fail to bind."
        else
            log_info "Port ${port} is available"
        fi
    done
}

configure_firewall() {
    log_step "Step 4/6: Configuring firewall..."

    # Check firewalld
    if systemctl is-active --quiet firewalld 2>/dev/null; then
        for port in "${REQUIRED_PORTS[@]}"; do
            if ! firewall-cmd --zone=public --list-ports 2>/dev/null | grep -q "${port}/tcp"; then
                log_warn "Opening port ${port} in firewalld..."
                sudo firewall-cmd --zone=public --add-port=${port}/tcp --permanent
                sudo firewall-cmd --reload
                log_info "Port ${port} opened in firewalld"
            else
                log_info "Port ${port} already open in firewalld"
            fi
        done
    else
        log_info "firewalld is not active, skipping firewall configuration"
        echo "  ⚠  Make sure to open port 8501 in Alibaba Cloud Security Group!"
    fi

    # Check SELinux
    if command -v getenforce &> /dev/null; then
        if [ "$(getenforce)" = "Enforcing" ]; then
            log_warn "SELinux is Enforcing. This may block container networking."
            echo "  To temporarily disable: sudo setenforce 0"
            echo "  To permanently disable: sudo sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config"
        else
            log_info "SELinux is not blocking (status: $(getenforce))"
        fi
    fi
}

build_and_start() {
    log_step "Step 5/6: Building and starting containers..."

    # Build the image
    echo "Building Docker image..."
    docker compose build --no-cache

    # Stop existing containers if running
    docker compose down 2>/dev/null || true

    # Start services
    echo "Starting services..."
    docker compose up -d

    # Wait for healthy
    echo "Waiting for service to be ready..."
    for i in $(seq 1 15); do
        if curl -s http://localhost:8501/_stcore/health &> /dev/null; then
            log_info "Service is healthy!"
            break
        fi
        sleep 2
    done

    log_info "Containers started successfully"
    docker compose ps
}

print_success() {
    log_step "Step 6/6: Deployment complete!"

    # Try to detect public IP
    PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ip.sb 2>/dev/null || echo "YOUR_SERVER_IP")

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✅  Deployment Successful!                      ║${NC}"
    echo -e "${GREEN}╠══════════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}║  🌐 Access URL:  http://${PUBLIC_IP}:8501          ║${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}║  📋 Useful commands:                                     ║${NC}"
    echo -e "${GREEN}║     docker compose logs -f    # View logs                ║${NC}"
    echo -e "${GREEN}║     docker compose ps         # Check status             ║${NC}"
    echo -e "${GREEN}║     docker compose restart    # Restart services         ║${NC}"
    echo -e "${GREEN}║     docker compose down       # Stop services            ║${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Remind about security group
    echo -e "${YELLOW}⚠  Don't forget to open port 8501 in Alibaba Cloud Security Group!${NC}"
    echo -e "${YELLOW}   ECS Console → Security Groups → Add Rule → TCP 8501${NC}"
    echo ""

    # Suggest systemd setup
    echo -e "${BLUE}💡 To enable auto-start on boot, run:${NC}"
    echo -e "   ${BLUE}sudo cp deploy/marketing.service /etc/systemd/system/${NC}"
    echo -e "   ${BLUE}sudo systemctl enable --now marketing.service${NC}"
    echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    print_banner

    # Ensure we're in the project directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    cd "$PROJECT_DIR"

    check_docker
    check_env
    check_port
    configure_firewall
    build_and_start
    print_success
}

main "$@"
