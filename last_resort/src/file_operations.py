import datetime
import os
import re
import shutil
import sys
import uuid

from fpdf import FPDF

import utils
import config_parser
from tkinter import messagebox
import user_interface as ui

global forms_dir
global final_mask_dir, dataprep_dir, revision_dir, mask_name_dir
global ruid, run_report_file


def match_folder(folder_name, patterns):
    """
    Check if a folder name matches any pattern in a given set.

    This function iterates over a dictionary of patterns and checks if the folder name
    matches any of the regex patterns. If a match is found, it logs the match and returns
    the name of the matched pattern.

    Args:
        folder_name (str): The name of the folder to check.
        patterns (dict): A dictionary where keys are pattern names and values are regex patterns.

    Returns:
        str: The name of the matched pattern, or None if no match is found.
    """
    for name, pattern in patterns.items():
        if re.match(pattern, folder_name):
            utils.debug(
                message=f"Matched startup folder to {folder_name} with pattern {pattern}"
            )
            return name
    return None


def navigate_directory(path, levels, pattern=None):
    """
    Traverse directories up or down a specified number of levels.

    This function navigates through directories starting from a given path. It can move
    up or down a specified number of levels and optionally match subdirectories against
    a regex pattern.

    Args:
        path (str): The starting directory path.
        levels (int): Number of levels to move. Positive for descending, negative for ascending.
        pattern (re.Pattern, optional): Regex pattern to filter subdirectories. Defaults to None.

    Returns:
        str: The resulting directory path after navigation.

    Raises:
        FileNotFoundError: If no matching subdirectory is found.
    """
    if levels == 0:
        return path

    if levels < 0:
        for _ in range(levels):
            path = os.path.dirname(path)
    if levels > 0:
        for _ in range(abs(levels)):
            subdirectories = [
                d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))
            ]
            if pattern:
                subdirectories = [d for d in subdirectories if pattern.match(d)]
            if not subdirectories:
                raise FileNotFoundError(f"No matching subdirectory found in: {path}")
            path = os.path.join(path, subdirectories[0])

    return path


