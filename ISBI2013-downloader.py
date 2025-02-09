#!/usr/bin/env python3
"""
TCIA Batch Downloader Using getImage API
- Parses all .tcia manifest files in a dataset directory.
- Creates folders named after the .tcia files (without extension).
- For each series UID in a manifest, builds a URL like:
    https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?SeriesInstanceUID=<UID>
- Downloads each series (as a ZIP file) into its respective folder.
- Implements a simple retry mechanism on failures.
"""

import os
import glob
import time
import requests

def parse_manifest(manifest_path):
    """
    Parses a TCIA .tcia manifest file.
    
    Returns:
      - download_url (str): The original download URL from the manifest (not used here).
      - databasket_id (str): The databasket ID (not used here).
      - include_annotation (str): The includeAnnotation flag (not used here).
      - series_list (list): A list of Series Instance UIDs to download.
    """
    config = {}
    series_list = []
    reading_series = False

    with open(manifest_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Parse key=value pairs until we hit the series list.
            if not reading_series and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key == "ListOfSeriesToDownload":
                    reading_series = True
                else:
                    config[key] = value
            else:
                if reading_series:
                    series_list.append(line)
    
    return (config.get("downloadServerUrl"),
            config.get("databasketId"),
            config.get("includeAnnotation", "true"),
            series_list)

def download_tcia(manifest_path, output_folder):
    """
    Downloads each series from a manifest using the getImage endpoint.
    Each series is saved as a separate ZIP file in output_folder.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    # We only need the series list; the other parameters aren’t used here.
    _, _, _, series_list = parse_manifest(manifest_path)
    
    # Define the base URL for the REST API endpoint that works.
    BASE_URL = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage"
    print(f"\nDownloading series for manifest: {os.path.basename(manifest_path)}")
    print(f"Saving into folder: {output_folder}")
    
    for idx, uid in enumerate(series_list, start=1):
        url = f"{BASE_URL}?SeriesInstanceUID={uid}"
        print(f"\n[{idx}/{len(series_list)}] Downloading series UID: {uid}")
        MAX_RETRIES = 5
        response = None
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                break  # Successful download—exit retry loop.
            except requests.RequestException as err:
                print(f"  Attempt {attempt+1} failed for series {uid}: {err}")
                if attempt < MAX_RETRIES - 1:
                    wait_time = 2 ** attempt  # Exponential backoff.
                    print(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("  Maximum retries reached. Skipping this series.")
                    response = None
        if response is None:
            continue
        
        # Save each series as "series_1.zip", "series_2.zip", etc.
        out_file = os.path.join(output_folder, f"series_{idx}.zip")
        try:
            with open(out_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"  Saved series {uid} to {out_file}")
        except Exception as e:
            print(f"  Error saving series {uid}: {e}")

if __name__ == "__main__":
    # Adjust the glob path as needed.
    tcia_files = glob.glob("/home/ri/Desktop/Projects/Datasets/ISBI2013/**/*.tcia", recursive=True)
    
    if not tcia_files:
        print("No .tcia files found!")
        exit(1)
    
    print(f"Found {len(tcia_files)} .tcia files. Starting downloads...")
    
    for manifest_path in tcia_files:
        manifest_name = os.path.splitext(os.path.basename(manifest_path))[0]
        output_folder = os.path.join(os.path.dirname(manifest_path), manifest_name)
        download_tcia(manifest_path, output_folder)
