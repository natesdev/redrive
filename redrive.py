#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import argparse

parser = argparse.ArgumentParser(
                    prog='Redrive',
                    description='Generates a direct download link for Google Drive.')

parser.add_argument('id', help='file ID')
parser.add_argument('-a', '--auto', action='store_true', help="after generating link automatically downloads the file")
parser.add_argument('-v', '--verbose', action='store_true', help="enable verbose output for debugging")
args = parser.parse_args()


id = args.id
auto = args.auto
verbose = args.verbose
url = f"https://drive.google.com/uc?export=download&id={id}"

def debug_log(text):
    """Prints debug messages if verbose mode is enabled."""
    if verbose:
        print(f"\033[92m[DEBUG]\033[0m {text}")

def get_uuid(url):
    """
    Retrieves the UUID from a Google Drive file page if a download warning is present.

    Args:
        url (str): The URL of the Google Drive file.
    
    Returns:
        str: The UUID if found, otherwise None.
    """
    uuid = None
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    warning_text = soup.find('p', class_='uc-warning-caption')
    if warning_text and "Google Drive has detected issues with your download" in warning_text.text:
        uuid_input = soup.find('input', {'name': 'uuid'})
        if uuid_input:
            uuid = uuid_input['value']
            debug_log(f"UUID found: {uuid}")            
        else:
            debug_log("UUID not found.")
    else:
        debug_log("No download warning found, proceeding without UUID.")

    return uuid

def get_filename(id):
    """
    Retrieves the filename of the Google Drive file using the Google Drive API.

    Args:
        id (str): The Google Drive file ID.
    
    Returns:
        str: The name of the file.
    """
    apiUrl = f"https://www.googleapis.com/drive/v2/files/{id}"
    params = {
        "fields": "title",
        "key": "AIzaSyC1eQ1xj69IdTMeii5r7brs3R90eck-m7k"
    }

    headers = {
        "Referer": "https://drive.google.com"
    }

    metadata_response = requests.get(apiUrl, params=params, headers=headers)
    metadata = metadata_response.json()

    filename = metadata.get("title", "downloaded_file")
    debug_log(filename)
    return filename

def download(id, uuid, filename):
    """
    Downloads the file from Google Drive using the generated download link.

    Args:
        id (str): The Google Drive file ID.
        uuid (str): The UUID required if a download warning is present.
        filename (str): The name of the file to save locally.
    """

    # Change the referer header to prevent redirecting to download confirmation
    headers = {
        "Referer": "https://drive.google.com"
    }
    if uuid:
        download_link = f"https://drive.usercontent.google.com/download?id={id}&export=download&authuser=0&confirm=t&uuid={uuid}"
    else:
        download_link = f"https://drive.google.com/uc?export=download&id={id}"
    debug_log(download_link)
    with requests.get(download_link, headers=headers, allow_redirects=True, stream=True) as file:
        file.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in file.iter_content(chunk_size=8192):
                f.write(chunk)

if (__name__ == '__main__'):
    uuid = get_uuid(url)
    get_filename(id)
    if auto:
        download(id, uuid, get_filename(id))
