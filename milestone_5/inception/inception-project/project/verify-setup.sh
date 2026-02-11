#!/bin/bash
# =============================================================================
# Inception Setup Verification Script
# =============================================================================
# Run this script to verify your setup before building
# Usage: ./verify-setup.sh [login]

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Get login from argument or environment
LOGIN=${1:-${USER}}
DOMAIN="${LOGIN}.42.fr"
DATA_PATH="/home/${LOGIN}/data"

echo "=============================================="
echo "  Inception Setup Verification"
echo "=============================================="
echo ""
echo "Using login: ${LOGIN}"
echo "Domain: ${DOMAIN}"
echo ""

ERRORS=0

# Check Docker installation
echo -n "Checking Docker... "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Installed${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check Docker Compose
echo -n "Checking Docker Compose... "
if docker compose version &> /dev/null; then
    echo -e "${GREEN}✓ Installed${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check Docker daemon
echo -n "Checking Docker daemon... "
if docker info &> /dev/null; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running or no permissions${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check /etc/hosts
echo -n "Checking /etc/hosts for ${DOMAIN}... "
if grep -q "${DOMAIN}" /etc/hosts; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${YELLOW}⚠ Not found - add with:${NC}"
    echo "    echo \"127.0.0.1 ${DOMAIN}\" | sudo tee -a /etc/hosts"
    ERRORS=$((ERRORS + 1))
fi

# Check data directories
echo -n "Checking data directory (wordpress)... "
if [ -d "${DATA_PATH}/wordpress" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${YELLOW}⚠ Not found - will be created by 'make'${NC}"
fi

echo -n "Checking data directory (mariadb)... "
if [ -d "${DATA_PATH}/mariadb" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${YELLOW}⚠ Not found - will be created by 'make'${NC}"
fi

# Check secrets directory
echo -n "Checking secrets directory... "
if [ -d "secrets" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check secret files
echo -n "Checking secrets/db_password.txt... "
if [ -f "secrets/db_password.txt" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo -n "Checking secrets/db_root_password.txt... "
if [ -f "secrets/db_root_password.txt" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo -n "Checking secrets/credentials.txt... "
if [ -f "secrets/credentials.txt" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check .env file
echo -n "Checking srcs/.env... "
if [ -f "srcs/.env" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
    
    # Check if login is still placeholder
    if grep -q "DOMAIN_NAME=login.42.fr" srcs/.env; then
        echo -e "${YELLOW}  ⚠ Warning: .env still has 'login' as placeholder${NC}"
        echo "    Update it with: sed -i \"s/login/${LOGIN}/g\" srcs/.env"
    fi
else
    echo -e "${RED}✗ Not found${NC}"
    echo "  Copy from template: cp srcs/.env.example srcs/.env"
    ERRORS=$((ERRORS + 1))
fi

# Check Dockerfiles exist
echo -n "Checking nginx Dockerfile... "
if [ -f "srcs/requirements/nginx/Dockerfile" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo -n "Checking wordpress Dockerfile... "
if [ -f "srcs/requirements/wordpress/Dockerfile" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo -n "Checking mariadb Dockerfile... "
if [ -f "srcs/requirements/mariadb/Dockerfile" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check docker-compose.yml
echo -n "Checking docker-compose.yml... "
if [ -f "srcs/docker-compose.yml" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check Makefile
echo -n "Checking Makefile... "
if [ -f "Makefile" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "=============================================="

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}All checks passed! Ready to build.${NC}"
    echo ""
    echo "Run 'make' to build and start the project."
else
    echo -e "${RED}Found ${ERRORS} issue(s). Please fix before building.${NC}"
fi

echo "=============================================="
exit $ERRORS
