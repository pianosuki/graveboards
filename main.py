from pathlib import Path

from app import connexion_app, daemon_thread
from setup import setup


if __name__ == "__main__":
    setup()
    connexion_app.run(f"{Path(__file__).stem}:connexion_app")
elif __name__ == Path(__file__).stem:
    daemon_thread.start()
