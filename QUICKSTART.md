# Quick Start Guide

## Installation

```bash
cd flwr-k8s-deploy
pip install -e .
```

## Usage

### 1. Initialize Your Project

```bash
cd /path/to/your/flower/project
flwr-k8s init --server-address YOUR_SERVER_IP:9092
```

### 2. Generate Files

```bash
flwr-k8s generate
```

### 3. Build Docker Image

```bash
docker login
flwr-k8s build
```

### 4. Deploy

Start your SuperLink server first:

```bash
flower-superlink --insecure
```

Then deploy clients:

```bash
flwr-k8s deploy
```

### 5. Monitor

```bash
# Check status
flwr-k8s status

# View logs
flwr-k8s logs -f
```

### 6. Run Training

On your server machine:

```bash
flwr run .
```

## Commands Cheat Sheet

| Command | Description |
|---------|-------------|
| `flwr-k8s init` | Initialize configuration |
| `flwr-k8s generate` | Generate deployment files |
| `flwr-k8s build` | Build Docker image |
| `flwr-k8s deploy` | Deploy to Kubernetes |
| `flwr-k8s status` | Check deployment status |
| `flwr-k8s logs` | View pod logs |
| `flwr-k8s config` | Show configuration |
| `flwr-k8s delete` | Delete deployment |

## Configuration File

Edit `flwr-k8s-config.yaml` to customize:

- Number of client replicas
- Resource limits (CPU/memory)
- Server address
- Training parameters

See README.md for complete documentation.
