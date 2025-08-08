from django.db import models
from django.utils import timezone
from datetime import timedelta


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    wallet_address = models.CharField(max_length=42, unique=True)  # Ethereum address
    credit_level = models.IntegerField()

    def __str__(self):
        return f"Dr. {self.name}"


class Patient(models.Model):
    synthea_id = models.CharField(max_length=100, unique=True)
    given = models.CharField(max_length=100)
    family = models.CharField(max_length=100)
    birthdate = models.DateField()
    gender = models.CharField(max_length=10)

    def __str__(self):
     return f"{self.given} {self.family}"


class TemporaryAccessToken(models.Model):
    token = models.CharField(max_length=100, unique=True)
    patient_id = models.CharField(max_length=100)
    expires_at = models.DateTimeField()


class AccessLog(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
