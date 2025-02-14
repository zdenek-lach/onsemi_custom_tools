import os
import re
import tkinter as tk
from tkinter import messagebox

import config_parser
import utils
import file_operations
import argument_parser

buttons_row = 10
global chl_vars
we_done = False
global checklist_items


def init_main_window(root):
    """
    Initialize the main window of the application.

    Args:
        root (tk.Tk): The root window of the Tkinter application.
    """
    title = "Last Resort"
    version = utils.get_release_version()
    window_size = "320x350"
    root.title(f"{title} - {version}")
    root.eval("tk::PlaceWindow . center")
    root.geometry(window_size)
    root.protocol("WM_DELETE_WINDOW", lambda: close_app(root))


def confirm_button_action(root):
    """
    Perform actions when the confirm button is clicked.
    1. Closes subprocesses
    2. saves checklist to the pdf
    3. Starts prompting user with gather_intel function

    Args:
        root (tk.Tk): The root window of the Tkinter application.
    """

    utils.kill_processes()
    file_operations.save_checklist_to_pdf()
    utils.gather_intel(root)


def load_checklist(root, selected_po):

    """
    Load the checklist items into the main window.

    Args:
        root (tk.Tk): The root window of the Tkinter application.
        selected_po (str): The selected .po file.
    """
    global chl_vars, checklist_items
    chl_vars = [tk.IntVar() for _ in checklist_items]

    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20)

    for i, item in enumerate(checklist_items):
        tk.Checkbutton(frame, text=item, variable=chl_vars[i]).grid(
            row=i, column=1, sticky="w", padx=10, pady=5
        )

    def on_save():
        confirm_button_action(root)

    save_button = tk.Button(frame, text="Save", command=on_save)
    save_button.grid(row=buttons_row - 1, column=1, padx=20, pady=10)


def resize_based_on_input_length(root, options):
    """
    Resize the window based on the length of the input options.

    Args:
        root (tk.Tk): The root window of the Tkinter application.
        options (list): A list of options to be displayed.
    """
    max_length = max(len(option) for option in options)
    width = max_length * 10
    min_width = 300
    width = max(width, min_width)
    root.geometry(f"{width}x200")


def prompt_selection(root, options, title, is_file_list=None, is_folder_list=None):
    """
    Prompt the user to select an option from a list.

    Args:
        root (tk.Tk): The root window of the Tkinter application.
        options (list): A list of options to choose from.
        title (str): The title of the prompt window.
        is_file_list (bool, optional): Indicates if the selection is meant for a list of files. Defaults to None.
        is_folder_list (bool, optional): Indicates if the selection is meant for a list of folders. Defaults to None.

    Returns:
        str: The selected option.
    """
    selected_option = None

    def on_select():
        nonlocal selected_option
        selected_option = full_paths[var.get()] if is_folder_list else var.get()
        utils.debug(message="Prompt selected: " + selected_option, log=True)
        selection_window.destroy()

    # Create a mapping of displayed values to full paths if is_folder_list is True
    if is_folder_list:
        full_paths = {os.path.basename(option): option for option in options}
        display_options = list(full_paths.keys())
    else:
        display_options = options

    selection_window = tk.Toplevel(root)
    selection_window.title(title)

    tk.Label(selection_window, text=title).pack(pady=10)
    center_window(selection_window)
    resize_based_on_input_length(selection_window, display_options)

    var = tk.StringVar(selection_window)

    # Retrieve the pattern from config_parser
    pattern = config_parser.get("final_mask_pattern")  # anonymized
    regex = re.compile(pattern)

    # Check each option to see if it contains the pattern
    default_option = display_options[0]
    if is_file_list or is_folder_list:
        for option in display_options:
            if regex.search(option):
                default_option = option
                break

    var.set(default_option)

    dropdown = tk.OptionMenu(selection_window, var, *display_options)
    dropdown.pack(pady=10)

    select_button = tk.Button(selection_window, text="Select", command=on_select)
    select_button.pack(pady=10)

    selection_window.grab_set()
    root.wait_window(selection_window)
    return selected_option


