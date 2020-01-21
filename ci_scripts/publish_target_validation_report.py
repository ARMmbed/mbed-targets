"""Generates and publishes a validation report for all targets available to mbed-targets."""
import sys
import argparse
import dotenv
import logging
import tempfile
from target_validation_report import PlatformValidator
from utils.aws_helpers import upload_directory
from utils.logging import log_exception, set_log_level

logger = logging.getLogger(__name__)


def generate_validation_report_and_publish():
    """Calls for the creation of the validation report and uploads to final location."""
    with tempfile.TemporaryDirectory() as tmp_directory:
        platform_validator = PlatformValidator(tmp_directory, True)
        platform_validator.render_results()
        if platform_validator.processing_error:
            raise Exception("Report generation failed")
        upload_directory(tmp_directory, 'validation')


def main():
    """Handle command line arguments to generate a results summary file."""
    parser = argparse.ArgumentParser(
        description='Publish target data report to AWS.')
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Verbosity, by default errors are reported.")
    args = parser.parse_args()
    set_log_level(args.verbose)

    # Retrieve environment settings (if any) stored in a .env file
    dotenv.load_dotenv(
        dotenv.find_dotenv(usecwd=True, raise_error_if_not_found=False))
    try:
        generate_validation_report_and_publish()
    except Exception as e:
        log_exception(logger, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
