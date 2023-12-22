import os
from connexion import FlaskApp
from connexion.resolver import RestyResolver
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from authlib.integrations.flask_client import OAuth
from config import FlaskConfig, OAUTH, SPEC_PATH, FLASK_SERVER_ARGS

connexion_app = FlaskApp(__name__, specification_dir=SPEC_PATH, server_args=FLASK_SERVER_ARGS)
flask_app = connexion_app.app

flask_app.config.from_object(FlaskConfig)
connexion_app.add_api(os.path.join(SPEC_PATH, "openapi.yaml"), resolver=RestyResolver("api.v1"))

db = SQLAlchemy(flask_app)
ma = Marshmallow(flask_app)
oauth = OAuth(flask_app)
oauth.register(**OAUTH)

from .routes import main_bp, oauth_bp
flask_app.register_blueprint(main_bp, url_prefix="/")
flask_app.register_blueprint(oauth_bp, url_prefix="/oauth")
