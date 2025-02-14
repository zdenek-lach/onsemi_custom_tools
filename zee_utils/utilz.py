import os
import re
import shutil
import tarfile
from enum import Enum
import argument_parser
import file_op_z


class Type(Enum):
    """
    Enumeration for log message types.

    This enum defines the types of log messages that can be used in the application.
    The types include:
    - INFO: Informational messages.
    - WARNING: Warning messages.
    - ERROR: Error messages.
    - QUESTION: Question messages.
    - OPTION: Used in combination with QUESTION messages.
    """

    INFO = 1
    WARNING = 2
    ERROR = 3
    QUESTION = 4
    OPTION = 5


def custom_tab(size=None):
    """
    Generate a string of spaces for tabulation to prevent "leave out too many symbols" behavior.

    Args:
        size (int, optional): The number of tab lengths to generate. Defaults to None.

    Returns:
        str: A string of spaces for tabulation.
    """

    tab_length = 8  # Default tab length
    if size is None:
        return tab_length * " "
    else:
        return int(size * tab_length) * " "


def printer(message, log_type=None):
    """
    Print a formatted message with a specific log type.

    Requirements for import:
    printer, custom_tab, Type

    Args:
        message (str): The message to print.
        log_type (Type, optional): The type of log message (INFO, WARNING, or None). Defaults to PRINTER.

    Returns:
        None
    """
    arguments = argument_parser.get()

    # Determine the print tag based on the log type
    if log_type == Type.INFO:
        print_tag = "INFO"
    elif log_type == Type.WARNING:
        print_tag = "WARNING"
    elif log_type == Type.ERROR:
        print_tag = "ERROR"
    elif log_type == Type.QUESTION:
        print_tag = "QUESTION"
    elif log_type == Type.OPTION:
        print_tag = "OPTION"
    else:
        print_tag = "PRINTER"
    # Get the terminal width
    terminal_width = shutil.get_terminal_size().columns

    # Calculate the padding needed to align the end tag
    padding_length = (
        terminal_width - len(print_tag) * 2 - len(message) - len(custom_tab()) * 2
    )
    padding = " " * max(padding_length, 0)

    # Format the message
    formatted_message = (
        f"{print_tag}{custom_tab()}{message}{padding}{custom_tab()}{print_tag}"
    )
    if arguments.silent:
        return
    else:
        print(formatted_message)


def format_line(text, fill_symbol=None, edge_symbol=None, title=None):
    """
    Format a line of text with optional fill and edge symbols.

    This function formats a line of text to fit within a predefined width, optionally
    filling the line with a specified symbol and adding edge symbols. It ensures that
    the text is centered within the line. It is meant to be used for a 'text in the box'
    kind of formatting for the CL UI.

    Args:
        text (str): The text to format.
        fill_symbol (str, optional): Symbol to fill the line. If provided, the entire line
                                     will be filled with this symbol. Defaults to None.
        edge_symbol (str, optional): Symbol for the edges of the line. If provided, the line
                                     will be enclosed with this symbol. Defaults to None.

    Returns:
        str: The formatted line of text.
        :param title: Used for the title line
    """
    tab_length = 8
    version = get_release_version()
    app_title = f"{title} version {version}"
    intro_full_line = (
        custom_tab()
        + "+"
        + tab_length * "="
        + len(app_title) * "="
        + tab_length * "="
        + "="
        + "+"
    )
    total_length = len(intro_full_line) - 2
    text_length = len(text)
    space_length = total_length - text_length

    side_space = space_length // 2
    if space_length % 2 != 0:
        side_space += 1

    if fill_symbol:
        if edge_symbol:
            output_string = (
                f"{edge_symbol} {fill_symbol * (total_length - 2)} {edge_symbol}"
            )
        else:
            output_string = f"{fill_symbol * (total_length + 2)}"
    else:
        left_space = custom_tab(side_space / tab_length)
        right_space = custom_tab((space_length - side_space) / tab_length)
        output_string = f"+{left_space}{text}{right_space}+"

    return custom_tab() + output_string.strip()


