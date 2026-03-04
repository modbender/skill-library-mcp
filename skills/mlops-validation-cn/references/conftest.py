# Shared pytest fixtures
# Copy to tests/conftest.py

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile


@pytest.fixture
def sample_df():
    """Sample dataframe for testing"""
    np.random.seed(42)
    return pd.DataFrame({
        'feature_1': np.random.randn(100),
        'feature_2': np.random.randn(100),
        'target': np.random.randint(0, 2, 100)
    })


@pytest.fixture
def temp_dir():
    """Temporary directory for file tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Sample configuration dict"""
    return {
        'batch_size': 32,
        'learning_rate': 0.001,
        'random_state': 42,
        'n_estimators': 100,
    }


@pytest.fixture
def train_test_split(sample_df):
    """Pre-split data for testing"""
    from sklearn.model_selection import train_test_split
    X = sample_df[['feature_1', 'feature_2']]
    y = sample_df['target']
    return train_test_split(X, y, test_size=0.2, random_state=42)
