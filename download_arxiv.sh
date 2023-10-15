
urls=(
    "https://huggingface.co/datasets/unum-cloud/ann-arxiv-2m/resolve/main/abstract.e5-base-v2.fbin"
    "https://huggingface.co/datasets/unum-cloud/ann-arxiv-2m/resolve/main/title_abstract.tsv"
)

# Directory to save the downloaded files
save_dir="./data/arxiv"

# Create the directory if it doesn't exist
mkdir -p "$save_dir"

# Download and unpack each file
for url in "${urls[@]}"; do

  # Download the file
  wget -P "$save_dir" "$url"
done