def identify_folders(root):
    """
    Determine and set paths for various project directories.

    This function identifies the current working directory and matches it against
    predefined patterns to set paths for mask_name, revision, dataprep, and final_mask
    directories. It handles different launch scenarios based on the recognized directory.

    Args:
        root (tk.Tk): The root window of the Tkinter application.

    Returns:
        dict: A dictionary with paths for mask_name, revision, dataprep, and final_mask directories.

    Raises:
        ValueError: If the current directory does not match any expected patterns.
    """
    global final_mask_dir, dataprep_dir, revision_dir, mask_name_dir
    current_directory = os.getcwd()

    mask_name_pattern = re.compile(
        config_parser.get(
            "mask_name_pattern_secret"  # anonymized
            if os.getenv("RDPSITE") == "secret"  # anonymized
            else "mask_name_pattern"  # anonymized
        )
    )
    revision_pattern = re.compile(
        config_parser.get(
            "revision_pattern_secret"  # anonymized
            if os.getenv("RDPSITE") == "secret"  # anonymized
            else "revision_pattern"  # anonymized
        )
    )
    final_mask_pattern = re.compile(config_parser.get("final_mask_pattern"))  # anonymized
    dataprep_pattern = re.compile(config_parser.get("dataprep_pattern"))  # anonymized
    patterns = {
        "mask_name_dir": mask_name_pattern,
        "revision_dir": revision_pattern,
        "dataprep_dir": dataprep_pattern,
        "final_mask_dir": final_mask_pattern,
    }

    current_folder_name = os.path.basename(current_directory)
    try:
        recognized = match_folder(current_folder_name, patterns)
        if not recognized:
            raise ValueError("Current directory doesn't match any expected patterns.")
    except ValueError:
        utils.printer(
            message="Current directory doesn't match any expected patterns.",
            log_type=utils.Type.ERROR,
        )
        utils.startup_dir_check()
        exit(-1)

    if recognized == "mask_name_dir":
        utils.debug(message="Recognized launch in the 'Mask Name' folder")
        mask_name_dir = current_folder_name
        revision_dir = navigate_directory(current_directory, 1, revision_pattern)

        revision_options = [
            directory
            for directory in os.listdir(os.path.dirname(revision_dir))
            if os.path.isdir(os.path.join(os.path.dirname(revision_dir), directory))
            and revision_pattern.match(directory)
        ]

        revision_dir = ui.prompt_selection(
            root, revision_options, "Please select revision"
        )
        dataprep_dir = navigate_directory(revision_dir, 1, dataprep_pattern)
        try:
            final_mask_dir = navigate_directory(dataprep_dir, 1, final_mask_pattern)
        except FileNotFoundError:
            utils.printer(
                message="Final mask folder not found!", log_type=utils.Type.WARNING
            )
            utils.printer(
                message="Attempting to use secret instead of the final folder!",
                log_type=utils.Type.WARNING,
            )
            final_mask_dir = os.path.join(dataprep_dir + "/secret")

    elif recognized == "revision_dir":
        utils.debug(message="Recognized launch in 'revision' folder.")
        revision_dir = current_directory
        mask_name_dir = os.path.dirname(current_directory)
        dataprep_dir = navigate_directory(current_directory, 1, dataprep_pattern)
        try:
            final_mask_dir = navigate_directory(dataprep_dir, 1, final_mask_pattern)
        except FileNotFoundError:
            final_mask_dir = os.path.join(dataprep_dir + "/secret")

    elif recognized == "dataprep_dir":
        utils.debug(message="Recognized launch in the 'dataprep' folder.")
        dataprep_dir = current_directory
        revision_dir = os.path.dirname(current_directory)
        mask_name_dir = os.path.dirname(os.path.dirname(current_directory))
        try:
            final_mask_dir = navigate_directory(
                current_directory, 1, final_mask_pattern
            )
        except FileNotFoundError:
            final_mask_dir = os.path.join(dataprep_dir + "/secret")
    elif recognized == "final_mask_dir":
        utils.debug(message="Recognized launch in the 'Final mask folder'.")
        final_mask_dir = current_directory
        dataprep_dir = os.path.dirname(current_directory)
        revision_dir = os.path.dirname(dataprep_dir)
        mask_name_dir = os.path.dirname(os.path.dirname(dataprep_dir))

    handle_multiple_final_mask_folders(root)

    return {
        "mask_name": mask_name_dir,
        "revision": revision_dir,
        "dataprep": dataprep_dir,
        "final_mask": final_mask_dir,
    }


def handle_multiple_final_mask_folders(root):
    """
    Manage multiple final mask folders by prompting the user to select one.

    This function retrieves the pattern from the configuration, finds folders matching
    the pattern in the dataprep directory, filters them, and prompts the user to select
    one if multiple matches are found.

    Args:
        root (tk.Tk): The root window of the Tkinter application.
    """
    # Retrieve the pattern from the configuration
    global final_mask_dir
    pattern = config_parser.get("final_mask_pattern")
    regex = re.compile(pattern)

    # Find folders matching the pattern in the dataprep_dir
    name_matching_folders = find_folders(directory=dataprep_dir)

    # Filter folders that match the regex pattern
    regex_matching_folders = [
        folder for folder in name_matching_folders if regex.search(folder)
    ]

    # Check if there is more than one matching folder
    if len(regex_matching_folders) > 1:
        selected_folder = ui.prompt_selection(
            root=root,
            options=regex_matching_folders,
            title="Please select which final folder to use:",
            is_folder_list=True,
        )
        utils.printer(
            message=f"Prompt selection: {selected_folder}", log_type=utils.Type.INFO
        )
        final_mask_dir = selected_folder


