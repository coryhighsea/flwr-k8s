#!/bin/bash
# Example: Complete deployment workflow

set -e

echo "=========================================="
echo "Flower Kubernetes Deployment - Example"
echo "=========================================="

# Configuration
PROJECT_DIR="../predictive-maintenance"
SERVER_IP="192.168.1.100"

echo ""
echo "Step 1: Installing flwr-k8s-deploy..."
pip install -e .

echo ""
echo "Step 2: Initializing project..."
cd "$PROJECT_DIR"
flwr-k8s init \
  --server-address "${SERVER_IP}:9092" \
  --docker-username cjhisey \
  --replicas 2

echo ""
echo "Step 3: Generating deployment files..."
flwr-k8s generate

echo ""
echo "Step 4: Building Docker image..."
echo "Make sure you're logged into Docker Hub: docker login"
read -p "Press Enter to continue..."
flwr-k8s build

echo ""
echo "Step 5: Deployment configuration complete!"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Start SuperLink on your server:"
echo "   flower-superlink --insecure"
echo ""
echo "2. Deploy clients to Kubernetes:"
echo "   cd $PROJECT_DIR"
echo "   flwr-k8s deploy"
echo ""
echo "3. Monitor deployment:"
echo "   flwr-k8s status"
echo "   flwr-k8s logs -f"
echo ""
echo "4. Run training (from server):"
echo "   flwr run ."
echo ""
echo "=========================================="
