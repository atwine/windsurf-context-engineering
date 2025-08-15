"""
Entry point for the ML Heart Prediction example.
This is a minimal scaffold to confirm the example directory is wired.
Full pipeline steps will be implemented after approval to execute the /tripod-ml-pipeline workflow.
"""

from pathlib import Path
from typing import NoReturn

from config import Settings


def main() -> NoReturn:
    settings = Settings()
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[ML Heart Prediction] Scaffold ready.")
    print(f"Output directory: {output_dir.resolve()}")
    print("Next step: Await explicit approval to run /tripod-ml-pipeline.")


if __name__ == "__main__":
    main()