def init_folder_structure(root):
    """
    Set up the folder structure by identifying project directories.

    This function initializes the folder structure by calling identify_folders and
    logging the identified directories.

    Args:
        root (tk.Tk): The root window of the Tkinter application.

    Returns:
        list: A list of identified directory paths.
    """
    utils.startup_dir_check()
    dir_logger = identify_folders(root)
    utils.verbose(message=f"Mask Name: {dir_logger['mask_name']}")
    utils.verbose(message=f"Revision: {dir_logger['revision']}")
    utils.verbose(message=f"Dataprep: {dir_logger['dataprep']}")
    utils.verbose(message=f"Final Mask: {dir_logger['final_mask']}")

    return list(dir_logger.values())


def find_folders(directory):
    """
    Locate all folders within a specified directory.

    This function walks through the directory tree and collects all folder paths.

    Args:
        directory (str): The directory to search for folders.

    Returns:
        list: A list of folder paths.
    """
    folders = []
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            folders.append(os.path.join(root, dir_name))
    return folders


def find_files(base_name=None, extension=None, directory=None):
    """
    Search for files in a directory that match a specific base name and/or extension.

    This function walks through the directory tree starting from the specified directory
    and collects files that match the given base name and/or extension.

    Args:
        base_name (str, optional): The base name of the files to find. Defaults to None.
        extension (str, optional): The file extension to find. Defaults to None.
        directory (str, optional): The directory to search in. Defaults to the current working directory.

    Returns:
        list: A list of matching file paths.
    """
    if directory is None:
        directory = os.getcwd()

    matching_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if base_name and extension:
                pattern = re.compile(rf"{base_name}_v(\d+){extension}")
                if pattern.match(file):
                    utils.debug(
                        f"Found file: {file} with extension: {extension} in [{base_name}]"
                    )
                    matching_files.append(os.path.join(root, file))
            elif extension:
                if file.endswith(extension):
                    utils.debug(f"Found file: {file} with extension: {extension}")
                    matching_files.append(os.path.join(root, file))
            else:
                utils.debug(
                    f"matching_files.append(os.path.join(root: {root}, file: {file}))"
                )
                matching_files.append(os.path.join(root, file))

    return matching_files


def generate_ruid():
    """
    Create a unique run identifier (RUID) and generate a run report file.

    This function generates a unique RUID, creates a run report file in the run_archive directory,
    and writes the RUID to the file.

    Returns:
        str: The generated RUID.

    Raises:
        OSError: If the run report file cannot be written.
    """
    global ruid, run_report_file
    # Generate a unique run identifier
    utils.debug(message="Generating RUID...")
    ruid = str(uuid.uuid4())
    utils.debug(message="Generated RUID: " + ruid)

    # Get the run archive path from the config
    config_archive_dir = os.path.join(config_parser.get("run_archive_path"))  # anonymized
    run_archive_dir = config_archive_dir

    # If run_archive_path is not defined in the config, use the app project folder
    if not run_archive_dir:
        run_archive_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))),
            "run_archive",
        )

    # Create the run_archive directory if it doesn't exist
    os.makedirs(run_archive_dir, exist_ok=True)
    utils.debug(message="Checking if run_archive exists? -> " + run_archive_dir)
    # Create a filename based on the current date
    date_str = datetime.datetime.now().strftime("%d%m%y-%H%M%S")
    filename = f"run_{date_str}.lr"
    run_report_file = os.path.join(run_archive_dir, filename)
    utils.verbose(message="Writing Run Report to " + filename)
    try:
        # Save the RUID to the file
        with open(run_report_file, "w") as file:
            file.write(f"RUID: {ruid}\n")
        utils.debug(message="Run report successfully written.")
    except OSError:
        raise OSError("Failed to write RUN REPORT file.")

    return ruid


