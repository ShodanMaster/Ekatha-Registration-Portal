from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
from django import forms
from datetime import *

current_year = datetime.now().year

class SignUpForm(UserCreationForm):
    GROUP_CHOICES = [
        ('', 'Select a group'),
        ('Contractor', 'Contractor'),
        ('Migrant', 'Migrant'),
    ]

    group = forms.ChoiceField(choices=GROUP_CHOICES,required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

GENDER_CHOICES = [
    ('', 'Select Gender'),
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

STATE_CHOICE = [
    ('', 'Select State'),
    ('Andhra Pradesh','Andhra Pradesh'),
    ("Arunachal Pradesh","Arunachal Pradesh"),
    ("Assam","Assam"),
    ("Bihar","Bihar"),
    ("Chhattisgarh","Chhattisgarh"),
    ("Goa","Goa"),
    ("Gujarat","Gujarat"),
    ("Haryana","Haryana"),
    ("Himachal Pradesh","Himachal Pradesh"),
    ("Jharkhand","Jharkhand"),
    ("Karnataka","Karnataka"),
    ("Kerala","Kerala"),
    ("Madhya Pradesh","Madhya Pradesh"),
    ("Maharashtra","Maharashtra"),
    ("Manipur","Manipur"),
    ("Meghalaya","Meghalaya"),
    ("Mizoram","Mizoram"),
    ("Nagaland","Nagaland"),
    ("Odisha","Odisha"),
    ("Punjab","Punjab"),
    ("Rajasthan","Rajasthan"),
    ("Sikkim","Sikkim"),
    ("Tamil Nadu","Tamil Nadu"),
    ("Telangana","Telangana"),
    ("Tripura","Tripura"),
    ("Uttarakhand","Uttarakhand"),
    ("Uttar Pradesh","Uttar Pradesh"),
    ("West Bengal","West Bengal"),
    ("Dummy","Dummy"),
]

policemail={
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
    "Dummy":'migregproj@gamil.com',
}


class ContractorForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=GENDER_CHOICES,required=True)
    state = forms.ChoiceField(choices=STATE_CHOICE,required=True)
    birth_date = forms.DateField(widget=forms.SelectDateWidget(years=range(1900,current_year+1)),required=True)
    phone_number = forms.CharField(max_length=10)
    adhaar = forms.CharField(max_length=12)
    
    class Meta:
        model = ContractorDetails
        fields = [ 'name','gender','birth_date','phone_number', 'mail','adhaar','panchayathlicence','gstnum',  'address', 'district', 'state',  'photo']

class MigrantForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=GENDER_CHOICES,required=True)
    state = forms.ChoiceField(choices=STATE_CHOICE,required=True)
    birth_date = forms.DateField(widget=forms.SelectDateWidget(years=range(1900,current_year+1)),required=True)
    phone_number = forms.CharField(max_length=10)
    adhaar = forms.CharField(max_length=12)
    class Meta:
        model = MigrantDetails
        #fields = '__all__'
        fields = ['name','gender','birth_date','phone_number',
                  'mail','adhaar','native_address',
                  'current_address','district','state','photo']

class UpdateForm(forms.ModelForm):
    from_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000,current_year+1)),required=True)
    to_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000,current_year+1)),required=True,)

    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.fields['from_date'].initial = date.today()
        self.fields['to_date'].initial = date.today()
    
    def __str__(self):
        return f"UpdateDetails for {self.contractor}"

    class Meta:
        model = UpdateDetails
        fields = ['username', 'from_date', 'to_date','place']

