from cryptography.fernet import Fernet

# -------------------------------
# Step 1: Key Generation
# -------------------------------
def generate_key():
    """
    Generates a new symmetric encryption key.
    Returns:
        key (bytes): The generated key
    """
    key = Fernet.generate_key()
    print(f"Generated Key: {key.decode()}")
    return key

# -------------------------------
# Step 2: Encrypt Message
# -------------------------------
def encrypt_message(message, key):
    """
    Encrypts a message using the provided key.
    Args:
        message (str): Plaintext message
        key (bytes): Symmetric encryption key
    Returns:
        encrypted_message (bytes): Ciphertext
    """
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    print(f"Encrypted Message: {encrypted_message.decode()}")
    return encrypted_message

# -------------------------------
# Step 3: Decrypt Message
# -------------------------------
def decrypt_message(encrypted_message, key):
    """
    Decrypts an encrypted message using the provided key.
    Args:
        encrypted_message (bytes): Ciphertext
        key (bytes): Symmetric encryption key
    Returns:
        decrypted_message (str): Original plaintext
    """
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message).decode()
    print(f"Decrypted Message: {decrypted_message}")
    return decrypted_message

# -------------------------------
# Main Execution
# -------------------------------
if __name__ == "__main__":
    # Generate key
    key = generate_key()

    # Message to encrypt
    message = "Hello, this is a secret message!"

    # Encrypt
    encrypted_msg = encrypt_message(message, key)

    # Decrypt
    decrypted_msg = decrypt_message(encrypted_msg, key)