def write_history(message):
    """
    Append a message to the run report file with a timestamp.

    This function writes a given message to the run report file, prefixed with the current timestamp.

    Args:
        message (str): The message to append to the run report file.

    Returns:
        None
    """
    global run_report_file
    if not run_report_file:
        utils.debug(message="Run report file not set. Cannot write history.")
        return

    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append the message to the run report file
    if not ui.we_done:
        try:
            with open(run_report_file, "a") as file:
                file.write(f"{timestamp} - {message}\n")
        except OSError as e:
            utils.debug(f"Failed to write to run report file: {e}")


def convert_lr_to_pdf(file_in_lr_format):
    """
    Transform a .lr file into a .pdf file.

    This function converts a specified .lr file to a .pdf file by invoking the txt_to_pdf function.
    It logs the conversion process for debugging purposes.

    Args:
        file_in_lr_format (str): The path to the .lr file to be converted.

    Returns:
        bool: True if the conversion is successful, False otherwise.
    """
    utils.debug(
        f"Converting {file_in_lr_format} to {file_in_lr_format.replace('.lr', '.pdf')}",
        log=True,
    )
    return txt_to_pdf(file_in_lr_format, file_in_lr_format.replace(".lr", ".pdf"))


def save_checklist_to_file():
    """
    Save checklist items to a file in the 'docs' directory.

    This function creates the docs directory if it doesn't exist, generates a new filename,
    and writes the checklist items to the file.

    Returns:
        str: The path to the saved checklist file, or None if an error occurs.
    """
    docs_directory = "/".join(dataprep_dir.split("/")[:-1]) + "/docs"

    if not os.path.exists(docs_directory):
        utils.debug(
            "save_checklist(): Docs directory not found, please investigate why this happened."
        )
        try:
            os.makedirs(docs_directory, exist_ok=True)
            utils.verbose(message=f"Created directory: {docs_directory}")
        except PermissionError:
            messagebox.showerror("Error", f"Permission denied: {docs_directory}")
            utils.debug(
                "save_checklist(): Error encountered when trying to create docs folder here: "
                + docs_directory
            )
            return
    elif not os.access(docs_directory, os.W_OK):
        messagebox.showerror(
            "Error", f"No write permission for docs directory: {docs_directory}"
        )
        return

    save_path = generate_checklist_filename("LR_Checklist", ".lrc", docs_directory)
    utils.debug(message=f"Writing temporary checklist file: {save_path}")

    # Additional debugging to check permissions
    if not os.access(docs_directory, os.W_OK):
        utils.debug(f"Write permission denied for directory: {docs_directory}")
        messagebox.showerror(
            "Error", f"No write permission for docs directory: {docs_directory}"
        )
        return

    checklist_items = ui.checklist_items
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    first_name, last_name, username = utils.get_full_name()
    app_version = utils.get_release_version()
    try:
        utils.debug(message="Attempting to write a checklist file: ", log=True)
        with open(save_path, "w") as file:
            file.write(
                f"Created on: {timestamp} by {first_name} {last_name} ({username})."
                f"\nLast Resort version: {app_version}\n\n"
            )
            utils.debug(
                message=f"Created on: {timestamp} by {first_name} {last_name} ({username}).",
                log=True,
            )
            utils.debug(message=f"\nLast Resort version: {app_version}\n", log=True)

            for i, item in enumerate(checklist_items):
                file.write(
                    f"{item}: {'Checked' if ui.chl_vars[i].get() else 'Unchecked'}\n"
                )
                utils.debug(
                    message=f"{item}: {'Checked' if ui.chl_vars[i].get() else 'Unchecked'}"
                )
    except PermissionError as e:
        utils.debug(f"PermissionError: {e}")
        messagebox.showerror("Error", f"Permission denied: {save_path}")
        return

    return save_path


