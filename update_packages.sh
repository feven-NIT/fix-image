#!/bin/sh

set -e

# Function to get the package type from the JSON file
get_package_type() {
    package_name="$1"
    awk -v package_name="$package_name" '
    BEGIN { package_type = "" }
    /"pkgsType":/ { type = $2; gsub(/"/, "", type); gsub(/,/, "", type) }
    /"name":/ {
        name = $2;
        gsub(/"/, "", name);
        gsub(/,/, "", name);
        if (name == package_name) {
            package_type = type;
            exit
        }
    }
    END { print package_type }
    ' /tmp/tpackage-json.txt
}

# Function to update the package based on its type
update_package() {
    distro="$1"
    package="$2"
    fixed_version="$3"
    package_type="$4"

    case "$package_type" in
        python)
            echo "Handling Python package update using update_packages.py..."
            python3 /tmp/update_packages.py
            ;;
        nodejs)
            echo "Installing Node.js and npm..."
            yum install -y nodejs npm
            echo "Successfully installed Node.js and npm."
            echo "Updating $package to version $fixed_version"
            npm install "$package@$fixed_version"
            echo "Successfully updated $package to version $fixed_version."
            echo "Removing Node.js and npm..."
            yum remove -y nodejs npm
            echo "Successfully removed Node.js and npm."
            ;;
        package)
            echo "Updating $package..."
            yum update "$package" -y
            echo "Successfully updated $package."
            echo "Installing $package version $fixed_version"
            yum install "$package-$fixed_version" -y
            echo "Successfully installed $package-$fixed_version."
            ;;
        *)
            echo "Unsupported package type: $package_type"
            exit 1
            ;;
    esac
}

# Main function to read the CSV and update packages
main() {
    echo "Starting package updates..."
    while IFS=, read -r repo tag scan_time distro cve_id severity package package_version status cvss published fix_date description link; do
        if [ "$status" != "Status" ]; then  # Skip header
            if echo "$status" | grep -q "fixed in"; then
                fixed_version=$(echo "$status" | awk '{print $NF}')
                package_type=$(get_package_type "$package")
                if [ "$package_type" ]; then
                    echo "Updating package $package of type $package_type in $distro to version $fixed_version."
                    update_package "$distro" "$package" "$fixed_version" "$package_type"
                else
                    echo "Package type for $package not found."
                fi
            elif [ "$status" = "affected" ]; then
                echo "Package $package in $distro is affected by $cve_id but no fixed version specified."
            fi
        fi
    done < /tmp/scan.csv
    echo "Package updates completed successfully."
}

main
