import os
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

APP_DIR = Path.home() / ".stash_pass"
VAULT_FILE = APP_DIR / "vault.json"
SALT_FILE = APP_DIR / "vault.salt"

APP_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Vault file helpers
# -----------------------------
def load_vault() -> dict:
    """
    Load the vault from the vault file.
    Returns an empty dict if the vault file does not exist.

    Returns:
        dict: The vault data as a dictionary.
    """
    if not VAULT_FILE.exists():
        return {}
    with open(VAULT_FILE, "r") as f:
        return json.load(f)


def save_vault(vault: dict) -> None:
    """
    Save the vault dictionary to the vault file as JSON.

    Args:
        vault (dict): The vault data to save.
    """
    with open(VAULT_FILE, "w") as f:
        json.dump(vault, f, indent=2)


# -----------------------------
# Salt and key derivation
# -----------------------------
def get_salt() -> bytes:
    """
    Retrieve the salt used for key derivation. Generates and saves 
    a new salt if it does not exist.

    Returns:
        bytes: The salt value.
    """
    if not SALT_FILE.exists():
        salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
    else:
        with open(SALT_FILE, "rb") as f:
            salt = f.read()
    return salt


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Derive a Fernet-compatible key from a password and salt using PBKDF2HMAC.

    Args:
        password (str): The master password.
        salt (bytes): The salt value.

    Returns:
        bytes: The derived key, base64-encoded for Fernet.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def get_fernet(password: str) -> Fernet:
    """
    Create a Fernet object for encryption/decryption using the provided password.

    Args:
        password (str): The master password.

    Returns:
        Fernet: A Fernet object initialized with the derived key.
    """
    salt = get_salt()
    key = derive_key_from_password(password, salt)
    return Fernet(key)
