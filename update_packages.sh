#!/bin/sh

set -e

update_package() {
    distro="$1"
    package="$2"
    fixed_version="$3"
    package_type="$4"

    case "$package_type" in
        python)
            python3 /tmp/update_packages.py
            ;;
        nodejs)
            echo "Installing Node.js and npm..."
            yum install -y nodejs npm
            echo "Updating $package to version $fixed_version"
            npm install "$package@$fixed_version"
            echo "Removing Node.js and npm..."
            yum remove -y nodejs npm
            ;;
        package)
            echo "Updating $package..."
            yum update "$package" -y
            echo "Installing $package version $fixed_version"
            yum install "$package-$fixed_version" -y
            ;;
        *)
            echo "Unsupported package type: $package_type"
            exit 1
            ;;
    esac
}

main() {
    while IFS=, read -r distro package status cve_id; do
        if [ "$status" != "Status" ]; then  # Skip header
            if echo "$status" | grep -q "fixed in"; then
                fixed_version=$(echo "$status" | awk '{print $NF}')
                package_type=$(python3 -c "
import json
with open('/tmp/tpackage-json.txt', 'r') as file:
    data = json.load(file)
    package_type = None
    for repo, content in data.items():
        for pkg_group in content['packages']:
            for pkg in pkg_group['pkgs']:
                if pkg['name'] == '$package':
                    package_type = pkg_group['pkgsType']
                    break
    print(package_type)
                ")
                if [ "$package_type" ]; then
                    update_package "$distro" "$package" "$fixed_version" "$package_type"
                else
                    echo "Package type for $package not found."
                fi
            elif [ "$status" = "affected" ]; then
                echo "Package $package in $distro is affected by $cve_id but no fixed version specified."
            fi
        fi
    done < /tmp/scan.csv
}

main
