from .graveboards_daemon import GraveboardsDaemon
from .services import ServiceClass

daemon_app = GraveboardsDaemon()
daemon_app.register_service(ServiceClass.SCORE_FETCHER)
daemon_app.register_service(ServiceClass.MAPPER_INFO_FETCHER)
daemon_app.register_service(ServiceClass.QUEUE_REQUEST_HANDLER)

from .daemon_thread import DaemonThread

daemon_thread = DaemonThread(daemon_app)
