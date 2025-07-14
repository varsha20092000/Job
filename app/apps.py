from django.apps import AppConfig
from django.core.management import call_command
import os

class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Jobs'

    def ready(self):
        if os.environ.get("RENDER") == "true":
            try:
                call_command("loaddata", "admin_jobs_fixed.json")
                call_command("loaddata", "applications_from_sqlite_fixed.json")
            except Exception as e:
                print(f"❌ Fixture load error: {e}")
