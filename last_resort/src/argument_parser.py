import argparse

# Global variable to store the arguments
arguments = None


def _initialize_():
    """
    Initialize the argument parser and parse command-line arguments.

    This function sets up the argument parser with the following options:
    - -d, --debug: Enable debug mode (detailed output for troubleshooting).
    - -v, --verbose: Enable verbose mode (more detailed output).
    - -t, --test: Run the application in test mode.
    - -i, --info: Show this help message and exit.
    - -c, --config: Accepts a path to a custom configuration file.
    - -dc, --define_config: Allows the user to alter the currently used configuration.
    The parsed arguments are stored in the global 'arguments' variable.
    """
    global arguments
    if arguments is None:
        parser = argparse.ArgumentParser(
            prog="The Last Resort",
            description="Program allows the RDP engineer to perform "
            "a last check before sending data to the vendor and revealing any possible typos, "
            "missing or incorrect information.",
            epilog="If you find any problems with the app, contact Zdenek Lach",
        )

        parser.add_argument(
            "-s",
            "--silent",
            action="store_true",
            help="Enable silent mode (suppress output).",
        )
        parser.add_argument(
            "-d",
            "--debug",
            action="store_true",
            help="Enable debug mode " "(detailed output for troubleshooting).",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enable verbose mode (more detailed output).",
        )
        parser.add_argument(
            "-t",
            "--test",
            action="store_true",
            help="Run the application in test mode.",
        )
        parser.add_argument(
            "-i", "--info", action="store_true", help="Show this help message and exit."
        )
        parser.add_argument(
            "-c",
            "--config",
            type=str,
            help=" CONFIG = Path to provide a custom configuration file.",
        )
        parser.add_argument(
            "-dc",
            "--define_config",
            action="store_true",
            help="Open a window to define a new temporary configuration for this session.",
        )
        arguments = parser.parse_args()


def get():
    """
    Retrieve the parsed command-line arguments.

    If the arguments have not been parsed yet, this function initializes the parser
    and parses the arguments. It then returns the parsed arguments.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    global arguments

    if arguments is None:
        _initialize_()
    if arguments is not None:
        return arguments
