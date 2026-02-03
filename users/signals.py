from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from shop.models import Cart, Notification

@receiver(post_save, sender=User)
def create_user_cart_and_notification(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
        # Xabarlandırıw
        Notification.objects.create(
            user=instance,
            message=f"Assalawma aleykum {instance.username}! Dúkanımızǵa xosh keldińiz!"
        )