def verbose(message):
    """
    Print a verbose message if verbose or debug mode is enabled.

    This function formats and prints a verbose message with a custom tag if either
    verbose or debug mode is active.

    Args:
        message (str): The verbose message to print.

    Returns:
        None
    """
    arguments = argument_parser.get()
    if arguments.silent:
        return
    if arguments.verbose or arguments.debug:
        # Custom verbose tag
        verbose_tag = "VERBOSE"

        # Get the terminal width
        terminal_width = shutil.get_terminal_size().columns

        # Calculate the padding needed to align the end tag
        padding_length = (
            terminal_width - len(verbose_tag) * 2 - len(message) - len(custom_tab()) * 2
        )
        padding = " " * max(padding_length, 0)

        # Format the message
        formatted_message = (
            f"{verbose_tag}{custom_tab()}{message}{padding}{custom_tab()}{verbose_tag}"
        )
        if len(formatted_message) > terminal_width:
            print(f"{verbose_tag}{custom_tab()}{message}")
        else:
            print(formatted_message)


def debug(message):
    """
    Print a debug message if debug mode is enabled.

    This function formats and prints a debug message with a custom tag if debug mode is active.
    It also writes the message to the history log if a log argument is provided.

    Args:
        message (str): The debug message to print.

    Returns:
        None
    """
    arguments = argument_parser.get()
    if arguments.silent:
        return
    if arguments.debug:
        # Custom verbose tag
        debug_tag = "DEBUG"

        # Get the terminal width
        terminal_width = shutil.get_terminal_size().columns

        # Calculate the padding needed to align the end tag
        padding_length = (
            terminal_width - len(debug_tag) * 2 - len(message) - len(custom_tab()) * 2
        )
        padding = " " * max(padding_length, 0)

        # Format the message
        formatted_message = (
            f"{debug_tag}{custom_tab()}{message}{padding}{custom_tab()}{debug_tag}"
        )
        if len(formatted_message) > terminal_width:
            print(f"{debug_tag}{custom_tab()}{message}")
        else:
            print(formatted_message)


def get_release_version():
    """
    Retrieve the release version from the releaseTag.txt file.

    This function reads the releaseTag.txt file located in the specified directory
    and returns the release version.

    Returns:
        str: The release version.
    """
    with open(
        os.getenv("SECRET_ENV_VAR") + "/secret_path/releaseTag.txt"  #anonymized
    ) as releaseTagTxt:

        for line in releaseTagTxt:

            if line.startswith("secret"):  #anonymized
                return line.split(":")[1].strip()


def create_tar_archive(files_to_tar, tar_path, should_contain_subdir=True):
    try:
        with tarfile.open(tar_path, "w:gz") as tar:
            for file_path in files_to_tar:
                arch_name = (
                    os.path.relpath(file_path, os.path.dirname(file_path))
                    if should_contain_subdir
                    else os.path.basename(file_path)
                )
                tar.add(file_path, arcname=arch_name)
        printer(message=f"Created tar archive: {tar_path}", log_type=Type.INFO)
    except Exception as e:
        printer(
            message=f"ERROR: Failed to create tar file: {str(e)}", log_type=Type.ERROR
        )


