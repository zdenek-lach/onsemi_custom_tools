import sys

import yaml
import os
import argument_parser

# Global variable to store the configuration
full_configuration = None


def _find_config_file_(filename="last_resort_default_config.yaml"):
    """
    Search for the configuration file in the specified directory and its subdirectories.

    Args:
        filename (str): The name of the configuration file to search for. Defaults to 'default_config.yaml'.

    Returns:
        str: The path to the configuration file if found, otherwise None.
    """
    # Get the parsed arguments
    arguments = argument_parser.get()

    # Use the provided config file path if available
    if arguments.config:
        config_path = arguments.config
    else:
        # Get the absolute path of the script
        script_path = os.path.abspath(sys.argv[0])

        # Get the directory name of the script
        script_dir = os.path.dirname(script_path)

        # Go one directory up
        parent_dir = os.path.dirname(script_dir)

        # Path to the default_config.yaml
        config_path = os.path.join(parent_dir, filename)
    if filename != "default_config.yaml":
        print("INFO        Using config file: " + config_path)  # anonymized
    return config_path


def initialize():
    """
    Initialize and load the configuration file into memory.

    This function searches for the configuration file named 'default_config.yaml' in the current directory
    and its subdirectories. If the file is found, it loads the configuration into the global variable
    'full_configuration'. If the file is not found, it raises a FileNotFoundError.

    Raises:
        FileNotFoundError: If the configuration file is not found.
    """
    global full_configuration
    if full_configuration is None:
        config_path = _find_config_file_()
        if config_path:
            with open(config_path, "r") as file:
                full_configuration = yaml.safe_load(file)
        else:
            raise FileNotFoundError("Configuration file not found.")


def get(key):
    """
    Retrieve a value from the configuration.

    This function ensures that the configuration is initialized and then retrieves the value
    associated with the specified key from the configuration.

    Args:
        key (str): The key to look up in the configuration.

    Returns:
        The value associated with the specified key in the configuration.

    Raises:
        ValueError: If the key is not found in the configuration.
        FileNotFoundError: If the configuration file is not found.
    """
    global full_configuration

    if full_configuration is None:
        initialize()
    if full_configuration is not None:
        if key in full_configuration:
            return full_configuration.get(key)
        else:
            raise ValueError("Key '" + key + "' not found in the configuration file.")
    else:
        raise FileNotFoundError("Configuration file not found.")
