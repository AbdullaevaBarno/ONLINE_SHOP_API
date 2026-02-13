from rest_framework import serializers

class TelegramLoginSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, help_text="Telegram bot jibergen kod")