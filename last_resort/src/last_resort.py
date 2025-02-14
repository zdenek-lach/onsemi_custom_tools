#!/custom/tools/wrappers/lang/python
import tkinter as tk

import argument_parser

import utils
import file_operations
import user_interface


def cleanup():
    """
    Perform cleanup actions.

    This function performs necessary cleanup actions such as deleting swap files
    and locking the run report.

    Returns:
        None
    """
    utils.printer(message="Performing cleanup actions..", log_type=utils.Type.INFO)
    file_operations.cleanup_swp_files()
    file_operations.lock_run_report()


def main():
    """
    Main entry point for the Last Resort application.

    This function initializes the application by performing a series of setup and initialization tasks.
    It handles the following steps:

    1. Parses command-line arguments using the argument_parser module.
       - The arguments include options for silent mode, debug mode, verbose mode, test mode, and displaying help information.
    2. Initializes the Tkinter root window.
       - Sets up the main window for the graphical user interface.
    3. If the --info argument is provided, prints the help message and exits.
       - Provides users with detailed usage instructions and exits the application.
    4. Prints the introductory message.
       - Displays a welcome message and information about the application.
    5. Generates a unique identifier (RUID) for the session.
       - Creates a unique run identifier to track the session.
    6. Identifies all folders around the launch directory.
       - Determines the paths for various project directories such as mask_name, revision, dataprep, and final_mask.
    7. Initializes the main window of the user interface.
       - Sets up the main window components and layout.
    8. Initializes the folder structure.
       - Calls the init_folder_structure function to set up the necessary directories.
    9. Searches for .jb and .po files in the revision directory.
       - Looks for job files (.jb) and purchase order files (.po) in the specified directory.
    10. If no .po or .jb files are found, raises a FileNotFoundError.
        - Ensures that the necessary files are present before proceeding.
    11. Prompts the user to select .jb and .po files, loads the selected .po file into the checklist,
        and opens both files for preview in the selected editor.
        - Provides a graphical interface for the user to select and preview the required files.
    12. If the --test argument is provided, loads the first .po file into the checklist and expands the window.
        - Automatically selects the first .po file for testing purposes and adjusts the window size.
    13. Starts the Tkinter main loop to display the main window.
        - Enters the main event loop to keep the application running and responsive.

    Raises:
        FileNotFoundError: If no .po or .jb files are found in the revision directory.
    """
    arguments = argument_parser.get()
    ui_root = tk.Tk()
    utils.print_intro()

    if arguments.info:
        utils.print_help()
        exit(0)

        # identify all folders around launch dir
    user_interface.checklist_items = [
        "Mask-set",
        "Vendor",
        "CC",
        "Layer names",
        "PO number",
        "Price",
        "Formatting",
        "Mask Grade",
    ]
    user_interface.init_main_window(ui_root)

    # Check if --define_config or -dc is provided
    if arguments.define_config:
        user_interface.show_config_popup(ui_root)
        # Load the default configuration and update arguments
        arguments = argument_parser.get()

    file_operations.generate_ruid()

    file_operations.init_folder_structure(ui_root)
    # ask for po and jb via gui
    all_jb_files = file_operations.find_files(
        extension=".jb", directory=file_operations.final_mask_dir
    )
    all_po_files = file_operations.find_files(
        extension=".po", directory=file_operations.final_mask_dir
    )
    # Filter the arguments to only include those that are True
    filtered_arguments = {k: v for k, v in vars(arguments).items() if v}
    utils.debug(message=f"Launch arguments: {filtered_arguments}", log=True)
    if not len(all_po_files) > 0:
        raise FileNotFoundError("No PO files found")
    if not len(all_jb_files) > 0:
        raise FileNotFoundError("No JB files found")

    if arguments.test:
        selected_jb = all_jb_files[0]
        selected_po = all_po_files[0]
        user_interface.load_checklist(ui_root, selected_po)
        user_interface.expanded_view(ui_root)
    else:

        if len(all_jb_files) > 1:
            selected_jb = user_interface.prompt_selection(
                root=ui_root,
                options=all_jb_files,
                title="Please select desired .jb file",
                is_file_list=True,
            )
            utils.printer(
                message=f"Prompt selection: {selected_jb}", log_type=utils.Type.INFO
            )

        else:
            selected_jb = all_jb_files[0]
            utils.verbose(message=f"Preselected the only found JB file: {selected_jb}")
        if len(all_po_files) > 1:
            selected_po = user_interface.prompt_selection(
                root=ui_root,
                options=all_po_files,
                title="Please select desired .po file",
                is_file_list=True,
            )
            utils.printer(
                message=f"Prompt selection: {selected_po}", log_type=utils.Type.INFO
            )
        else:
            selected_po = all_po_files[0]
            utils.verbose(message=f"Preselected the only found PO file: {selected_po}")

        user_interface.load_checklist(ui_root, selected_po)
        utils.open_for_preview(selected_jb, "left")
        utils.open_for_preview(selected_po, "right")
        ui_root.attributes("-topmost", True)
    # show main window
    ui_root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        utils.printer(
            message="Application forcefully terminated!", log_type=utils.Type.ERROR
        )
        utils.debug("Caught KeyboardInterrupt!", log=True)
        cleanup()
    except RuntimeError:
        utils.printer(
            message="Application forcefully terminated!", log_type=utils.Type.ERROR
        )
        utils.debug("Caught RuntimeError!", log=True)
        cleanup()
