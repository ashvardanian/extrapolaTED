#!/bin/bash

# Define the SSD devices
declare -a ssds=(
  "nvme1n1"
  "nvme9n1"
)

# Loop through each SSD
for ssd in "${ssds[@]}"
do
  echo "Processing $ssd..."
  
  # Create a partition on the SSD
  echo "Creating partition on $ssd..."
  sudo parted /dev/$ssd mklabel gpt
  sudo parted /dev/$ssd mkpart primary ext4 0% 100%
  
  # Format the partition with ext4
  echo "Formatting partition on $ssd with ext4..."
  sudo mkfs.ext4 /dev/${ssd}p1
  
  # Create a mount point
  echo "Creating mount point for $ssd..."
  sudo mkdir -p /mnt/$ssd
  
  # Mount the partition
  echo "Mounting $ssd..."
  sudo mount /dev/${ssd}p1 /mnt/$ssd
  
  # Add entry to fstab to ensure the SSD is mounted at boot
  echo "Adding $ssd to /etc/fstab..."
  echo "/dev/${ssd}p1 /mnt/$ssd ext4 defaults 0 0" | sudo tee -a /etc/fstab

done
