#Parts of the code in this model were generated with the assistance of AI and subsequently revised and validated by the author.

import xml.etree.ElementTree as ET
import csv
import os
import xml.dom.minidom
import sys
import shutil


def format_xml(filename):
    """Formats the XML file using minidom for pretty printing."""
    with open(filename, 'r', encoding='utf-8') as f:
        xml_string = f.read()

    # Do not parse if the file is empty
    if not xml_string.strip():
        return

    dom = xml.dom.minidom.parseString(xml_string)
    pretty_xml_as_string = dom.toprettyxml(indent="  ")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_as_string)


def remove_persons_from_xml(updated_csv, main_output_path, second_output_path):
    """
    Reads a list of PIDs from a CSV file and completely removes the corresponding <person> elements from the XML file.
    """
    # Note: This script now directly modifies the main_output_path file.
    # We assume main_output_path is both the source and destination file.
    original_xml_path = main_output_path

    # --- 1. Read the set of PIDs to be deleted ---
    try:
        with open(updated_csv, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            headers = next(reader)

            if 'PID' not in headers:
                raise ValueError("Error: Required column name 'PID' is missing in the CSV file.")

            pid_index = headers.index('PID')
            pid_set_to_delete = set(row[pid_index] for row in reader if row[pid_index])
            print(f"Found {len(pid_set_to_delete)} PIDs to be deleted from the XML.")

    except FileNotFoundError:
        sys.stderr.write(f"Error: CSV file not found at '{updated_csv}'\n")
        sys.exit(1)

    # --- 2. Read and parse the XML file ---
    try:
        population = ET.parse(original_xml_path)
        root = population.getroot()
    except (FileNotFoundError, ET.ParseError):
        sys.stderr.write(f"Error: XML file not found or corrupted at '{original_xml_path}'\n")
        # If the original XML does not exist, there is nothing to delete.
        return

    # Find and delete the entire <person> element ---
    # First, find all person elements to be removed
    persons_to_remove = [person for person in root.findall('person') if person.get('ID') in pid_set_to_delete]

    # Then, remove them from the root element
    if persons_to_remove:
        print(f"Deleting plans for {len(persons_to_remove)} persons from the XML...")
        for person in persons_to_remove:
            root.remove(person)
    else:
        print("No persons matching the PIDs in the CSV were found in the XML.")

    # --- 4. Write the updated content back to the main file ---
    os.makedirs(os.path.dirname(main_output_path), exist_ok=True)
    population.write(main_output_path, encoding='utf-8', xml_declaration=True)
    format_xml(main_output_path)
    print(f"Main file '{main_output_path}' has been updated.")

    # --- 5. Copy the updated main file to the secondary path ---
    try:
        second_output_dir = os.path.dirname(second_output_path)
        if second_output_dir and not os.path.exists(second_output_dir):
            os.makedirs(second_output_dir)
        shutil.copy2(main_output_path, second_output_path)
        print(f"Updated file has been copied to '{second_output_path}'.")
    except Exception as e:
        sys.stderr.write(f"Error: Failed to copy file to the secondary path: {e}\n")
        sys.exit(1)
