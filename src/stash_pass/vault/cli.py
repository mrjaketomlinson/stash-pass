import typer
import getpass
from .core import Vault

app = typer.Typer(help="Manage stored passwords")
vault = Vault()


@app.command("add")
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
def get_password(
    name: str = typer.Argument(..., help="The name/identifier for the password to retrieve.")
):
    """Retrieve a password from the vault."""
    try:
        pwd = vault.get(name)
        typer.echo(f"[+] Password for {name}: {pwd}")
    except KeyError as e:
        typer.echo(f"[!] {e}")


@app.command("list")
def list_passwords():
    """List all stored password names in the vault."""
    accounts = vault.list_accounts()
    if not accounts:
        typer.echo("[!] Vault is empty.")
    else:
        typer.echo("[+] Stored passwords:")
        for acc in accounts:
            typer.echo(f"  - {acc}")


@app.command("delete")
def delete_password(
    name: str = typer.Argument(..., help="The name/identifier for the password to delete.")
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
