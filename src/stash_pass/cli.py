import typer
from .vault.cli import app as vault_app
from .settings.cli import app as settings_app

app = typer.Typer(help="🔑 Stash Pass CLI")

# Mount sub-apps
app.add_typer(vault_app, name="vault")
app.add_typer(settings_app, name="settings")

def main():
    app()

if __name__ == "__main__":
    main()
