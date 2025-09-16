# 🔒 Secure File Portal Using Python Flask

## Overview
This project is a **secure file portal** where users can **upload and download files safely**.  
Files are **encrypted using AES-GCM** before storage to ensure **confidentiality and integrity**.

**Features:**
- Upload files securely (AES encryption applied automatically)  
- Download files securely (AES decryption applied automatically)  
- Simple and user-friendly web interface  
- AES key stored securely in `secret.key`  
- File integrity verification  
- Safe handling of filenames  

## Project Structure:
file-portal/
├── app.py             # Main Flask application
├── secret.key         # AES key stored securely
├── uploads/           # Encrypted files storage
└── templates/
├── index.html     # Upload form + file list
└── files.html     # Optional separate file list

## Screenshots


## Technologies
- Python 3.13.5  
- Flask Web Framework  
- cryptography library (AES / Fernet)  
- HTML + Bootstrap  

## Setup Instructions

1. **Clone the repository:**
git clone <repository_url>
cd file_portal

2. **Install dependencies:**
pip install flask cryptography

3. **Run the application:**
python app.py

4. Open your browser at:
http://127.0.0.1:5000/

## Security Measures
* AES-GCM encryption ensures secure file storage
* Key management: AES key stored securely, never hard-coded
* File integrity checked during decryption
* Filenames sanitized using `secure_filename`
* Files served only via Flask routes

## Testing
* Upload text, PDF, and image files
* Download files → verify SHA-256 checksum matches original
* Inspect `uploads/` → files appear encrypted
* Deleting or modifying the key prevents decryption

## Conclusion
This project demonstrates:
* Secure file upload/download
* AES encryption & key management
* File integrity validation
* Simple Flask web interface
