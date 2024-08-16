from .graveboards_daemon import GraveboardsDaemon
from .services import ServiceClass

daemon_app = GraveboardsDaemon()
daemon_app.register_service(ServiceClass.SCORE_FETCHER)
daemon_app.register_service(ServiceClass.MAPPER_INFO_FETCHER)

from .daemon_thread import DaemonThread

daemon_thread = DaemonThread(daemon_app)
