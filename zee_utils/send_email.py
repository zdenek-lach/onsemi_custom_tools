#!/usr/bin/env python
import argparse
import os
import pwd
import re
import shutil
import subprocess
import smtplib
import sys

import po_parser
import file_op_z
import utilz
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class Person:
    def __init__(self, first_name, last_name, phone, email):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email


# Create the dictionary with person details
RDP_secret_TEAM_MEMBERS = {
    "user1": Person("First", "Last", "secret", "secret"),  #anonymized
    "user2": Person("First", "Last", "secret", "secret"),  #anonymized
    "user3": Person("First", "Last", "secret", "secret"),  #anonymized
    "user4": Person("First", "Last", "secret", "secret"),  #anonymized
    "user5": Person("First", "Last", "secret", "secret"),  #anonymized
}


def get_full_user_details(username):
    """
    Get detailed information about a user.

    This function retrieves detailed information about a user from the system's
    passwd entry and additional details from the RDP_secret_TEAM_MEMBERS dictionary.
    It returns a dictionary containing the user's details, including username,
    encrypted password, user ID, group ID, full name, first name, last name,
    home directory, shell, phone number, and email address.

    Args:
        username (str): The username of the user to retrieve details for.

    Returns:
        dict: A dictionary containing the user's details, or None if the user
              does not exist or an error occurs.

    Raises:
        subprocess.CalledProcessError: If an error occurs while retrieving the
                                       passwd entry for the user.

    Example:
        >>> get_full_user_details("username")
        {
            'username': 'username',
            'encrypted_password': 'x',
            'user_id': 'XXXX',
            'group_id': 'XXXX',
            'full_name': 'first_name last_name',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'home_directory': '/home/username',
            'shell': '/bin/bash',
            'phone': 'XXX XX XXXX',
            'email': 'first_name.last_name@domain.com'
        }
    """
    try:
        # Get user details from the passwd entry
        passwd_entry = (
            subprocess.check_output(["getent", "passwd", username]).decode().strip()
        )

        # Split passwd entry into fields
        fields = passwd_entry.split(":")

        # Assign fields to descriptive variable names
        username = fields[0]  # Username - often used in logs and id commands
        encrypted_password = fields[
            1
        ]  # Encrypted password (usually 'x' if shadow passwords are used)
        user_id = fields[2]  # User ID (UID)
        group_id = fields[3]  # Primary Group ID (GID)
        user_info = fields[4]  # User Information (full name, etc.)
        home_directory = fields[5]  # Home directory
        shell = fields[6]  # User's login shell

        # Extract the full name, first name, and last name from the RDP_secret_TEAM_MEMBERS dictionary
        person = RDP_secret_TEAM_MEMBERS.get(username)
        if person:
            full_name = f"{person.first_name} {person.last_name}"
            first_name = person.first_name
            last_name = person.last_name
        else:
            # Fallback to extracting from user_info if not found in the dictionary
            full_name = user_info.split(",")[
                0
            ].strip()  # Take the first part before any comma
            if " " in full_name:
                first_name, last_name = full_name.split(" ", 1)
            else:
                first_name = full_name
                last_name = ""  # No last name provided

        # Clean up any potential trailing information
        last_name = last_name.split("-")[
            0
        ].strip()  # Remove "-<USERNAME>" from last name if exists

        # Return the user details as a dictionary
        return {
            "username": username,
            "encrypted_password": encrypted_password,
            "user_id": user_id,
            "group_id": group_id,
            "full_name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "home_directory": home_directory,
            "shell": shell,
            "phone": person.phone,
            "email": person.email,
        }

    except subprocess.CalledProcessError as e:
        # Handle error if the user does not exist
        utilz.printer(
            message=f"Error retrieving details for user '{username}': {e}",
            log_type=utilz.Type.ERROR,
        )
        return None


