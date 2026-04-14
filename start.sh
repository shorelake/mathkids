#!/bin/bash
# MathKids - One-click startup script
# Usage: ./start.sh [backend|student|admin|all]

set -e
cd "$(dirname "$0")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Load .env if present and export all vars to child processes
if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

# Resolve defaults for every configurable value
BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-18000}"
STUDENT_PORT="${STUDENT_PORT:-3000}"
ADMIN_PORT="${ADMIN_PORT:-3001}"
BACKEND_PUBLIC_URL="${BACKEND_PUBLIC_URL:-http://localhost:${BACKEND_PORT}}"
STUDENT_PUBLIC_URL="${STUDENT_PUBLIC_URL:-http://localhost:${STUDENT_PORT}}"
ADMIN_PUBLIC_URL="${ADMIN_PUBLIC_URL:-http://localhost:${ADMIN_PORT}}"

start_backend() {
    echo -e "${BLUE}Starting Backend (FastAPI) on ${BACKEND_HOST}:${BACKEND_PORT}...${NC}"
    cd backend
    if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/anaconda3/etc/profile.d/conda.sh"
    else
        echo "conda.sh not found — check your conda installation path"
        exit 1
    fi
    conda activate mathkids
    pip install -q -r requirements.txt --break-system-packages 2>/dev/null || pip install -q -r requirements.txt
    python -m uvicorn main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" --reload &
    BACKEND_PID=$!
    echo -e "${GREEN}Backend started (PID: $BACKEND_PID)${NC}"
    cd ..
}

start_student() {
    echo -e "${BLUE}Starting Student App on port ${STUDENT_PORT}...${NC}"
    cd student-app
    npm install --silent 2>/dev/null
    npm run dev &
    STUDENT_PID=$!
    echo -e "${GREEN}Student App started (PID: $STUDENT_PID)${NC}"
    cd ..
}

start_admin() {
    echo -e "${BLUE}Starting Admin App on port ${ADMIN_PORT}...${NC}"
    cd admin-app
    npm install --silent 2>/dev/null
    npm run dev &
    ADMIN_PID=$!
    echo -e "${GREEN}Admin App started (PID: $ADMIN_PID)${NC}"
    cd ..
}

case "${1:-all}" in
    backend)
        start_backend
        ;;
    student)
        start_student
        ;;
    admin)
        start_admin
        ;;
    all)
        start_backend
        sleep 2
        start_student
        start_admin
        echo ""
        echo -e "${GREEN}============================================${NC}"
        echo -e "${GREEN}  MathKids is running${NC}"
        echo -e "${GREEN}============================================${NC}"
        echo -e "  ${YELLOW}Backend API:${NC}  ${BACKEND_PUBLIC_URL}"
        echo -e "  ${YELLOW}API docs:${NC}     ${BACKEND_PUBLIC_URL}/docs"
        echo -e "  ${YELLOW}Student app:${NC}  ${STUDENT_PUBLIC_URL}"
        echo -e "  ${YELLOW}Admin app:${NC}    ${ADMIN_PUBLIC_URL}"
        echo -e "${GREEN}============================================${NC}"
        echo ""
        echo -e "Press ${RED}Ctrl+C${NC} to stop all services"
        wait
        ;;
    *)
        echo "Usage: ./start.sh [backend|student|admin|all]"
        exit 1
        ;;
esac

wait
