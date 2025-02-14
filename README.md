# Publicable Code Project

This project contains a collection of tools designed to assist RDP engineers in various tasks. Each tool has been anonymized to protect confidential information.

## Tools

### Last Resort

The Last Resort application is an internal tool designed for RDP engineers to perform a final check before sending data to the vendor. It ensures that there are no typos, missing, or incorrect information in the data. This application provides a graphical user interface (GUI) for easy interaction and verification of project directories and files.

#### Usage

```sh
python last_resort.py [OPTIONS]
```

Options:

- `-s, --silent`: Enable silent mode (suppress output).
- `-d, --debug`: Enable debug mode (detailed output for troubleshooting).
- `-v, --verbose`: Enable verbose mode (more detailed output).
- `-t, --test`: Run the application in test mode.
- `-i, --info`: Show the help message and exit.
- `-c, --config`: Path to a custom configuration file.

Examples:

Run the application normally:

```sh
python last_resort.py
```

Run the application in test mode:

```sh
python last_resort.py --test
```

Enable verbose output:

```sh
python last_resort.py --verbose
```

Enable debug mode for troubleshooting:

```sh
python last_resort.py --debug
```

Show the help message:

```sh
python last_resort.py --info
```

Run the application with a custom configuration file:

```sh
python last_resort.py --config /path/to/config.yaml
```

#### Configuration

The application supports a custom configuration file that can be specified using the `-c` or `--config` option. The configuration file should be in YAML format and can include the following settings:

```yaml
final_mask_pattern: 'secret' # anonymized
mask_name_pattern: 'secret' # anonymized
mask_name_pattern_efk: 'secret' # anonymized
revision_pattern: 'secret' # anonymized
revision_pattern_efk: 'secret' # anonymized
dataprep_pattern: 'secret' # anonymized
editor_of_choice: 'built_in' # anonymized
run_archive_path: 'secret/run_archive' # anonymized
```

#### How It Works

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

### Alias Util

The Alias Util script helps manage shell aliases efficiently. It allows users to list, add, modify, and delete aliases, as well as restore backups.

#### Usage

Run the script and follow the prompts to manage your aliases.

### Send Email V2

The Send Email V2 script automates the process of sending emails with attachments. It constructs the email body using provided information and sends the email to the specified recipients.

#### Usage

Run the script and provide the necessary arguments to send an email.

### File Presenter

The File Presenter script helps present files in a structured manner. It can be used to display file contents and organize files for review.

#### Usage

Run the script and provide the necessary arguments to present files.

### PO Parser

The PO Parser script parses purchase order (PO) files and extracts relevant information. It prints the parsed information in a nicely formatted way.

#### Usage

```sh
python po_parser.py <path_to_po_file>
```

### Mebes Converter

The Mebes Converter script converts MEBES1 files to MEBES3 format using CATS. It handles the conversion process and moves old files to an `original_files` directory.

#### Usage

```sh
python mebes_converter.py [OPTION]
```

Options:

- `-run`: Start the conversion.
- `-help, -h, --help, --h`: Display the help message.

### Daps Trans Updater

The Daps Trans Updater script updates DAPS transactions. It automates the process of updating transaction files.

#### Usage

Run the script to update DAPS transactions.

### Quick-reload Terminal

The Quick-reload Terminal script reloads the terminal to apply changes made to aliases or other configurations.

#### Usage

Run the script to reload the terminal.

## Contact

For more information or if you encounter any issues, please contact Zdenek Lach.