def load_file(filename):
    """
    Load a file and yield lines as lists of words.

    This function checks if the specified file exists. If it does, it reads the file
    and returns a list of lines, where each line is split into a list of words.
    If the file does not exist, it logs an error message and returns an empty list.

    Args:
        filename (str): The path to the file to be loaded.

    Returns:
        list: A list of lines, where each line is a list of words. Returns an empty
              list if the file does not exist.

    Example:
        >>> load_file("example.txt")
        [['This', 'is', 'a', 'line'], ['Another', 'line', 'here']]
    """
    if not os.path.isfile(filename):
        utilz.printer(message=f"{filename} does not exist", log_type=utilz.Type.ERROR)
        return []

    with open(filename, "r") as file:
        return [line.split() for line in file]


def extract_mask_layers(po_lines):
    """
    Extract mask layers from the given lines.

    This function takes a list of lines (each line being a list of words) and
    extracts mask layers that match the pattern "P\\d+[A-Z]?" (e.g., P1, P2A).
    It returns a list of all extracted mask layers.

    Args:
        po_lines (list): A list of lines, where each line is a list of words.

    Returns:
        list: A list of extracted mask layers that match the pattern.

    Example:
        >>> extract_mask_layers([['P1', 'some', 'text'], ['P2A', 'more', 'text']])
        ['P1', 'P2A']
    """
    pattern = re.compile(r"P\d+[A-Z]?")
    extracted_mask_layers = []

    for line in po_lines:
        line_str = " ".join(line)
        matches = pattern.findall(line_str)
        extracted_mask_layers.extend(matches)

    return extracted_mask_layers


def determine_shipping_address_string(fab):
    """
    Determine the shipping address based on the fab type.

    This function returns the shipping address and a description based on the
    specified fab type. It supports "secret" and "secret" fab types.

    Args:
        fab (str): The fab type ("secret" or "secret").

    Returns:
        tuple: A tuple containing the shipping address string and a description.

    Raises:
        ValueError: If an invalid fab type is specified.

    Example:
        >>> determine_shipping_address_string("secret")
        ('Ship reticles to: secret, secret<br>...',
         'secret in the secret')
    """
    if fab == "secret1":
        return (
            f"""\
            Ship reticles to: secret<br>  #anonymized
            {'&nbsp;' * 18}secret<br>  #anonymized
            {'&nbsp;' * 18}secret<br>  #anonymized
            {'&nbsp;' * 18}Attention: secret""",  #anonymized
            "secret",  #anonymized
        )
    elif fab == "secret2":
        return (
            f"""\
            Ship reticles to: secret<br>  #anonymized
            {'&nbsp;' * 18}Attn: secret / secret""",  #anonymized
            "secret",  #anonymized
        )
    raise ValueError("Invalid fab specified.")


def select_vendor(po_lines):
    """
    Determine the vendor based on PO content.

    This function checks the content of the purchase order (PO) lines and
    determines the vendor based on predefined keywords.

    Args:
        po_lines (list): A list of lines from the purchase order.

    Returns:
        str: The name of the vendor.

    Raises:
        ValueError: If no matching vendor is found.

    Example:
        >>> select_vendor([[], [], [], [], ['secret']])
        'secret'
    """
    vendors = {
        "Vendor1": ["secret", "secret", "secret"],  #anonymized
        "Vendor2": ["secret", "secret", "secret", "secret"],  #anonymized
        "Vendor3": [  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
        ],
    }

    for vendor_name, items in vendors.items():
        if any(item in po_lines[4] for item in items):
            return vendor_name
    raise ValueError("No matching vendor found.")


