from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    USER_TYPES = (
        (1, 'Staff'),
        (2, 'Admin'),
    )

    email = models.EmailField(unique=True)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPES, default=1)

    def __str__(self):
        return self.username


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Staff(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class VisitorTag(models.Model):
    tag_number = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.tag_number} {'(Active)' if self.is_active else ''}"
    
class VisitingPurpose(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name
    

class RatingOption(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Visitor(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    purpose_of_visit = models.ForeignKey('VisitingPurpose', on_delete=models.CASCADE)
    host = models.ForeignKey('Staff', on_delete=models.CASCADE, null=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    possessions = models.TextField(blank=True, null=True)
    drive_in = models.BooleanField(default=False)
    walk_in = models.BooleanField(default=False)
    number_plate = models.CharField(max_length=20, blank=True, null=True)
    tag = models.ForeignKey(
        VisitorTag, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    otp = models.CharField(max_length=4, blank=True,
                           null=True)
    verified = models.BooleanField(default=False)
    checked_out_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.full_name
    
class Rating(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    rate = models.ForeignKey(RatingOption, on_delete=models.CASCADE)
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.rate.name if self.rate else 'Unrated'
