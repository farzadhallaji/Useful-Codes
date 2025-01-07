import os
import requests
from bs4 import BeautifulSoup

# Define the base URL for downloading
BASE_URL = "https://www.cs.toronto.edu/~vmnih/data/"

# Load the HTML file
html_file = "road-dataset.html"

# Function to sanitize directory paths
def sanitize_path(path):
    return path.replace(':', '').replace('\\', '/').replace('?', '')

# Function to download a file if it doesn't exist
def download_file(url, output_dir):
    filename = url.split('/')[-1]
    output_path = os.path.join(output_dir, filename)

    if not os.path.exists(output_path):
        print(f"Downloading: {url}")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {url}")
    else:
        print(f"File already exists: {filename}")

# Function to parse an index.html file and download all linked files
def process_index_file(index_file_path, base_url):
    with open(index_file_path, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href:
            # Determine the corresponding subdirectory based on the link's path
            subdirectory = sanitize_path(os.path.dirname(href).replace('/', os.sep))
            output_directory = os.path.join(os.getcwd(), subdirectory)

            # Create the subdirectory if it doesn't exist
            os.makedirs(output_directory, exist_ok=True)

            # Download the file
            full_url = base_url + href if not href.startswith("http") else href
            download_file(full_url, output_directory)

            # If the downloaded file is an index.html, process it recursively
            if href.endswith("index.html"):
                process_index_file(os.path.join(output_directory, "index.html"), os.path.dirname(full_url) + '/')

# Parse the main HTML file
with open(html_file, 'r') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Find all links in the main HTML file
links = soup.find_all('a')

# Process each link
for link in links:
    href = link.get('href')
    if href:
        # Determine the corresponding subdirectory based on the link's path
        subdirectory = sanitize_path(os.path.dirname(href).replace('/', os.sep))
        output_directory = os.path.join(os.getcwd(), subdirectory)

        # Create the subdirectory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)

        # Download the file
        full_url = BASE_URL + href if not href.startswith("http") else href
        download_file(full_url, output_directory)

        # If the downloaded file is an index.html, process it
        if href.endswith("index.html"):
            process_index_file(os.path.join(output_directory, "index.html"), BASE_URL)
