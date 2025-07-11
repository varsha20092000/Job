from django.apps import AppConfig
import os

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App'

    def ready(self):
        if os.environ.get("RENDER") == "true":
            from django.core.management import call_command
            from django.db.utils import OperationalError
            try:
                call_command("loaddata", "full_data.json")
                print("✅ Loaded full_data.json successfully on Render.")
            except OperationalError:
                print("⚠️ Database not ready yet.")
            except Exception as e:
                print(f"❌ Error loading fixture: {e}")