def close_app(root):
    """
    Close the application and perform cleanup actions.

    Args:
        root (tk.Tk): The root window of the Tkinter application.
    """
    global we_done
    root.destroy()
    we_done = True
    utils.kill_processes()
    file_operations.lock_run_report(pdf_mode=True)
    exit(0)


def expanded_view(root):
    """
    Reveal additional buttons in the main window. To allow manual operations.

    Args:
        root (tk.Tk): The root window of the Tkinter application.
    """

    def on_run_secret():
        utils.debug(message="Running secret via gui button.", log=True)
        utils.debug(
            message=f"Current final_mask_dir = {file_operations.final_mask_dir}"
        )
        utils.run_secret()

    def on_send_email():
        utils.printer(message="Email script launched.", log_type=utils.Type.INFO)
        utils.send_email(root)

    def on_print_vars():
        dirs_log = file_operations.get_identified_folders()
        for key, folder in dirs_log.items():
            utils.printer(f"{key}: {folder}", log_type=utils.Type.INFO)
        formatted_dirs_log = "\n".join(
            [f"{key}: {folder}\n" for key, folder in dirs_log.items()]
        )
        messagebox.showinfo("Variables", formatted_dirs_log)

    # Create a frame to hold the checklist and buttons
    button_frame = tk.Frame(root)
    button_frame.pack(padx=20, pady=20)
    email_button = tk.Button(button_frame, text="Send Email", command=on_send_email)
    simulation_button = tk.Button(
        button_frame, text="Simulate secret", command=utils.simulate_secret
    )
    trans_button = tk.Button(
        button_frame, text="Run secret", command=on_run_secret
    )
    tar_button = tk.Button(
        button_frame, text="Force tar file operation", command=utils.tar_file
    )
    generate_folder_button = tk.Button(
        button_frame,
        text="Generate final folder",
        command=utils.generate_final_mask_folder,
    )
    print_vars_button = tk.Button(
        button_frame, text="Print folder structure", command=on_print_vars
    )
    email_button.grid(row=buttons_row, column=0, padx=10, pady=10)
    simulation_button.grid(row=buttons_row, column=1, padx=10, pady=10)
    trans_button.grid(row=buttons_row, column=2, padx=10, pady=10)
    tar_button.grid(row=buttons_row + 1, column=1, padx=10, pady=10)
    generate_folder_button.grid(row=buttons_row + 1, column=0, padx=10, pady=10)
    print_vars_button.grid(row=buttons_row + 1, column=2, padx=10, pady=10)
    root.geometry("580x480")


def show_config_popup(root):
    def on_confirm():
        # Update the configuration with the values from the input fields
        for key, entry in entries.items():
            config_parser.full_configuration[key] = entry.get()
        config_window.destroy()

    config_window = tk.Toplevel(root)
    config_window.title("Define Configuration")
    config_window.geometry("550x410")
    tk.Label(config_window, text="Define Configuration for this session.").pack(pady=10)

    # Load the default configuration
    config_parser.initialize()
    default_config = config_parser.full_configuration

    # Create a dictionary to store the entry widgets
    entries = {}

    # Add input fields for each configuration key-value pair
    for key, value in default_config.items():
        frame = tk.Frame(config_window)
        frame.pack(fill="x", padx=20, pady=5)
        tk.Label(frame, text=key, width=20, anchor="w").pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="right", fill="x", expand=True)
        entry.insert(0, value)
        entries[key] = entry
    tk.Label(
        config_window, text="Note. Run archive is set to the app directory by default."
    ).pack(padx=10, pady=10)
    tk.Button(config_window, text="Confirm", height=10, command=on_confirm).pack(
        pady=10
    )
    center_window(config_window)
    config_window.grab_set()
    root.wait_window(config_window)


def center_window(window):
    """
    Attempt to center the window on the screen.

    Args:
        window (tk.Toplevel): The window to be centered.
    """
    window.focus()
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")
