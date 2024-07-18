from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import validate_email, validate_slug
from django.core.exceptions import ValidationError

from django.utils.text import slugify
import os

def validate_unique_phone_number(value):
    # Check if the phone number is unique across both tables
    if ContractorDetails.objects.filter(phone_number=value).exists() or MigrantDetails.objects.filter(phone_number=value).exists():
        raise ValidationError('Phone number must be unique across both ContractorDetails and MigrantDetails.')
    
def validate_unique_mail(value):
    # Check if the phone number is unique across both tables
    if ContractorDetails.objects.filter(mail=value).exists() or MigrantDetails.objects.filter(mail=value).exists():
        raise ValidationError('Mail must be unique across both ContractorDetails and MigrantDetails.')



class YouAre(models.Model):
    name = models.CharField(max_length=100, unique=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    youare = models.ForeignKey(YouAre, on_delete=models.CASCADE)

    form_submitted_groupa = models.BooleanField(default=False)
    form_submitted_groupb = models.BooleanField(default=False)

class ContractorDetails(models.Model):
    photo = models.ImageField(upload_to="Contractor")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10, validators=[validate_slug])
    mail = models.EmailField(validators=[validate_email])
    address = models.TextField()
    birth_date = models.DateField()
    adhaar = models.CharField(max_length = 12)
    panchayathlicence = models.CharField(max_length = 10)
    gstnum = models.CharField(max_length = 15)
    district = models.CharField(max_length=20)
    state = models.CharField(max_length=50)
    joined_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.user)
    
    def save(self, *args, **kwargs):
        '''if self.photo:
            filename, extension = os.path.splitext(self.photo.name)
            new_filename = f"{slugify(self.user.username)}{extension}"
            self.photo.name = os.path.join(new_filename)'''
        
        super().save(*args, **kwargs)

class MigrantDetails(models.Model):
    photo = models.ImageField(upload_to="Migrant")
    is_verified = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=50)
    birth_date = models.DateField()
    phone_number = models.CharField(max_length=10)
    mail = models.EmailField()
    police_mail = models.EmailField()
    adhaar = models.CharField(max_length = 12)
    native_address = models.TextField()
    current_address = models.TextField()
    district = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    joined_date = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return str(self.user)
    
    def save(self, *args, **kwargs):
        # Define a dictionary mapping states to police emails
        state_to_police_email = {
            'Andhra Pradesh':'AndhraPradesh@gmail.com',
            "Arunachal Pradesh":"ArunachalPradesh@gmail.com",
            "Assam":"Assam@gmail.com",
            "Bihar":"Bihar@gmail.com",
            "Chhattisgarh":"Chhattisgarh@gmail.com",
            "Goa":"Goa@gmail.com",
            "Gujarat":"Gujarat@gmail.com",
            "Haryana":"Haryana@gmail.com",
            "Himachal Pradesh":"HimachalPradesh@gmail.com",
            "Jharkhand":"Jharkhand@gmail.com",
            "Karnataka":"Karnataka@gmail.com",
            "Kerala":"Kerala@gmail.com",
            "Madhya Pradesh":"MadhyaPradesh@gmail.com",
            "Maharashtra":"Maharashtra@gmail.com",
            "Manipur":"Manipur@gmail.com",
            "Meghalaya":"Meghalaya@gmail.com",
            "Mizoram":"Mizoram@gmail.com",
            "Nagaland":"Nagaland@gmail.com",
            "Odisha":"Odisha@gmail.com",
            "Punjab":"Punjab@gmail.com",
            "Rajasthan":"Rajasthan@gmail.com",
            "Sikkim":"Sikkim@gmail.com",
            "Tamil Nadu":"TamilNadu@gmail.com",
            "Telangana":"Telangana@gmail.com",
            "Tripura":"Tripura@gmail.com",
            "Uttarakhand":"Uttarakhand@gmail.com",
            "Uttar Pradesh":"UttarPradesh@gmail.com",
            "West Bengal":"WestBengal@gmail.com",
            "Dummy":'akshaykrishnan922@gmail.com',
            # Add more states and their corresponding police emails as needed
        }

        # Set the police_mail field based on the state
        self.police_mail = state_to_police_email.get(self.state, '')

        '''if self.photo:
            filename, extension = os.path.splitext(self.photo.name)
            new_filename = f"{slugify(self.user.username)}{extension}"
            self.photo.name = os.path.join(new_filename)'''
        
        super().save(*args, **kwargs)

class UpdateDetails(models.Model):
    contractor = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length = 100)
    from_date = models.DateField()
    to_date = models.DateField()
    place = models.CharField(max_length = 100)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.contractor)
    
class Badge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name