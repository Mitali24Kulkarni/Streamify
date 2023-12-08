from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

AGE_CHOICES = (
    ('All', 'All'),
    ('Kids', 'Kids'),
)

MOVIE_CHOICES = (
    ('seasonal', 'Seasonal'),
    ('single', 'Single'),
)

PLAN_CHOICES = (
        ('BASIC', 'Basic'),
        ('STANDARD', 'Standard'),
        ('PREMIUM', 'Premium'),
)

SUBSCRIPTION_PLANS = {
    'BASIC': 30,  # 1 month
    'STANDARD': 180,  # 6 months
    'PREMIUM': 365  # 1 year
}

class CustomUser(AbstractUser):
    profiles = models.ManyToManyField('Profile', blank=True)
    def has_active_subscription(self):
        subscription = Subscription.objects.filter(user=self, is_active=True).first()
        return subscription is not None and subscription.end_date >= timezone.now()

class Profile(models.Model):
    name = models.CharField(max_length=1000)
    age_limit = models.CharField(choices=AGE_CHOICES, max_length=10)
    uuid = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=1000)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    type = models.CharField(choices=MOVIE_CHOICES, max_length=10)
    video = models.ManyToManyField('Video')
    image = models.ImageField(upload_to='covers')
    age_limit = models.CharField(choices=AGE_CHOICES, max_length=10)

    def __str__(self):
        return self.title

class Video(models.Model):
    title = models.CharField(max_length=1000)
    file = models.FileField(upload_to='movies')

    def __str__(self):
        return self.title

class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subscription_type = models.CharField(choices=PLAN_CHOICES, max_length=10,default="BASIC")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    
    def get_subscription_end_date(self):
        # Calculate the end date based on the subscription type and payment date
        if self.subscription_type == 'BASIC':
            duration = 1
        elif self.subscription_type == 'STANDARD':
            duration = 6
        elif self.subscription_type == 'PREMIUM':
            duration = 12

        payment_date = self.start_date

        end_date = payment_date + timedelta(days=30 * duration)

        return end_date
