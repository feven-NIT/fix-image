import json
import csv
import os
import subprocess

def get_package_type(package_name):
    with open('/tmp/tpackage-json.txt') as f:
        data = json.load(f)
        for repo, repo_data in data.items():
            for package_group in repo_data['packages']:
                for pkg in package_group['pkgs']:
                    if pkg['name'] == package_name:
                        return package_group['pkgsType']
    return None

def update_package(distro, package, fixed_version, package_type):
    if package_type == 'python':
        print(f"Updating Python package {package} to version {fixed_version}...")

        # Check if pip3 is installed, if not install it
        pip_installed = subprocess.run(['which', 'pip3'], capture_output=True, text=True)
        if pip_installed.returncode != 0:
            print("pip3 not found. Installing pip3...")
            subprocess.run(['yum', 'install', '-y', 'python3-pip'], check=True)
            print("pip3 installed successfully.")

        subprocess.run(['pip3', 'install', f'{package}=={fixed_version}'], check=True)
        print(f"Successfully updated Python package {package} to version {fixed_version}.")

        # Remove pip3 after updating
        print("Removing pip3...")
        subprocess.run(['yum', 'remove', '-y', 'python3-pip'], check=True)
        print("pip3 removed successfully.")

    elif package_type == 'nodejs':
        print("Installing Node.js and npm...")
        subprocess.run(['yum', 'install', '-y', 'nodejs', 'npm'], check=True)
        print("Successfully installed Node.js and npm.")
        print(f"Updating {package} to version {fixed_version}...")
        subprocess.run(['npm', 'install', f'{package}@{fixed_version}'], check=True)
        print(f"Successfully updated {package} to version {fixed_version}.")
        print("Removing Node.js and npm...")
        subprocess.run(['yum', 'remove', '-y', 'nodejs', 'npm'], check=True)
        print("Successfully removed Node.js and npm.")

    elif package_type == 'package':
        print(f"Updating {package}...")
        subprocess.run(['yum', 'update', package, '-y'], check=True)
        print(f"Successfully updated {package}.")
        print(f"Installing {package} version {fixed_version}...")
        subprocess.run(['yum', 'install', f'{package}-{fixed_version}', '-y'], check=True)
        print(f"Successfully installed {package}-{fixed_version}.")

    else:
        print(f"Unsupported package type: {package_type}")
        exit(1)

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
                    if package_type:
                        print(f"Updating package {row['Package']} of type {package_type} in {row['Distro']} to version {fixed_version}.")
                        update_package(row['Distro'], row['Package'], fixed_version, package_type)
                    else:
                        print(f"Package type for {row['Package']} not found.")
                elif status == 'affected':
                    print(f"Package {row['Package']} in {row['Distro']} is affected by {row['CVE ID']} but no fixed version specified.")
    print("Package updates completed successfully.")

if __name__ == "__main__":
    main()
