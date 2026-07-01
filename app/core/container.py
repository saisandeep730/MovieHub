from logging import getLogger

from app.database import db_manager
from app.repositories import (
    AdminRepository,
    BackupRepository,
    BroadcastRepository,
    CountersRepository,
    HealthRepository,
    MovieFileRepository,
    MovieRepository,
    RequestRepository,
    SessionRepository,
    SettingsRepository,
    UserRepository,
)
from app.services import (
    AdminService,
    BackupService,
    BroadcastService,
    ConfigService,
    DownloadService,
    HealthService,
    MovieService,
    NotificationService,
    RequestService,
    SearchService,
    SettingsService,
    StatisticsService,
    UploadService,
    UserService,
)

logger = getLogger(__name__)


class Container:
    """Centralized dependency injection container.

    Creates and manages all repository and service singletons.
    """

    def __init__(self) -> None:
        # Repositories
        self._movie_repo: MovieRepository | None = None
        self._movie_file_repo: MovieFileRepository | None = None
        self._settings_repo: SettingsRepository | None = None
        self._request_repo: RequestRepository | None = None
        self._user_repo: UserRepository | None = None
        self._admin_repo: AdminRepository | None = None
        self._broadcast_repo: BroadcastRepository | None = None
        self._backup_repo: BackupRepository | None = None
        self._health_repo: HealthRepository | None = None
        self._session_repo: SessionRepository | None = None
        self._counters_repo: CountersRepository | None = None

        # Services
        self._config_service: ConfigService | None = None
        self._movie_service: MovieService | None = None
        self._upload_service: UploadService | None = None
        self._search_service: SearchService | None = None
        self._download_service: DownloadService | None = None
        self._request_service: RequestService | None = None
        self._broadcast_service: BroadcastService | None = None
        self._settings_service: SettingsService | None = None
        self._backup_service: BackupService | None = None
        self._health_service: HealthService | None = None
        self._user_service: UserService | None = None
        self._admin_service: AdminService | None = None
        self._notification_service: NotificationService | None = None
        self._statistics_service: StatisticsService | None = None

    @property
    def movie_repo(self) -> MovieRepository:
        if self._movie_repo is None:
            self._movie_repo = MovieRepository()
        return self._movie_repo

    @property
    def movie_file_repo(self) -> MovieFileRepository:
        if self._movie_file_repo is None:
            self._movie_file_repo = MovieFileRepository()
        return self._movie_file_repo

    @property
    def settings_repo(self) -> SettingsRepository:
        if self._settings_repo is None:
            self._settings_repo = SettingsRepository()
        return self._settings_repo

    @property
    def request_repo(self) -> RequestRepository:
        if self._request_repo is None:
            self._request_repo = RequestRepository()
        return self._request_repo

    @property
    def user_repo(self) -> UserRepository:
        if self._user_repo is None:
            self._user_repo = UserRepository()
        return self._user_repo

    @property
    def admin_repo(self) -> AdminRepository:
        if self._admin_repo is None:
            self._admin_repo = AdminRepository()
        return self._admin_repo

    @property
    def broadcast_repo(self) -> BroadcastRepository:
        if self._broadcast_repo is None:
            self._broadcast_repo = BroadcastRepository()
        return self._broadcast_repo

    @property
    def backup_repo(self) -> BackupRepository:
        if self._backup_repo is None:
            self._backup_repo = BackupRepository()
        return self._backup_repo

    @property
    def health_repo(self) -> HealthRepository:
        if self._health_repo is None:
            self._health_repo = HealthRepository()
        return self._health_repo

    @property
    def session_repo(self) -> SessionRepository:
        if self._session_repo is None:
            self._session_repo = SessionRepository()
        return self._session_repo

    @property
    def counters_repo(self) -> CountersRepository:
        if self._counters_repo is None:
            self._counters_repo = CountersRepository()
        return self._counters_repo

    @property
    def statistics_service(self) -> StatisticsService:
        if self._statistics_service is None:
            self._statistics_service = StatisticsService()
        return self._statistics_service

    @property
    def config_service(self) -> ConfigService:
        if self._config_service is None:
            self._config_service = ConfigService(settings_repo=self.settings_repo)
        return self._config_service

    @property
    def movie_service(self) -> MovieService:
        if self._movie_service is None:
            self._movie_service = MovieService(
                movie_repo=self.movie_repo,
                movie_file_repo=self.movie_file_repo,
            )
        return self._movie_service

    @property
    def upload_service(self) -> UploadService:
        if self._upload_service is None:
            self._upload_service = UploadService(
                movie_repo=self.movie_repo,
                movie_file_repo=self.movie_file_repo,
                counters_repo=self.counters_repo,
                statistics_service=self.statistics_service,
            )
        return self._upload_service

    @property
    def search_service(self) -> SearchService:
        if self._search_service is None:
            self._search_service = SearchService(movie_repo=self.movie_repo)
        return self._search_service

    @property
    def download_service(self) -> DownloadService:
        if self._download_service is None:
            self._download_service = DownloadService(
                movie_repo=self.movie_repo,
                movie_file_repo=self.movie_file_repo,
            )
        return self._download_service

    @property
    def request_service(self) -> RequestService:
        if self._request_service is None:
            self._request_service = RequestService(request_repo=self.request_repo)
        return self._request_service

    @property
    def broadcast_service(self) -> BroadcastService:
        if self._broadcast_service is None:
            self._broadcast_service = BroadcastService(broadcast_repo=self.broadcast_repo)
        return self._broadcast_service

    @property
    def settings_service(self) -> SettingsService:
        if self._settings_service is None:
            self._settings_service = SettingsService(settings_repo=self.settings_repo)
        return self._settings_service

    @property
    def backup_service(self) -> BackupService:
        if self._backup_service is None:
            self._backup_service = BackupService(backup_repo=self.backup_repo)
        return self._backup_service

    @property
    def health_service(self) -> HealthService:
        if self._health_service is None:
            self._health_service = HealthService(health_repo=self.health_repo)
        return self._health_service

    @property
    def user_service(self) -> UserService:
        if self._user_service is None:
            self._user_service = UserService(user_repo=self.user_repo)
        return self._user_service

    @property
    def admin_service(self) -> AdminService:
        if self._admin_service is None:
            self._admin_service = AdminService(admin_repo=self.admin_repo)
        return self._admin_service

    @property
    def notification_service(self) -> NotificationService:
        if self._notification_service is None:
            self._notification_service = NotificationService()
        return self._notification_service


container = Container()
