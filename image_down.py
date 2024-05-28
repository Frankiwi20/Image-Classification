import requests
import os
from PIL import Image, ImageFile
from io import BytesIO
import hashlib

# To avoid truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Replace with your actual API key and search engine ID
api_key = ''
search_engine_id = ''
search_url = "https://www.googleapis.com/customsearch/v1"

# Function to get the hash of an image
def get_image_hash(image):
    image_hash = hashlib.md5(image.tobytes()).hexdigest()
    return image_hash

# Function to get the next image number for naming files
def get_next_image_number(save_dir):
    existing_files = [f for f in os.listdir(save_dir) if f.endswith(".jpg")]
    if not existing_files:
        return 0
    existing_files.sort()
    last_file = existing_files[-1]
    last_number = int(last_file.split('_')[-1].split('.')[0])
    return last_number + 1

# Function to download images based on a search term
def download_images(search_term, num_images, save_dir):
    os.makedirs(save_dir, exist_ok=True)  # Create the save directory if it doesn't exist
    downloaded_images = len([f for f in os.listdir(save_dir) if f.endswith(".jpg")])
    next_image_number = get_next_image_number(save_dir)
    image_paths = []
    existing_hashes = set()

    # Load existing image hashes to avoid duplicates
    for file_name in os.listdir(save_dir):
        if file_name.endswith(".jpg"):
            file_path = os.path.join(save_dir, file_name)
            try:
                with Image.open(file_path) as img:
                    img_hash = get_image_hash(img)
                    existing_hashes.add(img_hash)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    start = 1  # Initial start index for the API request
    while downloaded_images < num_images:
        params = {
            "q": search_term,
            "cx": search_engine_id,
            "key": api_key,
            "searchType": "image",
            "num": 30,
            "start": start
        }

        print(f"Requesting images with params: {params}")
        response = requests.get(search_url, params=params)
        if response.status_code != 200:
            print(f"Error: Failed to retrieve images. Status code: {response.status_code}")
            print(response.json())  # Print the response to see the error message
            break
        search_results = response.json()

        if "items" not in search_results:
            print("Error: No items found in the search results.")
            start += 10  # Increment start to move to the next set of results
            continue

        for item in search_results["items"]:
            image_url = item["link"]
            try:
                # Download the image
                image_data = requests.get(image_url)
                image_data.raise_for_status()

                # Check if the image is in JPEG format
                if "image/jpeg" not in image_data.headers["Content-Type"]:
                    print(f"Skipped non-JPEG image: {image_url}")
                    continue

                # Open the image and calculate hash
                image = Image.open(BytesIO(image_data.content))
                img_hash = get_image_hash(image)

                # Check if the image is a duplicate
                if img_hash in existing_hashes:
                    print(f"Duplicate image found: {image_url}")
                    continue

                # Save the image if it's not a duplicate
                image_path = os.path.join(save_dir, f"{search_term}_{next_image_number}.jpg")
                image.save(image_path)
                image_paths.append(image_path)
                existing_hashes.add(img_hash)
                downloaded_images += 1
                next_image_number += 1
                print(f"Downloaded {image_path}")

                if downloaded_images >= num_images:
                    break
            except Exception as e:
                print(f"Could not download {image_url} - {e}")

        start += 10  # Increment start to move to the next set of results

    return image_paths

# Main block to download images for specific search terms
if __name__ == "__main__":
    pencil_search_terms = ["pencil", "pencils", "colored pencils", "graphite pencils", "drawing pencils", "mechanical pencils"]
    non_pencil_search_terms = ["pen", "marker", "eraser", "notebook", "ruler", "scissors"]
    num_images_per_term = 100  # Adjust as needed
    pencil_save_dir = "data/pencils"
    non_pencil_save_dir = "data/not_pencils"

    for term in pencil_search_terms:
        download_images(term, num_images_per_term, pencil_save_dir)
    for term in non_pencil_search_terms:
        download_images(term, num_images_per_term, non_pencil_save_dir)

