from django.utils import timezone
from .models import SubscriptionOrder

def expire_subscription(user):
    """
    Expire all active subscriptions for a user if the end_date is passed.
    """
    expired_orders = SubscriptionOrder.objects.filter(
        user=user,
        is_active=True,
        end_date__lte=timezone.now()
    )

    for order in expired_orders:
        order.is_active = False
        if order.is_trial:
            order.payment_status = 'trial_expired'
        order.save()

        # Remove active plan from user
        user.subscription_plan = None
        user.save()
