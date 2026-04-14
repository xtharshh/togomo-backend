from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.marketplace"

    def ready(self) -> None:
        from . import signals  # noqa: F401
