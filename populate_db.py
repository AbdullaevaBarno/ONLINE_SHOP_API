import os
import django
import random
from django.utils.text import slugify

# 1. Django sazlamaların júklew (config - seniń proekt papkań atı)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 2. Ózińniń modellerińdi shaqırıw
from shop.models import Category, Product
from users.models import User
from faker import Faker

fake = Faker()

def run_seed():
    print("--- MAǴLIWMATLAR JAZILIWI BASLANDI ---")

    # 1. KATEGORIYALAR JARATIW
    print("1. Kategoriyalar tayarlanıp atır...")
    categories_data = {
        "Elektronika": ["Smartfonlar", "Noutbuklar", "Televizorlar"],
        "Kiyimler": ["Erler kiyimi", "Hayallar kiyimi"],
        "Kitaplar": ["Kórkem ádebiyat", "IT sabaqlıqları"]
    }

    all_sub_cats = []
    for main_name, subs in categories_data.items():
        # Ata kategoriya
        parent, _ = Category.objects.get_or_create(
            name=main_name, 
            defaults={'slug': slugify(main_name)}
        )
        
        for sub_name in subs:
            # Bala kategoriya
            sub, _ = Category.objects.get_or_create(
                name=sub_name,
                parent=parent,
                defaults={'slug': slugify(sub_name) + "-" + str(random.randint(1, 100))}
            )
            all_sub_cats.append(sub)

    # 2. ÓNIMLER JARATIW (50 dana)
    print("2. 50 dana ónim jaratılıp atır...")
    for _ in range(50):
        name = fake.catch_phrase()
        price = random.randint(50000, 5000000)
        
        Product.objects.create(
            category=random.choice(all_sub_cats),
            name=name,
            slug=slugify(name) + "-" + str(random.randint(1, 9999)),
            description=fake.text(),
            price=price,
            stock=random.randint(10, 100),
            is_active=True
        )

    # 3. PAYDALANIWSHILAR JARATIW (5 dana)
    print("3. Klientler jaratılıp atır...")
    for _ in range(5):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = fake.user_name() + str(random.randint(1, 100))
        
        User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password="password123",
            email=fake.email(),
            phone_number=f"+99890{random.randint(1000000, 9999999)}",
            address=fake.address(),
            role='client'
        )

    print("✅ AWMETLİ! Baza professional maǵlıwmatlar menen toltırıldı.")

if __name__ == '__main__':
    run_seed()