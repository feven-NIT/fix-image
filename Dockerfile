# Use a base image specified by an environment variable
FROM random

# Copy the scripts and necessary files into the image
COPY update_packages.py /tmp/update_packages.py
COPY scan.csv /tmp/scan.csv
COPY tpackage-json.txt /tmp/tpackage-json.txt

# Change the user to non-root
RUN useradd -m nonroot
USER nonroot

# Execute the Python script
RUN python3 /tmp/update_packages.py
