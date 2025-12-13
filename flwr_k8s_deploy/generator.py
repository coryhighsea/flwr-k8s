"""Template generator for Kubernetes deployment files"""

from pathlib import Path
from jinja2 import Template
from typing import Dict, Any

class TemplateGenerator:
    """Generate deployment files from templates"""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
    
    def generate(self, template_name: str, context: Dict[str, Any], output_path: Path) -> None:
        """Generate a file from a template"""
        template_path = self.template_dir / template_name
        
        with open(template_path, 'r') as f:
            template = Template(f.read())
        
        content = template.render(**context)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)
    
    def generate_all(self, context: Dict[str, Any], output_dir: Path) -> None:
        """Generate all deployment files"""
        # Ensure package_name is in context (convert hyphens to underscores)
        if 'package_name' not in context and 'project_name' in context:
            context['package_name'] = context['project_name'].replace('-', '_')
        
        files = {
            "Dockerfile.j2": output_dir / "Dockerfile",
            "deployment.yaml.j2": output_dir / "k8s" / "deployment.yaml",
            "configmap.yaml.j2": output_dir / "k8s" / "configmap.yaml",
            "build.sh.j2": output_dir / "build.sh",
            "deploy.sh.j2": output_dir / "deploy.sh",
            ".dockerignore.j2": output_dir / ".dockerignore",
        }
        
        for template_name, output_path in files.items():
            self.generate(template_name, context, output_path)
        
        # Make scripts executable
        for script in [output_dir / "build.sh", output_dir / "deploy.sh"]:
            if script.exists():
                script.chmod(0o755)
