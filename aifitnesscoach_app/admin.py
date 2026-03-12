from django.contrib import admin
from .models import Subscriptionplan,Register,SubscriptionOrder,Workouttips
# Register your models here.
admin.site.register(SubscriptionOrder)
admin.site.register(Workouttips)
admin.site.register(Register)