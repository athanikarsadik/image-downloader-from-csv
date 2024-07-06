import csv
import os
from zipfile import ZipFile
from io import BytesIO
from PIL import Image as PILImage
import numpy as np
from rembg import remove
import requests
from requests.exceptions import ConnectionError, Timeout
from urllib3.exceptions import NameResolutionError
import time

data_dir = "data"  # Folder for input CSV
output_dir = "output" # Folder for output zip
image_dir = os.path.join(output_dir, "images") # Folder for processed images 

# --- Create Directories if they don't exist ---
os.makedirs(data_dir, exist_ok=True)
os.makedirs(image_dir, exist_ok=True)

def download_image(url):
    """Downloads an image from a given URL."""
    try:
        response = requests.get(url, timeout=10) # Added timeout
        response.raise_for_status() 
        return BytesIO(response.content)
    except (ConnectionError, Timeout) as e:
        print(f"Error: Network problem downloading {url}: {e}")
        return None
    except NameResolutionError as e:
        print(f"Error: Could not resolve hostname for {url}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {url}: {e}")
        return None

def remove_background(image_data):
  """Removes the background of an image using rembg and saves as WebP."""
  try:
    img = PILImage.open(image_data)
    img = np.array(img)
    output = remove(img)
    output_buffer = BytesIO()

    # Save as WebP
    PILImage.fromarray(output).save(output_buffer, format="WebP", lossless=True)

    output_buffer.seek(0)
    return output_buffer
  except Exception as e:
    print(f"Error removing background: {e}")
    return None 

def process_csv(csv_file_path):
    """Processes the CSV file, extracts valid URLs, and handles image processing."""
    valid_urls = []
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            total_rows = sum(1 for _ in reader)
            file.seek(0)
            header = next(reader)

            print(f"Processing {total_rows} rows in the CSV file...")

            # 1. Extract Valid URLs:
            for row_index, row in enumerate(reader):
                for col_index, cell_value in enumerate(row):
                    urls_in_cell = cell_value.split(';')
                    for url in urls_in_cell:
                        url = url.strip()
                        if url.startswith("https://"): 
                            valid_urls.append(url)

            print(f"Found {len(valid_urls)} valid image URLs.")

            # 2. Process Images:
            processed_image_filenames = []
            for i, url in enumerate(valid_urls):
                start_time = time.time()
                print(f"Processing image {i+1}/{len(valid_urls)}: {url}") 
                
                # Download 
                image_data = download_image(url)
                if image_data is None:
                    print(f"  - Skipping {url} due to download error.")
                    continue

                # Remove Background
                processed_image = remove_background(image_data)
                if processed_image is None:
                    print(f"  - Skipping {url} due to background removal error.")
                    continue

                # Save Image 
                filename = f"processed_image_{i+1}.webp"
                save_path = os.path.join(image_dir, filename)
                with open(save_path, 'wb') as f:
                    f.write(processed_image.getvalue())
                processed_image_filenames.append(filename)

                end_time = time.time()
                processing_time = round(end_time - start_time, 2)
                print(f"  - Processed in {processing_time} seconds.")

        print("CSV processing complete!")
        return processed_image_filenames 

    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_file_path}'")
        return []
def zip_processed_images(image_filenames):
    """Zips processed images into an archive in the specified zip directory."""
    if image_filenames:
        zip_filename = os.path.join(output_dir, "processed_images.zip") 
        with ZipFile(zip_filename, 'w') as zipf:
            for filename in image_filenames:
                file_path = os.path.join(image_dir, filename)
                zipf.write(file_path, arcname=filename)  

        print(f"Processed images saved to {zip_filename}")
    else:
        print("No images were processed.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, data_dir, "input.csv") # Use data_dir

    processed_filenames = process_csv(csv_file) # Use image_dir
    if processed_filenames:
        zip_processed_images(processed_filenames, image_dir=image_dir, zip_dir=output_dir)