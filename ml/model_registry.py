"""
Model Registry System

Manages model versions, metadata, and deployment lifecycle.

Features:
- Register new models with metadata
- Version control (semantic versioning)
- Compare model performance
- Set production model
- Rollback capability
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import pickle

class ModelRegistry:
    """Manage ML model versions and deployment"""
    
    def __init__(self, registry_path: str = "models/registry.json"):
        self.registry_path = Path(registry_path)
        self.models_dir = self.registry_path.parent
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create registry
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                self.registry = json.load(f)
        else:
            self.registry = {
                'models': {},
                'production': None,
                'history': []
            }
            self._save_registry()
    
    def _save_registry(self):
        """Save registry to disk"""
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(self,
                      model_path: str,
                      version: str,
                      model_type: str,
                      metrics: Dict,
                      metadata: Optional[Dict] = None) -> bool:
        """
        Register a new model version
        
        Args:
            model_path: Path to model file
            version: Semantic version (e.g., "1.1.0")
            model_type: "logistic" or "xgboost"
            metrics: Performance metrics
            metadata: Additional metadata
            
        Returns:
            True if registered successfully
        """
        if version in self.registry['models']:
            print(f"⚠ Version {version} already exists!")
            return False
        
        # Create version directory
        version_dir = self.models_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy model file
        model_file = version_dir / f"{model_type}_model.pkl"
        shutil.copy(model_path, model_file)
        
        # Save metadata
        model_info = {
            'version': version,
            'model_type': model_type,
            'model_path': str(model_file),
            'metrics': metrics,
            'metadata': metadata or {},
            'registered_at': datetime.now().isoformat(),
            'status': 'registered'
        }
        
        # Save model metadata
        with open(version_dir / 'metadata.json', 'w') as f:
            json.dump(model_info, f, indent=2)
        
        # Update registry
        self.registry['models'][version] = model_info
        self.registry['history'].append({
            'action': 'register',
            'version': version,
            'timestamp': datetime.now().isoformat()
        })
        
        self._save_registry()
        
        print(f"✓ Model {version} registered successfully")
        return True
    
    def get_model(self, version: str) -> Optional[Dict]:
        """Get model information by version"""
        return self.registry['models'].get(version)
    
    def list_models(self) -> List[Dict]:
        """List all registered models"""
        return list(self.registry['models'].values())
    
    def compare_models(self, version1: str, version2: str) -> Dict:
        """Compare two model versions"""
        model1 = self.get_model(version1)
        model2 = self.get_model(version2)
        
        if not model1 or not model2:
            return {'error': 'One or both versions not found'}
        
        comparison = {
            'version1': version1,
            'version2': version2,
            'metrics_comparison': {}
        }
        
        # Compare metrics
        for metric in model1['metrics']:
            if metric in model2['metrics']:
                v1_val = model1['metrics'][metric]
                v2_val = model2['metrics'][metric]
                diff = v2_val - v1_val
                comparison['metrics_comparison'][metric] = {
                    'version1': v1_val,
                    'version2': v2_val,
                    'difference': diff,
                    'improvement': diff > 0
                }
        
        return comparison
    
    def set_production(self, version: str) -> bool:
        """Set a model version as production"""
        if version not in self.registry['models']:
            print(f"✗ Version {version} not found")
            return False
        
        old_production = self.registry['production']
        
        # Update production
        self.registry['production'] = version
        self.registry['models'][version]['status'] = 'production'
        
        # Update old production
        if old_production and old_production in self.registry['models']:
            self.registry['models'][old_production]['status'] = 'archived'
        
        # Log history
        self.registry['history'].append({
            'action': 'set_production',
            'version': version,
            'previous_version': old_production,
            'timestamp': datetime.now().isoformat()
        })
        
        self._save_registry()
        
        # Create symlink
        production_link = self.models_dir / 'production'
        if production_link.exists():
            production_link.unlink()
        
        version_dir = self.models_dir / version
        if version_dir.exists():
            # On Windows, copy instead of symlink
            if production_link.exists():
                shutil.rmtree(production_link)
            shutil.copytree(version_dir, production_link)
        
        print(f"✓ Set {version} as production model")
        if old_production:
            print(f"  Previous: {old_production}")
        
        return True
    
    def rollback(self) -> bool:
        """Rollback to previous production version"""
        if not self.registry['history']:
            print("✗ No history to rollback")
            return False
        
        # Find last set_production action
        for entry in reversed(self.registry['history']):
            if entry['action'] == 'set_production' and entry.get('previous_version'):
                previous_version = entry['previous_version']
                print(f"Rolling back to {previous_version}")
                return self.set_production(previous_version)
        
        print("✗ No previous production version found")
        return False
    
    def get_production_model(self) -> Optional[Dict]:
        """Get current production model info"""
        if not self.registry['production']:
            return None
        return self.get_model(self.registry['production'])
    
    def delete_model(self, version: str) -> bool:
        """Delete a model version"""
        if version not in self.registry['models']:
            print(f"✗ Version {version} not found")
            return False
        
        if self.registry['production'] == version:
            print(f"✗ Cannot delete production model")
            return False
        
        # Delete files
        version_dir = self.models_dir / version
        if version_dir.exists():
            shutil.rmtree(version_dir)
        
        # Remove from registry
        del self.registry['models'][version]
        
        self.registry['history'].append({
            'action': 'delete',
            'version': version,
            'timestamp': datetime.now().isoformat()
        })
        
        self._save_registry()
        
        print(f"✓ Deleted model {version}")
        return True

# Example usage
if __name__ == "__main__":
    print("="*60)
    print("MODEL REGISTRY DEMO")
    print("="*60)
    
    registry = ModelRegistry()
    
    # List all models
    print("\n📋 Registered Models:")
    models = registry.list_models()
    if models:
        for model in models:
            status = "🟢" if model['status'] == 'production' else "⚪"
            print(f"  {status} {model['version']} - {model['model_type']} (AUC: {model['metrics'].get('auc', 'N/A')})")
    else:
        print("  No models registered yet")
    
    # Show production model
    print("\n🚀 Production Model:")
    prod_model = registry.get_production_model()
    if prod_model:
        print(f"  Version: {prod_model['version']}")
        print(f"  Type: {prod_model['model_type']}")
        print(f"  AUC: {prod_model['metrics'].get('auc', 'N/A')}")
    else:
        print("  No production model set")
    
    print("\n" + "="*60)
    print("MODEL REGISTRY READY")
    print("="*60)
