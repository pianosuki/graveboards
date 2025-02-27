from connexion import AsyncApp
from connexion.exceptions import Forbidden
from connexion.resolver import RestyResolver
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

from .lifespan import lifespan
from .spec import openapi_spec
from .error_handlers import forbidden
from .config import SPEC_DIR

connexion_app = AsyncApp(__name__, specification_dir=SPEC_DIR, lifespan=lifespan)

connexion_app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
connexion_app.add_api(openapi_spec, resolver=RestyResolver("api.v1"))
connexion_app.add_error_handler(Forbidden, forbidden)
