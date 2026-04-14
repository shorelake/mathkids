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

start_backend() {
    echo -e "${BLUE}🚀 Starting Backend (FastAPI) on port 8000...${NC}"
    cd backend
    pip install -q -r requirements.txt --break-system-packages 2>/dev/null || pip install -q -r requirements.txt
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
    cd ..
}

start_student() {
    echo -e "${BLUE}🎮 Starting Student App on port 3000...${NC}"
    cd student-app
    npm install --silent 2>/dev/null
    npm run dev &
    STUDENT_PID=$!
    echo -e "${GREEN}✅ Student App started (PID: $STUDENT_PID)${NC}"
    cd ..
}

start_admin() {
    echo -e "${BLUE}📊 Starting Admin App on port 3001...${NC}"
    cd admin-app
    npm install --silent 2>/dev/null
    npm run dev &
    ADMIN_PID=$!
    echo -e "${GREEN}✅ Admin App started (PID: $ADMIN_PID)${NC}"
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
        echo -e "${GREEN}  MathKids 全部服务已启动！${NC}"
        echo -e "${GREEN}============================================${NC}"
        echo -e "  ${YELLOW}后端 API:${NC}    http://localhost:8000"
        echo -e "  ${YELLOW}API 文档:${NC}    http://localhost:8000/docs"
        echo -e "  ${YELLOW}学生端:${NC}      http://localhost:3000"
        echo -e "  ${YELLOW}管理端:${NC}      http://localhost:3001"
        echo -e "${GREEN}============================================${NC}"
        echo ""
        echo -e "按 ${RED}Ctrl+C${NC} 停止所有服务"
        wait
        ;;
    *)
        echo "Usage: ./start.sh [backend|student|admin|all]"
        exit 1
        ;;
esac

wait