def determine_grade_and_parameters(po_line):
    """
    Determine the stepper, fab, and magnification based on grade.

    This function analyzes the purchase order (PO) line to determine the stepper,
    fab, and magnification based on predefined grades.

    Args:
        po_line (list): A list of items from the purchase order line.

    Returns:
        tuple: A tuple containing the stepper, fab, magnification, and grade item.

    Raises:
        ValueError: If the grade does not match any available grades.

    Example:
        >>> determine_grade_and_parameters(['MS'])
        ('secret', 'secret', '5', 'secret')
    """
    grades = {
        "Grade1": ["secret", "secret"],  #anonymized
        "Grade2": ["secret"],  #anonymized
        "Grade3": ["secret", "secret", "secret"],  #anonymized
        "Grade4": ["secret", "secret"],  #anonymized
        "Grade5": ["secret", "secret"],  #anonymized
        "Grade6": ["secret"],  #anonymized
    }

    for grade_name, items in grades.items():
        for item in po_line:
            if item in items:  #anonymized
                if grade_name == "Grade1":
                    return "secret", "secret", "5", item  #anonymized
                elif grade_name == "Grade2":
                    return "secret", "secret", "2", item  #anonymized
                elif grade_name == "Grade3":
                    return "secret", "secret", "5", item  #anonymized
                elif grade_name == "Grade4":
                    return "secret", "secret", "1", item  #anonymized
                elif grade_name == "Grade5":
                    return "secret", "secret", "1", item  #anonymized
                elif grade_name == "Grade6":
                    return "secret", "secret", "1", item  #anonymized
    raise ValueError("Grade does not match any available grades.")


def get_vendor_name(vendor):
    """
    Determine the correct vendor name based on the provided vendor string.

    This function maps a given vendor string to the correct vendor name based on
    predefined vendor lists.

    Args:
        vendor (str): The vendor string to be mapped.

    Returns:
        str: The correct vendor name, or None if no match is found.

    Example:
        >>> get_vendor_name("secret")
        'secret'
    """
    vendors = {
        "Vendor1": ["secret", "secret", "secret"],  #anonymized
        "Vendor2": ["secret", "secret", "secret", "secret"],  #anonymized
        "Vendor3": [  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
        ],
    }

    for key, values in vendors.items():
        if vendor in values:
            return key
    return None


def select_email_contacts(vendor, fab):
    """
    Determine email contacts based on vendor and fab.

    This function determines the appropriate email contacts based on the provided
    vendor and fab type. It returns a list of email addresses for the specified
    vendor and fab. If no matching contacts are found, it returns a message indicating
    the failure to determine email addresses.

    Args:
        vendor (str): The vendor name.
        fab (str): The fab type ("secret" or "secret").

    Returns:
        list: A list of email addresses for the specified vendor and fab.

    Example:
        >>> select_email_contacts("secret", "secret")
        ['secret']
    """
    contacts = []
    vendor_name = get_vendor_name(vendor)

    if vendor_name == "Vendor1":
        contacts.append("secret")  #anonymized
    elif vendor_name == "Vendor2":
        contacts.extend(
            ["secret", "secret"]  #anonymized
        )
    elif vendor_name == "Vendor3":
        if fab == "secret1":
            contacts.extend(
                ["secret", "secret"]  #anonymized
            )
        else:  # FAB is secret2?
            contacts.extend(
                ["secret", "secret"]  #anonymized
            )
    if not contacts:
        contacts.append(
            f"Failed to determine email address! Supplied information: vendor: '{vendor}' and fab: '{fab}'"
        )
    return contacts


def get_cc_contacts(fab):
    """
    Get CC contacts based on the fab.

    This function returns a list of CC (carbon copy) email contacts based on the
    specified fab type. It includes common secret contacts and additional contacts
    specific to the fab type ("secret" or "secret").

    Args:
        fab (str): The fab type ("secret" or "secret").

    Returns:
        list: A list of CC email addresses for the specified fab.

    Example:
        >>> get_cc_contacts("secret")
        ['secret', 'secret', ..., 'secret']
    """
    # Define the common RDP_secret contacts

    rdp_secret_contacts = []

    # Use a for loop to append each email to the rdp_secret_contacts list
    for member in RDP_secret_TEAM_MEMBERS.values():
        rdp_secret_contacts.append(member.email)

    if fab == "secret1":
        return rdp_secret_contacts + [
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
        ]
    elif fab == "secret2":
        return rdp_secret_contacts + [
            "secret",  #anonymized
            "secret",  #anonymized
            "secret",  #anonymized
        ]
    return ["secret"]  #anonymized


