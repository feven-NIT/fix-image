# Use a base image specified by an environment variable
FROM random
# Copy the scripts and necessary files into the image
COPY update_packages.py /tmp/update_packages.py
COPY update_packages.sh /tmp/update_packages.sh
COPY scan.csv /tmp/scan.csv
COPY tpackage-json.txt /tmp/tpackage-json.txt

# Make the shell script executable
RUN chmod +x /tmp/update_packages.sh

# Execute the shell script
RUN /tmp/update_packages.sh

# Change the user to non-root
RUN useradd -m nonroot
USER nonroot
