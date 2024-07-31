import os
import csv
import subprocess

def update_package(distro, package, fixed_version):
    # Remove leading and trailing whitespace from distro
    distro = distro.strip()

    print(f"Distro: {distro}")
    print(f"Package: {package}")
    print(f"Distro Lower: {distro.lower()}")
    print(f"repr(distro): {repr(distro)}")  # Shows hidden characters
    print(f"Distro Lower == 'redhat': {distro.lower() == 'redhat'}")

    # Adjusted distro checks to handle whitespace issues
    if distro.lower() in ['ubuntu', 'debian', 'redhat']:
        subprocess.run(['apt-get', 'update'], check=True)
        subprocess.run(['apt-get', 'install', f'{package}={fixed_version}', '-y'], check=True)
    elif distro.lower() in ['centos', 'redhat', 'fedora']:
        subprocess.run(['yum', 'update', package, '-y'], check=True)
        subprocess.run(['yum', 'install', f'{package}-{fixed_version}', '-y'], check=True)
    elif distro.lower() == 'arch':
        subprocess.run(['pacman', '-Syu', package, '--noconfirm'], check=True)
    else:
        raise ValueError(f"Unsupported distribution: {distro}")

def main():
    csv_file = '/tmp/scan.csv'
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['Status'].startswith('fixed in'):
                fixed_version = row['Status'].split(' ')[-1]
                update_package(row['Distro'], row['Package'], fixed_version)
            elif row['Status'] == 'affected':
                print(f"Package {row['Package']} in {row['Distro']} is affected by {row['CVE ID']} but no fixed version specified.")

if __name__ == '__main__':
    main()
