import typer
import getpass
from functools import wraps
from .core import Vault
import pyperclip
from cryptography.exceptions import InvalidSignature
from cryptography.fernet import InvalidToken

app = typer.Typer(help="Manage stored passwords")
vault = Vault()


def require_master_password(func):
    """
    Decorator to ensure the master password is entered before running secure commands.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        vault.ensure_unlocked()
        return func(*args, **kwargs)

    return wrapper


@app.command("add")
@require_master_password
def add_password(
    name: str = typer.Argument(..., help="The name/identifier for the password to add.")
):
    """Add a new password to the vault."""
    pwd = getpass.getpass(f"Enter password for {name}: ")
    try:
        vault.add(name, pwd)
        typer.echo(f"[+] Saved password for {name}")
    except ValueError as e:
        typer.echo(f"[!] {e}")


@app.command("get")
@require_master_password
def get_password(
    name: str = typer.Argument(
        ..., help="The name/identifier for the password to retrieve."
    )
):
    """Retrieve a password from the vault and copy it to the clipboard."""
    try:
        pwd = vault.get(name)
        pyperclip.copy(pwd)
        typer.echo(f"[+] Password for {name} copied to clipboard.")
    except KeyError as e:
        typer.echo(f"[!] {e}")
    except InvalidSignature:
        typer.echo("[!] Incorrect master password.")
    except InvalidToken:
        typer.echo("[!] Incorrect master password.")


@app.command("list")
@require_master_password
def list_passwords():
    """List all stored password names in the vault."""
    try:
        accounts = vault.list_accounts()
        if not accounts:
            typer.echo("[!] Vault is empty.")
        else:
            typer.echo("[+] Stored passwords:")
            for acc in accounts:
                typer.echo(f"  - {acc}")
    except InvalidSignature:
        typer.echo("[!] Incorrect master password.")
    except InvalidToken:
        typer.echo("[!] Incorrect master password.")


@app.command("delete")
@require_master_password
def delete_password(
    name: str = typer.Argument(
        ..., help="The name/identifier for the password to delete."
    )
):
    """Delete a stored password from the vault."""
    try:
        typer.confirm(
            f"Are you sure you want to delete the password '{name}'?",
            abort=True,
        )
        vault.delete(name)
        typer.echo(f"[+] Deleted password {name}")
    except typer.Abort:
        typer.echo("[!] Cancelling delete.")
    except KeyError as e:
        typer.echo(f"[!] {e}")
    except InvalidSignature:
        typer.echo("[!] Incorrect master password.")
    except InvalidToken:
        typer.echo("[!] Incorrect master password.")
