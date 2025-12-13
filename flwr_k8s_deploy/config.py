"""Configuration management for flwr-k8s-deploy"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "project": {
        "name": "predictive-maintenance",
        "version": "1.0.0",
    },
    "docker": {
        "registry": "docker.io",
        "username": "cjhisey",
        "image_name": "flwr-client",
        "tag": "latest",
        "platforms": ["linux/amd64", "linux/arm64"],
    },
    "kubernetes": {
        "namespace": "default",
        "replicas": 2,
        "server_address": "192.168.1.100:9092",
    },
    "flower": {
        "num_server_rounds": 10,
        "local_epochs": 2,
        "min_fit_clients": 2,
        "min_evaluate_clients": 2,
        "min_available_clients": 2,
    },
    "resources": {
        "requests": {
            "memory": "512Mi",
            "cpu": "250m",
        },
        "limits": {
            "memory": "2Gi",
            "cpu": "1000m",
        },
    },
}


class Config:
    """Configuration manager for flwr-k8s-deploy"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.cwd() / "flwr-k8s-config.yaml"
        self.data = DEFAULT_CONFIG.copy()
        
        if self.config_path.exists():
            self.load()
    
    def load(self) -> None:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            loaded_config = yaml.safe_load(f)
            if loaded_config:
                self._merge_configs(self.data, loaded_config)
    
    def save(self) -> None:
        """Save configuration to YAML file"""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)
    
    def _merge_configs(self, base: Dict, update: Dict) -> None:
        """Recursively merge update into base"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        data = self.data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        for key, value in updates.items():
            self.set(key, value)
