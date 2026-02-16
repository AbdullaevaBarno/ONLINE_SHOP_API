import random
import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .serializers import TelegramLoginSerializer
from users.serializers import (
    UserProfileSerializer, 
    SetPasswordSerializer,
)

User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
@extend_schema(tags=['Telegram Bot Authentication'])
class TelegramWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'telegram_webhook'

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            update = request.data
            
            if "message" in update:
                message = update["message"]
                chat_id = message["chat"]["id"]
                
                
                if "text" in message:
                    text = message["text"]
                    
                    if text == "/start":
                        self.send_contact_request(chat_id)
                    
                    # Login 
                    elif text == "/login" or text == "🔐 Login ushın kod alıw":
                        self.handle_login_request(chat_id)

                # kontakt
                elif "contact" in message:
                    self.handle_contact(message, chat_id)
            
            return Response({"status": "ok"})
        except Exception as e:
            print(f"Telegram Error: {e}")
            return Response({"status": "ok"})

    

    def check_rate_limit(self, chat_id):
        """
        Eger user sońǵı 1 minutta kod alǵan bolsa True qaytaradı.
        """
        is_limited = cache.get(f"rate_limit_{chat_id}")
        if is_limited:
            self.send_message(chat_id, "⚠️ Siz aldınǵı kodtı jaqında aldıńız.\n(Jańa kodtı birazdan(1 minuttan soń) ala alasız.)")
            return True
        return False

    def set_rate_limit(self, chat_id):
        """
        Userdi 1 minutqa (60 sekund) bloklaw
        """
        cache.set(f"rate_limit_{chat_id}", "true", timeout=60)

    # --- REQUEST HANDLERS ---

    def handle_login_request(self, chat_id):
        # 1. Rate Limit Tekseriw
        if self.check_rate_limit(chat_id):
            return

        try:
            user = User.objects.get(telegram_chat_id=str(chat_id))
            
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            cache_data = {
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "chat_id": chat_id
            }
            cache.set(f"auth_code_{code}", cache_data, timeout=180) 
            
            self.set_rate_limit(chat_id)
            self.send_message(chat_id, f"🔑 Login giltińiz: {code}\n⏳ Bul kod 3 minut dawamında aktiv")
            
        except User.DoesNotExist:
            self.send_message(chat_id, "Siz ele dizimnen ótpegensiz. Iltimas, 'Telefon nomerdi jiberiw' túymesin basıń.")
            self.send_contact_request(chat_id)

    def handle_contact(self, message, chat_id):
        if self.check_rate_limit(chat_id):
            return

        phone_number = message["contact"]["phone_number"]
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        first_name = message["from"].get("first_name", "")
        last_name = message["from"].get("last_name", "")
        
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        cache_data = {
            "phone_number": phone_number,
            "first_name": first_name,
            "last_name": last_name,
            "chat_id": chat_id
        }
        
        cache.set(f"auth_code_{code}", cache_data, timeout=180)
        
        self.set_rate_limit(chat_id)
        self.send_message(chat_id, f"🔑 Login giltińiz: {code}\n⏳ Bul kod 3 minut dawamında aktiv")


    def send_contact_request(self, chat_id):
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "Saytqa kiriw ushın telefon nomerińizdi jiberiń:",
            "reply_markup": {
                "keyboard": [
                    [{"text": "📱 Telefon nomerdi jiberiw", "request_contact": True}],
                    [{"text": "🔐 Login ushın kod alıw"}] 
                ],
                "resize_keyboard": True,
                "one_time_keyboard": False
            }
        }
        requests.post(url, json=payload)

    def send_message(self, chat_id, text):
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {
                "keyboard": [
                    [{"text": "🔐 Login ushın kod alıw"}] 
                ],
                "resize_keyboard": True
            }
        }
        requests.post(url, json=payload)

#TG Login 
@extend_schema(tags=['Telegram Bot Authentication'])
class LoginWithCodeView(APIView):
    serializer_class = TelegramLoginSerializer
    authentication_classes = []
    permission_classes = []

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'telegram_login'

    @extend_schema(request=TelegramLoginSerializer) 
    def post(self, request):
        serializer = TelegramLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        code = serializer.validated_data['code']
        
        cache_data = cache.get(f"auth_code_{code}")
        if not cache_data:
            return Response({"error": "Bul kod qáte yamasa múddeti ótken, iltimas kodıńızdı tekserip kóriń yaki qaytadan kod alıń!"}, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = cache_data.get("phone_number")
        first_name = cache_data.get("first_name", "")
        last_name = cache_data.get("last_name", "")
        chat_id = cache_data.get("chat_id")
        
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'username': phone_number,
                'first_name': first_name,
                'last_name': last_name,
                'telegram_chat_id': str(chat_id),
                'is_verified': True
            }
        )
        
        if str(chat_id) and user.telegram_chat_id != str(chat_id):
            user.telegram_chat_id = str(chat_id)
            user.is_verified = True
            user.save()

        cache.delete(f"auth_code_{code}")
        
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "phone_number": phone_number,
            "is_new_user": created,
            "message": "Xosh keldiniz!"
        })
    

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer



class SetPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=SetPasswordSerializer,responses={200:None})
    def post(self,request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password']) 
            user.save()
            
            return Response({'message':'Parol ornatıldı!'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)