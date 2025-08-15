"""
Minimal configuration for the ML Heart Prediction example.
Extended configuration (seeds, CV params, grids) will be added upon
approval to execute the /tripod-ml-pipeline workflow.
"""
from dataclasses import dataclass


@dataclass
class Settings:
    # Directory where artifacts will be stored
    output_dir: str = "examples/ml_heart_prediction/output"
