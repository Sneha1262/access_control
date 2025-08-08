from django.contrib import admin
from .models import Doctor, Patient, TemporaryAccessToken, AccessLog

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(TemporaryAccessToken)
admin.site.register(AccessLog)
