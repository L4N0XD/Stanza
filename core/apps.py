from django.apps import AppConfig

default_app_config = 'core.apps.CoreConfig'

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
