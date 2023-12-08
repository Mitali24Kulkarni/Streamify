from django.forms import ModelForm
from StreamifyApp.models import Profile, Subscription

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['uuid']

class SubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ['subscription_type']
