from django.shortcuts import render,  redirect, get_object_or_404
from .forms import *
from .models import UserProfile, YouAre
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
import logging
from django.http import Http404
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail

# Create your views here.

def home(request):
    context={}
    return render(request, "myapp/shared/index.html", context)

def contact(request):
    context={}
    return render(request, "myapp/shared/contact.html", context)

def about(request):
    context={}
    return render(request, "myapp/shared/about.html", context)

def service(request):
    context={}
    return render(request, "myapp/shared/service.html", context)



def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Log in the user
                login(request, user)
                
                # Redirect to a success page (you can change this to your desired URL)
                return redirect('home')
    else:
        form = AuthenticationForm(request)

    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    request.session.clear()
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save the user yet
            group_name = form.cleaned_data['group']
            
            # Get or create the YouAre instance
            youare, created = YouAre.objects.get_or_create(name=group_name)
            
            # Save the user and associate it with the group
            user.save()
            UserProfile.objects.create(user=user, youare=youare)
            
            login(request, user)
            return redirect('submitdetails')  # Redirect to the home page
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

@login_required(login_url='/login')
def ContractorTable(request):
    details = ContractorDetails.objects.all()
    
    if request.GET.get('search'):
        details = details.filter(name__icontains = request.GET.get('search'))

    if not details:
        messages.info(request, "No details available.")
        details = ContractorDetails.objects.all() 

    return render(request, 'other/contable.html',{'details' : details})


from .models import MigrantDetails, Badge
from django.contrib.auth.models import User, Group

def MigrantTable(request):
    verified_group = Group.objects.get(name='Verified')
    verified_users = User.objects.filter(groups=verified_group)
    
    for user in verified_users:
        badge, created = Badge.objects.get_or_create(user=user)
        if created:
            badge.is_verified = True
            badge.save()

    details = MigrantDetails.objects.all()
    if request.GET.get('search'):
        details = details.filter(name__icontains=request.GET.get('search'))

    for detail in details:
        detail.is_verified = detail.user in verified_users

    if not details:
        messages.info(request, "No details available.")
        details = MigrantDetails.objects.all() 
        #return render(request, 'other/migtable.html', {'details': details})
        
    if request.user.is_authenticated:
        is_contractor = ContractorDetails.objects.filter(user=request.user).exists()
    else:
        is_contractor = False

    return render(request, 'other/migtable.html', {'details': details,'is_contractor':is_contractor})

@login_required(login_url='/login')
def YourProfile(request):
    current_user = request.user
    verified_group = Group.objects.get(name='Verified')
    verified_users = User.objects.filter(groups=verified_group)
    
    # Assuming you have one-to-one relationships between User and MigrantDetails
    # and between User and ContractorDetails
    if current_user.is_superuser:
        return render(request, 'other/admin.html')
    else:
        migrant_details = MigrantDetails.objects.filter(user=current_user).first()
        contractor_details = ContractorDetails.objects.filter(user=current_user).first()

        details_list_migrant = []
        details_list_contractor = []
        
        if migrant_details:
            migrant_details.is_verified = migrant_details.user in verified_users
            details_list_migrant = [(field.name, getattr(migrant_details, field.name)) for field in migrant_details._meta.fields]

        if contractor_details:
            details_list_contractor = [(field.name, getattr(contractor_details, field.name)) for field in contractor_details._meta.fields]

        return render(request, 'other/yourprofile.html', {
            'details_list_migrant': details_list_migrant,
            'details_list_contractor': details_list_contractor,
            'current_user': current_user,'migrant_details':migrant_details
        })

@login_required(login_url='/login')
def success(request):
    return render(request,'other/success.html')


