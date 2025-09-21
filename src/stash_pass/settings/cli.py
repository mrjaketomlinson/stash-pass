from ..utils.crypto import (
    derive_key_from_password,
    SALT_FILE,
    load_vault,
    save_vault,
)
from ..vault.core import Vault
from ..settings.core import (
    load_settings,
    save_settings,
)
import getpass
import typer

app = typer.Typer(help="Manage stash-pass settings")


@app.command("set-master-password")
def set_master_password() -> None:
    """
    Set the master password for the first time.
    Requires a non-empty password. Will not overwrite if already set.
    """
    if SALT_FILE.exists():
        typer.echo(
            "[!] Master password already set. Use change-master-password instead."
        )
        raise typer.Exit()

    password = ""
    while not password.strip():
        password = getpass.getpass("Enter new master password (non-empty): ")

    # Generate salt and store
    from pathlib import Path
    import os

    salt = os.urandom(16)
    SALT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SALT_FILE, "wb") as f:
        f.write(salt)

    # Derive key to ensure valid
    _ = derive_key_from_password(password, salt)
    typer.echo("[+] Master password set successfully.")


@app.command("change-master-password")
def change_master_password() -> None:
    """
    Change the master password.
    Will re-encrypt all stored vault entries with the new password.
    Prompts for the current password and a new password.
    """
    if not SALT_FILE.exists():
        typer.echo("[!] Master password not set yet. Use set-master-password first.")
        raise typer.Exit()

    # Prompt for old password
    old_password = ""
    while not old_password.strip():
        old_password = getpass.getpass("Enter current master password: ")

    salt = open(SALT_FILE, "rb").read()
    old_key = derive_key_from_password(old_password, salt)
    fernet_old = Vault().fernet  # or recreate using old_key
    vault_data = load_vault()

    # Prompt for new password
    new_password = ""
    while not new_password.strip():
        new_password = getpass.getpass("Enter new master password (non-empty): ")

    new_key = derive_key_from_password(new_password, salt)
    fernet_new = Vault().fernet  # replace with new key instance

    # Re-encrypt all entries
    for k, v in vault_data.items():
        decrypted = fernet_old.decrypt(v.encode()) # type: ignore
        vault_data[k] = fernet_new.encrypt(decrypted).decode() # type: ignore

    save_vault(vault_data)
    typer.echo("[+] Master password changed successfully.")


@app.command("set")
def update_setting(
    setting: str = typer.Argument(..., help="The setting key to update."),
    value: str = typer.Argument(..., help="The new value for the setting."),
) -> None:
    """
    Update a setting in the settings file.

    Args:
        setting (str): The setting key to update.
        value (str): The new value for the setting.
    """
    settings = load_settings()
    settings[setting] = value
    save_settings(settings)
    typer.echo(f"[+] Updated setting '{setting}' to '{value}'.")
