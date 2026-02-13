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
    print("--- TAZALAW HÁM JAZIW BASLANDI ---")
    
    # 0. Eskilerdi óshiremiz (Taza baza bolıwı ushın)
    Product.objects.all().delete()
    # User.objects.filter(is_superuser=False).delete() # Qaleseńiz ápiwayı userlerdi de óshiriń

    # 1. KATEGORIYALAR JARATIW
    print("1. Kategoriyalar tayarlanıp atır...")
    categories_data = {
        "Elektronika": ["Smartfonlar", "Noutbuklar", "Televizorlar", "Qulaqshınlar"],
        "Kiyimler": ["Erler kiyimi", "Hayallar kiyimi", "Ayaq kiyimler"],
        "Kitaplar": ["Kórkem ádebiyat", "Biznes", "IT sabaqlıqları"]
    }

    all_sub_cats = []
    for main_name, subs in categories_data.items():
        parent, _ = Category.objects.get_or_create(
            name=main_name, 
            defaults={'slug': slugify(main_name)}
        )
        for sub_name in subs:
            sub, _ = Category.objects.get_or_create(
                name=sub_name,
                parent=parent,
                defaults={'slug': slugify(sub_name) + "-" + str(random.randint(1, 100))}
            )
            all_sub_cats.append(sub)

    # 2. ÓNIMLER JARATIW (Haqıyqıy atamalar menen)
    print("2. 50 dana professional ónim jaratılıp atır...")
    
    # Atamalar ushın úlgiler
    brands = ["Apple", "Samsung", "Xiaomi", "Nike", "Adidas", "Sony", "HP", "Dell", "LG"]
    product_types = ["Pro", "Max", "Ultra", "Air", "Classic", "Sport", "Gaming", "v2", "2024"]

    for _ in range(50):
        brand = random.choice(brands)
        p_type = random.choice(product_types)
        
        # Kategoriyanı saylaymız
        category = random.choice(all_sub_cats)
        
        # Atama jaratıw (Mısalı: Samsung Ultra Televizorlar 45)
        name = f"{brand} {p_type} {category.name[:-3]}" # 'lar' qosımtasın alıp taslaw ushın
        
        # Baha (100.000 den 10.000.000 ge shekem)
        price = random.randint(10, 1000) * 10000 
        
        temp_slug = slugify(name)[:40] + "-" + str(random.randint(1, 9999))

        Product.objects.create(
            category=category,
            name=name,
            slug=temp_slug,
            description=f"Bul júdá sapalı {name}. Ózbekstan boyınsha jetkerip beriw xızmeti bar!",
            price=price,
            stock=random.randint(10, 50),
            is_active=True
        )

    # 3. PAYDALANIWSHILAR JARATIW
    print("3. 5 dana test klientleri jaratılıp atır...")
    for _ in range(5):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = fake.user_name()
        
        # User bar-joǵın tekserip jaratamız
        if not User.objects.filter(username=username).exists():
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

    print("Baza maǵlıwmatlar menen toltırıldı.")

if __name__ == '__main__':
    run_seed()