from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
logger = logging.getLogger(__name__)
@login_required(login_url='/login')
def SubmitDetails(request):
    try:
        current_user = request.user
        user_profile = current_user.userprofile
        user_group = user_profile.youare.name

        if request.user.is_authenticated:
            migrant_exists = MigrantDetails.objects.filter(user=request.user).exists()
            contractor_exists = ContractorDetails.objects.filter(user=request.user).exists()

        if request.method == 'POST':
            # Handle form submission
            if user_group == 'Contractor':
                form = ContractorForm(request.POST, request.FILES)
            elif user_group == 'Migrant':
                form = MigrantForm(request.POST, request.FILES)
            else:
                messages.error(request, 'Invalid group.')
                return redirect('home')  # Redirect to the home page or an error page

            if form.is_valid():
                phone_number = form.cleaned_data.get('phone_number')
                mail = form.cleaned_data.get('mail')  
                adhaar = form.cleaned_data.get('adhaar')
                district =form.cleaned_data.get('district') 
                name = form.cleaned_data.get('name')
                birth_date =  form.cleaned_data.get('birth_date')
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))                

                if not name.replace(' ', '').isalpha():
                    messages.error(request, 'Name Should Only Contain Alphabets')
                    return render(request, 'other/submit.html', {"form": form})
                
                if age<18:
                    messages.error(request, 'Too Young to Join')
                    return render(request, 'other/submit.html', {"form": form})
                
                if age>70:
                    messages.error(request, 'Too Old to Join')
                    return render(request, 'other/submit.html', {"form": form})

                if not phone_number.startswith(('6', '7', '8', '9')):
                    print("Number Error")
                    messages.error(request, 'Invalid Phone Number Format')
                    form.fields['phone_number'].initial = None
                    return render(request, 'other/submit.html', {"form": form})
                
                if not phone_number.isdigit():
                    messages.error(request, 'Invalid Phone Number Format')
                    form.fields['phone_number'].initial = None
                    return render(request, 'other/submit.html', {"form": form})
                
                if len(phone_number) != 10:
                    print("10 ERROR")
                    messages.error(request, 'Phone Number Must Contain 10 Digits')
                    form.fields['phone_number'].initial = None
                    return render(request, 'other/submit.html', {"form": form})
                
                if ContractorDetails.objects.filter(phone_number=phone_number).exists() or MigrantDetails.objects.filter(phone_number=phone_number).exists():
                    messages.error(request, 'Phone number already exists.')
                    return render(request, 'other/submit.html', {"form": form})

                if ContractorDetails.objects.filter(mail=mail).exists() or MigrantDetails.objects.filter(mail=mail).exists():
                    messages.error(request, 'Email already exists.')
                    return render(request, 'other/submit.html', {"form": form})
                
                if len(adhaar) !=12:
                    messages.error(request, 'Adhaar must contain 12 digits.')
                    return render(request, 'other/submit.html', {"form": form})
                
                if not adhaar.isdigit():
                    messages.error(request, 'Invalid Adhaar Format.')
                    return render(request, 'other/submit.html', {"form": form})
                
                if not district.isalpha():
                    messages.error(request, 'Invalid District.')
                    return render(request, 'other/submit.html', {"form": form})

                
                else:
                    details = form.save(commit=False)
                    details.user = request.user
                    details.save()

                    if user_group == 'Migrant':
                        police_mail = details.police_mail
                        username = request.user
                        name  = form.cleaned_data.get('name')
                        mail = form.cleaned_data.get('mail')
                        phone_number = form.cleaned_data.get('phone_number')
                        native_address = form.cleaned_data.get('native_address')
                        district = form.cleaned_data.get('district')
                        state = form.cleaned_data.get('state')
                        birth_date = form.cleaned_data.get('birth_date').strftime('%d-%m-%Y')
                        gender = form.cleaned_data.get('gender')
                        adhaar = form.cleaned_data.get('adhaar')

                        details = f"Request to Verify this Personality:\nUsername: {username}\nName:{name}\ngender: {gender}\nbirth_date: {birth_date}\nphone_number:{phone_number}\nMail: {mail}\nadhaar: {adhaar}\nnative_address:{native_address}\ndistrict: {district}\nstate: {state}"
                        
                        subject = 'Migrant Details'
                        message = details
                        from_email = 'migregproj@gmail.com'
                        to_email = police_mail
                        email = EmailMessage(subject, message, from_email, [to_email])

                        # Get the photo value
                        migrant_details = MigrantDetails.objects.get(user=current_user)
                        photo = migrant_details.photo
                        print(photo)

                        email.attach_file(photo.path)
                        
                        email.send()
                        print("############emailsend############")

                        messages.success(request, 'Details saved successfully and have been sent to your corresponding POLICE CONTROL CELL. Please Wait until your Verification to recieve your ID Card.')
                        return redirect('success') 
            
                messages.success(request, 'Go to your profile to download Your ID Card.')
                return redirect('success')   
                
        else:
            # Render the form submission page based on the user's group
            if user_group == 'Contractor':
                form = ContractorForm()
                return render(request, 'other/submit.html', {"form": form})
            elif user_group == 'Migrant':
                form = MigrantForm()
                return render(request, 'other/submit.html', {"form": form})
            else:
                messages.error(request, 'Invalid group.')
                logger.error(f"User {request.user.username} has an invalid group: {user_group}")
                return redirect('home')

    except ValidationError as e:
        messages.error(request, e.message)
        return redirect('home')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('home')
        
