import os
import requests
import hashlib
from concurrent.futures import ThreadPoolExecutor
import time
import random

from PIL import Image
import pyarrow.csv as pc

DOWNLOAD_FOLDER = "./data/wiki-images/"
TSV_FOLDER = "./data/wiki-images/"

# Create the download folder if it doesn't exist
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


def resize_image(filepath):
    with Image.open(filepath) as img:
        # Convert the image to RGB mode if it's not
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        width, height = img.size
        min_dim = 448
        max_dim = 2 * min_dim

        # Calculate new dimensions while maintaining the aspect ratio
        if width < height:
            new_width = max(min_dim, width)
            new_height = int((new_width / width) * height)
            new_height = min(new_height, max_dim)
        else:
            new_height = max(min_dim, height)
            new_width = int((new_height / height) * width)
            new_width = min(new_width, max_dim)

        # Resize and save
        img = img.resize((new_width, new_height), Image.Resampling.NEAREST)
        img.save(filepath, "JPEG", quality=90)


# Multiple User-Agent strings
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0",
    "Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166",
    "Mozilla/5.0 (iPad; CPU OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G970F Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.62 Mobile Safari/537.36",
]


def download_and_resize_image(url, idx, total):
    try:
        # Download
        filename = hashlib.md5(url.encode()).hexdigest() + ".jpg"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        if os.path.exists(filepath):
            return

        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers)

        # Check if the response was successful and appears to be an image
        if response.status_code != 200:
            print(f"Failed to download {url}. HTTP Status: {response.status_code}")
            return

        if "image" not in response.headers["Content-Type"]:
            print(
                f"URL did not return an image: {url}. Content-Type: {response.headers['Content-Type']}"
            )
            return

        # Save the image
        with open(filepath, "wb") as file:
            file.write(response.content)

        # Check the validity of the image
        if not is_valid_image(filepath):
            print(f"Invalid image from {url}. Deleting...")
            os.remove(filepath)
            return

        # Resize
        resize_image(filepath)

        print(f"Processed {idx + 1}/{total} - {url}")

        # Introduce a delay
        time.sleep(0.1)
    except Exception as e:
        print(f"Error processing {url}. Error: {e}")


def is_valid_image(filepath):
    try:
        with Image.open(filepath) as img:
            img.verify()
        return True
    except:
        return False


def main():
    tsv_files = [file for file in os.listdir(TSV_FOLDER) if file.endswith(".tsv")]
    random.shuffle(tsv_files)

    for tsv_file in tsv_files:
        options = pc.ParseOptions(
            delimiter="\t",
            newlines_in_values=True,
            ignore_empty_lines=True,
        )
        table = pc.read_csv(os.path.join(TSV_FOLDER, tsv_file), parse_options=options)
        df = table.to_pandas()
        image_urls = df["image_url"].unique()

        with ThreadPoolExecutor(max_workers=100) as executor:
            for idx, image_url in enumerate(image_urls):
                executor.submit(
                    download_and_resize_image, image_url, idx, len(image_urls)
                )


if __name__ == "__main__":
    main()
