from django.apps import AppConfig
from django.core.management import call_command
import os

class AppReady(AppConfig):
    name = 'App'

    def ready(self):
        if os.environ.get("RENDER") == "true":
            try:
                call_command("loaddata", "full_data.json")
                print("✅ full_data.json loaded into Render PostgreSQL.")
            except Exception as e:
                print("❌ Failed to load full_data.json:", e)