def create_email_body(
    contacts,
    cc_contacts,
    stepper,
    urgency,
    address,
    user_details,
    country,
    sent_file,
    grade,
    po_info,
):
    """
    Prepare the body of the email using provided information.

    This function constructs the HTML body of an email using the provided
    information such as contacts, stepper, urgency, address, user details,
    country, sent file, grade, and purchase order (PO) information.

    Args:
        contacts (list): List of email addresses to send the email to.
        cc_contacts (list): List of email addresses to CC.
        stepper (str): The stepper type.
        urgency (str): The urgency of the order.
        address (str): The shipping address.
        user_details (dict): Dictionary containing user details.
        country (str): The country of the fab.
        sent_file (str): The name of the sent file.
        grade (str): The mask grade.
        po_info (dict): Dictionary containing purchase order information.

    Returns:
        str: The HTML body of the email.

    Example:
        >>> create_email_body(
                contacts=["example@example.com"],
                cc_contacts=["cc@example.com"],
                stepper="secret",
                urgency="Standard",
                address="123 Street, City, Country",
                user_details={"full_name": "John Doe", "email": "john.doe@example.com"},
                country="secret",
                sent_file="file.tar.gz",
                grade="A",
                po_info={"vendor": "Vendor", "maskset": "MaskSet", "layers": [{"name": "Layer1", "price": 100}]}
            )
        '<html>...</html>'
    """

    twitter = f'<a href="secret" style="color: #2A78B8;text-decoration: underline;">X</a>'  #anonymized
    facebook = f'<a href="secret" style="color: #2A78B8;text-decoration: underline;">Facebook</a>'  #anonymized
    linkedin = f'<a href="secret" style="color: #2A78B8;text-decoration: underline;">LinkedIn</a>'  #anonymized
    instagram = f'<a href="secret" style="color: #2A78B8;text-decoration: underline;">Instagram</a>'  #anonymized
    youtube = f'<a href="secret" style="color: #2A78B8;text-decoration: underline;">YouTube</a>'  #anonymized
    blog = f'<a href="secret" style="color: #2A78B8;text-decoration: underline;">Blog</a>'  #anonymized

    secret_logo = f"secret"  #anonymized
    with open(secret_logo, "rb") as f:
        img_data = f.read()
    logo = MIMEImage(img_data, secret_logo)
    logo.add_header("Content-ID", "<onlogo>")
    image = f'<img src="cid:onlogo" alt="Logo" style="width: 150px">'

    signature = f"""\
    <div style="font-family: Arial, sans-serif; color: #000000; font-size: 11pt;">
     <table>
      <tr>
       <td style="border-right: 3px solid black;padding-right: 5px;">{image}</td>
       <td style="padding-left: 5px; line-height: 1.4">
        <strong style="font-size: 11pt;">{user_details.get('full_name')}</strong><br>
        <strong style="font-size: 11pt;">Mask Preparation Engineer</strong><br>
        <span style="font-size: 8pt;">Building V12 <b>|</b> secret <b>|</b> secret <b>|</b> secret<br>  #anonymized
        <span style="font-size: 8pt;">{user_details.get('phone')} (O) <b>|</b> <a href="mailto:{user_details.get('email')}" style="color: #2A78B8;text-decoration: none;">{user_details.get('email')}</a></span>
        </td>
      </tr>
     </table>
     <p style="font-size: 9.5pt;font-weight:bold;">
    Follow us: {facebook} | {linkedin} | {twitter} | {instagram} | {youtube} | {blog}</p>
     <p style="font-size: 7.5pt; line-height: 1;">
    This email and any attachments may contain confidential and/or proprietary information and are solely for the review and use of the intended recipient. If you<br> have received this email in error, please notify the sender and destroy this email and any copies. Any disclosure, copying, or taking of any action in reliance<br> on an email received in error is strictly prohibited.</p>
    </div>"""

    mail_body = f"""\
<head>
    <style type="text/css">
        .tg{{font-family:"Courier New";text-align:left;vertical-align:top}}
        .tg .tg-e{{font-size: 4px}}
   </style>
</head>
<body>
    <p>This email need to be forwarder to the vendor and put people in CC. <b>Don't forget to delete "FW:" from Subject after forwarding</b></p>
    <p>Send email to:<br> {'; '.join(contacts)}</p>
    <p>Put in CC:<br> {'; '.join(cc_contacts)} + all listed in RBOM</p>
    <p>{'List of ordered layers: ' + ', '.join(layer['name'] for layer in po_info['layers']) if len(po_info['layers']) > 1 else 'Ordered layer: ' + po_info['layers'][0]['name']}</p>
    <p><h2><b>DOUBLE CHECK THE PO DOCUMENT!</h2> </b></p>
    <p>{"-" * 100}</p>
    <table class="tg">
        <tr>
            <td>To:</td>
            <td>{get_vendor_name(po_info['vendor'])} Customer Support/Order Entry</td>
        </tr>
        <tr><td colspan="2">&nbsp;</td></tr>
        <tr>
            <td>From:</td>
            <td>{user_details.get('full_name')}</td>
        </tr>
        <tr>
            <td></td>
            <td>Company, secret, secret</td>  #anonymized
        </tr>
        <tr><td colspan="2">&nbsp;</td></tr>
        <tr>
            <td>Re:</td>
             <td><b>{po_info['maskset']}</b> <b>{po_info['layers'][0]['name'] if po_info['reticle_count'] == 1 else ''}</b> {po_info.get('magnification')}X {stepper} Mask Order</td>
        </tr>
        <tr><td colspan="2">&nbsp;</td></tr>
            <td></td>
            <td>The data file <b>{'FILL IN FILE NAME' if sent_file is None else sent_file}</b> has been placed in the {get_vendor_name(po_info['vendor'])}/company ftp directory.</td>
        </tr>
        <tr><td class="tg-e" colspan="2">&nbsp;</td></tr>
        <tr>
            <td></td>
            <td>This file contains the etec data, job deck, and purchase order for the <b>{len(po_info['layers'])}</b> new reticle{"s" if len(po_info['layers']) > 1 else ""}. This is for set <b>{po_info['maskset']}</b> for the company, {country}</td>
        </tr>
        <tr><td  class="tg-e"colspan="2">&nbsp;</td></tr>
        <tr>
            <td></td>
            <td>Mask Grade is <b>{grade}</b> and the price is <b>${po_info['layers'][0]['price']}</b> per reticle.</td>
        </tr>
        <tr><td class="tg-e" colspan="2">&nbsp;</td></tr>
        <tr>
            <td></td>
            <td>{urgency}</td>
        </tr>
        <tr><td class="tg-e" colspan="2">&nbsp;</td></tr>
        <tr>
            <td></td>
            <td>{address}</td>
        </tr>
        <tr><td colspan="2">&nbsp;</td></tr>
        <tr>
            <td colspan="2">Contact {user_details.get('full_name')} if you have any questions regarding this order.</td>
        </tr>
        <tr><td colspan="2">&nbsp;</td></tr>
        <tr>
            <td colspan="2">Best regards,</td>
        </tr>

    </table>
  {signature}
</body>
</html>
"""
    return mail_body


