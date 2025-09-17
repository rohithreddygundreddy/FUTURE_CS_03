from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from io import BytesIO
import os
import secrets

# ----------------------------
# Initialize Flask app
# ----------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'supersecretkey'  # change in production

db = SQLAlchemy(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
KEY_FILE = "secret.key"

def load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            key = f.read()
        # Ensure key length is exactly 32 bytes
        if len(key) != 32:
            key = secrets.token_bytes(32)
            with open(KEY_FILE, "wb") as f:
                f.write(key)
        return key
    else:
        key = secrets.token_bytes(32)  # AES-256
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

# ----------------------------
# Database Model
# ----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ----------------------------
# Key management
# ----------------------------
def load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = secrets.token_bytes(32)  # AES-256
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

AES_KEY = load_or_create_key()


# ----------------------------
# AES Encryption/Decryption
# ----------------------------
def encrypt_file(data: bytes) -> bytes:
    iv = secrets.token_bytes(12)  # 96-bit IV for GCM
    encryptor = Cipher(
        algorithms.AES(AES_KEY),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return iv + encryptor.tag + ciphertext


def decrypt_file(data: bytes) -> bytes:
    iv = data[:12]
    tag = data[12:28]
    ciphertext = data[28:]
    decryptor = Cipher(
        algorithms.AES(AES_KEY),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


# ----------------------------
# Auth Routes
# ----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome {user.username}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# ----------------------------
# File Portal Routes
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected!", "danger")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No file selected!", "danger")
            return redirect(request.url)

        data = file.read()
        encrypted_data = encrypt_file(data)
        save_path = os.path.join(UPLOAD_FOLDER, file.filename + ".enc")
        with open(save_path, "wb") as f:
            f.write(encrypted_data)

        # Save file info in database
        new_file = File(filename=file.filename + ".enc", owner_id=session['user_id'])
        db.session.add(new_file)
        db.session.commit()

        flash(f"File '{file.filename}' uploaded and encrypted successfully!", "success")
        return redirect(url_for("index"))

    # Show only files belonging to the current user
    user_files = File.query.filter_by(owner_id=session['user_id']).all()
    files = [f.filename for f in user_files]
    return render_template("index.html", files=files)


@app.route("/download/<filename>")
def download_file(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Check ownership
    file_record = File.query.filter_by(filename=filename, owner_id=session['user_id']).first()
    if not file_record:
        flash("File not found or access denied!", "danger")
        return redirect(url_for("index"))

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        flash("File not found!", "danger")
        return redirect(url_for("index"))

    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    try:
        decrypted_data = decrypt_file(encrypted_data)
    except Exception:
        flash("Decryption failed. Wrong key or corrupted file.", "danger")
        return redirect(url_for("index"))

    original_name = filename[:-4] if filename.endswith(".enc") else filename
    return send_file(
        BytesIO(decrypted_data),
        as_attachment=True,
        download_name=original_name
    )

    
    
@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Check ownership
    file_record = File.query.filter_by(filename=filename, owner_id=session['user_id']).first()
    if not file_record:
        flash("File not found or access denied!", "danger")
        return redirect(url_for("index"))

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(file_record)
    db.session.commit()
    flash(f"File '{filename}' has been deleted.", "success")
    return redirect(url_for("index"))


# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
