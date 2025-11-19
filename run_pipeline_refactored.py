#!/usr/bin/env python
"""
TALOS Studio Main Pipeline - Refactored Version

Orchestrates the complete animation generation pipeline:
1. 3D Reconstruction (TripoSR)
2. 2D Rendering (Blender)
3. Result Packaging (HTML comparison)
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.error_handler import PipelineError, setup_error_logging
from src.pipeline_executor import PipelineExecutor


def main():
    """Main entry point for pipeline execution."""
    # Setup logging
    logger = setup_error_logging("pipeline.log")
    logger = logging.getLogger("talos_studio")

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="TALOS Studio - AI Animation Generation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline_refactored.py --config config.yml --input_image input/image.png
  python run_pipeline_refactored.py --input_image image.png --output_dir ./results
        """
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yml",
        help="Path to configuration file (default: config.yml)"
    )

    parser.add_argument(
        "--input_image",
        type=str,
        required=True,
        help="Path to input image file"
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="Optional override for output directory"
    )

    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Set log level
    logging.getLogger("talos_studio").setLevel(getattr(logging, args.log_level))

    try:
        logger.info("=" * 70)
        logger.info("TALOS STUDIO - ANIMATION GENERATION PIPELINE")
        logger.info("=" * 70)

        # Initialize executor
        executor = PipelineExecutor(config_path=args.config)

        # Execute pipeline
        output_path = executor.execute(
            input_image=args.input_image,
            output_dir=args.output_dir
        )

        logger.info(f"\n✓ Pipeline completed successfully!")
        logger.info(f"Results saved to: {output_path}\n")

        return 0

    except PipelineError as e:
        e.log_and_exit(logger)
        return e.exit_code

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Pipeline interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
