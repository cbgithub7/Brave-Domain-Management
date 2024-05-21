import subprocess
import json
import re
import csv
import os

def execute_powershell_script(action, *args):
    script_path = "Manage-DomainsInRegistry.ps1"
    command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path, action] + list(args)
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing PowerShell script: {e.stderr.strip()}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def check_registry_path():
    result = execute_powershell_script("5")
    return result

def check_brave_installation():
    result = execute_powershell_script("4")
    if "Brave is not installed" in result:
        return False
    else:
        return True

def fetch_existing_domains():
    result = execute_powershell_script("1")
    try:
        existing_domains = json.loads(result)
        return existing_domains
    except json.decoder.JSONDecodeError as e:
        return f"Error decoding JSON: {e}\nRaw response: {result}"

def clean_domain(domain):
    # Regex pattern to match valid domain formats
    domain_pattern = r"^([a-zA-Z0-9-]+\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"

    # Extract domain without URL prefix and path info
    cleaned_domain = re.sub(r'^(https?://)?(www\.)?', '', domain)  # Remove prefixes
    cleaned_domain = re.sub(r'/.+', '', cleaned_domain)  # Remove path info

    if not re.match(domain_pattern, cleaned_domain):
        raise ValueError(f"Invalid domain format: {domain}. Please use [subdomain].[domain].[TLD] format.")

    return cleaned_domain

def add_domain(domain):
    try:
        cleaned_domain = clean_domain(domain)
        result = execute_powershell_script("2", cleaned_domain)
        return result.strip()
    except ValueError as e:
        return str(e)

def remove_domain(index):
    result = execute_powershell_script("3", index)
    return result.strip()

def process_text_file(file_path, update_feedback):
    try:
        file_name = os.path.basename(file_path)  # Extract the file name
        with open(file_path, "r") as file:
            for line in file:
                domain = line.strip()
                result = add_domain(domain)
                yield file_name, result, domain  # Adjust the order of values being yielded
    except Exception as e:
        update_feedback(f"Error processing text file: {e}")

def process_csv_file(file_path, update_feedback):
    try:
        file_name = os.path.basename(file_path)  # Extract the file name
        with open(file_path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                domain = row[0].strip()  # Assuming the domain is in the first column
                result = add_domain(domain)
                yield file_name, result, domain  # Adjust the order of values being yielded
    except Exception as e:
        update_feedback(f"Error processing CSV file: {e}")

def process_json_file(file_path, update_feedback):
    try:
        file_name = os.path.basename(file_path)  # Extract the file name
        with open(file_path, "r") as file:
            data = json.load(file)
            for domain in data:
                result = add_domain(domain)
                yield file_name, result, domain  # Adjust the order of values being yielded
    except Exception as e:
        update_feedback(f"Error processing JSON file: {e}")

def undo_action():
    # Call PowerShell script to perform undo action
    try:
        subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "Manage-DomainsInRegistry.ps1", "Undo-Action"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing undo action: {e}")

def redo_action():
    # Call PowerShell script to perform redo action
    try:
        subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "Manage-DomainsInRegistry.ps1", "Redo-Action"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing redo action: {e}")
