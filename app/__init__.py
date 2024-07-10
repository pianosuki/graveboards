import os

from connexion import FlaskApp
from connexion.resolver import RestyResolver
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from authlib.integrations.flask_client import OAuth

from .config import FlaskConfig, OAUTH_AUTHORIZATION_CODE, OAUTH_CLIENT_CREDENTIALS, SPEC_DIR, FLASK_SERVER_ARGS

connexion_app = FlaskApp(__name__, specification_dir=SPEC_DIR, server_args=FLASK_SERVER_ARGS)
flask_app = connexion_app.app

flask_app.config.from_object(FlaskConfig)
connexion_app.add_api(os.path.join(SPEC_DIR, "openapi.yaml"), resolver=RestyResolver("api.v1"))

db = SQLAlchemy(flask_app)
ma = Marshmallow(flask_app)
oauth = OAuth(flask_app)
oauth.register(**OAUTH_AUTHORIZATION_CODE)
oauth.register(**OAUTH_CLIENT_CREDENTIALS)

from .thread_synchronization import ThreadSynchronization
sync = ThreadSynchronization(flask_app)

from .osu_api import OsuAPIClient
from .beatmap_manager import BeatmapManager
from .crud import Crud
oac = OsuAPIClient(app=flask_app)
bm = BeatmapManager(app=flask_app)
cr = Crud(app=flask_app)

from .daemon import GraveboardsDaemon, DaemonThread
from .services import ScoreFetcher, ServiceName
appd = GraveboardsDaemon(app=flask_app)
appd.register_service(ServiceName.SCORE_FETCHER, ScoreFetcher)
daemon_thread = DaemonThread(appd)
