#!/bin/bash
# Generate src package structure

set -e

PACKAGE_NAME="${1:-my_package}"
PACKAGE_DIR="${PACKAGE_NAME//-/_}"

echo "🏗️  Creating package structure: $PACKAGE_NAME"

# Create directories
mkdir -p "src/$PACKAGE_DIR"/{io,domain,application}
mkdir -p tests

# Create __init__.py files
touch "src/$PACKAGE_DIR/__init__.py"
touch "src/$PACKAGE_DIR/io/__init__.py"
touch "src/$PACKAGE_DIR/domain/__init__.py"
touch "src/$PACKAGE_DIR/application/__init__.py"
touch "tests/__init__.py"

# Create sample module
cat > "src/$PACKAGE_DIR/domain/features.py" << 'EOF'
"""Feature engineering - Pure functions only"""

from typing import Any
import pandas as pd


def transform_features(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Transform raw features into ML features.
    
    Args:
        df: Raw input dataframe
        config: Feature configuration
        
    Returns:
        Transformed dataframe
    """
    # Add feature transformations here
    return df
EOF

# Create sample I/O module
cat > "src/$PACKAGE_DIR/io/data.py" << 'EOF'
"""Data I/O operations"""

from pathlib import Path
import pandas as pd


def load_data(path: Path) -> pd.DataFrame:
    """Load data from disk.
    
    Args:
        path: Path to data file
        
    Returns:
        Loaded dataframe
    """
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def save_data(df: pd.DataFrame, path: Path) -> None:
    """Save data to disk.
    
    Args:
        df: Dataframe to save
        path: Output path
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
EOF

# Create sample application module
cat > "src/$PACKAGE_DIR/application/train.py" << 'EOF'
"""Training orchestration"""

from pathlib import Path
import pandas as pd
from pydantic import BaseModel

from ..io.data import load_data, save_data
from ..domain.features import transform_features


class TrainingConfig(BaseModel):
    """Training configuration"""
    data_path: Path
    output_path: Path
    random_state: int = 42


def train(config: TrainingConfig) -> None:
    """Run training pipeline.
    
    Args:
        config: Training configuration
    """
    # Load
    df = load_data(config.data_path)
    
    # Transform
    df = transform_features(df, config.model_dump())
    
    # Train (add your model here)
    
    # Save
    save_data(df, config.output_path)
EOF

echo "✅ Package structure created!"
echo ""
echo "Next steps:"
echo "  - Edit src/$PACKAGE_DIR/domain/features.py"
echo "  - Add your model logic"
echo "  - Register CLI in pyproject.toml"
