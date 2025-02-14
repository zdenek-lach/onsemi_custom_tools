import os
import pwd
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from _tkinter import TclError

import psutil

from enum import Enum
from tkinter import messagebox

import file_operations
import config_parser
import argument_parser
import user_interface

global secret_process

# List to keep track of editor processes
editor_processes = []


class Type(Enum):
    """
    Enumeration for log message types.

    This enum defines the types of log messages that can be used in the application.
    The types include:
    - INFO: Informational messages.
    - WARNING: Warning messages.
    - ERROR: Error messages.
    - QUESTION: Question messages.
    """

    INFO = 1
    WARNING = 2
    ERROR = 3
    QUESTION = 4


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


def format_line(text, fill_symbol=None, edge_symbol=None):
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
    """
    tab_length = 8
    title = "Last Resort"
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


def print_intro():
    """
    Print the introductory message for the application.

    This function prints the application title, version, and usage instructions
    based on the command-line arguments provided.
    """
    arguments = argument_parser.get()
    title = "Last Resort"
    version = get_release_version()
    app_title = f"{title} version {version}"
    print(format_line(text="", fill_symbol="="))
    print(format_line(text=app_title))
    print(format_line(text="", fill_symbol="=", edge_symbol="+"))

    if not arguments.verbose and not arguments.debug:
        print(format_line("Use -i or --info the help message"))
        print(format_line("about the Last Resort application."))
        print(format_line(text="", fill_symbol="-", edge_symbol="+"))
        print(format_line("Use -v or --verbose for more information"))
        print(format_line("about the runtime behavior."))
        print(format_line(text="", fill_symbol="-", edge_symbol="+"))
        print(format_line("Use -d or --debug if something is misbehaving"))
        print(format_line("and you need to know more."))

    if arguments.verbose and not arguments.debug and not arguments.silent:
        print(format_line("Verbose mode is active."))
        print(format_line("This will provide more informative output."))
    if arguments.debug and not arguments.silent:
        print(format_line("Debug mode is active."))
        print(format_line("This will provide extensive output."))

    print(format_line(text="", fill_symbol="=", edge_symbol="+"))
    print(format_line("If you encounter problems with this app,"))
    print(format_line("please contact Zdenek Lach."))
    print(format_line(text="", fill_symbol="="))
    print("\n\n")


def verbose(message):
    """
    Print a verbose message if verbose or debug mode is enabled.

    This function formats and prints a verbose message with a custom tag if either
    verbose or debug mode is active. It also writes the message to the history log.

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

    file_operations.write_history(message)


