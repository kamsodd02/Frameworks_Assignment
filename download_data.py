import gdown
import os

def download_data():
    url = "https://drive.google.com/uc?id=19fOOzkftyl39YKQONCNNqLTYTWdMmPLj"  # Replace with your file ID
    output = "metadata_subset.csv"

    if not os.path.exists(output):
        print("Downloading dataset from Google Drive...")
        gdown.download(url, output, quiet=False)
    else:
        print("Dataset already exists. Skipping download.")

if __name__ == "__main__":
    download_data()
