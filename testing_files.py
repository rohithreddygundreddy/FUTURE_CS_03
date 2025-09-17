import requests
import hashlib

# Flask app must already be running on http://127.0.0.1:5000

UPLOAD_URL = "http://127.0.0.1:5000/"
DOWNLOAD_URL = "http://127.0.0.1:5000/download/"

# Step 1: Create a test file
test_filename = "Testing file-portal.txt"
with open(test_filename, "w") as f:
    f.write("Hello, Secure Portal! This is a test file.\n")

# Step 2: Upload the file
with open(test_filename, "rb") as f:
    files = {"file": (test_filename, f)}
    r = requests.post(UPLOAD_URL, files=files, allow_redirects=True)
    print("Upload status:", r.status_code)

# Step 3: Download the file back
download_name = test_filename + ".enc"   # server stores with .enc
r = requests.get(DOWNLOAD_URL + download_name, allow_redirects=True)
downloaded_file = "downloaded_" + test_filename

with open(downloaded_file, "wb") as f:
    f.write(r.content)
print("Downloaded:", downloaded_file)

# Step 4: Compare hashes
def sha256sum(filename):
    h = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

orig_hash = sha256sum(test_filename)
down_hash = sha256sum(downloaded_file)

print("Original SHA256:", orig_hash)
print("Downloaded SHA256:", down_hash)

if orig_hash == down_hash:
    print(" File integrity test passed! Files are identical.")
else:
    print(" Integrity test failed! Files differ.")
