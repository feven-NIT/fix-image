import json
import csv
import os
import subprocess
from datetime import datetime, timedelta

# Determine the package manager to use
REPO_FOLDER = os.getenv('REPO_FOLDER', '')
USE_MICRODNF = 'micro' in REPO_FOLDER or 'minimal' in REPO_FOLDER
PACKAGE_MANAGER_INSTALL = 'microdnf' if USE_MICRODNF else 'yum'
PACKAGE_MANAGER_REMOVE = 'microdnf' if USE_MICRODNF else 'yum'

def get_package_type(package_name):
    with open('/tmp/tpackage-json.txt') as f:
        data = json.load(f)
        for repo, repo_data in data.items():
            for package_group in repo_data['packages']:
                for pkg in package_group['pkgs']:
                    if pkg['name'] == package_name:
                        return package_group['pkgsType']
    return None

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

def update_package(distro, package, fixed_version, package_type):
    if package_type == 'python':
        if not install_pip_if_needed():
            print(f"Skipping Python package {package} update due to pip3 installation failure.")
            return
        print(f"Updating Python package {package} to version {fixed_version}...")
        try:
            subprocess.run(['pip3', 'install', f'{package}=={fixed_version}'], check=True)
            print(f"Successfully updated Python package {package} to version {fixed_version}.")
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
                    fixed_version = status.split('fixed in ')[1].split(', ')[0]
                    package_type = get_package_type(row['Package'])
                    severity = row['Severity']
                    fix_date = row['Fix Date']
                    if package_type and should_update(fix_date, severity):
                        print(f"Updating package {row['Package']} of type {package_type} in {row['Distro']} to version {fixed_version}.")
                        update_package(row['Distro'], row['Package'], fixed_version, package_type)
                    else:
                        print(f"Package {row['Package']} fix is either too recent or not critical.")
                elif status == 'affected':
                    print(f"Package {row['Package']} in {row['Distro']} is affected by {row['CVE ID']} but no fixed version specified.")
    print("Package updates completed successfully.")

if __name__ == "__main__":
    main()
