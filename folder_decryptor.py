import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# === CONFIGURATION ===
ENCRYPTED_FOLDER = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'files.log')  # Encrypted folder (files.log)
KEY_FILE = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'key.bin')  # AES key file
RESTORED_FOLDER = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'restored_staging_copy')  # Folder to restore files

# Function to decrypt a single file
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
    rel_path = os.path.relpath(file_path, ENCRYPTED_FOLDER)
    restored_file_path = os.path.join(RESTORED_FOLDER, rel_path)

    # Ensure the directory structure exists for the restored file
    os.makedirs(os.path.dirname(restored_file_path), exist_ok=True)

    # Write the decrypted content to the restored folder
    with open(restored_file_path, 'wb') as f:
        f.write(decrypted_data)

    print(f"[+] Decrypted and restored: {restored_file_path}")

# Function to decrypt the entire folder
def decrypt_folder(encrypted_folder, key):
    print(f"[+] Scanning folder: {encrypted_folder}")
    
    for root, dirs, files in os.walk(encrypted_folder):
        for file in files:
            encrypted_file_path = os.path.join(root, file)
            print(f"[+] Found file: {encrypted_file_path}")  # Debugging: show each file found
            decrypt_file(encrypted_file_path, key)

if __name__ == '__main__':
    # Step 1: Check if the AES key file exists
    if not os.path.exists(KEY_FILE):
        print(f"[!] Key file '{KEY_FILE}' not found. Aborting.")
        exit(1)

    # Step 2: Load the AES key from the key file
    with open(KEY_FILE, 'rb') as f:
        key = f.read()
    print("[+] Loading AES key...")

    # Step 3: Ensure the restored folder exists
    if not os.path.exists(RESTORED_FOLDER):
        os.makedirs(RESTORED_FOLDER)
        print(f"[+] Created folder: {RESTORED_FOLDER}")

    # Step 4: Decrypt the folder contents
    print("[+] Decrypting folder contents...")
    decrypt_folder(ENCRYPTED_FOLDER, key)

    # Step 5: Confirm decryption is complete
    print(f"[+] Decryption complete. Restored files are in: {RESTORED_FOLDER}")