def tar_op_finale():
    """
    The function needs to figure out if it's in the dataprep folder or final_mask_dir.
    This should be done by matching current dir to either "dataprep" or the final_mask_dir regex pattern: 'secret'.
    Then it should tar the archive in 2 ways: one with final_mask_dir style with subdir and one with secret style without subdir.
    It utilizes tar_content function from utilz lib.
    """
    tar_path_review = None
    tar_path_vendor = None
    try:
        current_dir = os.getcwd()
        printer(message=f"Current directory: {current_dir}", log_type=Type.INFO)

        dataprep_dir = None
        final_mask_dir = None
        final_pattern = '[A-Za-z0-9]+_[Mm][Ss][Ww]?_\d{2}[A-Za-z]{3}\d{2}'
        current_dir_matches_final_mask_dir = re.compile(final_pattern).match(os.path.basename(current_dir))
        if current_dir.endswith("dataprep"):
            dataprep_dir = current_dir
            printer(message=f"Detected dataprep directory: {dataprep_dir}", log_type=Type.INFO)

            found_final_masks_folders = file_op_z.find_folder_by_pattern(
                searched_pattern=final_pattern, search_location=dataprep_dir
            )
            printer(message=f"Found final masks: {found_final_masks_folders}", log_type=Type.INFO)

            if len(found_final_masks_folders) < 1:
                final_mask_dir = found_final_masks_folders[0]  # Automatically select the first match
                printer(message=f"Automatically selected final_mask_dir: {final_mask_dir}", log_type=Type.INFO)
            else:
                printer(message="Too many final-folders found. Please choose from the options:", log_type=Type.QUESTION)
                for i, folder in enumerate(found_final_masks_folders):
                    printer(message=f"{i + 1}: {os.path.basename(folder)}", log_type=Type.OPTION)
                choice = int(input("Enter the number of your choice: ")) - 1
                final_mask_dir = found_final_masks_folders[choice]
                printer(message=f"User selected final_mask_dir: {final_mask_dir}", log_type=Type.INFO)
        elif current_dir_matches_final_mask_dir:
            final_mask_dir = current_dir
            dataprep_dir = os.path.dirname(final_mask_dir)
            printer(message=f"Detected final_mask_dir: {final_mask_dir}", log_type=Type.INFO)
            printer(message=f"Derived dataprep_dir: {dataprep_dir}", log_type=Type.INFO)
        text_maskname = os.path.basename(os.path.dirname(os.path.dirname(dataprep_dir)))  # go 2 up from dataprep
        text_pattern = os.path.basename(os.path.dirname(dataprep_dir))[:3]  # go 1 up from dataprep
        text_revision = os.path.basename(os.path.dirname(dataprep_dir))[3:]

        vendor_tar_name = ("0" + text_maskname + "_" + text_pattern + "_" + text_revision).upper() + ".tar.gz"
        review_tar_name = os.path.basename(final_mask_dir) + ".tgz"

        tar_path_review = os.path.join(dataprep_dir, review_tar_name)
        tar_path_vendor = os.path.join(final_mask_dir, vendor_tar_name)

        printer(message=f"Review tar path constructed: {tar_path_review}", log_type=Type.INFO)
        printer(message=f"Vendor tar path constructed: {tar_path_vendor}", log_type=Type.INFO)

        try:
            with tarfile.open(tar_path_review, "w:gz") as tar:
                for root, dirs, files in os.walk(final_mask_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not file_path.endswith(".tgz"):
                            tar.add(file_path, arcname=os.path.relpath(file_path, final_mask_dir))
            printer(message=f"Created review tar archive: {tar_path_review}", log_type=Type.INFO)

        except Exception as e:
            printer(message=f"ERROR: Failed to create review tar file: {str(e)}", log_type=Type.ERROR)

        try:
            with tarfile.open(tar_path_vendor, "w:gz") as tar:
                for root, dirs, files in os.walk(final_mask_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not file_path.endswith(".tar.gz"):
                            tar.add(file_path, arcname=os.path.relpath(file_path, final_mask_dir))
            printer(message=f"Created vendor tar archive: {tar_path_vendor}", log_type=Type.INFO)

        except Exception as e:
            printer(message=f"ERROR: Failed to create vendor tar file: {str(e)}", log_type=Type.ERROR)

        return tar_path_review, tar_path_vendor

    except Exception as e:
        printer(message=f"ERROR: Failed to run tar operation: {str(e)}", log_type=Type.ERROR)
    return tar_path_review, tar_path_vendor


def test():
    print("Testing begins..")
    print(tar_op_finale())
    print("Testing ends..")


if __name__ == "__main__":
    test()
