# Scripts -- ml-feature-engineering

Bundled utility scripts for the consolidated ML Feature Engineering skill.

## Pipeline Automation (from automl-pipeline-builder-2)

- **data_validation.py** -- Validate input data quality before pipeline execution.
- **model_evaluation.py** -- Evaluate trained model performance and generate reports.
- **pipeline_deployment.py** -- Deploy a trained pipeline with rollback support.

## Feature Engineering (from machine-learning-feature-engineering-toolkit)

- **feature_engineering_pipeline.py** -- End-to-end feature engineering process.
- **feature_importance_analyzer.py** -- Analyse feature importance (permutation, SHAP, tree-based).
- **data_visualizer.py** -- Visualise feature distributions and target relationships.
- **feature_store_integration.py** -- Integrate with feature stores (Feast, Tecton).

## Usage

All scripts accept `--help` for argument documentation:

```bash
python scripts/data_validation.py --help
python scripts/feature_importance_analyzer.py --help
```
