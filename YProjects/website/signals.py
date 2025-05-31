from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Contact, Newsletter
from .utils import send_contact_notification, send_newsletter_welcome
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Contact)
def contact_created(sender, instance, created, **kwargs):
    """Send notification when new contact is created"""
    if created:
        try:
            # Send email notification in background (consider using Celery for production)
            send_contact_notification(instance.id)
            logger.info(f'Contact notification triggered for {instance.name}')
        except Exception as e:
            logger.error(f'Failed to send contact notification: {str(e)}')

@receiver(post_save, sender=Newsletter)
def newsletter_subscribed(sender, instance, created, **kwargs):
    """Send welcome email when someone subscribes to newsletter"""
    if created:
        try:
            # Send welcome email
            send_newsletter_welcome(instance.email)
            logger.info(f'Newsletter welcome email sent to {instance.email}')
        except Exception as e:
            logger.error(f'Failed to send newsletter welcome email: {str(e)}')