from datetime import datetime

@login_required(login_url='/login')
def ContractorUpdation(request):
    form = UpdateForm()
    verified_group = Group.objects.get(name='Verified')
    verified_users = User.objects.filter(groups=verified_group)
    details = MigrantDetails.objects.filter(user__in=verified_users)

    updated_migrant = None  # Initialize updated_migrant with None

    if request.method == 'POST':
        form = UpdateForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            username = form.cleaned_data['username']
            exists = MigrantDetails.objects.filter(user__username=username).exists()
            uexists = UpdateDetails.objects.filter(contractor=request.user,
                    username=username,
                    from_date=from_date,
                    to_date=to_date
                ).exists()

            if not exists:
                messages.error(request, "User Not Found in Table")
                qset = UpdateDetails.objects.filter(
                    contractor__username=request.user.username
                ).order_by('-from_date', '-to_date')
                return render(request, 'other/update.html/', {'form': form,'qset':qset})

            if from_date > to_date:
                messages.error(request, "To date should not be earlier than from date.")
                qset = UpdateDetails.objects.filter(
                    contractor__username=request.user.username
                ).order_by('-from_date', '-to_date')
                return render(request, 'other/update.html/', {'form': form,'qset':qset})
            
            elif to_date> date.today():
                messages.error(request, "To date should not be Future than from date.")
                qset = UpdateDetails.objects.filter(
                    contractor__username=request.user.username
                ).order_by('-from_date', '-to_date')
                return render(request, 'other/update.html/', {'form': form,'qset':qset})

            if uexists:
                messages.error(request,"A record with this username, from date, and to date already exists in the UpdateDetails table.")
                qset = UpdateDetails.objects.filter(
                    contractor__username=request.user.username
                ).order_by('-from_date', '-to_date')
                return render(request, 'other/update.html/', {'form': form,'qset':qset})
            
            if UpdateDetails.objects.filter(
                contractor=request.user,
                username=username,
                from_date__lte=from_date,
                to_date__gte=from_date
            ).exists():
                messages.error(request, "The new date should not come between existing from date and to date.")
                qset = UpdateDetails.objects.filter(
                    contractor__username=request.user.username
                ).order_by('-from_date', '-to_date')
                return render(request, 'other/update.html/', {'form': form, 'qset': qset})

            else:

                contractor_details = ContractorDetails.objects.get(user=request.user)
                contractor_user = contractor_details.user
                details = form.save(commit=False)
                details.contractor = contractor_user
                details.save()
                messages.success(request, "Contractor details updated successfully.")

                # Check if the updated migrant is verified
                updated_migrant = MigrantDetails.objects.get(user__username=username)
                updated_migrant.is_verified = updated_migrant.user in verified_users
                updated_migrant.save()
                return redirect('updatetable')
        else:
            messages.error(request, "Invalid form data.")
        # Your existing code for handling POST requests
        pass
    else:
        # Handle GET requests with search query
        
        # Handle GET requests with search query
        search_query = request.GET.get('q')
        from_query =  request.GET.get('f')
        to_query =  request.GET.get('t')

        if search_query:
            # Filter UpdateDetails queryset based on search query
            qset = UpdateDetails.objects.filter(
                Q(contractor__username=request.user.username) &
                (Q(username__icontains=search_query) |
                Q(place__icontains=search_query) 
                ) ).order_by('-from_date', '-to_date')
            
        elif from_query:
            from_date = datetime.strptime(from_query, '%Y-%m-%d').strftime('%Y-%m-%d')
            qset = UpdateDetails.objects.filter(
                Q(contractor__username=request.user.username) &
                Q(from_date__gte=from_date))
            
        elif to_query:
            to_date = datetime.strptime(to_query, '%Y-%m-%d').strftime('%Y-%m-%d')
            qset = UpdateDetails.objects.filter(
                Q(contractor__username=request.user.username) &
                Q(to_date__lte=to_date))
            
        else:
            qset = UpdateDetails.objects.filter(
                    contractor__username=request.user.username
                ).order_by('-from_date', '-to_date')

        if not qset.exists():
            qset = UpdateDetails.objects.filter(
                    contractor__username=request.user.username
                ).order_by('-from_date', '-to_date')
            messages.info(request, "No Data Available")    
        

        #if not qset.exists():
         #   messages.info(request, 'No data available')

    return render(request, 'other/update.html', {'form': form, 'qset': qset, 'details': details, 'updated_migrant': updated_migrant})

