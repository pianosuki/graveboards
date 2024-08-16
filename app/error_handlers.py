from connexion.problem import problem
from connexion.exceptions import Forbidden
from connexion.lifecycle import ConnexionRequest, ConnexionResponse


def forbidden(request: ConnexionRequest, exc: Exception | Forbidden) -> ConnexionResponse:
    return problem(status=403, title="Forbidden", detail=exc.detail, type="about:blank")