def send_email(body, stepper, po_pdf_full_path, fab, user_details, po_info):
    """
    Send the email with the prepared body and attachments.

    This function sends an email with the provided HTML body and attachments,
    including a logo image and a PDF file. The email is sent to the user's email address.

    Args:
        body (str): The HTML body of the email.
        stepper (str): The stepper type.
        po_pdf_full_path (str): The full path to the PO PDF file.
        fab (str): The fab type ("secret" or "secret").
        user_details (dict): Dictionary containing user details.
        po_info (dict): Dictionary containing purchase order information.

    Example:
        >>> send_email(
                body="<html>...</html>",
                stepper="secret",
                po_pdf_full_path="/path/to/po.pdf",
                fab="secret",
                user_details={"full_name": "John Doe", "email": "john.doe@example.com"},
                po_info={"vendor": "Vendor", "maskset": "MaskSet", "layers": [{"name": "Layer1", "price": 100}]}
            )
    """
    # Set up email parameters
    msg = MIMEMultipart()
    msg["From"] = user_details.get("email")
    msg["To"] = user_details.get("email")
    msg[
        "Subject"
    ] = f"{po_info.get('maskset')} {po_info.get('magnification')}X New {stepper} Mask Order for {fab}"

    # Attach the body message
    body_text = MIMEText(body, "html")
    msg.attach(body_text)
    # print(msg) uncomment for testing
    # Attach the logo
    secret_logo_path = f"secret"  #anonymized
    with open(secret_logo_path, "rb") as f:
        img_data = f.read()
    logo = MIMEImage(img_data, secret_logo_path)
    logo.add_header("Content-ID", "<onlogo>")
    msg.attach(logo)

    # Attach the PDF file
    with open(po_pdf_full_path, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="pdf")
        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=os.path.basename(po_pdf_full_path),
        )
        msg.attach(attachment)
    # comment following 2 lines for testing
    with smtplib.SMTP("localhost") as smtp:
        smtp.send_message(msg)
    utilz.printer(
        message=f"Email sent successfully to {user_details.get('email')}",
        log_type=utilz.Type.INFO,
    )