@login_required(login_url='/login')
def SeeDetails(request, username):
    try:
        user = get_object_or_404(User, username=username)
        user_profile = user.userprofile
        user_group = user_profile.youare.name.lower()

        if user_group == 'migrant':
            model_class = MigrantDetails
            is_contractor = False
        elif user_group == 'contractor':
            model_class = ContractorDetails
            is_contractor = True
        else:
            raise Http404(f"Invalid user type: {user_group}")

        details = get_object_or_404(model_class, user=user)
        details_list = [(field.name, getattr(details, field.name)) for field in model_class._meta.fields]

        # Check if the user is verified
        is_verified = False
        if user_group == 'migrant':
            is_verified = details.is_verified
        

# Use a list comprehension to construct a list of tuples containing the specific field names and their values
        
            

        return render(request, 'other/seedetails.html', {'details_list': details_list, 'is_contractor': is_contractor, 'is_verified': is_verified})
    except Http404 as e:
        raise Http404(f"User details not found for username '{username}'") from e

@login_required(login_url='/login')
def ContractorUpdated(request, username):

    qset = UpdateDetails.objects.filter(contractor__username=username).order_by('-from_date', '-to_date')
    search_query = request.GET.get('q')
    from_query =  request.GET.get('f')
    to_query =  request.GET.get('t')

    if search_query:
        # Filter UpdateDetails queryset based on search query
        qset = UpdateDetails.objects.filter(
            Q(contractor__username=username) &
            (Q(username__icontains=search_query) |
            Q(place__icontains=search_query) 
            ) ).order_by('-from_date', '-to_date')
    elif from_query:
        from_date = datetime.strptime(from_query, '%Y-%m-%d').strftime('%Y-%m-%d')
        qset = UpdateDetails.objects.filter(
            Q(contractor__username=username) &
            Q(from_date__gte=from_date))
    elif to_query:
        to_date = datetime.strptime(to_query, '%Y-%m-%d').strftime('%Y-%m-%d')
        qset = UpdateDetails.objects.filter(
            Q(contractor__username=username) &
            Q(to_date__lte=to_date))
    else:
        qset = UpdateDetails.objects.filter(contractor__username=username).order_by('-from_date', '-to_date')
    
    if not qset.exists():
        qset = UpdateDetails.objects.filter(contractor__username=username).order_by('-from_date', '-to_date')
        messages.info(request, "No Data Available")

        
    # Pass the ContractorDetails and UpdateDetails records to the template
    return render(request, 'other/updatedtable.html', {'username': username,'qset':qset})

@login_required(login_url='/login')
def IdCard(request, username):
    current_user = request.user

    migrant_details = MigrantDetails.objects.filter(user=current_user).first()
    contractor_details = ContractorDetails.objects.filter(user=current_user).first()

    context = {
        'migrant_details': migrant_details,
        'contractor_details': contractor_details,
        'username': username,
    }

    return render(request,'other/card.html',context)


from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.generic import ListView

class CustomListView(ListView):
    model = MigrantDetails
    template = 'other/card.html'
    
@login_required(login_url='/login')
def custompdf(request, *args, **kwargs):
    current_user = request.user
    migrant_details = MigrantDetails.objects.filter(user=current_user).first()
    contractor_details = ContractorDetails.objects.filter(user=current_user).first()

    context = {
        'migrant_details': migrant_details,
        'contractor_details': contractor_details,
        
    }
    #migrant = get_object_or_404(MigrantDetails, user=c)
    template_path = 'other/result.html'
    #context = {'migarnt': migrant}

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="{}.pdf"'.format(request.user)
    #response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(request.user)

    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context, request)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # if error, then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response


