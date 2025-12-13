"""Command-line interface for flwr-k8s-deploy"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import subprocess
import sys
import os
import shutil

from .config import Config
from .generator import TemplateGenerator

console = Console()


def find_kubectl():
    """Find kubectl command in PATH or common locations"""
    # Try to find in PATH
    kubectl = shutil.which('kubectl')
    if kubectl:
        return kubectl
    
    # Try common locations
    common_paths = [
        '/usr/local/bin/kubectl',
        '/usr/bin/kubectl',
        '/opt/homebrew/bin/kubectl',
        os.path.expanduser('~/.local/bin/kubectl'),
    ]
    
    for path in common_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    return None


def run_kubectl(args, env=None, **kwargs):
    """Run kubectl command with proper PATH resolution"""
    kubectl = find_kubectl()
    
    if not kubectl:
        console.print("[red]❌ kubectl not found. Please ensure kubectl is installed and in your PATH.[/red]")
        console.print("\nInstallation instructions:")
        console.print("  macOS: brew install kubectl")
        console.print("  Linux: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/")
        sys.exit(1)
    
    # Merge environment variables
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    
    return subprocess.run([kubectl] + args, env=run_env, **kwargs)


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Flower Kubernetes Deployment Tool
    
    Deploy Flower Federated Learning projects to Kubernetes with ease.
    """
    pass


@main.command()
@click.option('--project-dir', type=click.Path(), default='.', help='Project directory (default: current directory)')
@click.option('--server-address', prompt='SuperLink server address', help='Server address (e.g., 192.168.1.100:9092)')
@click.option('--docker-username', default='cjhisey', help='Docker Hub username')
@click.option('--replicas', default=2, type=int, help='Number of client replicas')
def init(project_dir, server_address, docker_username, replicas):
    """Initialize flwr-k8s deployment configuration"""
    project_path = Path(project_dir).resolve()
    config_path = project_path / "flwr-k8s-config.yaml"
    
    console.print(Panel.fit(
        "[bold cyan]Initializing Flower Kubernetes Deployment[/bold cyan]",
        border_style="cyan"
    ))
    
    # Create configuration
    config = Config(config_path)
    config.set('kubernetes.server_address', server_address)
    config.set('docker.username', docker_username)
    config.set('kubernetes.replicas', replicas)
    config.set('flower.min_fit_clients', replicas)
    config.set('flower.min_evaluate_clients', replicas)
    config.set('flower.min_available_clients', replicas)
    
    # Detect project name from pyproject.toml if exists
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        try:
            import sys
            if sys.version_info >= (3, 11):
                import tomllib
            else:
                import tomli as tomllib
            
            with open(pyproject, 'rb') as f:
                data = tomllib.load(f)
                project_name = data.get('project', {}).get('name', project_path.name)
                config.set('project.name', project_name)
        except:
            pass
    
    config.save()
    
    console.print(f"\n✅ Configuration saved to: [bold]{config_path}[/bold]")
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("  1. Review and edit configuration: [cyan]flwr-k8s-config.yaml[/cyan]")
    console.print("  2. Generate deployment files: [cyan]flwr-k8s generate[/cyan]")
    console.print("  3. Build Docker image: [cyan]flwr-k8s build[/cyan]")
    console.print("  4. Deploy to Kubernetes: [cyan]flwr-k8s deploy[/cyan]")


