import os
import csv
import subprocess

def install_python_with_pip():
    # Install Python and pip using yum
    print("Installing Python and pip...")
    subprocess.run(['yum', 'install', '-y', 'python3', 'python3-pip'], check=True)

def update_package(distro, package, fixed_version, package_type):
    # Remove leading and trailing whitespace from distro
    distro = distro.strip()
    package_type = package_type.strip()

    print(f"Distro: '{distro}'")
    print(f"Package: '{package}'")
    print(f"Package Type: '{package_type}'")
    print(f"Distro Lower: '{distro.lower()}'")
    print(f"repr(distro): '{repr(distro)}'")  # Shows hidden characters
    print(f"Distro Lower == 'redhat': {distro.lower() == 'redhat'}")

    if package_type.lower() == 'python':
        if distro.lower() in ['centos', 'redhat', 'fedora']:
            install_python_with_pip()
        # Print and run pip command for Python packages
        command = ['pip3', 'install', f'{package}=={fixed_version}']
        print(f"Executing command: {' '.join(command)}")
        subprocess.run(command, check=True)
    elif distro.lower() in ['ubuntu', 'debian']:
        # Print and run apt-get commands for Ubuntu/Debian
        update_command = ['apt-get', 'update']
        install_command = ['apt-get', 'install', f'{package}={fixed_version}', '-y']
        print(f"Executing command: {' '.join(update_command)}")
        subprocess.run(update_command, check=True)
        print(f"Executing command: {' '.join(install_command)}")
        subprocess.run(install_command, check=True)
    elif distro.lower() in ['centos', 'redhat', 'fedora']:
        # Print and run yum commands for CentOS/RedHat/Fedora
        update_command = ['yum', 'update', package, '-y']
        install_command = ['yum', 'install', f'{package}-{fixed_version}', '-y']
        print(f"Executing command: {' '.join(update_command)}")
        subprocess.run(update_command, check=True)
        print(f"Executing command: {' '.join(install_command)}")
        subprocess.run(install_command, check=True)
    elif distro.lower() == 'arch':
        # Print and run pacman command for Arch
        command = ['pacman', '-Syu', package, '--noconfirm']
        print(f"Executing command: {' '.join(command)}")
        subprocess.run(command, check=True)
    else:
        raise ValueError(f"Unsupported distribution: {distro}")

def main():
    csv_file = '/tmp/scan.csv'
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['Status'].startswith('fixed in'):
                fixed_version = row['Status'].split(' ')[-1]
                # Pass the PackageType to the update_package function
                update_package(row['Distro'], row['Package'], fixed_version, row['PackageType'])
            elif row['Status'] == 'affected':
                print(f"Package {row['Package']} in {row['Distro']} is affected by {row['CVE ID']} but no fixed version specified.")

if __name__ == '__main__':
    main()