def debug(message, log=None):
    """
    Print a debug message if debug mode is enabled.

    This function formats and prints a debug message with a custom tag if debug mode is active.
    It also writes the message to the history log if a log argument is provided.

    Args:
        message (str): The debug message to print.
        log (log, optional): An optional log to write the message to.

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

    if log:
        file_operations.write_history(message)


def open_for_preview(file_to_open, screen_position="left"):
    """
    Launch a file for preview using the configured editor.

    This function opens the specified file in the configured editor and tracks the process ID.
    It supports positioning the window on the left or right side of the screen.

    Args:
        file_to_open (str): The path to the file to open.
        screen_position (str): The screen position for the window ('left' or 'right').

    Returns:
        None
    """
    editor = config_parser.get("editor_of_choice")
    debug(message=f"Opening {file_to_open} using {editor}")
    if editor == "built_in":
        lr_app_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        file_presenter = os.path.join(lr_app_path, "file_presenter.py")
        try:
            process = subprocess.Popen([file_presenter, file_to_open, screen_position])
        except TclError as e:
            debug(
                message=f"File Presenter shut down unexpectedly. Error: {e}", log=True
            )
        except KeyboardInterrupt:
            debug(message="File Presenter was forcefully terminated.")
    else:
        process = subprocess.Popen([editor, file_to_open])

    editor_processes.append(process.pid)


def kill_processes():
    """
    Terminate all running instances of the configured editor.

    This function iterates through all running processes and terminates any process
    that matches the name or PID of the configured editor. It also performs cleanup
    actions such as removing swap files.

    Returns:
        None

    Raises:
        OSError: If no process with the name of the configured editor is found.
        Exception: For any other errors that occur while attempting to kill the processes.
    """
    try:
        editor = config_parser.get("editor_of_choice")
        for process in psutil.process_iter():
            if process.name() == editor or process.pid in editor_processes:
                debug(message=f"Killing process {str(process)}")
                process.kill()
        file_operations.cleanup_swp_files()
    except OSError:
        printer(
            message=f"No process found with the name {editor}.", log_type=Type.ERROR
        )
    except Exception as e:
        printer(
            message=f"An error occurred while closing editor window: {e}",
            log_type=Type.ERROR,
        )


def get_full_name():
    """
    Retrieve the full name of the current user.

    This function gets the current username, retrieves the full name from the system's
    password database, and splits it into first name, last name, and username.

    Returns:
        tuple: A tuple containing the first name, last name, and username.
    """
    # Get the current username
    username = os.popen("whoami").read().strip()
    # Get the full name of the user
    passwd_entry = pwd.getpwnam(username)
    full_name = passwd_entry.pw_gecos.split(",")[0]
    # Split the full name into first name and rest
    first_name, rest = full_name.split(" ", 1)
    # Split the rest into last name and username
    last_name, username = rest.split("-", 1)

    return first_name, last_name, str.lower(username.strip())


def get_user_name():
    """
    Retrieve the current user's name.

    Returns:
        str: The current user's name.
    """
    return os.getlogin()


def last_resort():
    """
    Execute the final set of actions for the application.

    This function performs critical final steps including:
    1. Setting paths for the final mask and dataprep forms directories.
    2. Identifying the .po file within the final mask directory.
    3. Running the daps_po2pdf command to convert the .po file to a .pdf.
    4. Locating the generated .pdf file.
    5. Moving the .pdf file to the 'forms' directory.

    Returns:
        None
    """
    # Define paths
    final_mask_folder = file_operations.final_mask_dir
    dataprep_forms_folder = os.path.join(file_operations.dataprep_dir, "forms")
    debug(f"dataprep_forms_folder set to: {dataprep_forms_folder}")

    # Find the .po file in the final_mask_folder
    po_files = [f for f in os.listdir(final_mask_folder) if f.endswith(".po")]
    if len(po_files) != 1:
        debug(
            f"Simulation expected exactly one .po file, found {len(po_files)}", log=True
        )
        return

    debug(f"selected_po_file set to: {po_files[0]}")

    # Set the created file name
    pdf_to_create = f"{po_files[0]} + .pdf"
    debug(f"pdf_to_create set to: {pdf_to_create}", log=True)

    # Run the daps_po2pdf in the final_mask_folder
    debug(message="Running daps_po2pdf in" + str(final_mask_folder), log=True)
    subprocess.run(["daps_po2pdf", po_files[0]], cwd=final_mask_folder)
    debug(message="daps_po2pdf command executed", log=True)

    # Find the .pdf file in the final_mask_folder
    pdf_files = [f for f in os.listdir(final_mask_folder) if f.endswith(".pdf")]
    debug(message="Created pdf file: " + pdf_files[0])
    if len(pdf_files) != 1:
        debug(f"Expected exactly one .pdf file, found {len(pdf_files)}", log=True)
        return

    created_pdf_with_path = os.path.join(file_operations.final_mask_dir, pdf_files[0])
    debug(f"created_pdf_with_path set to: {created_pdf_with_path}", log=True)

    # Destination path in the forms folder
    destination_folder = os.path.join(file_operations.dataprep_dir, "forms")
    debug(f"destination_file set to: {destination_folder}", log=True)

    # Check if the file exists before moving
    if os.path.exists(created_pdf_with_path):
        debug(message="Moving the created file to the forms folder", log=True)
        shutil.move(
            created_pdf_with_path, os.path.join(destination_folder, pdf_files[0])
        )
        debug(
            "File moved successfully from '"
            + created_pdf_with_path
            + "' to '"
            + os.path.join(destination_folder, pdf_files[0])
            + "'.",
            log=True,
        )
    else:
        debug(f"PDF file not found: {pdf_files[0]}", log=True)

    debug(message="Simulation function completed")


def send_email(root, user_input_expedite=None):
    """
    Initiate the email sending process using a specified script.

    This function attempts to run an email script and handles any errors that occur.
    If multiple .po files cause the process to fail, it adjusts the directory and retries.

    Args:
        root (tk.Tk): The root window of the Tkinter application.
        user_input_expedite: The functions stores the user-selected
        input in case it's recursively ran again after creating the tar file after a failed attempt.
    Returns:
        None
    """
    if os.getenv("RDPSITE") != "secret":  # anonymized
        printer(
            message="Environment not secret, email functionality disabled.",  # anonymized
            log_type=Type.WARNING,
        )
        return
    email_script = os.path.join(
        os.path.dirname(os.path.abspath(sys.argv[0])),
        "../../secret/secret/send_email.py",  # anonymized
    )

    # Create a temporary file in the current working directory
    with tempfile.NamedTemporaryFile(delete=False, dir=os.getcwd()) as temp_file:
        tmp_output_file = temp_file.name
    verbose(message=f"Sending email in '{file_operations.final_mask_dir}'")
    email_command = f" python {email_script} > {tmp_output_file} 2>&1"

    # Prompt the user for input
    if user_input_expedite is None:
        expedite_mode = messagebox.askyesno(
            "secret Mode", "Do you want to send the email in secret mode? [y/n]"
        )
        user_input_expedite = "y\n" if expedite_mode else "n\n"

    # Run the command and simulate user input
    email_process = subprocess.Popen(
        args=email_command,
        cwd=file_operations.final_mask_dir,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    # Send the input to the email script
    stdout, stderr = email_process.communicate(input=user_input_expedite)

    # Wait for 5 seconds to ensure the email script has time to complete
    printer(
        message="Waiting for 3 seconds to let the email run.", log_type=Type.WARNING
    )
    time.sleep(3)

    # Ensure the file is created before reading
    if not os.path.exists(tmp_output_file):
        debug(message=f"Temporary output file {tmp_output_file} does not exist.")

    # Read the output file
    try:
        with open(tmp_output_file, "r") as file:
            output = file.read()
            debug(message="The email script output: " + str(output), log=True)
        # Check for the specific error message in the output
        if "*.tar.gz file does not exist" in output:
            # Add debug message before showing the prompt
            debug(message="Prompting user to create tar file.")
            if messagebox.askyesno(
                "Tar does not exist", "Would you like to create it automatically?"
            ):
                debug(message="Creating tar file after email failed.", log=True)
                tar_file()
                if messagebox.askyesno(
                    "Try again?", "Would you like to try to send the email again?"
                ):
                    send_email(root=root, user_input_expedite=user_input_expedite)
        elif (
            'selection = int(input("Select which file to use (enter the number): ")) - 1'
            in output
        ):
            printer(
                message="There is more than one archive in the target directory,"
                " make sure there is only one archive and try again.",
                log_type=Type.ERROR,
            )
            messagebox.showwarning(
                "Too many archives!",
                "There is more than one archive in the target directory, make sure there is only one archive (.tar.gz / .tgz / .tar) and try again.",
            )
            if messagebox.askyesno(
                "Email script failed!", "Would you like to try to send the email again?"
            ):
                send_email(root=root, user_input_expedite=user_input_expedite)

        elif "Email send successfully to" in output:
            messagebox.showinfo("Success", "Email sent successfully!")
            printer(message="Email sent successfully!", log_type=Type.INFO)
        else:
            printer(message="Something unexpected happened.", log_type=Type.INFO)
            if messagebox.askyesno(
                "Email script failed!", "Would you like to try to send the email again?"
            ):
                send_email(root=root, user_input_expedite=user_input_expedite)
    except ValueError:
        printer(
            message="Email script failed to find target archive.", log_type=Type.ERROR
        )

    except Exception as e:
        debug(message=f"Error reading temporary output file: {e}")
    # Clean up the temporary file
    try:
        os.remove(tmp_output_file)
        debug(message=f"Temporary file {tmp_output_file} deleted.")
    except Exception as e:
        debug(message=f"Error deleting output file: {e}")


def run_secret():
    """
    Execute the secret command and manage its output.

    This function runs the secret command within the final mask directory,
    displays a reminder message, and logs the output for debugging purposes.

    Returns:
        bool: True if the command executes successfully, False otherwise.
    """
    global secret_process
    final_folder = file_operations.final_mask_dir
    if str(final_folder).endswith("/secret"):
        verbose(message="Final mask directory is /secret")
        final_folder = os.path.join(file_operations.dataprep_dir + "/secret")

    secret_process = subprocess.Popen(
        ["secret"],
        cwd=final_folder,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    debug(message="Running secret in " + str(final_folder), log=True)
    printer(message="Please copy this path to the FTP Directory:", log_type=Type.INFO)

    print(f"\n--> {custom_tab(1.5)} {final_folder} {custom_tab(1.5)} <--\n")

    messagebox.showinfo(
        title="Reminder",
        message="You can copy the FTP directory path from the terminal.",
    )

    if secret_process.returncode != 0:
        debug(
            f"secret process failed with return code {secret_process.returncode}",
            log=True,
        )
        return False

    debug(f"secret pid: {secret_process.pid} has finished.")
    secret_process = None
    return True


def simulate_secret():
    """
    Simulate the secret process.

    This function attempts to run the last_resort function. If a FileNotFoundError is caught,
    it checks if the final mask directory is "/secret". If so, it prompts the user to create
    the final mask folder, attempts to copy the folder, set the new final mask directory,
    create a tar file, and rerun the last_resort function.

    Raises:
        FileNotFoundError: If the final mask directory is not found.
        PermissionError: If there is a permission error while copying the folder.
        Exception: If any other unexpected error occurs.
    """
    try:
        debug(message="Starting last_resort function")
        last_resort()
        tar_file()
    except FileNotFoundError:
        debug(message="FileNotFoundError caught in simulate_secret")
        if file_operations.final_mask_dir == "/secret":
            verbose(message="Final mask directory is '/secret'")
            debug(
                f"Replacing '{file_operations.final_mask_dir}' "
                f"with {os.path.join(file_operations.dataprep_dir, 'secret')}"
            )
            file_operations.final_mask_dir = os.path.join(
                file_operations.dataprep_dir, "secret"
            )
            if messagebox.askyesno(
                "Final mask folder missing",
                "Would you like to create final mask folder?",
            ):
                file_operations.final_mask_dir = generate_final_mask_folder()
                debug(
                    f"New final mask directory set to {file_operations.final_mask_dir}"
                )
            tar_file()
            last_resort()
        messagebox.showinfo("Done.", "Simulation completed.")
        printer(message="secret simulation completed.", log_type=Type.INFO)


def generate_final_mask_folder():
    """
    Create a new final mask folder by copying the 'secret' directory.

    This function logs the user's choice to create a final mask folder, attempts to copy
    the 'secret' directory from the data preparation directory to a new directory, and
    returns the path to the newly created directory.

    Returns:
        str: The path to the newly created directory.

    Raises:
        PermissionError: If there is a permission issue during the folder copying process.
        Exception: If any other unexpected error occurs.
    """
    debug(message="User chose to create final mask folder", log=True)
    try:
        generated_final_folder_name = file_operations.generate_final_folder_name()
        new_dir = file_operations.copy_folder(
            source_dir=os.path.join(file_operations.dataprep_dir, "secret"),
            destination_dir=os.path.join(
                file_operations.dataprep_dir, generated_final_folder_name
            ),
        )
        if new_dir:
            messagebox.showinfo(
                "Success!", f"Folder created!\n{generated_final_folder_name}"
            )

        return new_dir
    except PermissionError as e:
        debug(f"PermissionError: {e}")
    except Exception as e:
        debug(f"An unexpected error occurred: {e}")


def tar_file():
    """
    Create a tar archive of the final mask directory.

    This function constructs the path for the tar archive and creates a tar.gz file
    containing all files in the final mask directory, excluding any existing tar.gz files.
    It displays a success message upon completion or an error message if the process fails.

    Raises:
        Exception: If there is an error creating the tar file or running the tar command.
    """
    try:
        # Create tar archive for the final mask and place it
        # not inside -dataprep- but in the final mask folder from which the secret is launched by default
        final_mask_dir = file_operations.final_mask_dir
        dataprep_dir = file_operations.dataprep_dir
        if str(final_mask_dir).endswith("/secret"):
            final_mask_dir = os.path.join(file_operations.dataprep_dir + "/secret")
        # RENAME TO 0maskname_pattern_revision.tar.gz
        text_maskname = os.path.basename(file_operations.mask_name_dir)
        text_pattern = os.path.basename(file_operations.revision_dir)[:3]
        text_revision = os.path.basename(file_operations.revision_dir)[3:]
        proper_tar_name = (
            "0" + text_maskname + "_" + text_pattern + "_" + text_revision
        ).upper() + ".tar.gz"
        tar_path_review = os.path.join(dataprep_dir, proper_tar_name)
        tar_path_vendor = os.path.join(final_mask_dir, proper_tar_name)
        debug(message="Review tar path constructed: " + tar_path_review, log=True)
        debug(message="Vendor tar path constructed: " + tar_path_vendor, log=True)
        try:
            with tarfile.open(tar_path_review, "w:gz") as tar:
                for root, dirs, files in os.walk(final_mask_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not file_path.endswith(".tgz"):
                            tar.add(
                                file_path,
                                arcname=os.path.relpath(file_path, final_mask_dir),
                            )
            verbose(message=f"Created tar archive: {tar_path_review}")
            messagebox.showinfo(
                "Compression successful",
                f"Tar file created successfully at {os.path.abspath(tar_path_review)}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create tar file.")
            printer(
                message="ERROR: Failed to create tar file: " + str(e),
                log_type=Type.ERROR,
            )
        try:
            with tarfile.open(tar_path_vendor, "w:gz") as tar:
                for root, dirs, files in os.walk(final_mask_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not file_path.endswith(".tar.gz"):
                            tar.add(
                                file_path,
                                arcname=os.path.relpath(file_path, final_mask_dir),
                            )
            verbose(message=f"Created tar archive: {tar_path_vendor}")
            messagebox.showinfo(
                "Compression successful",
                f"Tar file created successfully at {os.path.abspath(tar_path_vendor)}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create tar file.")
            printer(
                message="ERROR: Failed to create tar file: " + str(e),
                log_type=Type.ERROR,
            )
        return
    except Exception as e:
        messagebox.showerror("Error", "Failed to run tar command.")
        printer(
            message="ERROR: Failed to run tar command: " + str(e), log_type=Type.ERROR
        )


def gather_intel(root):
    """
    Collect information and prompt the user for necessary actions.

    This function prompts the user to confirm if they have run secret. If not, it offers
    to run secret. It also prompts the user to send an email and reveals additional options
    in the user interface.

    Args:
        root (tk.Tk): The root window of the Tkinter application.

    Returns:
        None
    """
    # Have you run daps trans?
    secret_ran = messagebox.askyesno(
        "secret", "Have you used secret already?"
    )
    if not secret_ran:
        if messagebox.askyesno("secret", "Would you like to run secret now?"):
            debug(message="secret launch requested by the user.", log=True)
            run_secret()
        else:
            debug(message="secret initial run declined by the user", log=True)

    else:
        # ask to send email
        if messagebox.askyesno("Email?", "Would you like to send the email?"):
            debug(message="Email requested by the user.", log=True)
            send_email(root)
        else:
            debug(message="Email declined by the user.", log=True)

    debug(message="Showing extended options.")
    user_interface.expanded_view(root)


def startup_dir_check():
    """
    Validate the current directory for running the application.

    This function checks if the current working directory starts with the configured
    masks project directory. If not, it prints error messages and exits the application.

    Returns:
        None
    """
    current_directory = os.getcwd()
    proj_dir = None
    if os.getenv("RDPSITE") == "secret":  # anonymized
        proj_dir = "secret"  # anonymized
    if os.getenv("RDPSITE") == "secret":  # anonymized
        proj_dir = "secret"  # anonymized

    printer(message=f"Starting directory: {current_directory}", log_type=Type.INFO)
    if not current_directory.startswith(proj_dir) and "TEST" not in current_directory:
        if "test" in str(current_directory):
            printer(
                message=f"Starting in TEST directory: {current_directory}",
                log_type=Type.INFO,
            )
            return
        else:
            printer(
                message=f"The app must be executed inside a mask folder within {proj_dir}!",
                log_type=Type.ERROR,
            )
            printer(
                message="You are launching Last Resort in the wrong directory.",
                log_type=Type.WARNING,
            )
            exit(0)


def get_release_version():
    """
    Retrieve the release version from the releaseTag.txt file.

    This function reads the releaseTag.txt file located in the $secret directory
    and returns the release version.

    Returns:
        str: The release version.
    """

    with open(
        os.getenv("secret") + "/secret/" + "/releaseTag.txt"  # anonymized
    ) as releaseTagTxt:

        for line in releaseTagTxt:

            if line.startswith("secret"):
                return line.split(":")[1].strip()


def print_help():
    """
    Display the comprehensive help message for the Last Resort application.

    This function prints detailed usage instructions, available options, a description of the application,
    and examples of how to run the application. It is intended to guide users on how to effectively use
    the last_resort.py script.

    The help message includes:
        - Usage syntax
        - List of command-line options with descriptions
        - A detailed description of the application's purpose and functionality
        - Step-by-step explanation of the application's workflow
        - Examples demonstrating common usage scenarios


    Usage:
        last_resort.py [OPTIONS]


    Options:
        -s, --silent           Enable silent mode (suppress output).
        -d, --debug            Enable debug mode (detailed output for troubleshooting).
        -v, --verbose          Enable verbose mode (more detailed output).
        -t, --test             Run the application in test mode.
        -i, --info             Show this help message and exit.
        -c, --config [PATH]    Path to provide a custom configuration file.
        -dc, --define_config   Open a window to define a new temporary configuration for this session.


    Description:
        The Last Resort application allows RDP engineers to perform a final check before sending data to the vendor,
        ensuring there are no typos, missing, or incorrect information.

    The application performs the following steps:
        1. Parses command-line arguments.
        2. Initializes the Tkinter root window.
        3. Prints an introductory message.
        4. Generates a unique identifier (RUID).
        5. Identifies all folders around the launch directory.
        6. Initializes the main window of the user interface.
        7. Initializes the folder structure.
        8. Finds all `.jb` and `.po` files in the revision directory.
        9. Depending on whether the 'test' argument is provided:
            - If 'test' is True, loads the first `.po` file into the checklist for testing purposes.
            - If 'test' is False, prompts the user to select `.jb` and `.po` files,
            loads the selected `.po` file into the checklist, and opens both selected files for preview.


    Examples:
        Run the application normally:
            $ python last_resort.py

        Run the application in test mode:
            $ python last_resort.py --test

        Enable verbose output:
            $ python last_resort.py --verbose

        Enable debug mode for troubleshooting:
            $ python last_resort.py --debug

        Show this help message:
            $ python last_resort.py --info

        Use a specific configuration file:
            $ python last_resort.py --config /path/to/config.yaml

        Open a window to define a new temporary configuration for this session:
            $ python last_resort.py --define_config


    For more information or if you encounter any issues, please contact Zdenek Lach.
    """
    help_message = f"""
    Usage: last_resort.py [OPTIONS]

    Options:
        -s, --silent           Enable silent mode (suppress output).
        -d, --debug            Enable debug mode (detailed output for troubleshooting).
        -v, --verbose          Enable verbose mode (more detailed output).
        -t, --test             Run the application in test mode.
        -i, --info             Show this help message and exit.
        -c, --config [PATH]    Path to provide a custom configuration file.
        -dc, --define_config   Open a window to define a new temporary configuration for this session.

    Description:
        The Last Resort application allows RDP engineers to perform a final check before sending data to the vendor,
        ensuring there are no typos, missing, or incorrect information. The application performs the following steps:
        
        1. Parses command-line arguments.
        2. Initializes the Tkinter root window.
        3. Prints an introductory message.
        4. Generates a unique identifier (RUID).
        5. Identifies all folders around the launch directory.
        6. Initializes the main window of the user interface.
        7. Initializes the folder structure.
        8. Finds all `.jb` and `.po` files in the revision directory.
        9. Depending on whether the 'test' argument is provided:
            - If 'test' is True, loads the first `.po` file into the checklist for testing purposes.
            - If 'test' is False, prompts the user to select `.jb` and `.po` files, loads the selected `.po` file into the checklist, and opens both selected files for preview.

    Examples:
        Run the application normally:
            $ python last_resort.py

        Run the application in test mode:
            $ python last_resort.py --test

        Enable verbose output:
            $ python last_resort.py --verbose

        Enable debug mode for troubleshooting:
            $ python last_resort.py --debug

        how this help message:
            $ python last_resort.py --info

        Use a specific configuration file:
            $ python last_resort.py --config /path/to/config.yaml

        Open a window to define a new temporary configuration for this session:
            $ python last_resort.py --define_config

    For more information or if you encounter any issues, please contact Zdenek Lach.
    """
    print(help_message)


def format_date(date):
    """
    Format a date into a specific string format.

    This function formats a given date into the format "ddMMMyy", where "MMM" is the
    abbreviated month name with the first letter capitalized.

    Args:
        date (datetime.date): The date to be formatted.

    Returns:
        str: The formatted date string.
    """
    month_abbr = date.strftime("%b")
    formatted_month = month_abbr[0].upper() + month_abbr[1:].lower()
    return date.strftime(f"%d{formatted_month}%y")