def save_checklist_to_pdf():
    """
    Save checklist items to a PDF file.

    This function saves the checklist items to a temporary file, converts it to a PDF,
    and sets the PDF file to read-only.

    Returns:
        str: The path to the saved PDF file, or None if an error occurs.
    """
    lrc_file = save_checklist_to_file()
    pdf_filename = txt_to_pdf(lrc_file, lrc_file.replace(".lrc", ".pdf"))

    # Check if the PDF file was created
    if not os.path.exists(pdf_filename):
        utils.verbose(message=f"PDF file not found: {pdf_filename}")
        # os.remove(lrc_file)
        return None

    # Remove the temporary .po file
    os.remove(lrc_file)

    utils.verbose(message=f"Generated PDF: {pdf_filename} and set to read-only")

    messagebox.showinfo(
        "Success", f"File saved successfully at {os.path.abspath(pdf_filename)}"
    )
    utils.printer(message="Checklist successfully saved.", log_type=utils.Type.INFO)

    # Set the generated PDF to read-only
    os.chmod(pdf_filename, 0o444)
    utils.debug(f"Set file to read-only (0o444): {pdf_filename}")

    return pdf_filename


def generate_checklist_filename(base_name, extension, checklist_dir=None):
    """
    Generate a new filename with an incremented version number.

    This function checks for existing files with the same base name and extension,
    increments the version number, and generates a new filename.

    Args:
        base_name (str): The base name of the file.
        extension (str): The file extension.
        checklist_dir (str, optional): The directory to search for existing files. Defaults to None.

    Returns:
        str: The generated filename with the incremented version number.
    """
    version = 1
    pattern = re.compile(rf"{base_name}_v(\d+){extension}")

    if checklist_dir:
        utils.debug(message="Directory for storing checklists: " + checklist_dir)
        existing_files = find_files(base_name, extension, checklist_dir)
        utils.debug(
            message=f"Found {len(existing_files)} previous checklist versions: {str(existing_files)}"
        )
        last_version = 0
        for file in existing_files:
            match = pattern.search(file)
            if match:
                file_version = int(match.group(1))
                if file_version >= last_version:
                    last_version = file_version
        version = last_version + 1
        utils.debug(message="Checklist version number to use: " + str(version))
    new_filename = f"{base_name}_v{version}{extension}"
    full_path = (
        os.path.join(checklist_dir, new_filename) if checklist_dir else new_filename
    )
    utils.verbose(message=f"Generated new filename: {full_path}")
    return full_path


class PDF(FPDF):
    def footer(self):
        """
        Add a footer to the PDF with the RUID.

        This method sets the footer to 1.5 cm from the bottom, selects Arial italic font,
        and prints the RUID centered at the bottom of the page.
        """
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        # Select Arial italic 8
        self.set_font("Arial", "I", 8)
        # Print centered RUID
        self.cell(0, 10, f"RUID: {ruid}", 0, 0, "C")


def txt_to_pdf(txt_file, pdf_file):
    """
    Convert a text file to a PDF file.

    This function reads the content of a text file, writes it to a PDF file,
    and handles any permission errors by generating a new filename.

    Args:
        txt_file (str): The path to the text file.
        pdf_file (str): The path for the PDF file to be created at.

    Returns:
        str: The path to the created PDF file.
    """
    global ruid
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    with open(txt_file, "r", encoding="utf-8") as file:
        for line in file:
            # Split long lines into multiple lines that fit within the page width
            pdf.multi_cell(0, 15, line)

    try:
        pdf.output(pdf_file)
        utils.verbose(message=f"PDF generated: {pdf_file}")
    except PermissionError as e:
        utils.debug(message=f"PermissionError: {e}")
        # Extract base name and extension correctly
        base_name, extension = os.path.splitext(os.path.basename(pdf_file))
        base_name = base_name.rsplit("_v", 1)[0]  # Remove any existing version suffix
        # Generate a new filename with incremented version
        pdf_file = generate_checklist_filename(
            base_name, extension, os.path.dirname(pdf_file)
        )
        pdf.output(pdf_file)
    return pdf_file


