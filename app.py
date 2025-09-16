import os
import io
from flask import Flask, request, redirect, url_for, render_template, send_file, flash
from cryptography.fernet import Fernet
import secrets
print(secrets.token_bytes(32).hex())

# -------------------------------
# Configurations
# -------------------------------
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'}

# Flask setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback_secret")

# -------------------------------
# Secure Key Management
# -------------------------------
env_key = os.environ.get("FILE_PORTAL_KEY")
if not env_key:
    raise RuntimeError("❌ FILE_PORTAL_KEY not set! Please set it as an environment variable.")

fernet = Fernet(env_key.encode())

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------------------------------
# Helpers
# -------------------------------
def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------
# Routes
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page: upload form + file list"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part provided')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            data = file.read()
            encrypted = fernet.encrypt(data)

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename + ".enc")
            with open(filepath, "wb") as f:
                f.write(encrypted)

            flash('✅ File uploaded & encrypted successfully!')
            return redirect(url_for('index'))

    files = [f.replace(".enc", "") for f in os.listdir(app.config['UPLOAD_FOLDER'])]
    return render_template('index.html', files=files)


@app.route('/download/<filename>')
def download_file(filename):
    """Decrypt before sending file"""
    enc_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".enc")
    if not os.path.exists(enc_path):
        flash("❌ File not found")
        return redirect(url_for('index'))

    with open(enc_path, "rb") as f:
        encrypted = f.read()

    decrypted = fernet.decrypt(encrypted)

    return send_file(
        io.BytesIO(decrypted),
        as_attachment=True,
        download_name=filename
    )


@app.route('/files')
def files():
    """Optional separate file list page"""
    files = [f.replace(".enc", "") for f in os.listdir(app.config['UPLOAD_FOLDER'])]
    return render_template('files.html', files=files)


# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
