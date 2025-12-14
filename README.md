# flwr-k8s-deploy

**Kubernetes Deployment Tool for Flower Federated Learning Projects**

Simplify deploying Flower FL applications to Kubernetes clusters with automated Docker image building, manifest generation, and deployment management.

---

## 🚀 Features

- **CLI-Based Workflow**: Simple commands to init, build, and deploy
- **Multi-Architecture Support**: Automatic AMD64 and ARM64 image builds
- **Template-Based Generation**: Customizable Dockerfile and Kubernetes manifests
- **Configuration Management**: YAML-based configuration with sensible defaults
- **Deployment Monitoring**: Built-in commands for status, logs, and management

---

## 🌸 About Flower

[Flower (flwr)](https://flower.ai/) is a friendly federated learning framework that enables distributed machine learning across multiple clients while keeping data decentralized. This tool simplifies deploying Flower projects to Kubernetes.

### Setting Up a Flower Project

1. **Create a virtual environment** (Python 3.11 recommended for better compatibility with PyTorch and Flower):
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

2. **Install Flower and create a new project**:
   ```bash
   pip install flwr
   flwr new new-project
   cd new-project
   pip install -e .
   ```

3. **Clone this deployment tool**:
   ```bash
   git clone https://github.com/coryhighsea/flwr-k8s.git
   ```

Now you're ready to deploy your Flower project to Kubernetes!

---

## 📦 Installation

### From Source

```bash
git clone https://github.com/coryhighsea/flwr-k8s.git
cd flwr-k8s
pip install -e .
```

### Verify Installation

```bash
flwr-k8s --version
```

---

## 🎯 Quick Start

### 1. Initialize Configuration

Navigate to your Flower project directory and initialize:

```bash
cd /path/to/your/flower/project
flwr-k8s init
```

You'll be prompted for:
- **SuperLink server address**: Your server's IP and port (e.g., `192.168.1.100:9092`)
- **Docker Hub username**: Your Docker Hub account (default: `Docker_username`)
- **Number of replicas**: Number of client pods (default: `2`)

This creates `flwr-k8s-config.yaml` in your project directory.

### 2. Review and Edit Configuration

```bash
cat flwr-k8s-config.yaml
```

Edit if needed:

```yaml
project:
  name: predictive-maintenance
  version: 1.0.0

docker:
  registry: docker.io
  username: username
  image_name: flwr-client
  tag: latest
  platforms:
    - linux/amd64
    - linux/arm64

kubernetes:
  namespace: default
  replicas: 2
  server_address: 192.168.1.100:9092

flower:
  num_server_rounds: 10
  local_epochs: 2
  min_fit_clients: 2
  min_evaluate_clients: 2
  min_available_clients: 2

resources:
  requests:
    memory: 512Mi
    cpu: 250m
  limits:
    memory: 2Gi
    cpu: 1000m
```

### 3. Generate Deployment Files

```bash
flwr-k8s generate
```

This generates:
- `Dockerfile` - Multi-arch Docker image definition
- `.dockerignore` - Optimized build context
- `k8s/deployment.yaml` - Kubernetes Deployment manifest
- `k8s/configmap.yaml` - Configuration for clients
- `build.sh` - Docker build script
- `deploy.sh` - Kubernetes deployment script

### 4. Build Docker Image

Login to Docker Hub:

```bash
docker login
```

Build and push multi-architecture image:

```bash
flwr-k8s build
```

Or use the generated script:

```bash
./build.sh
```

This builds for both AMD64 (Linux PC) and ARM64 (Raspberry Pi) architectures.

### 5. Deploy to Kubernetes

Ensure your `kubectl` is configured to access your cluster:
Make sure kubectl is installed on main machine

```bash
kubectl cluster-info
kubectl get nodes
```

Deploy:

```bash
flwr-k8s deploy
```

Or use the generated script:

```bash
./deploy.sh
```

---

## 📋 CLI Commands

### `flwr-k8s init`

Initialize deployment configuration.

```bash
flwr-k8s init [OPTIONS]

Options:
  --project-dir PATH        Project directory (default: current directory)
  --server-address TEXT     SuperLink server address
  --docker-username TEXT    Docker Hub username (default: username)
  --replicas INTEGER        Number of client replicas (default: 2)
```

### `flwr-k8s generate`

Generate Dockerfile and Kubernetes manifests.

```bash
flwr-k8s generate [OPTIONS]

Options:
  --project-dir PATH   Project directory
  --output-dir PATH    Output directory for generated files
```

### `flwr-k8s build`

Build Docker image.

```bash
flwr-k8s build [OPTIONS]

Options:
  --project-dir PATH     Project directory
  --push/--no-push       Push image to registry (default: push)
```

### `flwr-k8s deploy`

Deploy to Kubernetes cluster.

```bash
flwr-k8s deploy [OPTIONS]

Options:
  --project-dir PATH    Project directory
  --kubeconfig PATH     Path to kubeconfig file
```

### `flwr-k8s status`

Show deployment status.

```bash
flwr-k8s status [OPTIONS]

Options:
  --namespace TEXT    Kubernetes namespace (default: default)
```

### `flwr-k8s logs`

View pod logs.

```bash
flwr-k8s logs [OPTIONS]

Options:
  --namespace TEXT    Kubernetes namespace (default: default)
  --follow, -f        Follow log output
  --pod TEXT          Specific pod name
```

### `flwr-k8s delete`

Delete Kubernetes deployment.

```bash
flwr-k8s delete [OPTIONS]

Options:
  --namespace TEXT    Kubernetes namespace (default: default)
```

### `flwr-k8s config`

Show current configuration.

```bash
flwr-k8s config [OPTIONS]

Options:
  --project-dir PATH    Project directory
```

---

## 🏗️ Complete Workflow Example

### Prerequisites

1. **Kubernetes Cluster Setup**

   Install k3s on your nodes:

   ```bash
   # On Linux PC (master node)
   curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
   
   # Get the join token
   sudo cat /var/lib/rancher/k3s/server/node-token
   
   # On Raspberry Pi (worker node)
   export K3S_URL="https://<MASTER_IP>:6443"
   export K3S_TOKEN="<TOKEN_FROM_MASTER>"
   curl -sfL https://get.k3s.io | K3S_URL=$K3S_URL K3S_TOKEN=$K3S_TOKEN sh -
   ```

2. **Configure kubectl on Your MacBook**

   ```bash
   # Copy kubeconfig from Linux PC
   mkdir -p ~/.kube
   # Edit and change server IP to your Linux PC's IP
   nano ~/.kube/config
   
   # Verify
   kubectl get nodes
   ```

3. **Docker Hub Account**

   Sign up at https://hub.docker.com if you don't have an account.

### Deployment Steps

```bash
# 1. Navigate to your Flower project
cd /path/to/predictive-maintenance

# 2. Install flwr-k8s-deploy
cd ../flwr-k8s-deploy
pip install -e .

# 3. Initialize (back in your project)
cd ../predictive-maintenance
flwr-k8s init \
  --server-address 192.168.1.100:9092 \
  --docker-username username \
  --replicas 2

# 4. Review configuration
flwr-k8s config

# 5. Generate deployment files
flwr-k8s generate

# 6. Build and push Docker image
docker login
flwr-k8s build

# 7. Start SuperLink on your server
flower-superlink --insecure

# 8. Deploy clients to Kubernetes
flwr-k8s deploy

# 9. Monitor deployment
flwr-k8s status
flwr-k8s logs -f

# 10. Run training from your server
flwr run . --run-config "num-server-rounds=10 local-epochs=2"
```

---

## 🔧 Configuration Reference

### Docker Settings

```yaml
docker:
  registry: docker.io              # Docker registry
  username: username               # Your Docker Hub username
  image_name: flwr-client         # Image name
  tag: latest                     # Image tag
  platforms:                      # Target platforms
    - linux/amd64                 # Intel/AMD (Linux PC)
    - linux/arm64                 # ARM (Raspberry Pi)
```

### Kubernetes Settings

```yaml
kubernetes:
  namespace: default              # K8s namespace
  replicas: 2                     # Number of client pods
  server_address: 192.168.1.100:9092  # SuperLink address
```

**Important**: The `server_address` should be:
- Your server machine's **local network IP** (not localhost)
- Port `9092` for Fleet API (where SuperNodes connect)
- Format: `<IP>:<PORT>`

### Flower Settings

```yaml
flower:
  num_server_rounds: 10          # Training rounds
  local_epochs: 2                # Local epochs per round
  min_fit_clients: 2             # Min clients for training
  min_evaluate_clients: 2        # Min clients for evaluation
  min_available_clients: 2       # Min clients to start
```

### Resource Settings

```yaml
resources:
  requests:                      # Minimum guaranteed resources
    memory: 512Mi
    cpu: 250m
  limits:                        # Maximum allowed resources
    memory: 2Gi
    cpu: 1000m
```

Adjust based on your hardware:
- **Raspberry Pi**: Keep defaults
- **More powerful nodes**: Increase limits

---

## 📁 Project Structure

After running `flwr-k8s generate`, your project will have:

```
your-flower-project/
├── flwr-k8s-config.yaml          # Configuration file
├── Dockerfile                    # Multi-arch Docker image
├── .dockerignore                # Build context optimization
├── build.sh                      # Docker build script
├── deploy.sh                     # K8s deployment script
├── k8s/
│   ├── deployment.yaml          # K8s Deployment manifest
│   └── configmap.yaml           # K8s ConfigMap
├── pyproject.toml               # Your Flower project config
└── predictive_maintenance/      # Your Flower app code
    ├── __init__.py
    ├── task.py
    ├── client_app.py
    └── server_app.py
```

---

## 🐛 Troubleshooting

### Pods Not Starting

Check pod status:

```bash
kubectl get pods -l app=flwr-client
kubectl describe pod <pod-name>
```

Common issues:
- **ImagePullBackOff**: Image not found in registry. Check Docker Hub.
- **CrashLoopBackOff**: Application error. Check logs: `flwr-k8s logs`

### Cannot Connect to Server

Verify network connectivity from cluster:

```bash
# SSH into one of your K8s nodes
ssh user@node-ip

# Test connection to server
curl -v telnet://192.168.1.100:9092
```

Ensure:
- Server IP is correct in `flwr-k8s-config.yaml`
- Server machine firewall allows port 9092
- All devices are on the same network

### Build Fails

Check Docker Buildx:

```bash
docker buildx version
docker buildx ls
```

If buildx is missing:

```bash
# Install Docker Desktop (includes buildx)
# Or on Linux:
docker buildx create --use
```

### Deployment Exists

If you get "already exists" errors:

```bash
flwr-k8s delete
flwr-k8s deploy
```

---

## 🔄 Updating Deployment

### Update Configuration

1. Edit `flwr-k8s-config.yaml`
2. Regenerate files: `flwr-k8s generate`
3. Rebuild image: `flwr-k8s build`
4. Redeploy: `flwr-k8s deploy`

### Update Application Code

1. Make changes to your Flower app
2. Rebuild image: `flwr-k8s build`
3. Restart deployment:

```bash
kubectl rollout restart deployment/flwr-client
kubectl rollout status deployment/flwr-client
```

---

## 🎓 Advanced Usage

### Custom Models

The deployment system works with any Flower project structure. To use a custom model:

1. Ensure your project has:
   - `pyproject.toml` with Flower configuration
   - `task.py` with model definition
   - `client_app.py` with ClientApp
   - `server_app.py` with ServerApp

2. Initialize deployment in your project:

```bash
cd /path/to/your/custom/flower/project
flwr-k8s init
flwr-k8s generate
```

### Multiple Deployments

Deploy different projects by using separate config files:

```bash
# Project A
flwr-k8s init --project-dir ./project-a
cd project-a
flwr-k8s generate
flwr-k8s build

# Project B
flwr-k8s init --project-dir ./project-b
cd project-b
flwr-k8s generate
flwr-k8s build
```

### Private Docker Registry

Update configuration:

```yaml
docker:
  registry: your-registry.com
  username: your-username
  image_name: flwr-client
```

Create image pull secret in Kubernetes:

```bash
kubectl create secret docker-registry regcred \
  --docker-server=your-registry.com \
  --docker-username=your-username \
  --docker-password=your-password
```

Edit generated `deployment.yaml` to add:

```yaml
spec:
  template:
    spec:
      imagePullSecrets:
      - name: regcred
```

---

## 📝 Notes

- **Architecture**: Automatically detects and builds for your target platforms
- **Security**: Uses `--insecure` flag for testing. For production, enable TLS
- **Scalability**: Easily scale by changing `replicas` in config
- **Monitoring**: Use `flwr-k8s status` and `flwr-k8s logs` for observability

---

## 🤝 Contributing

Contributions welcome! Please submit issues or pull requests.

---

## 📄 License

MIT

---

## 🔗 Resources

- [Flower Documentation](https://flower.ai/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [k3s Documentation](https://k3s.io/)

---

**Happy Federated Learning! 🌸**
