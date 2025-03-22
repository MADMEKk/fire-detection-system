from django.apps import AppConfig

class FireDetectionAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fire_detection_app'

    def ready(self):
        import fire_detection_app.signals
