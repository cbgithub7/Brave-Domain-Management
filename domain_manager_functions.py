import subprocess
import json
import re

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

def add_domain(domain):
    # Check if the domain already exists
    existing_domains = fetch_existing_domains()
    if domain in existing_domains:
        return f"Domain '{domain}' already exists in the registry. No action taken."
    
    # Regex pattern to match valid domain formats
    domain_pattern = r"^([a-zA-Z0-9-]+\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"

    # Extract domain without URL prefix and path info
    cleaned_domain = re.sub(r'^(https?://)?(www\.)?', '', domain)  # Remove prefixes
    #removed_path_info = re.findall(r'/.+', cleaned_domain)  # Find path info
    cleaned_domain = re.sub(r'/.+', '', cleaned_domain)  # Remove path info

    # Extract cleaned prefixes and path info from the original input
    '''
    matched_prefixes = re.findall(r'^(https?://)?(www\.)?', domain)
    cleaned_prefixes = [''.join(prefix) for prefix in matched_prefixes]

    cleaned_info_msg = ""
    if cleaned_prefixes:
        cleaned_info_msg += f"Removed URL prefixes: {' '.join(cleaned_prefixes)}\n"
    if removed_path_info:
        cleaned_info_msg += f"Removed URL path: {' '.join(removed_path_info)}\n" 
    '''

    if not re.match(domain_pattern, cleaned_domain):
        return f"Invalid domain format: {domain}. Please use [subdomain].[domain].[TLD] format."

    result = execute_powershell_script("2", cleaned_domain)
    #return f"{cleaned_info_msg}\n{result.strip()}"
    return f"{result.strip()}"

def remove_domain(index):
    result = execute_powershell_script("3", index)
    return result.strip()