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
RUN case "$REPO_FOLDER" in \
    *micro*|*minimal*) microdnf install -y python3-pip ;; \
    *) yum install -y python3-pip ;; \
    esac

# Change the user to non-root
RUN useradd -m nonroot
USER nonroot

# Execute the Python script
RUN python3 /tmp/update_packages.py

# Switch back to root to clean up
USER root
RUN case "$REPO_FOLDER" in \
    *micro*|*minimal*) microdnf remove -y python3-pip ;; \
    *) yum remove -y python3-pip ;; \
    esac
USER nonroot
