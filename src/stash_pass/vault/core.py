from ..utils.crypto import load_vault, save_vault, get_fernet, SALT_FILE
import getpass
import sys


class Vault:
    """
    Manages Stash Pass vault with encrypted storage.
    Handles adding, retrieving, listing, and deleting password entries.
    """

    def __init__(self):
        """
        Initializes the Vault.
        """
        self.fernet = None

    def ensure_unlocked(self):
        """
        Prompts for the master password and initializes Fernet if not already unlocked.
        If the master password is not set, instructs the user to run the settings set-master-password command.
        """
        if not SALT_FILE.exists():
            print(
                "[!] Master password is not set. Please run: stash-pass settings set-master-password"
            )
            sys.exit(1)
        if self.fernet is None:
            master_password = ""
            while not master_password.strip():
                master_password = getpass.getpass("Enter master password (non-empty): ")
            self.fernet = get_fernet(master_password)

    def add(self, name: str, password: str):
        """
        Adds a new password entry to the vault.

        Args:
            name (str): The name/identifier for the account.
            password (str): The password to store (will be encrypted).

        Raises:
            ValueError: If an entry with the given name already exists.
        """
        vault = load_vault()
        if name in vault:
            raise ValueError(f"Entry for '{name}' already exists.")
        vault[name] = self.fernet.encrypt(password.encode()).decode()
        save_vault(vault)

    def get(self, name: str) -> str:
        """
        Retrieves and decrypts a password entry from the vault.

        Args:
            name (str): The name/identifier for the account.

        Returns:
            str: The decrypted password.

        Raises:
            KeyError: If no entry with the given name exists.
        """
        vault = load_vault()
        if name not in vault:
            raise KeyError(f"No entry found for '{name}'.")
        return self.fernet.decrypt(vault[name].encode()).decode()

    def list_accounts(self):
        """
        Lists all account names stored in the vault.

        Returns:
            list: A list of account names (str).
        """
        return list(load_vault().keys())

    def delete(self, name: str):
        """
        Deletes a password entry from the vault.

        Args:
            name (str): The name/identifier for the account to delete.

        Raises:
            KeyError: If no entry with the given name exists.
        """
        vault = load_vault()
        if name not in vault:
            raise KeyError(f"No entry found for '{name}'.")
        del vault[name]
        save_vault(vault)
