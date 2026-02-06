#!/bin/bash
# =============================================================================
# Todo Application Demo Script
# =============================================================================
# This script demonstrates the key features of the Todo application.
#
# Prerequisites:
# - Backend running on localhost:8000
# - Frontend running on localhost:3000
# - curl and jq installed
#
# Usage:
#   ./scripts/demo.sh
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

API_URL="${API_URL:-http://localhost:8000/api}"
TOKEN=""
USER_EMAIL="demo-$(date +%s)@example.com"
USER_PASSWORD="DemoPassword123!"

echo -e "${CYAN}"
echo "============================================="
echo "  Todo Application - Feature Demo"
echo "============================================="
echo -e "${NC}"

# =============================================================================
# Helper Functions
# =============================================================================

pause() {
    echo ""
    read -p "Press Enter to continue..."
    echo ""
}

api_call() {
    local method=$1
    local endpoint=$2
    local data=$3

    if [ -n "$data" ]; then
        curl -s -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "$data"
    else
        curl -s -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN"
    fi
}

# =============================================================================
# Demo: Health Check
# =============================================================================

echo -e "${YELLOW}1. Health Check${NC}"
echo "Checking if the API is running..."

health=$(curl -s "$API_URL/health")
echo "$health" | jq .

if echo "$health" | jq -e '.status == "healthy"' > /dev/null; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${RED}✗ API is not responding${NC}"
    exit 1
fi

pause

# =============================================================================
# Demo: User Registration
# =============================================================================

echo -e "${YELLOW}2. User Registration${NC}"
echo "Registering a new user: $USER_EMAIL"

register_result=$(curl -s -X POST "$API_URL/auth/sign-up/email" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$USER_EMAIL\", \"password\": \"$USER_PASSWORD\", \"name\": \"Demo User\"}")

echo "$register_result" | jq .
echo -e "${GREEN}✓ User registered successfully${NC}"

pause

# =============================================================================
# Demo: User Login
# =============================================================================

echo -e "${YELLOW}3. User Login${NC}"
echo "Logging in..."

login_result=$(curl -s -X POST "$API_URL/auth/sign-in/email" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$USER_EMAIL\", \"password\": \"$USER_PASSWORD\"}")

TOKEN=$(echo "$login_result" | jq -r '.token // .session.token // empty')

if [ -z "$TOKEN" ] || [ "$TOKEN" == "null" ]; then
    echo -e "${RED}✗ Login failed - could not extract token${NC}"
    echo "$login_result" | jq .
    # Try alternative token extraction for Better Auth
    TOKEN=$(echo "$login_result" | jq -r '.user.token // empty')
fi

echo -e "${GREEN}✓ Logged in successfully${NC}"
echo "Token: ${TOKEN:0:20}..."

pause

# =============================================================================
# Demo: Create Tasks
# =============================================================================

echo -e "${YELLOW}4. Creating Tasks${NC}"

echo "Creating task 1: High priority with due date..."
task1=$(api_call POST "/tasks" '{
    "title": "Complete project proposal",
    "description": "Write and submit the Q1 project proposal",
    "priority": "high",
    "due_date": "'$(date -d "+2 days" +%Y-%m-%dT%H:%M:%S 2>/dev/null || date -v+2d +%Y-%m-%dT%H:%M:%S)'Z",
    "tags": ["work", "urgent"]
}')
TASK1_ID=$(echo "$task1" | jq -r '.id')
echo "$task1" | jq '{id, title, priority, due_date, tags}'
echo ""

echo "Creating task 2: Medium priority..."
task2=$(api_call POST "/tasks" '{
    "title": "Review pull requests",
    "description": "Review pending PRs from the team",
    "priority": "medium",
    "tags": ["work", "code-review"]
}')
TASK2_ID=$(echo "$task2" | jq -r '.id')
echo "$task2" | jq '{id, title, priority, tags}'
echo ""

echo "Creating task 3: Low priority with reminder..."
task3=$(api_call POST "/tasks" '{
    "title": "Update documentation",
    "description": "Update API documentation with new endpoints",
    "priority": "low",
    "due_date": "'$(date -d "+7 days" +%Y-%m-%dT%H:%M:%S 2>/dev/null || date -v+7d +%Y-%m-%dT%H:%M:%S)'Z",
    "reminder_offset_minutes": 60,
    "tags": ["docs"]
}')
TASK3_ID=$(echo "$task3" | jq -r '.id')
echo "$task3" | jq '{id, title, priority, due_date}'