@main.command()
@click.option('--project-dir', type=click.Path(), default='.', help='Project directory')
@click.option('--output-dir', type=click.Path(), default='.', help='Output directory for generated files')
def generate(project_dir, output_dir):
    """Generate Dockerfile and Kubernetes manifests"""
    project_path = Path(project_dir).resolve()
    output_path = Path(output_dir).resolve()
    config_path = project_path / "flwr-k8s-config.yaml"
    
    if not config_path.exists():
        console.print("[red]❌ Configuration not found. Run 'flwr-k8s init' first.[/red]")
        sys.exit(1)
    
    config = Config(config_path)
    
    console.print(Panel.fit(
        "[bold cyan]Generating Deployment Files[/bold cyan]",
        border_style="cyan"
    ))
    
    # Prepare template context
    project_name = config.get('project.name')
    package_name = project_name.replace('-', '_')  # Flower converts hyphens to underscores
    
    context = {
        'project_name': project_name,
        'package_name': package_name,
        'docker_registry': config.get('docker.registry'),
        'docker_username': config.get('docker.username'),
        'image_name': config.get('docker.image_name'),
        'tag': config.get('docker.tag'),
        'full_image': f"{config.get('docker.username')}/{config.get('docker.image_name')}:{config.get('docker.tag')}",
        'platforms': ','.join(config.get('docker.platforms')),
        'namespace': config.get('kubernetes.namespace'),
        'replicas': config.get('kubernetes.replicas'),
        'server_address': config.get('kubernetes.server_address'),
        'num_server_rounds': config.get('flower.num_server_rounds'),
        'local_epochs': config.get('flower.local_epochs'),
        'resources': config.get('resources'),
    }
    
    # Get template directory
    template_dir = Path(__file__).parent / "templates"
    generator = TemplateGenerator(template_dir)
    
    try:
        generator.generate_all(context, output_path)
        
        console.print("\n✅ [green]Generated files:[/green]")
        console.print(f"  📄 {output_path / 'Dockerfile'}")
        console.print(f"  📄 {output_path / '.dockerignore'}")
        console.print(f"  📄 {output_path / 'k8s' / 'deployment.yaml'}")
        console.print(f"  📄 {output_path / 'k8s' / 'configmap.yaml'}")
        console.print(f"  📜 {output_path / 'build.sh'}")
        console.print(f"  📜 {output_path / 'deploy.sh'}")
        
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("  Build image: [cyan]flwr-k8s build[/cyan] or [cyan]./build.sh[/cyan]")
        console.print("  Deploy: [cyan]flwr-k8s deploy[/cyan] or [cyan]./deploy.sh[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Error generating files: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--project-dir', type=click.Path(), default='.', help='Project directory')
@click.option('--push/--no-push', default=True, help='Push image to registry')
def build(project_dir, push):
    """Build Docker image"""
    project_path = Path(project_dir).resolve()
    config_path = project_path / "flwr-k8s-config.yaml"
    
    if not config_path.exists():
        console.print("[red]❌ Configuration not found. Run 'flwr-k8s init' first.[/red]")
        sys.exit(1)
    
    config = Config(config_path)
    
    console.print(Panel.fit(
        "[bold cyan]Building Docker Image[/bold cyan]",
        border_style="cyan"
    ))
    
    build_script = project_path / "build.sh"
    if not build_script.exists():
        console.print("[red]❌ build.sh not found. Run 'flwr-k8s generate' first.[/red]")
        sys.exit(1)
    
    try:
        result = subprocess.run(
            ["bash", str(build_script)],
            cwd=project_path,
            check=True
        )
        
        if result.returncode == 0:
            console.print("\n✅ [green]Docker image built successfully![/green]")
            
            if push:
                image = f"{config.get('docker.username')}/{config.get('docker.image_name')}:{config.get('docker.tag')}"
                console.print(f"  Image: [cyan]{image}[/cyan]")
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Build failed with exit code {e.returncode}[/red]")
        sys.exit(1)


@main.command()
@click.option('--project-dir', type=click.Path(), default='.', help='Project directory')
@click.option('--kubeconfig', type=click.Path(), help='Path to kubeconfig file')
def deploy(project_dir, kubeconfig):
    """Deploy to Kubernetes cluster"""
    project_path = Path(project_dir).resolve()
    config_path = project_path / "flwr-k8s-config.yaml"
    
    if not config_path.exists():
        console.print("[red]❌ Configuration not found. Run 'flwr-k8s init' first.[/red]")
        sys.exit(1)
    
    config = Config(config_path)
    
    console.print(Panel.fit(
        "[bold cyan]Deploying to Kubernetes[/bold cyan]",
        border_style="cyan"
    ))
    
    k8s_dir = project_path / "k8s"
    if not k8s_dir.exists():
        console.print("[red]❌ k8s directory not found. Run 'flwr-k8s generate' first.[/red]")
        sys.exit(1)
    
    kubectl_env = {}
    if kubeconfig:
        kubectl_env['KUBECONFIG'] = kubeconfig
    
    try:
        # Apply ConfigMap
        console.print("\n📦 Applying ConfigMap...")
        run_kubectl(
            ["apply", "-f", str(k8s_dir / "configmap.yaml")],
            env=kubectl_env,
            check=True
        )
        
        # Apply Deployment
        console.print("📦 Applying Deployment...")
        run_kubectl(
            ["apply", "-f", str(k8s_dir / "deployment.yaml")],
            env=kubectl_env,
            check=True
        )
        
        console.print("\n✅ [green]Deployment successful![/green]")
        console.print("\n[yellow]Monitor deployment:[/yellow]")
        console.print("  Status: [cyan]flwr-k8s status[/cyan]")
        console.print("  Logs: [cyan]flwr-k8s logs[/cyan]")
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Deployment failed: {e}[/red]")
        sys.exit(1)
    except FileNotFoundError:
        pass  # Already handled by run_kubectl


@main.command()
@click.option('--namespace', default='default', help='Kubernetes namespace')
def status(namespace):
    """Show deployment status"""
    console.print(Panel.fit(
        "[bold cyan]Deployment Status[/bold cyan]",
        border_style="cyan"
    ))
    
    try:
        # Get pods
        result = run_kubectl(
            ["get", "pods", "-n", namespace, "-l", "app=flwr-client", "-o", "wide"],
            capture_output=True,
            text=True,
            check=True
        )
        
        console.print("\n[bold]Pods:[/bold]")
        console.print(result.stdout)
        
        # Get deployment
        result = run_kubectl(
            ["get", "deployment", "-n", namespace, "-l", "app=flwr-client"],
            capture_output=True,
            text=True,
            check=True
        )
        
        console.print("\n[bold]Deployment:[/bold]")
        console.print(result.stdout)
        
    except subprocess.CalledProcessError:
        console.print("[red]❌ Failed to get status. Is kubectl configured?[/red]")
        sys.exit(1)
    except FileNotFoundError:
        pass  # Already handled by run_kubectl


@main.command()
@click.option('--namespace', default='default', help='Kubernetes namespace')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--pod', help='Specific pod name')
def logs(namespace, follow, pod):
    """View pod logs"""
    console.print(Panel.fit(
        "[bold cyan]Pod Logs[/bold cyan]",
        border_style="cyan"
    ))
    
    try:
        if not pod:
            # Get first pod
            result = run_kubectl(
                ["get", "pods", "-n", namespace, "-l", "app=flwr-client", "-o", "jsonpath={.items[0].metadata.name}"],
                capture_output=True,
                text=True,
                check=True
            )
            pod = result.stdout.strip()
        
        if not pod:
            console.print("[red]❌ No pods found[/red]")
            sys.exit(1)
        
        console.print(f"\n[yellow]Showing logs for pod: {pod}[/yellow]\n")
        
        cmd = ["logs", "-n", namespace, pod]
        if follow:
            cmd.append("-f")
        
        run_kubectl(cmd, check=True)
        
    except subprocess.CalledProcessError:
        console.print("[red]❌ Failed to get logs[/red]")
        sys.exit(1)
    except FileNotFoundError:
        pass  # Already handled by run_kubectl


@main.command()
@click.option('--namespace', default='default', help='Kubernetes namespace')
@click.confirmation_option(prompt='Are you sure you want to delete the deployment?')
def delete(namespace):
    """Delete Kubernetes deployment"""
    console.print(Panel.fit(
        "[bold red]Deleting Deployment[/bold red]",
        border_style="red"
    ))
    
    try:
        run_kubectl(
            ["delete", "deployment,configmap", "-n", namespace, "-l", "app=flwr-client"],
            check=True
        )
        
        console.print("\n✅ [green]Deployment deleted successfully[/green]")
        
    except subprocess.CalledProcessError:
        console.print("[red]❌ Failed to delete deployment[/red]")
        sys.exit(1)
    except FileNotFoundError:
        pass  # Already handled by run_kubectl


@main.command()
@click.option('--project-dir', type=click.Path(), default='.', help='Project directory')
def config(project_dir):
    """Show current configuration"""
    project_path = Path(project_dir).resolve()
    config_path = project_path / "flwr-k8s-config.yaml"
    
    if not config_path.exists():
        console.print("[red]❌ Configuration not found. Run 'flwr-k8s init' first.[/red]")
        sys.exit(1)
    
    cfg = Config(config_path)
    
    console.print(Panel.fit(
        "[bold cyan]Current Configuration[/bold cyan]",
        border_style="cyan"
    ))
    
    # Display as table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    def add_section(section_name, section_data, prefix=""):
        for key, value in section_data.items():
            full_key = f"{prefix}{key}" if prefix else key
            if isinstance(value, dict):
                add_section(key, value, f"{full_key}.")
            else:
                table.add_row(full_key, str(value))
    
    add_section("", cfg.data)
    console.print(table)


if __name__ == '__main__':
    main()