def lock_run_report(pdf_mode=True):
    """
    Set the run report file to read-only.

    This function changes the permissions of the run report file to read-only (0o444).
    If pdf_mode is True, it converts the run report to a PDF before setting it to read-only.

    Args:
        pdf_mode (bool): Whether to convert the run report to a PDF before locking it. Defaults to True.
    """
    global run_report_file
    try:
        if pdf_mode:
            pdf_file = convert_lr_to_pdf(run_report_file)
            os.remove(run_report_file)
            utils.debug(message=f"Removing run report in .lr format.", log=True)
            os.chmod(pdf_file, 0o444)  # Change the permissions of the new PDF file
        else:
            os.chmod(run_report_file, 0o444)
    except FileNotFoundError as error:
        utils.debug("Caught FileNotFoundError in file_operations!", log=True)
        utils.debug(f"The error message: {error}!", log=True)

    utils.debug(message="Run report locked.", log=True)


def copy_folder(source_dir, destination_dir):
    """
    Copy the contents of the source directory to the destination directory.

    Args:
        source_dir (str): The path to the source directory.
        destination_dir (str): The path to the destination directory.

    Returns:
        str: The path to the destination directory.

    Raises:
        Exception: If an unexpected error occurs during the copying process.
    """
    utils.debug(f"Starting to copy {source_dir} to {destination_dir}")

    if not os.path.exists(destination_dir):
        utils.debug(
            f"Destination directory {destination_dir} does not exist. Creating it."
        )
        os.makedirs(destination_dir)
    else:
        utils.debug(f"Destination directory {destination_dir} already exists.")
    try:
        shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
        utils.debug(f"Copied contents from {source_dir} to {destination_dir}")
        return destination_dir
    except Exception as e:
        utils.debug(f"An unexpected error occurred while copying: {e}")
        raise


def search_string_in_file(file_path, search_string):
    """
    Search for a specific string in a file.

    This function reads the content of a file and checks if a given string is present.
    It handles file not found and other exceptions, logging errors as needed.

    Args:
        file_path (str): The path to the file to be searched.
        search_string (str): The string to search for in the file.

    Returns:
        bool: True if the string is found, False otherwise.
    """
    try:
        with open(file_path, "r") as file:
            content = file.read()
            return search_string in content
    except FileNotFoundError:
        utils.printer(
            message=f"The file at {file_path} was not found.", log_type=utils.Type.ERROR
        )
        return False
    except Exception as e:
        utils.printer(message=f"An error occurred: {e}", log_type=utils.Type.ERROR)
        return False


def generate_final_folder_name():
    """
    Generate the final folder name based on mask name, grade, and date.

    This function constructs the final folder name using the mask name, mask grade (MS or MSW),
    and the current date. It logs the process for debugging purposes.

    Returns:
        str: The generated folder name, or None if the mask grade cannot be determined.
    """
    path, the_name = os.path.split(mask_name_dir)

    mask_name = str(the_name).upper()
    utils.debug(message=f"mask_name: {mask_name}", log=True)

    formatted_date = utils.format_date(datetime.date.today())
    utils.debug(message=f"formatted_date: {formatted_date}", log=True)

    generated_name = f"{mask_name}_MS_{formatted_date}"
    utils.debug(message=f"Generated folder {generated_name}", log=True)

    return generated_name


def cleanup_swp_files():
    """
    Delete all .swp files in the specified directory and its subdirectories.

    This function finds and deletes all swap (.swp) files in the final mask directory.

    Returns:
        None
    """
    swp_files = find_files(extension=".swp", directory=final_mask_dir)

    utils.verbose(message=f"Found swap files: {swp_files}" if swp_files else "")
    for swp_file in swp_files:
        try:
            os.remove(swp_file)
            utils.verbose(f"Deleted: {swp_file}")
        except Exception as e:
            utils.printer(f"Error deleting {swp_file}: {e}", log_type=utils.Type.ERROR)


def get_identified_folders():
    global final_mask_dir, dataprep_dir, revision_dir, mask_name_dir

    return {
        "mask_name": mask_name_dir,
        "dataprep": dataprep_dir,
        "revision": revision_dir,
        "final_folder": final_mask_dir,
    }
