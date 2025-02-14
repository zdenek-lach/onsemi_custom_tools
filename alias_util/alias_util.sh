#!/bin/bash

# Define the file paths for the alias file and its backup
ALIAS_FILE="/home/$(whoami)/.aliases_personal"
BACKUP_FILE="/home/$(whoami)/.aliases_personal.bak"
TEMP_FILE=$(mktemp)


function ensure_alias_file_exists() {
    if [[ ! -f $ALIAS_FILE ]]; then
        read -p "Alias file does not exist. Do you want to create it? (y/n): " create_file
        if [[ $create_file == [yY] ]]; then
            touch $ALIAS_FILE
            echo "Alias file created at $ALIAS_FILE."
        else
            echo "Operation cancelled."
            exit 1
        fi
    fi
}

function list_aliases() {
    local colors=(31 32 33 34 35 36 37) # Array of color codes to use
    local num_colors=${#colors[@]} # Number of colors to use
    ensure_alias_file_exists
    clear
    echo ""
    echo "Current aliases:"
    # Read each alias line and print it with a random color
    grep '^alias ' $ALIAS_FILE | while IFS= read -r line || [[ -n "$line" ]]; do
        local color=${colors[$RANDOM % $num_colors]}
        echo -e "\033[${color}m${line}\033[0m"
    done
    echo ""
    echo "Press any key to continue."
    echo ""
    read -n 1
    clear
}

# Function to add a new alias to .personal_aliases
function add_alias() {
    echo ""
    ensure_alias_file_exists
    local alias_name
    local alias_command
    local alias_line
    local current_user=$(whoami)

   # Prompt user for alias name and command
    read -p "Name the new alias: " alias_name
    read -p "Command: " alias_command
    alias_line="alias $alias_name='$alias_command'"

    # Confirm addition of the new alias
    echo "New alias entry: $alias_line"
    read -p "Do you want to add this new alias? (y/n): " confirm
    if [[ $confirm == [yY] ]]; then
        echo "$alias_line" >> /home/"$current_user"/.aliases_personal
        echo "Alias added: $alias_line"
    else
        echo "Alias not added."
    fi
}

# Function to remove an alias (one or more) by line number
function remove_alias() {
    echo ""
    if [[ ! -f $ALIAS_FILE ]]; then
        echo "Alias file does not exist."
        exit 1
    fi

    # Backup the alias file
    cp $ALIAS_FILE "${ALIAS_FILE}.bak"
    echo "Current aliases:"
    # List aliases with line numbers
    grep '^alias ' $ALIAS_FILE | nl -w 4 -s ' ] ' -n ln | sed 's/^/   [   /'

    echo "Enter line numbers to remove, separated by spaces (or type 'x' to cancel):"
    read -a lines_to_remove

    if [[ " ${lines_to_remove[@]} " =~ " x " ]]; then
        echo "Operation cancelled."
        return
    fi

    TEMP_FILE=$(mktemp)
    line_number=1
    # Read each line and remove selected aliases
    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ "$line" =~ ^alias ]]; then
            if [[ ! " ${lines_to_remove[@]} " =~ " ${line_number} " ]]; then
                echo "$line" >> $TEMP_FILE
            else
                echo "Removed alias: $line"
            fi
            ((line_number++))
        else
            echo "$line" >> $TEMP_FILE
        fi
    done < $ALIAS_FILE

    mv $TEMP_FILE $ALIAS_FILE
    echo "Selected aliases removed. Original file backed up as ${ALIAS_FILE}.bak."
}

# Function to restore the alias file from a backup
function restore_backup() {
    echo ""
    if [[ -f $BACKUP_FILE ]]; then
        mv $BACKUP_FILE $ALIAS_FILE
        echo "Backup restored. Your aliases file has been reverted to the backup version."
    else
        echo "No backup found."
    fi
}

# Function to modify an existing alias
function modify_alias() {
    echo ""
    if [[ ! -f $ALIAS_FILE ]]; then
        echo "Alias file does not exist."
        exit 1
    fi
    # Backup the alias file
    cp $ALIAS_FILE "${ALIAS_FILE}.bak" 
    echo "Current aliases:"
    # List aliases with line numbers
    grep '^alias ' $ALIAS_FILE | nl -w 4 -s ' ] ' -n ln | sed 's/^/   [   /'
    echo "Enter the line number to modify, or type 'x' to cancel:"
    read line_number
    if [[ "$line_number" == "x" ]]; then
        echo "Operation cancelled."
        return
    fi

    alias_to_modify=$(grep '^alias ' $ALIAS_FILE | sed -n "${line_number}p")
    alias_name=$(echo "$alias_to_modify" | awk -F'=' '{print $1}' | sed 's/alias //')
    alias_command=$(echo "$alias_to_modify" | awk -F'=' '{print $2}')

    echo "Do you want to change the NAME OR the COMMAND? (N / C)"
    read choice
    case $choice in
        N|n)
            read -p "Please enter a new name: " new_name
            echo "Do you want to keep the original command ($alias_command)? (Y / N)"
            read keep_command
            if [[ "$keep_command" == "Y" || "$keep_command" == "y" ]]; then
                new_alias="alias $new_name=$alias_command"
            else
                read -p "Please enter the new command: " new_command
                new_alias="alias $new_name='$new_command'"
            fi
            ;;
        C|c)
            read -p "Please enter the new command: " new_command
            new_alias="alias $alias_name='$new_command'"
            ;;
        *)
            echo "Invalid option"
            return
            ;;
    esac

    # Only modify if the alias has changed
    if [[ "$new_alias" != "$alias_to_modify" ]]; then
        new_alias_escaped=$(echo "$new_alias" | sed 's/[&/\]/\\&/g')
        sed -i "s|^alias $alias_name=.*|$new_alias_escaped|" $ALIAS_FILE
        echo "Alias modified: $new_alias"
    else
        echo "No changes made to the alias."
    fi
}

