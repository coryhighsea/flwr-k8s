#!/bin/bash
# Installation and Quick Test Script for flwr-k8s-deploy

set -e

echo "=========================================="
echo "flwr-k8s-deploy - Installation & Test"
echo "=========================================="

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "Step 1: Installing package..."
pip install -e .

echo ""
echo "Step 2: Verifying installation..."
if command -v flwr-k8s &> /dev/null; then
    echo "✅ flwr-k8s command found"
    flwr-k8s --version
else
    echo "❌ flwr-k8s command not found"
    exit 1
fi

echo ""
echo "Step 3: Testing CLI commands..."

# Test help
echo "Testing: flwr-k8s --help"
flwr-k8s --help > /dev/null 2>&1 && echo "✅ Help command works" || echo "❌ Help command failed"

# Test each command's help
for cmd in init generate build deploy status logs delete config; do
    flwr-k8s $cmd --help > /dev/null 2>&1 && echo "✅ $cmd command available" || echo "❌ $cmd command failed"
done

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Package installed successfully at:"
echo "  $SCRIPT_DIR"
echo ""
echo "Available commands:"
echo "  flwr-k8s init      - Initialize configuration"
echo "  flwr-k8s generate  - Generate deployment files"
echo "  flwr-k8s build     - Build Docker image"
echo "  flwr-k8s deploy    - Deploy to Kubernetes"
echo "  flwr-k8s status    - Check deployment status"
echo "  flwr-k8s logs      - View pod logs"
echo "  flwr-k8s config    - Show configuration"
echo "  flwr-k8s delete    - Delete deployment"
echo ""
echo "Next steps:"
echo "  1. Navigate to your Flower project directory"
echo "  2. Run: flwr-k8s init"
echo "  3. Follow the prompts"
echo ""
echo "Documentation:"
echo "  📖 Full guide: $SCRIPT_DIR/README.md"
echo "  ⚡ Quick start: $SCRIPT_DIR/QUICKSTART.md"
echo "  📦 Package info: $SCRIPT_DIR/PACKAGE_SUMMARY.md"
echo ""
echo "Example workflow:"
echo "  Run: $SCRIPT_DIR/example-workflow.sh"
echo ""
echo "=========================================="
