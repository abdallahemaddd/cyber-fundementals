import os

# Target file extensions
TARGET_EXTENSIONS = ['.txt', '.docx', '.jpg']

def find_files(start_dir, extensions):
    matched_files = []
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                matched_files.append(full_path)
    return matched_files

def log_results(file_list, output_file='files.log'):
    with open(output_file, 'w') as f:
        for file_path in file_list:
            f.write(file_path + '\n')
    print(f"[+] Found {len(file_list)} files. Logged to {output_file}")

if __name__ == '__main__':
    start_dir = input("Enter the path to search: ").strip()

    if not os.path.isdir(start_dir):
        print("[-] The provided path is not a directory.")
    else:
        results = find_files(start_dir, TARGET_EXTENSIONS)
        log_results(results)
