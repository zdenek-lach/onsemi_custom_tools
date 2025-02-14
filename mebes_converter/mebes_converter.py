#!/custom/tools/lang/release7.8/python3.12.6/bin/python

import os
import sys
import subprocess
import shutil


def set_default_envs():
    """
    Set the default environment variables required for Synopsys CATS.

    This function sets the ON_CATS, CATS_HOME, PATH, and CATSHOST environment variables
    to ensure the CATS tools are available and correctly configured.
    """
    # os.environ[
    #    "ON_CATS"
    # ] = "current,/prod/cad/daps/dapsdata/cats/"  # - seems to be needed
    os.environ["CATS_HOME"] = "/secret" #anonymized
    os.environ["PATH"] += os.pathsep + os.environ["secret"] + "/bin"#anonymized
    os.environ["CATSHOST"] = os.uname().nodename


def show_help():
    """
    Display the help message for the script.

    This function prints a detailed help message that explains the usage, options,
    and environment variables required by the script.
    """

    help_message = """
    Version: {version}
    Usage: {script_name} [OPTION]

    This script converts mebes1 to mebes3 files using CATS. It is designed to work
    universally across all secret environments. If launched outside the ONCR environment,
    it allows the user to select a CATS version from a list of options.

    Options:
      none
          Shows main menu.

      -run
          Explicitly run the conversion. 

      -help, -h, --help, --h
          Display this help message. Use this option to get detailed information about the
          script's usage, options, and behavior.

    Examples:
      {script_name}
          Run the script in default mode. This will use the Python script for conversion.

      {script_name} -run
          Explicitly run the script in default mode using the Python script.

    Environment Variables:
      ON_CATS
          Specifies the current CATS environment. This variable is set automatically based
          on the hostname or user selection.

      CATS_HOME
          Specifies the home directory of the CATS installation. This variable is set
          automatically based on the hostname or user selection.

      PATH
          The system PATH variable is updated to include the CATS binary directory.

      CATSHOST
          The hostname of the current machine. This variable is used to determine the
          appropriate CATS environment.

    Notes:
      - The script checks for mebes files with the naming convention of 9 characters followed
        by a dot and a 2-character extension (e.g., file00001.o0). Ensure your files follow
        this convention.
      - If you encounter any issues or need further assistance, please contact your developer.
    """.format(
        script_name=os.path.basename(__file__), version=get_release_verison()
    )
    print(help_message)


def check_files():
    """
    Check for MEBES files in the current directory.

    This function lists all files in the current directory and filters them based on the
    naming convention of 9 characters followed by a dot and a 2-character extension.
    It prints the status of each file and counts the number of matching files.
    """
    # List all files in the current directory
    files = os.listdir(".")

    # Filter files based on the naming convention
    mebes_files = []
    for f in files:
        parts = f.split(".")
        # print(f"Checking {parts}")
        if (
            len(parts) == 2
            and len(parts[0]) == 9
            and len(parts[1]) == 2
            and not parts[1] == "jb"
        ):
            mebes_files.append(f)
            print(f"Checking file: {parts} - detected mebes naming standard")
        elif len(parts) == 2 and parts[1] == "cflt":
            mebes_files.append(f)
            print(f"Checking file: {parts} - detected .cflt file")
        elif len(parts) == 2 and parts[1] == "jb":
            mebes_files.append(f)
            print(f"Checking file: {parts} - detected .jb file")
        else:
            print(f"Checking file: {parts} - not a mebes file")

    # Count the number of matching files
    count = len(mebes_files)

    if count == 0:
        print("\nError: No mebes files to convert.")
        sys.exit(1)
    else:
        print(f"\nFound {count} files for conversion.")


# Function to run a command and handle the output
def run_command(command):
    """
    Run a shell command and handle the output.

    Args:
        command (str): The command to run.

    Returns:
        str: The standard output of the command.
    """
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error running command: {command}\n{stderr.decode()}")
    return stdout.decode()


# Function to handle prompts
def handle_readfile_prompts(output):
    """
    Handle interactive prompts during the readfile command.

    Args:
        output (str): The output from the readfile command.

    Returns:
        str: The final output after handling prompts.
    """
    while True:
        if "--More--" in output:
            output = run_command(" ")
        elif "Is this list OK" in output:
            output = run_command("y")
        else:
            break
        print(output)
    return output


def conversion():
    """
    Perform the conversion from MEBES1 to MEBES3 format.

    This function runs the necessary commands to convert mebes1 files to .cflt files,
    then converts .cflt files to the new MEBES3 format. It also handles moving old
    mebes1 files to an original_files directory.
    """
    try:
        # Convert all .?? files to .cflt
        print("Running readfile command...")
        output = run_command("readfile -input *.??")
        print(output)
        output = handle_readfile_prompts(output)

        # Convert .cflt files to new MEBES3 format
        print("Running writefile command...")
        output = run_command("writefile *.cflt")
        print(output)
        output = handle_readfile_prompts(output)
        print(output)
        # End of script
        print("Running exit command...")
        run_command("exit")

        # Find original_files folder, if not present, create it and move all *.o0 old files there
        if not os.path.exists("original_files"):
            print("Creating original_files folder...")
            os.mkdir("original_files")

        print("Moving original files to 'original_files' folder...")
        for file in os.listdir("."):
            if file.endswith(".o0") or file.endswith(".cflt"):
                shutil.move(file, "original_files/")
                print(f"Moved {file} to /original_files")
    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        sys.exit(1)


def get_release_verison():

    """Returns the release version from the $secret/releaseTag.txt""" #anonymized

    with open(
        os.getenv("secret") + "/secret/" + "/releaseTag.txt" #anonymized
    ) as releaseTagTxt:

        for line in releaseTagTxt:

            if line.startswith("secret"): #anonymized

                return line.split(":")[1].strip()


def show_main_menu():
    print("\n")
    print("                       +-------------------+")
    print("                       |  Mebes Converter  |")
    print("  +--------------------+-------------------+--------------------+")
    print("  |   This script converts mebes1 to mebes3 files using cats.   |")
    print("  |   It should work universally across                         |")
    print("  |   all secret environments and if launched                   |")
    print("  |   outside ONCR env it allows the user                       |")
    print("  |   to select CATS version out of the list of options.        |")
    print("  +--+-------------------------------------------------------+--+")
    print("     |                                                       |   ")
    print("     |   Usage:                                              |   ")
    print("     |        Use this menu to select actions                |   ")
    print("     |                                                       |   ")
    print("     |   or run with an argument for quickstart:             |   ")
    print("     |        -run           Start the conversion            |   ")
    print("     |        -help, -h      Display help message            |   ")
    print("     |                                                       |   ")
    print("     +-------------------------------------------------------+   \n\n")


def interactive_menu():
    """
    Display an interactive menu for the user to choose the next action.
    """
    show_main_menu()
    while True:

        choice = input("Please enter your choice (r)un conversion, (h)elp, (q)uit): ")

        if choice == "r":
            check_files()
            set_default_envs()
            conversion()
            break
        elif choice == "h":
            show_help()
        elif choice == "q":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    """
    Main function to handle command-line arguments and run the appropriate functions.

    This function checks the command-line arguments and either displays the help message,
    runs the conversion process, or shows the main menu.
    """
    if len(sys.argv) == 1:
        interactive_menu()
    elif sys.argv[1] == "-help":
        show_help()
    elif sys.argv[1] == "-run":
        check_files()
        set_default_envs()
        conversion()


if __name__ == "__main__":
    main()