def main():
    """
    Main function to execute the script.

    This function orchestrates the execution of the script, including retrieving
    user details, parsing purchase order (PO) files, determining shipping address,
    and sending an email with the prepared body and attachments.
    """
    # Get user info
    user_details = get_full_user_details("secret")  #anonymized
    # Find .po files
    po_files = file_op_z.find_files(search_directory="secret", extension=".po")  #anonymized
    if len(po_files) != 1:
        utilz.printer(
            message=f"There must be exactly one *.po file.", log_type=utilz.Type.ERROR
        )
        exit()

    po_file = po_files[0]
    po_info = po_parser.parse_po_file(po_file)

    # Print the extracted information
    po_parser.print_po(po_info)

    # Ask about urgency
    use_expedite_mode = (
        input("Do you want to process set in expedite mode? [y/n]: ").strip().lower()
    )

    # List of allowed extensions to search for
    extensions = [".tar.gz"] #, ".tgz", ".tar"

    # Find sent compressed files
    sent_files = []
    for ext in extensions:
        sent_files = file_op_z.find_files(search_directory=os.getcwd(), extension=ext)
        if sent_files:
            break
        sent_files = file_op_z.find_files(
            search_directory=os.path.dirname(os.path.dirname(os.getcwd())),
            extension=ext,
        )
        if sent_files:
            break

    if len(sent_files)<1:
        utilz.printer(
            message="The *.tar.gz file does not exist.", log_type=utilz.Type.ERROR
        )

        if input("Would you like to have the tar archives generated for you? (y/n): ") == 'y':
            (tar_path_review, tar_path_vendor) = utilz.tar_op_finale()
            utilz.printer(message=f"Generated '{tar_path_review}' file for review and '{tar_path_vendor}' for the vendor email.", log_type=utilz.Type.INFO)
            if tar_path_vendor:
                selected_file = tar_path_vendor
            else:
                sent_files = None
                pass
        else:
            sent_files = None
            pass

    try:
        if sent_files is None:
            selected_file = None
        elif len(sent_files) > 1:
            utilz.printer(
                message="Multiple archive files found:", log_type=utilz.Type.INFO
            )

            for idx, file in enumerate(sent_files):
                print(f"{idx + 1}: {file}")
            selection = (
                int(input("Select which file to use (enter the number): ")) - 1
            )
            selected_file = sent_files[selection]
        elif len(sent_files) == 1:
            selected_file = sent_files[0]
    except ValueError:
        selected_file = None
        pass

    utilz.printer(message=f"Selected file: {selected_file}", log_type=utilz.Type.INFO)
    # Find PO PDF in ../forms
    forms_dir = "secret"  #anonymized
    utilz.printer(
        message=f"Looking for forms PDF in forms folder in '{os.path.join(os.path.dirname(os.getcwd()))}/forms",
        log_type=utilz.Type.INFO,
    )
    pdf_files = file_op_z.find_files(search_directory=forms_dir, extension=".pdf")
    if not pdf_files:
        utilz.printer(
            message=f"No PDF files found in ../forms.", log_type=utilz.Type.ERROR
        )
        if (
            input("Would you like to create have it created automatically? (y)es/(n)o:")
            .strip()
            .lower()
            == "y"
        ):
            subprocess.run(["secret", po_file], cwd=os.getcwd())
            pdf_files = [f for f in os.listdir(os.getcwd()) if f.endswith(".pdf")]
            if len(pdf_files) != 1:
                utilz.printer(
                    message=f"Expected exactly one .pdf file, found {len(pdf_files)}",
                    log_type=utilz.Type.ERROR,
                )
                exit("Something went wrong when creating the PDF from PO document.")

            utilz.printer(
                message=f"Moving PDF file {pdf_files[0]} from {os.getcwd()} to {os.path.join(forms_dir, pdf_files[0])}",
                log_type=utilz.Type.INFO,
            )
            shutil.move(
                os.path.join(os.getcwd(), pdf_files[0]),
                os.path.join(forms_dir, pdf_files[0]),
            )

    po_pdf_full_path = "secret"  #anonymized

    # Get rid of the errors
    fab = None
    grade = None
    stepper = None
    country = None
    address = None

    try:
        # Determine stepper, fab, and magnification
        stepper, fab, mag, grade = determine_grade_and_parameters(
            load_file(po_file)[15]
        )
        utilz.printer(
            message=f"Found values for stepper: '{stepper}'", log_type=utilz.Type.INFO
        )
        utilz.printer(
            message=f"Found values for fab: '{fab}'", log_type=utilz.Type.INFO
        )
        utilz.printer(
            message=f"Found values for grade: '{grade}'", log_type=utilz.Type.INFO
        )
        # Determine shipping address
        address, country = determine_shipping_address_string(fab)
        address_log_format = address
        split_address = (
            address_log_format.replace("&nbsp;", "")
            .replace("            ", "")
            .replace("\n", " ")
            .split("<br> ")
        )

        if len(split_address) >= 2:
            log_address, log_attention = split_address[0], split_address[1]
        else:
            log_address, log_attention = split_address[0], ""

        utilz.printer(
            message=f"Found values for address: '{log_address}'",
            log_type=utilz.Type.INFO,
        )
        utilz.printer(message=f"'{log_attention}'", log_type=utilz.Type.INFO)
        utilz.printer(
            message=f"Found values for country: '{country}'", log_type=utilz.Type.INFO
        )
    except ValueError as e:
        utilz.printer(message=f"Error: '{e}", log_type=utilz.Type.ERROR)

    # Get email contacts
    contacts = select_email_contacts(po_info["vendor"], fab)
    utilz.printer(
        message=f"Found values for " f"contacts: '{contacts}'",
        log_type=utilz.Type.INFO,
    )
    cc_contacts = get_cc_contacts(fab)
    utilz.printer(
        message=f"Found values for " f"cc_contacts: '{cc_contacts}'",
        log_type=utilz.Type.INFO,
    )
    urgency = (
        f"<h2 style='color: red;'>Process reticle{'s' if po_info['reticle_count'] > 1 else ''} in expedite mode.</h2>"
        if use_expedite_mode == "y"
        else "The reticles can be processed using the standard cycle and delivery."
    )
    # Create email body
    email_body = create_email_body(
        user_details=user_details,
        contacts=contacts,
        cc_contacts=cc_contacts,
        stepper=stepper,
        urgency=urgency,
        address=address,
        country=country,
        sent_file=os.path.basename(selected_file),
        grade=grade,
        po_info=po_info,
    )

    # Send the email
    send_email(
        body=email_body,
        user_details=user_details,
        stepper=stepper,
        po_pdf_full_path=po_pdf_full_path,
        fab=fab,
        po_info=po_info,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        utilz.printer(
            message="Application forcefully terminated!", log_type=utilz.Type.ERROR
        )
