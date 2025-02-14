#!/usr/bin/env python
import tkinter as tk
from tkinter import messagebox
import sys
from _tkinter import TclError


def file_presenter(provided_file=None, screen_position="left"):
    """
    Launch a read-only file presenter window.

    This function creates a Tkinter window to display the contents of a specified file in read-only mode.
    The window can be positioned on the left or right side of the screen based on the provided argument.

    Args:
        provided_file (str, optional): The path to the file to open. Defaults to None.
        screen_position (str, optional): The screen position for the window ('left' or 'right'). Defaults to 'left'.

    Returns:
        None
    """

    def load_file(file_path):
        """
        Load the content of the specified file into the text widget.

        Args:
            file_path (str): The path to the file to load.

        Returns:
            None
        """
        with open(file_path, "r") as file:
            content = file.read()
            text_widget.config(state=tk.NORMAL)  # Enable editing to insert text
            text_widget.delete(1.0, tk.END)  # Clear existing content
            text_widget.insert(tk.END, content)  # Insert file content
            text_widget.config(state=tk.DISABLED)  # Make text widget read-only

    def on_exit():
        """
        Handle the window close event.

        This function is called when the window is closed to perform any necessary cleanup.

        Returns:
            None
        """
        lrfp.destroy()

    lrfp = tk.Tk()
    lrfp.title(f"Preview - {sys.argv[1]}")
    lrfp.geometry(
        "950x780+1920+0" if screen_position == "left" else "950x780+2880+0"
    )  # Adjust positions

    # Create a scrollbar
    scrollbar = tk.Scrollbar(lrfp)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget = tk.Text(lrfp, wrap="word", yscrollcommand=scrollbar.set)
    text_widget.pack(expand=1, fill="both")
    text_widget.config(state=tk.DISABLED)  # Make text widget read-only initially

    # Configure the scrollbar
    scrollbar.config(command=text_widget.yview)

    if provided_file:
        load_file(provided_file)
    else:
        print("File to open was not found!")

    lrfp.protocol("WM_DELETE_WINDOW", on_exit)
    lrfp.mainloop()


if __name__ == "__main__":
    try:
        if len(sys.argv) > 2:
            file_presenter(sys.argv[1], sys.argv[2])
        elif len(sys.argv) > 1:
            file_presenter(sys.argv[1])
        else:
            print("Usage: python lr_previewer.py <file_to_open> [left|right]")
    except TclError:
        print("WARNING\tFile Presenter shut down unexpectedly.")
    except KeyboardInterrupt:
        print("WARNING\tFile Presenter was forcefully terminated.")
