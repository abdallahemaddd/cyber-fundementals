import os
import shutil

# === CONFIGURATION ===
TARGET_EXTENSIONS = ('.txt', '.docx', '.jpg')  # You can add more extensions
SOURCE_DIR = input("Enter the folder to search: ")  # User specifies source folder
STAGING_DIR = os.path.join(os.environ['USERPROFILE'], 'Desktop', '.staging_copy')  # Folder to copy files to
LOG_FILE = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'files.log')  # Log file to record paths of copied files

def collect_files(source_dir, target_dir):
    """Collect files from source_dir matching TARGET_EXTENSIONS and copy them to target_dir."""
    if not os.path.exists(source_dir):
        print(f"[!] Source folder '{source_dir}' does not exist. Aborting.")
        return
    
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)  # Clean up previous staging directory
    os.makedirs(target_dir)  # Create the new staging directory

    results = []  # To store file paths to log

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(TARGET_EXTENSIONS):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, source_dir)  # Preserve folder structure
                dest_path = os.path.join(target_dir, rel_path)

                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(full_path, dest_path)  # Copy the file to the new location
                results.append(dest_path)  # Add the copied file path to results
                print(f"[+] Copied: {full_path} -> {dest_path}")
    
    # Log the results to files.log on Desktop
    log_results(results)

def log_results(results):
    """Log the file paths of copied files to 'files.log'."""
    with open(LOG_FILE, 'w') as log_file:
        for result in results:
            log_file.write(result + '\n')
    print(f"[+] Results logged to {LOG_FILE}")

if __name__ == '__main__':
    print(f"[+] Searching files with extensions {TARGET_EXTENSIONS}...")
    collect_files(SOURCE_DIR, STAGING_DIR)
    print("[+] File collection complete.")
