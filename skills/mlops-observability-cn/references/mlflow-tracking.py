# MLflow tracking example

import mlflow
from mlflow import MlflowClient
from pathlib import Path
import pandas as pd


def setup_tracking():
    """Setup MLflow tracking"""
    # Local tracking
    mlflow.set_tracking_uri("file:./mlruns")
    
    # Or remote server
    # mlflow.set_tracking_uri("http://localhost:5000")
    
    # Set experiment
    mlflow.set_experiment("my-experiment")


def log_training_run(config: dict, metrics: dict, model):
    """Log a complete training run"""
    with mlflow.start_run():
        # Log config
        mlflow.log_params(config)
        
        # Auto-log sklearn/pytorch/tensorflow
        mlflow.autolog()
        
        # Log custom metrics
        for name, value in metrics.items():
            mlflow.log_metric(name, value)
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        # Log dataset
        df = pd.read_csv(config['data_path'])
        dataset = mlflow.data.from_pandas(df, name="training_data")
        mlflow.log_input(dataset, context="training")
        
        # Log git commit
        import git
        repo = git.Repo()
        commit = repo.head.commit.hexsha
        mlflow.set_tag("git_commit", commit)


def register_model(model_name: str, run_id: str):
    """Register model to MLflow Model Registry"""
    client = MlflowClient()
    
    # Register
    model_uri = f"runs:/{run_id}/model"
    model_version = client.create_model_version(
        name=model_name,
        source=model_uri,
        run_id=run_id
    )
    
    # Set alias
    client.set_registered_model_alias(
        name=model_name,
        alias="production",
        version=model_version.version
    )
    
    print(f"✅ Registered {model_name} v{model_version.version}")


def load_production_model(model_name: str):
    """Load production model from registry"""
    client = MlflowClient()
    
    # Get by alias
    model_version = client.get_model_version_by_alias(
        name=model_name,
        alias="production"
    )
    
    # Load model
    model = mlflow.sklearn.load_model(
        f"models:/{model_name}/{model_version.version}"
    )
    
    return model


# Usage example
if __name__ == "__main__":
    setup_tracking()
    
    config = {
        "n_estimators": 100,
        "max_depth": 10,
        "data_path": "data/train.csv"
    }
    
    # After training
    metrics = {
        "accuracy": 0.95,
        "f1_score": 0.93
    }
    
    # log_training_run(config, metrics, trained_model)
