from django.contrib import admin
from . import models

admin.site.register(models.User)
admin.site.register(models.Doctor)
admin.site.register(models.Patient)
admin.site.register(models.Measurement)
admin.site.register(models.Limit)
admin.site.register(models.Notification)
