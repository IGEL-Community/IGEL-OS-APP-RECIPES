#!/bin/bash
# Tailscale IGEL OS 12 Smoke Test Script
# This script should be run on the IGEL OS 12 device after package installation

set -e

echo "=== Tailscale IGEL OS 12 Smoke Test ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" &>/dev/null; then
        echo -e "${GREEN}PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAILED${NC}"
        ((TESTS_FAILED++))
        echo "  Command: $test_command"
    fi
}

# 1. Check if tailscale binaries are installed
run_test "Tailscale binary exists" "test -f /usr/bin/tailscale"
run_test "Tailscaled binary exists" "test -f /usr/bin/tailscaled"

# 2. Check if service file exists
run_test "Systemd service file exists" "test -f /lib/systemd/system/tailscaled.service"

# 3. Check if service is enabled
run_test "Tailscaled service is enabled" "systemctl is-enabled tailscaled"

# 4. Check if service is running
run_test "Tailscaled service is active" "systemctl is-active tailscaled"

# 5. Check if tailscale commands work
run_test "Tailscale version command" "tailscale version"

# 6. Check network interface (may not exist until authenticated)
if ip link show tailscale0 &>/dev/null; then
    run_test "Tailscale network interface exists" "ip link show tailscale0"
else
    echo -e "Info: ${YELLOW}tailscale0 interface not yet created (need to authenticate first)${NC}"
fi

# 7. Check tailscale status
echo
echo "=== Tailscale Status ==="
if tailscale status &>/dev/null; then
    tailscale status
else
    echo -e "${YELLOW}Not authenticated yet. Run: sudo tailscale up --authkey=<your-key>${NC}"
fi

# 8. Check service logs (last 10 lines)
echo
echo "=== Recent Service Logs ==="
sudo journalctl -u tailscaled -n 10 --no-pager || echo "Unable to fetch logs"

# 9. Check IGEL-specific directories
echo
echo "=== IGEL-specific Checks ==="
run_test "Session config exists" "test -d /userhome/.config/sessions"
run_test "RW partition mounted" "mount | grep -q '/userhome'"

# Summary
echo
echo "=== Test Summary ==="
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed! Tailscale is ready for authentication.${NC}"
    echo -e "To authenticate, run: ${YELLOW}sudo tailscale up --authkey=<your-key>${NC}"
else
    echo -e "\n${RED}Some tests failed. Please check the installation.${NC}"
    exit 1
fi

# Additional manual verification steps
echo
echo "=== Manual Verification Steps ==="
echo "1. Authenticate: sudo tailscale up --authkey=<your-key>"
echo "2. Check status: tailscale status"
echo "3. Test connectivity: tailscale ping <another-node>"
echo "4. Verify in admin console: https://login.tailscale.com/admin/machines"
