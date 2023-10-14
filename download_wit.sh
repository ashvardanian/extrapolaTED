#!/bin/bash

# List of URLs to download
urls=(
  "https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-00000-of-00010.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-00001-of-00010.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-00002-of-00010.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-00003-of-00010.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-00004-of-00010.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-00005-of-00010.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-00006-of-00010.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-00007-of-00010.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-00008-of-00010.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-00009-of-00010.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.val.all-00000-of-00005.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.val.all-00001-of-00005.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.val.all-00002-of-00005.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.val.all-00003-of-00005.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.val.all-00004-of-00005.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.test.all-00000-of-00005.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.test.all-00001-of-00005.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.test.all-00002-of-00005.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.test.all-00003-of-00005.tsv.gz"
  "https://storage.googleapis.com/gresearch/wit/wit_v1.test.all-00004-of-00005.tsv.gz"
)

# Directory to save the downloaded files
save_dir="/mnt/nvme2n1/wit"

# Create the directory if it doesn't exist
mkdir -p "$save_dir"

# Download and unpack each file
for url in "${urls[@]}"; do
  # Get the file name from the URL
  file_name=$(basename "$url")

  # Full path to the downloaded file
  file_path="$save_dir/$file_name"

  # Download the file
  wget -P "$save_dir" "$url"

  # Unpack the file
  gunzip "$file_path"
done
