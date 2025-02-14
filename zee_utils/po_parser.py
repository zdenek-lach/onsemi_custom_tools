#!/usr/bin/env python
import re
import sys


def parse_po_file(file_to_parse_path):
    """
    Parses the provided PO file and extracts relevant information.

    Args:
        file_to_parse_path (str): The path to the PO file.

    Returns:
        dict: A dictionary containing the extracted information.
    """
    with open(file_to_parse_path, "r") as file:
        content = file.readlines()

    # Initialize variables
    vendor = None
    po_number = None
    requestor = None
    department = None
    ou_cc = None
    po_item_no = None
    dollar_amount = None
    reticle_count = 0
    total_li_cost = None
    maskset = None
    magnification = None
    layers = []
    grade = None
    total_cost = 0

    # Iterate through lines to find the required information
    for i, line in enumerate(content):
        # Extract vendor
        if "VENDOR:" in line:
            vendor_line_index = i + 1
            vendor_start_index = line.index("VENDOR:")
            vendor_line = content[vendor_line_index]
            vendor = (
                re.search(r"\S+\s+\S+", vendor_line[vendor_start_index:])
                .group()
                .split(" ")[0]
                .strip()
            )

        # Extract PO number
        if "P.O. #:" in line:
            po_number_line_index = i + 1
            po_number_start_index = line.index("P.O. #:")
            po_number_line = content[po_number_line_index]
            po_number = (
                re.search(r"\d+", po_number_line[po_number_start_index:])
                .group()
                .split(" ")[0]
                .strip()
            )

        # Extract requestor
        if "REQUESTOR:" in line:
            requestor_line_index = i + 1
            requestor_start_index = line.index("REQUESTOR:")
            requestor_line = content[requestor_line_index]
            # Adjust the start index if the character before the requestor's name is not "|" or " "
            if requestor_line[requestor_start_index] != "|" or " ":
                requestor_start_index -= 1
            requestor = (
                re.search(r"\S+\s+\S+", requestor_line[requestor_start_index:])
                .group()
                .strip()
            )

        # Extract department
        if "DEPT:" in line:
            department_line_index = i + 1
            department_start_index = line.index("DEPT:")
            department_line = content[department_line_index]
            department = (
                re.search(r"\S+", department_line[department_start_index:])
                .group()
                .split(" ")[0]
                .strip()
            )

        # Extract OU and CC and merge them
        if "OU:" in line and "CC:" in line:
            ou_cc_line_index = i + 1
            ou_cc_start_index_ou = line.index("OU:")
            ou_cc_start_index_cc = line.index("CC:")
            ou_cc_line = content[ou_cc_line_index]
            ou = re.search(r"\d+", ou_cc_line[ou_cc_start_index_ou:]).group().strip()
            cc = re.search(r"\d+", ou_cc_line[ou_cc_start_index_cc:]).group().strip()
            ou_cc = f"{ou}-{cc}"

        # Extract data from item lines
        if re.match(r"\|\s+\d+\s+[A-Za-z]{2}\d{2}", line):
            parts = [
                part.strip()
                for part in line.split("|") and line.split(" ")
                if part and part != "|"
            ]

            if parts:
                try:
                    maskset = parts[1]
                    layer_name = parts[2]
                    magnification = parts[4]
                    grade = parts[8]
                    li_cost = parts[9]
                    total_li_cost = parts[10]
                    quantity = parts[11]
                    dollar_amount = parts[13]
                    layers.append(
                        {"name": layer_name, "quantity": quantity, "price": li_cost}
                    )
                    reticle_count = layers.__len__()
                except IndexError as ie:
                    print(f"IndexError caught: [{ie}]")
                    pass
        # Extract total cost
        if "T O T A L" in line:
            total_cost_match = re.search(r"T O T A L\s+(\d+\.\d{2})", line)
            if total_cost_match:
                total_cost = float(total_cost_match.group(1))

    return {
        "vendor": vendor,
        "po_number": po_number,
        "requestor": requestor,
        "department": department,
        "ou_cc": ou_cc,
        "maskset": maskset,
        "magnification": magnification,
        "layers": layers,
        "grade": grade,
        "total_cost": total_cost,
        "total_li_cost": total_li_cost,
        "dollar_amount": dollar_amount,
        "reticle_count": reticle_count,
    }


def print_po(po):
    """
    Prints the parsed PO information in a nicely formatted way.

    Args:
        po (dict): The parsed PO information.
    """
    print("Purchase Order Information:")
    print(f"Vendor: {po['vendor']}")
    print(f"PO Number: {po['po_number']}")
    print(f"Requestor: {po['requestor']}")
    print(f"Department: {po['department']}")
    print(f"OU-CC: {po['ou_cc']}")
    print(f"Maskset: {po['maskset']}")
    print(f"Magnification: {po['magnification']}")
    print(f"Grade: {po['grade']}")
    print(f"Number of reticles: {po['reticle_count']}")
    print("Layers:")
    for layer in po["layers"]:
        print(
            f"\t- Name: {layer['name']}, Quantity: {layer['quantity']}, Price: {layer['price']}"
        )
    print(f"Total Cost: {po['total_cost']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python po_parser.py <path_to_po_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    po_info = parse_po_file(file_path)
    print_po(po_info)
