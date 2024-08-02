# Use a base image specified by an environment variable
FROM random

# Copy the scripts and necessary files into the image
COPY update_packages.py /tmp/update_packages.py
COPY scan.csv /tmp/scan.csv
COPY tpackage-json.txt /tmp/tpackage-json.txt

# Install pip3 as root user
USER root
RUN yum install -y python3-pip

# Change the user to non-root
RUN useradd -m nonroot
USER nonroot

# Execute the Python script
RUN python3 /tmp/update_packages.py

# Switch back to root to clean up
USER root
RUN yum remove -y python3-pip
USER nonroot
