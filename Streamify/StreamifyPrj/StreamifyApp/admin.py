from django.contrib import admin
from StreamifyApp.models import Movie, Video, Profile, CustomUser, Subscription


admin.site.register(Movie)
admin.site.register(Video)
admin.site.register(Profile)
admin.site.register(CustomUser)
admin.site.register(Subscription)
