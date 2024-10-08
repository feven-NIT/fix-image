import json
import csv
import os
import subprocess
from datetime import datetime, timedelta
import re

# Determine the package manager to use
REPO_FOLDER = os.getenv('REPO_FOLDER', '')
USE_MICRODNF = 'micro' in REPO_FOLDER or 'minimal' in REPO_FOLDER
PACKAGE_MANAGER_INSTALL = 'microdnf' if USE_MICRODNF else 'yum'
PACKAGE_MANAGER_REMOVE = 'microdnf' if USE_MICRODNF else 'yum'

def get_package_type_and_path(package_name, package_version):
    with open('/tmp/tpackage-json.txt') as f:
        data = json.load(f)
        for repo, repo_data in data.items():
            for package_group in repo_data['packages']:
                for pkg in package_group['pkgs']:
                    if pkg['name'] == package_name and pkg['version'] == package_version:
                        return package_group['pkgsType'], pkg['path']
    return None, None

def install_pip_if_needed():
    pip_installed = subprocess.run(['which', 'pip3'], capture_output=True, text=True)
    if pip_installed.returncode != 0:
        print("pip3 not found. Installing pip3...")
        try:
            subprocess.run([PACKAGE_MANAGER_INSTALL, 'install', '-y', 'python3-pip'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing pip3: {e}")
            return False
        print("Successfully installed pip3.")
    return True

def extract_numeric_version(version):
    """Extracts the numeric part of a version string for comparison."""
    return [int(part) for part in re.findall(r'\d+', version)]

def compare_versions(version1, version2):
    """Compares two version strings based on their numeric components."""
    v1_parts = extract_numeric_version(version1)
    v2_parts = extract_numeric_version(version2)

    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1

    if len(v1_parts) > len(v2_parts):
        return 1
    elif len(v1_parts) < len(v2_parts):
        return -1
    else:
        return 0

def get_closest_version(current_version, fixed_versions):
    closest_version = None
    for fixed_version in fixed_versions:
        if compare_versions(fixed_version, current_version) > 0:
            if closest_version is None or compare_versions(fixed_version, closest_version) < 0:
                closest_version = fixed_version
    return closest_version

def update_package(distro, package, fixed_version, package_type, original_path=None):
    if package_type == 'python':
        if not install_pip_if_needed():
            print(f"Skipping Python package {package} update due to pip3 installation failure.")
            return
        print(f"Updating Python package {package} to version {fixed_version}...")
        try:
            subprocess.run(['pip3', 'install', f'{package}=={fixed_version}'], check=True)
            print(f"Successfully updated Python package {package} to version {fixed_version}.")

            # Remove the original package's .egg-info or .dist-info directory
            if original_path:
                print(f"Removing original package files from {original_path}...")
                try:
                    subprocess.run(['rm', '-rf', original_path], check=True)
                    print(f"Successfully removed original package files at {original_path}.")
                except subprocess.CalledProcessError as e:
                    print(f"Error removing original package files at {original_path}: {e}")
        except subprocess.CalledProcessError as e:
            print(f"Error updating Python package {package} to version {fixed_version}: {e}")
            print(f"The version {fixed_version} is not available for package {package}.")

    elif package_type == 'nodejs':
        print("Installing Node.js and npm...")
        try:
            subprocess.run([PACKAGE_MANAGER_INSTALL, 'install', '-y', 'nodejs', 'npm'], check=True)
            print("Successfully installed Node.js and npm.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing Node.js and npm: {e}")
            return

        print(f"Updating {package} to version {fixed_version}...")
        try:
            subprocess.run(['npm', 'install', f'{package}@{fixed_version}'], check=True)
            print(f"Successfully updated {package} to version {fixed_version}.")
        except subprocess.CalledProcessError as e:
            print(f"Error updating {package} to version {fixed_version}: {e}")
            print(f"The version {fixed_version} is not available for package {package}.")

        print("Removing Node.js and npm...")
        try:
            subprocess.run([PACKAGE_MANAGER_REMOVE, 'remove', '-y', 'nodejs', 'npm'], check=True)
            print("Successfully removed Node.js and npm.")
        except subprocess.CalledProcessError as e:
            print(f"Error removing Node.js and npm: {e}")

    elif package_type == 'package':
        print(f"Updating {package}...")
        try:
            subprocess.run([PACKAGE_MANAGER_INSTALL, 'update', package, '-y'], check=True)
            print(f"Successfully updated {package}.")
        except subprocess.CalledProcessError as e:
            print(f"Error updating {package}: {e}")
            return

        print(f"Installing {package} version {fixed_version}...")
        try:
            subprocess.run([PACKAGE_MANAGER_INSTALL, 'install', f'{package}-{fixed_version}', '-y'], check=True)
            print(f"Successfully installed {package}-{fixed_version}.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package} version {fixed_version}: {e}")
            print(f"The version {fixed_version} is not available for package {package}.")
    else:
        print(f"Unsupported package type: {package_type}")
        exit(1)

def should_update(fix_date_str, severity):
    if severity.lower() == 'critical':
        return True
    fix_date = datetime.strptime(fix_date_str, '%Y-%m-%d %H:%M:%S')
    three_months_ago = datetime.now() - timedelta(days=90)
    return fix_date <= three_months_ago

def main():
    print("Starting package updates...")
    with open('/tmp/scan.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            status = row['Status']
            if status != 'Status':  # Skip header
                if 'fixed in' in status:
                    fixed_versions = status.split('fixed in ')[1].split(', ')
                    package_version = row['Package Version']
                    closest_version = get_closest_version(package_version, fixed_versions)

                    if closest_version:
                        package_type, original_path = get_package_type_and_path(row['Package'], package_version)
                        severity = row['Severity']
                        fix_date = row['Fix Date']
                        if package_type and should_update(fix_date, severity):
                            print(f"Updating package {row['Package']} of type {package_type} in {row['Distro']} to version {closest_version}.")
                            update_package(row['Distro'], row['Package'], closest_version, package_type, original_path)
                        else:
                            print(f"Package {row['Package']} fix is either too recent or not critical.")
                    else:
                        print(f"No newer fixed version found for package {row['Package']}.")
                elif status == 'affected':
                    print(f"Package {row['Package']} in {row['Distro']} is affected by {row['CVE ID']} but no fixed version specified.")
    print("Package updates completed successfully.")

if __name__ == "__main__":
    main()
