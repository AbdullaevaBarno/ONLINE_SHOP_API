from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from users.models import Notification
from shop.models import Cart

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_cart_and_notification(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
        
        Notification.objects.create(
            user=instance,
            message=f"Assalawma aleykum {instance.username}! Dúkanimizǵa xosh keldińiz!"
        )
        print(f"DEBUG: {instance.username} ushın notification hám cart jaratıldı!")
        
