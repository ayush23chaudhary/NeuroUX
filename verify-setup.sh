#!/bin/bash
# NeuroUX Project Setup & Verification Script

echo "🧠 NeuroUX Phase 1 - Setup Verification"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📁 Checking Project Structure...${NC}"
echo ""

# Check directories
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} Directory: $1"
    else
        echo -e "${RED}❌${NC} Missing: $1"
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} File: $1"
    else
        echo -e "${RED}❌${NC} Missing: $1"
    fi
}

# Backend structure
echo -e "${BLUE}Backend Structure:${NC}"
check_dir "backend"
check_dir "backend/tests"
check_file "backend/main.py"
check_file "backend/models.py"
check_file "backend/config.py"
check_file "backend/requirements.txt"
check_file "backend/.env.example"
check_file "backend/tests/test_models.py"
echo ""

# Frontend structure
echo -e "${BLUE}Frontend Structure:${NC}"
check_dir "frontend/src"
check_dir "frontend/src/context"
check_dir "frontend/src/hooks"
check_dir "frontend/src/components"
check_file "frontend/package.json"
check_file "frontend/vite.config.js"
check_file "frontend/tailwind.config.js"
check_file "frontend/postcss.config.js"
check_file "frontend/.eslintrc.json"
check_file "frontend/index.html"
check_file "frontend/src/main.jsx"
check_file "frontend/src/App.jsx"
check_file "frontend/src/index.css"
check_file "frontend/src/context/NeuroProvider.jsx"
check_file "frontend/src/hooks/useNeuroTracker.js"
check_file "frontend/src/components/AdaptiveUI.jsx"
echo ""

# Documentation
echo -e "${BLUE}Documentation:${NC}"
check_file "README.md"
check_file "QUICKSTART.md"
check_file "ARCHITECTURE.md"
check_file "DEPLOYMENT.md"
check_file "TESTING.md"
check_file "PROJECT_SUMMARY.md"
check_file "FILE_STRUCTURE.md"
check_file ".github/copilot-instructions.md"
check_file ".gitignore"
echo ""

echo "========================================"
echo -e "${GREEN}✨ NeuroUX Phase 1 Project Complete!${NC}"
echo ""
echo "📖 Next Steps:"
echo "1. Read: ./QUICKSTART.md"
echo "2. Backend: cd backend && python main.py"
echo "3. Frontend: cd frontend && npm run dev"
echo ""
echo "🧪 Testing:"
echo "- Check TESTING.md for comprehensive scenarios"
echo "- Manually test bot detection"
echo "- Monitor WebSocket events in DevTools"
echo ""
echo "📚 Documentation:"
echo "- README.md: Full overview"
echo "- ARCHITECTURE.md: System design"
echo "- FILE_STRUCTURE.md: Complete file guide"
echo ""
echo "🚀 Ready to launch!"
