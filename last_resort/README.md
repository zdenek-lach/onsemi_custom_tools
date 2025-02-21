# Last Resort Application

The Last Resort application is an internal tool designed for RDP engineers to perform a final check before sending data to the vendor. It ensures that there are no typos, missing, or incorrect information in the data. This application provides a graphical user interface (GUI) for easy interaction and verification of project directories and files.

## Usage

To run the Last Resort application, use the following command:

```bash
python last_resort.py [OPTIONS]
Options
-s, --silent : Enable silent mode (suppress output).
-d, --debug : Enable debug mode (detailed output for troubleshooting).
-v, --verbose : Enable verbose mode (more detailed output).
-t, --test : Run the application in test mode.
-i, --info : Show the help message and exit.
-c, --config : Path to a custom configuration file.
Examples
Run the application normally:

python last_resort.py
Run the application in test mode:

python last_resort.py --test
Enable verbose output:

python last_resort.py --verbose
Enable debug mode for troubleshooting:

python last_resort.py --debug
Show the help message:

python last_resort.py --info
Run the application with a custom configuration file:

python last_resort.py --config /path/to/config.yaml
```

## Configuration

The application supports a custom configuration file that can be specified using the -c or --config option. The configuration file should be in YAML format and can include the following settings:

```yaml
final_mask_pattern: 'secret' # anonymized
mask_name_pattern: 'secret' # anonymized
mask_name_pattern_secret: 'secret' # anonymized
revision_pattern: 'secret' # anonymized
revision_pattern_secret: 'secret' # anonymized
dataprep_pattern: 'secret' # anonymized
editor_of_choice: 'built_in' # anonymized
run_archive_path: 'secret/run_archive' # anonymized
```

## How It Works

The Last Resort application performs the following steps:

- Parses command-line arguments.
- Initializes the Tkinter root window.
- Prints an introductory message.
- Generates a unique identifier (RUID).
- Identifies all folders around the launch directory.
- Initializes the main window of the user interface.
- Initializes the folder structure.
- Finds all .jb and .po files in the revision directory.
- Depending on the 'test' argument:
- If 'test' is True, loads the first .po file into the checklist.
- If 'test' is False, prompts the user to select .jb and .po files, loads the selected .po file into the checklist, and opens both selected files for preview.

## Why Use Last Resort?

The Last Resort application is designed to streamline the final verification process for RDP engineers, ensuring that all necessary checks are performed before data is sent to the vendor. By providing a user-friendly interface and automating many of the verification steps, it helps reduce errors and improve efficiency.

## Contact

For more information or if you encounter any issues, please contact Zdenek Lach.
