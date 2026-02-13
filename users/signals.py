from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from users.models import Notification
from shop.models import Cart

@receiver(post_save, sender=User)
def create_user_cart_and_notification(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
        
        Notification.objects.create(
            user=instance,
            message=f"Assalawma aleykum {instance.username}! Dúkanımızǵa xosh keldińiz!"
        )
        Cart.objects.create(user=instance)
