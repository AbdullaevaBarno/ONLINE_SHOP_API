Online Dúkan API (Backend)
Bul proekt — Django REST Framework hám Docker texnologiyaları tiykarında jaratılǵan.

Texnologiyalar Stack-i
Til: Python 3.10+
Framework: Django 4.2+ & Django REST Framework
Maǵlıwmatlar bazası: PostgreSQL
Autentifikaciya: JWT (Simple JWT) hám Passwordless Telegram OTP (One-Time Password)
Hújjetlestiriw: Swagger UI 
Konteynerizaciya: Docker & Docker-compose

Proektti Iske Túsiriw (Instrukciya)
Kompyuterińizde Docker ornatılǵan bolıwı shárt!
```github.com/AbdullaevaBarno/ONLINE_SHOP_API.git
cd ONLINE_SHOP_API```

2. Ortalıqtı (.env) sazlaw
Tiykarǵı papkada .env faylın jaratıń hám tómendegi maǵlıwmatlardı kiritiń:
```SECRET_KEY=super-secret-key-2026
DEBUG=True
DB_HOST=db
POSTGRES_DB=online_dukan
POSTGRES_USER=admin
POSTGRES_PASSWORD=adminpass
TELEGRAM_BOT_TOKEN=(Siziń bot tokenińiz)```

3. Docker-di iske túsiriw
```docker-compose up --build -d```

4. Migraciyalarnı qollanıw hám Admin jaratıw
```# Bazanı jıynaw
docker-compose exec web python manage.py migrate

# Bazanı test tovarları menen toltırıw
docker-compose exec web python populate_db.py

# Admin (Superuser) jaratıw
docker-compose exec web python manage.py createsuperuser```

5. API Endpointler (Hújjetlestiriw)
Server iske túskennen keyin, barlıq mánzillerdi mına siltemeler arqalı kóre alasız:
Swagger UI (Interaktiv): http://127.0.0.1:8000/swagger/

Tiykarǵı Endpointler Dizimi
   Paydalanıwshılar hám Avtorizaciya 
POST	/api/users/register/	Jańa klient dizimnen ótiwi (Atı-familiyası menen)
POST	/api/users/login/	2FA Login: Login-parol (username menen password)
POST	/api/users/token/refresh/	JWT Access tokendi jańalaw
GET	/api/users/profile/	Jeke profil maǵlıwmatların kóriw
PATCH	/api/users/profile/	Profil maǵlıwmatların bólek jańalaw
POST	/api/users/profile/set-password/	Qawipsiz parol ózgertiw
POST  /api/tg-bot/login-telegram/ Telegram bot arqalı kod alıp login qılıw
POST  /api/tg-bot/webhook/  Telegram platformasınıń API menen baylanısı

   Kataloglar & Ónimler hám Pikirler
GET	/api/shop/categories/	Ierarxiyalıq katalog (Terek strukturası)
GET	/api/shop/products/	Barlıq ónimler (Search, Filter, Price Range)
GET	/api/shop/products/{id}/	Ónimlerdi id sı boyınsha kóriw
GET	/api/shop/reviews/	Ónimlerge jazılǵan pikirlerdi kóriw
POST	/api/shop/reviews/	Verified Review: Tek satıp alǵanlar pikir jazadı
PATCH /api/shop/reviews/{id}/  Ózińiz jazǵan pikirdiń reytingin yamasa tekstin bólek jańalaw
DELETE /api/shop/reviews/{id}/ Ózińiz qaldırǵan pikirdi bazadan pútinley alıp taslaw

   Sebet hám Buyırtpa
POST	/api/shop/cart/add/	Sebetke ónim qosıw
GET	/api/shop/cart/my_cart/	Jeke sebeti hám ulıwma summanı kóriw
PATCH	/api/shop/cart-items/{id}/	Sebettegi tovardıń sanın ózgertiw
DELETE	/api/shop/cart-items/{id}/	Tovardı sebetten alıp taslaw
GET  /api/shop/orders/  Paydalanıwshınıń barlıq satıp alǵan zatların dizim túrinde kóredi
GET /api/shop/orders/{id}/  Anıq bir buyırtpanıń ishinde qanday tovarlar bar ekenin (chekin) kóredi
POST	/api/shop/orders/checkout/  Sebetten buyırtpa jaratıw
POST	/api/shop/orders/{id}/t_m/	Buyırtpa statusın 'Tólendi'ge ótkeriw
