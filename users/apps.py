import sys
import threading
import requests
from django.apps import AppConfig
from django.conf import settings

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals

        if self.is_manage_py_command():
            return

        threading.Thread(target=self.set_telegram_webhook, daemon=True).start()

    def is_manage_py_command(self):
        ignored_commands = ['migrate', 'makemigrations', 'collectstatic', 'createsuperuser', 'test']
        return any(cmd in sys.argv for cmd in ignored_commands)

    def set_telegram_webhook(self):
        try:
            token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
            webhook_url = getattr(settings, 'TELEGRAM_WEBHOOK_URL', None)

            if token and webhook_url:
                url = f"https://api.telegram.org/bot{token}/setWebhook"
                response = requests.post(url, json={"url": webhook_url}, timeout=5)
                
                if response.status_code == 200:
                    print(f"🚀 [AUTO-BOT] Webhook sátiyli jańalandı: {webhook_url}")
                else:
                    print(f"⚠️ [AUTO-BOT] Webhook ornatılmadı: {response.text}")
        except Exception as e:
            print(f" [AUTO-BOT] Webhook Error: {e}")