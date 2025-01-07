import os
import requests

# Base URL for the dataset
BASE_URL = "https://www.cs.toronto.edu/~vmnih/data/"

# List of dataset URLs
DATASET_URLS = [
    "mass_roads/train/sat/index.html",
    "mass_roads/train/map/index.html",
    "mass_roads/valid/sat/index.html",
    "mass_roads/valid/map/index.html",
    "mass_roads/test/sat/index.html",
    "mass_roads/test/map/index.html",
    "mass_roads/massachusetts_roads_shape.zip"
]

# Function to create directories
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Function to download a file
def download_file(url, save_path):
    if not os.path.exists(save_path):
        print(f"Downloading: {url}")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Downloaded: {save_path}")
        else:
            print(f"Failed to download: {url}")
    else:
        print(f"File already exists: {save_path}")

# Function to process an index.html file
def process_index_file(url, save_dir):
    index_file_path = os.path.join(save_dir, "index.html")
    download_file(f"{BASE_URL}{url}", index_file_path)

    # Read the index.html file to find linked .tiff files
    with open(index_file_path, 'r') as file:
        content = file.readlines()

    for line in content:
        if ".tiff" in line:
            # Extract the .tiff file URL
            start = line.find("href=\"") + 6
            end = line.find(".tiff") + 5
            tiff_url = line[start:end]

            # If the URL is relative, prepend BASE_URL
            if not tiff_url.startswith("http"):
                tiff_url = f"{BASE_URL}{tiff_url}"

            # Save the .tiff file
            tiff_save_path = os.path.join(save_dir, os.path.basename(tiff_url))
            download_file(tiff_url, tiff_save_path)

# Download each dataset URL
for url in DATASET_URLS:
    if "index.html" in url:
        # Create the corresponding directory
        folder_structure = url.replace("mass_roads/", "").replace("/index.html", "")
        save_dir = os.path.join(os.getcwd(), "mass_roads", folder_structure)
        create_directory(save_dir)

        # Process the index.html file
        process_index_file(url, save_dir)
    else:
        # Directly download other files like shapefile
        save_path = os.path.join(os.getcwd(), "mass_roads", os.path.basename(url))
        download_file(f"{BASE_URL}{url}", save_path)