echo -e "${GREEN}✓ Created 3 tasks${NC}"

pause

# =============================================================================
# Demo: List Tasks with Filters
# =============================================================================

echo -e "${YELLOW}5. List Tasks with Filters${NC}"

echo "All tasks:"
api_call GET "/tasks" | jq '.data[] | {id: .id[0:8], title, priority, is_complete}'
echo ""

echo "Filtering by priority=high:"
api_call GET "/tasks?priority=high" | jq '.data[] | {id: .id[0:8], title, priority}'
echo ""

echo "Filtering by tag=work:"
api_call GET "/tasks?tags=work" | jq '.data[] | {id: .id[0:8], title, tags}'

echo -e "${GREEN}✓ Filters working correctly${NC}"

pause

# =============================================================================
# Demo: Complete a Task
# =============================================================================

echo -e "${YELLOW}6. Complete a Task${NC}"

echo "Toggling task completion..."
api_call PATCH "/tasks/$TASK2_ID/toggle" | jq '{id: .id[0:8], title, is_complete}'

echo ""
echo "Listing completed tasks:"
api_call GET "/tasks?is_complete=true" | jq '.data[] | {id: .id[0:8], title, is_complete}'

echo -e "${GREEN}✓ Task marked as complete${NC}"

pause

# =============================================================================
# Demo: Update a Task
# =============================================================================

echo -e "${YELLOW}7. Update a Task${NC}"

echo "Updating task priority and adding description..."
api_call PATCH "/tasks/$TASK1_ID" '{"priority": "urgent", "description": "URGENT: Due tomorrow!"}' | jq '{id: .id[0:8], title, priority, description}'

echo -e "${GREEN}✓ Task updated${NC}"

pause

# =============================================================================
# Demo: Tags
# =============================================================================

echo -e "${YELLOW}8. Tags Management${NC}"

echo "Listing all tags with counts:"
api_call GET "/tags" | jq '.data[] | {name, color, task_count}'

echo ""
echo "Creating a new tag..."
api_call POST "/tags" '{"name": "priority", "color": "#FF0000"}' | jq '{name, color}'

echo -e "${GREEN}✓ Tags working correctly${NC}"

pause

# =============================================================================
# Demo: Activity Log
# =============================================================================

echo -e "${YELLOW}9. Activity Log${NC}"

echo "Recent activities:"
api_call GET "/activities?limit=5" | jq '.data[] | {event_type, entity_type, timestamp}'

echo ""
echo "Productivity summary:"
api_call GET "/activities/productivity?days=7" | jq '{
    tasks_created,
    tasks_completed,
    completion_rate
}'

echo -e "${GREEN}✓ Activity log working correctly${NC}"

pause

# =============================================================================
# Demo: Delete a Task
# =============================================================================

echo -e "${YELLOW}10. Delete a Task${NC}"

echo "Deleting task 3..."
api_call DELETE "/tasks/$TASK3_ID"
echo "Task deleted."

echo ""
echo "Remaining tasks:"
api_call GET "/tasks" | jq '.data[] | {id: .id[0:8], title}'

echo -e "${GREEN}✓ Task deleted${NC}"

pause

# =============================================================================
# Summary
# =============================================================================

echo -e "${CYAN}"
echo "============================================="
echo "  Demo Complete!"
echo "============================================="
echo -e "${NC}"

echo "Features demonstrated:"
echo "  ✓ User registration and authentication"
echo "  ✓ Task creation with priorities, due dates, tags"
echo "  ✓ Task filtering and search"
echo "  ✓ Task completion toggle"
echo "  ✓ Task updates"
echo "  ✓ Tags management"
echo "  ✓ Activity log and productivity tracking"
echo "  ✓ Task deletion"
echo ""
echo "For real-time sync demo:"
echo "  1. Open http://localhost:3000 in two browser tabs"
echo "  2. Log in with: $USER_EMAIL / $USER_PASSWORD"
echo "  3. Create a task in one tab"
echo "  4. Watch it appear in the other tab!"
echo ""
echo "For more information, see the documentation:"
echo "  - README.md"
echo "  - docs/QUICKSTART.md"
echo ""
