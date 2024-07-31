import os
import csv
import json
import subprocess

def install_python_with_pip():
    # Install Python and pip using yum
    print("Installing Python and pip...")
    subprocess.run(['yum', 'install', '-y', 'python3-pip'], check=True)

def remove_python_with_pip():
    # Remove Python and pip using yum
    print("Removing Python and pip...")
    subprocess.run(['yum', 'remove', '-y', 'python3-pip'], check=True)

def update_package(distro, package, fixed_version, package_type):
    # Remove leading and trailing whitespace from distro and package_type
    distro = distro.strip()

    print(f"Distro: '{distro}'")
    print(f"Package: '{package}'")
    print(f"Package Type: '{package_type}'")

    if package_type.lower() == 'python':
        install_python_with_pip()
        # Print and run pip command for Python packages
        command = ['pip3', 'install', f'{package}=={fixed_version}']
        print(f"Executing command: {' '.join(command)}")
        subprocess.run(command, check=True)
        remove_python_with_pip()
    elif package_type.lower() == 'package':
        # Print and run yum commands for general packages
        update_command = ['yum', 'update', package, '-y']
        install_command = ['yum', 'install', f'{package}-{fixed_version}', '-y']
        print(f"Executing command: {' '.join(update_command)}")
        subprocess.run(update_command, check=True)
        print(f"Executing command: {' '.join(install_command)}")
        subprocess.run(install_command, check=True)
    else:
        raise ValueError(f"Unsupported package type: {package_type}")

def get_package_type(package_name):
    with open('/tmp/tpackage-json.txt', 'r') as file:
        data = json.load(file)
        for repo, content in data.items():
            for pkg_group in content['packages']:
                for pkg in pkg_group['pkgs']:
                    if pkg['name'] == package_name:
                        return pkg_group['pkgsType']
    return None

def main():
    csv_file = '/tmp/scan.csv'
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['Status'].startswith('fixed in'):
                fixed_version = row['Status'].split(' ')[-1]
                package_type = get_package_type(row['Package'])
                if package_type:
                    update_package(row['Distro'], row['Package'], fixed_version, package_type)
                else:
                    print(f"Package type for {row['Package']} not found.")
            elif row['Status'] == 'affected':
                print(f"Package {row['Package']} in {row['Distro']} is affected by {row['CVE ID']} but no fixed version specified.")

if __name__ == '__main__':
    main()
