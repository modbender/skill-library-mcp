#!/usr/bin/env bash
set -euo pipefail

cd "$1"

git init
git config user.email "dev@interleaved.local"
git config user.name "Benchmark Developer"

# =============================================================================
# project-alpha/ — Flask API with a bug (u.full_name instead of u.name)
# =============================================================================
mkdir -p project-alpha

cat > project-alpha/app.py << 'PYEOF'
from flask import Flask, jsonify
from models import User, Order, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/users')
def list_users():
    users = User.query.all()
    # BUG: references user.full_name but the model column is user.name
    return jsonify([{"id": u.id, "name": u.full_name, "email": u.email} for u in users])

@app.route('/orders')
def list_orders():
    orders = Order.query.all()
    return jsonify([{"id": o.id, "product": o.product, "amount": o.amount} for o in orders])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
PYEOF

cat > project-alpha/models.py << 'PYEOF'
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Note: column is "name", not "full_name"
    email = db.Column(db.String(120), unique=True, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
PYEOF

cat > project-alpha/test_app.py << 'PYEOF'
import unittest
import sys
import os
import re

# Static tests — no Flask/SQLAlchemy import needed.
# We parse the source files directly to check for the bug.

class TestUserModel(unittest.TestCase):
    def _read(self, filename):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(path) as f:
            return f.read()

    def test_model_defines_name_column(self):
        """The User model in models.py should define a 'name' column."""
        content = self._read('models.py')
        self.assertRegex(content, r'name\s*=\s*db\.Column',
                         "models.py does not define a 'name' column on User")

    def test_model_does_not_define_full_name_column(self):
        """The User model should NOT define a 'full_name' column — only 'name'."""
        content = self._read('models.py')
        # Check that no column named full_name is defined
        self.assertNotRegex(content, r'full_name\s*=\s*db\.Column',
                            "models.py defines a 'full_name' column but should not")

    def test_users_endpoint_uses_correct_attribute(self):
        """app.py references u.full_name but model has u.name — this should be fixed."""
        content = self._read('app.py')
        # After fix, app.py should use u.name, not u.full_name
        self.assertNotIn('u.full_name', content,
                         "app.py still uses u.full_name instead of u.name")

if __name__ == '__main__':
    unittest.main()
PYEOF

cat > project-alpha/requirements.txt << 'PYEOF'
flask
flask-sqlalchemy
PYEOF

# =============================================================================
# project-beta/ — Data pipeline with config
# =============================================================================
mkdir -p project-beta

cat > project-beta/pipeline.py << 'PYEOF'
import yaml

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def run_pipeline():
    config = load_config()
    db_host = config['database_host']
    db_port = config['database_port']
    print(f"Connecting to {db_host}:{db_port}")
    print("Running data pipeline...")
    print("Pipeline complete.")

if __name__ == '__main__':
    run_pipeline()
PYEOF

cat > project-beta/config.yaml << 'PYEOF'
database_host: db-legacy.internal
database_port: 5432
database_name: analytics
batch_size: 1000
output_format: parquet
PYEOF

cat > project-beta/README.md << 'PYEOF'
# Data Pipeline

Processes analytics data from the database.

## Configuration
Edit `config.yaml` to set database connection details.
PYEOF

# =============================================================================
# Commit everything
# =============================================================================
git add -A
git commit -m "Initial commit: add project-alpha and project-beta"