# Function to quit the script and optionally open a new terminal (deprecated)
function old_quit() {
    clear
    read -p "Do you want to open a new terminal? (y/n): " choice
    if [[ $choice == [yY] ]]; then
        if [[ "$(uname)" == "Linux" ]]; then
            if command -v gnome-terminal &> /dev/null; then
                gnome-terminal &
            elif command -v xterm &> /dev/null; then
                xterm &
            else
                echo "No supported terminal emulator found."
            fi
        elif [[ "$(uname)" == "Darwin" ]]; then
            open -a Terminal "$(pwd)"
        else
            echo "Unsupported OS"
        fi
    else 
        local colors=(31 32 33 34 35 36 37)  # Array of color codes
        local num_colors=${#colors[@]}
        local message="!! Don't forget to close the terminal and open a fresh one to see the changes !!"
        
        # Flashy banner for better visibility
        for i in {1..360}; do
            local color=${colors[$((RANDOM % num_colors))]}
            clear
            echo -e "\033[1;${color}m#####################################################################################\033[0m"
            echo -e "\033[1;${color}m#                                                                                   #\033[0m"
            echo -e "\033[1;${color}m#   Don't forget to CLOSE the terminal and open a fresh one to see the changes !!   #\033[0m"
            echo -e "\033[1;${color}m#                                                                                   #\033[0m"
            echo -e "\033[1;${color}m#####################################################################################\033[0m"
            sleep 0.1 
        done

        echo -en "\007"
    fi

    exit 0

}

# Function to quit the script and reload the terminal
function quit() {
    clear
    echo "Thank you for using Alias Util. " 
    sleep 1
    echo "Terminal reloaded."
    sleep 1
    exec bash
    exit 0
}
function show_usage() {
    clear
    local colors=(31 32 33 34 35 36 37 90 91 92 93 94 95 96 97)
    local num_colors=${#colors[@]}

    echo "---------------------------------------------"
    echo "|           How to Use This Script          |"
    echo "---------------------------------------------"
    echo "This script helps you manage your shell aliases efficiently. Below are the available options and their descriptions:"
    echo ""

    local options=(
        "1. List my aliases: "
        "Displays all current aliases in your .aliases_personal file with colorful output for better readability."
        "2. Add alias: "
        "Prompts you to enter a new alias name and the command it should execute. After confirmation, the new alias is added to your .aliases_personal file."
        "3. Modify alias: "
        "Allows you to change an existing alias. You can modify either the alias name or the command it executes. The script guides you through the process."
        "4. Delete alias: "
        "Enables you to remove one or more aliases. You will see a list of current aliases with line numbers, and you can specify which ones to delete by entering their corresponding line numbers."
        "5. Restore backup: "
        "Restores the .aliases_personal file from a backup. Use this option to revert changes by replacing the current alias file with the backup version."
        "6. Tutorial: "
        "Displays this detailed description of how to use the script and its various options."
        "7. Exit: "
        "Exits the script. If you have made changes to your aliases, you do not have to restart your terminal to see the effects."
    )

    for option in "${options[@]}"; do
        local color=${colors[$RANDOM % $num_colors]}
        echo -e "\033[${color}m${option}\033[0m"
        echo ""
    done

    echo "To navigate through the options, simply enter the number corresponding to the action you want to perform and follow the prompts."
    echo "---------------------------------------------"
    echo "Press any key to return to the menu."
    read -n 1
    clear
}


function show_pretty_menu() {
    echo "-------------------------------"
    echo "| - Alias Management Script - |"
    echo "-------------------------------"
    echo "|      1. List my aliases     |"
    echo "|      2. Add alias           |"
    echo "|      3. Modify alias        |"
    echo "|      4. Delete alias        |"
    echo "|      5. Restore backup      |"
    echo "|      6. Tutorial            |"
    echo "|      7. Exit                |"
    echo "-------------------------------"
    echo -n "Choose an option: "
    read choice
    case $choice in
        1) list_aliases ;;
        2) add_alias ;;
        3) modify_alias ;;
        4) remove_alias ;;
        5) restore_backup ;;
        6) show_usage ;;
        7) quit ;;
        *) echo "Invalid option" ;;
    esac
}


while true; do
    show_pretty_menu
done
