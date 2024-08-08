# Use a base image specified by an environment variable
FROM random

# Environment variable for the repo folder
ARG REPO_FOLDER

# Copy the scripts and necessary files into the image
COPY update_packages.py /tmp/update_packages.py
COPY scan.csv /tmp/scan.csv
COPY tpackage-json.txt /tmp/tpackage-json.txt

# Install pip3 as root user
USER root

# Use microdnf if REPO_FOLDER contains "micro" or "minimal", otherwise use yum
RUN if echo "$REPO_FOLDER" | grep -q -E "micro|minimal"; then \
    microdnf install -y python3-pip; \
    else \
    yum install -y python3-pip; \
    fi

# Change the user to non-root
RUN useradd -m nonroot
USER nonroot

# Execute the Python script
RUN python3 /tmp/update_packages.py

# Switch back to root to clean up
USER root
RUN if echo "$REPO_FOLDER" | grep -q -E "micro|minimal"; then \
    microdnf remove -y python3-pip; \
    else \
    yum remove -y python3-pip; \
    fi
USER nonroot
