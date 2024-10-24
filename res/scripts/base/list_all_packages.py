import os
import subprocess
from art import text2art  # Make sure to install the 'art' library using `pip install art`

# Directory where the package lists are stored
package_dir = "package_lists"
unified_file = os.path.join(package_dir, "unified_packages_list.txt")  # Store unified file in package_lists directory

# Package managers and corresponding file names
package_files = {
    "dnf": "installed_packages_dnf.txt",
    "yum": "installed_packages_yum.txt",
    "flatpak": "installed_packages_flatpak.txt",
    "snap": "installed_packages_snap.txt",
    "apt": "installed_packages_apt.txt",
    "pacman": "installed_packages_pacman.txt",
    "brew": "installed_packages_brew.txt"
}

# Package manager commands
package_managers = {
    'dnf': ['dnf', 'list', 'installed'],
    'yum': ['yum', 'list', 'installed'],  
    'apt': ['dpkg', '--get-selections'],
    'pacman': ['pacman', '-Q'],
    'flatpak': ['flatpak', 'list'],
    'snap': ['snap', 'list'],
    'brew': ['brew', 'list', '--versions']
}

# Format functions for package managers
def format_dnf_packages(package_list):
    return "\n".join(package_list[1:])  # Skip header

def format_yum_packages(package_list):
    return "\n".join(package_list[1:])

def format_apt_packages(package_list):
    return "\n".join(line.replace("\t", " ") for line in package_list)

def format_pacman_packages(package_list):
    return "\n".join(package_list)

def format_flatpak_packages(package_list):
    formatted = ["Name\t\tApplication ID\t\tVersion\n"]
    for line in package_list[1:]:
        parts = line.split("\t")
        if len(parts) >= 3:
            name = parts[0].strip()
            app_id = parts[1].strip()
            version = parts[2].strip()
            formatted.append(f"{name:<20}\t{app_id:<30}\t{version}")
    return '\n'.join(formatted)

def format_snap_packages(package_list):
    return "\n".join(package_list)

def format_brew_packages(package_list):
    return "\n".join(package_list)

# Add brew to format functions
format_functions = {
    "dnf": format_dnf_packages,
    "yum": format_yum_packages,
    "apt": format_apt_packages,
    "pacman": format_pacman_packages,
    "flatpak": format_flatpak_packages,
    "snap": format_snap_packages,
    "brew": format_brew_packages  
}

def save_to_file(filename, content):
    try:
        with open(filename, 'w') as f:
            f.write(content)
    except Exception as e:
        print(f"Error saving to {filename}: {e}")

def detect_distro_name():
    # Detect the distribution name using lsb_release
    try:
        distro_info = subprocess.check_output(['lsb_release', '-d']).decode('utf-8')
        return distro_info.split(":")[1].strip() if "Description" in distro_info else "Unknown Distribution"
    except Exception:
        return "Unknown Distribution"

def detect_package_managers():
    detected_managers = []
    print("Detecting installed package managers...")

    # Check for installed package managers
    for manager in package_managers.keys():
        if subprocess.run(['which', manager], capture_output=True, text=True).returncode == 0:
            # Skip appending yum if dnf is already detected
            if manager == 'yum' and 'dnf' in detected_managers:
                continue
            detected_managers.append(manager)

    print(f"Detected package managers: {', '.join(detected_managers)}")
    return detected_managers


def list_installed_packages():
    if not os.path.exists(package_dir):
        os.makedirs(package_dir)

    detected_managers = detect_package_managers()
    if detected_managers:
        print("Listing all installed packages:")
        for manager in detected_managers:
            command = package_managers[manager]
            print(f"  - {manager.capitalize()}...")
            try:
                package_list = subprocess.check_output(command).decode('utf-8').splitlines()
                formatted_packages = format_functions[manager](package_list)
                save_to_file(os.path.join(package_dir, package_files[manager]), formatted_packages)
                print(f"    Installed packages for {manager} saved to '{package_files[manager]}'")
            except subprocess.CalledProcessError as e:
                print(f"    Error listing packages for {manager}: {e}")
    else:
        print("No supported package managers found.")

def read_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    else:
        return []

def format_unified_list(package_data, detected_managers):
    all_managers = ", ".join(package_managers.keys())
    detected_str = ", ".join(detected_managers).capitalize()
    
    unified_list = [f"Detected Package Managers: {detected_str}\n"]
    unified_list.append(f"Potential Package Managers: {all_managers}\n\n")
    
    for manager, data in package_data.items():
        if data:
            unified_list.append(f"{manager.capitalize()} Packages:")
            unified_list.extend(data)
            unified_list.append("\n")
    return "\n".join(unified_list)

def create_unified_list():
    detected_managers = detect_package_managers()
    package_data = {}
    
    for manager, filename in package_files.items():
        file_path = os.path.join(package_dir, filename)
        package_data[manager] = read_file(file_path)
    
    unified_list = format_unified_list(package_data, detected_managers)
    save_to_file(unified_file, unified_list)  # Use the save_to_file function
    print(f"Unified package list saved to {unified_file}")

def cleanup_files():
    for file in os.listdir(package_dir):
        file_path = os.path.join(package_dir, file)
        if file_path != unified_file:
            os.remove(file_path)
    print("Removed individual package list files.")

def main():
    print(text2art("Package List"))  # ASCII art header
    print("Starting package listing script...\n")
    
    distro_name = detect_distro_name()
    print(f"Detected distribution: {distro_name}\n")
    
    list_installed_packages()
    create_unified_list()
    cleanup_files()
    
    print("\nAll tasks completed successfully! The unified package list is ready for review.")

if __name__ == "__main__":
    main()
