from pathlib import Path

from app import connexion_app, appd
from app.daemon import DaemonThread
from setup import setup

if __name__ == "__main__":
    setup()
    connexion_app.run(f"{Path(__file__).stem}:connexion_app")
elif __name__ == Path(__file__).stem:
    daemon_thread = DaemonThread(appd)
    daemon_thread.start()
