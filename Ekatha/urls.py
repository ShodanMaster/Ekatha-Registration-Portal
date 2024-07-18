from .views import *
from django.urls import path

urlpatterns = [
    path("", home, name="home"),
    path("contact/", contact, name="contact"),
    path("about/", about, name="about"),
    path("service/", service, name="service"),

    #path("home/", home, name="home"),
    path('signup/', signup, name = 'signup'),
    path('login/',custom_login_view,name='login'),
    path('logout/', logout_view, name='logout'),
    path('contractor_table/', ContractorTable, name = 'contractortable'),
    path('migrant_table/', MigrantTable, name = 'migranttable'),
    path('submitdetails/', SubmitDetails, name='submitdetails'),
    path('yourprofile/',YourProfile,name='yourprofile'),
    path('success/', success, name = 'success'),
    path('updatetable/',ContractorUpdation,name='updatetable'),
    path('seedetails/<str:username>', SeeDetails,name='seedetails'),

    path('updatedtable/<str:username>/', ContractorUpdated, name='updatedtable'),
    path('idcard/<str:username>', IdCard,name='idcard'),
   #path('pdf/',render_pdf_view,name='pdf'),
    path('test/',CustomListView.as_view(),name='custom'),
    path('cpdf/<username>/', custompdf, name='cpdf'),

]