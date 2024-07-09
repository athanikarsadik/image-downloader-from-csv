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
import concurrent.futures

data_dir = "data"  # input CSV
output_dir = "output" # output zip
image_dir = os.path.join(output_dir, "images") # processed images 

os.makedirs(data_dir, exist_ok=True)
os.makedirs(image_dir, exist_ok=True)

def download_image(url):
    """Downloads an image from a given URL."""
    try:
        response = requests.get(url, timeout=10) 
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

    PILImage.fromarray(output).save(output_buffer, format="WebP", lossless=True)

    output_buffer.seek(0)
    return output_buffer
  except Exception as e:
    print(f"Error removing background: {e}")
    return None 

def process_image(url, row_index, col_index):
    """Processes a single image (download, remove background, save) 
       and uses row/col indices in the filename.
    """
    print(f"Processing image row:{row_index+1}, col:{col_index+1}")

    image_data = download_image(url) 
    if image_data is None:
        print(f"  - Skipping {url} due to download error.")
        return None

    processed_image = remove_background(image_data)
    if processed_image is None:
        print(f"  - Skipping {url} due to background removal error.")
        return None

    filename = f"{row_index+1}_{col_index+1}.webp" 
    save_path = os.path.join(image_dir, filename)
    with open(save_path, 'wb') as f:
        f.write(processed_image.getvalue())

    return filename

def process_csv(csv_file_path):
    """Processes the first 6 URLs found in each row of the CSV,
       skipping URLs for images that already exist in the output folder,
       and handles parallel image processing.
    """
    try:
        with open(csv_file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)

            print(f"Processing CSV file...")

            processed_image_filenames = []
            with concurrent.futures.ProcessPoolExecutor() as executor:
                futures = []
                for row_index, row in enumerate(reader):
                    url_count = 0  
                    for col_index, cell_value in enumerate(row):
                        urls_in_cell = cell_value.split(";")
                        for url_index, url in enumerate(urls_in_cell):
                            url = url.strip()
                            if url.startswith("https://") and url_count < 6:
                                filename = f"{row_index+1}_{col_index+1}.webp"
                                image_path = os.path.join(image_dir, filename)
                                if os.path.exists(image_path):
                                    print(
                                        f"  - Skipping {url} (image already exists)"
                                    )
                                    url_count += 1
                                    continue  

                                future = executor.submit(
                                    process_image, url, row_index, col_index
                                )
                                futures.append(future)
                                url_count += 1

                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result is not None:
                        processed_image_filenames.append(result)

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
    csv_file = os.path.join(script_dir, data_dir, "input.csv") 

    processed_filenames = process_csv(csv_file) 
    if processed_filenames:
        zip_processed_images(processed_filenames, image_dir=image_dir, zip_dir=output_dir)