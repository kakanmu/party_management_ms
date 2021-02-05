from django.forms import ModelForm
from django import forms
from party_base.models import Phone, Territory, Country, UserProfile, Industry, AccountProfile, SiteEnquiry

GENDER = (('M', 'Male'), ('F', 'Female'))


class PhoneNumberForm(ModelForm):
    country_code = forms.IntegerField(label='Dial Code', error_messages={'required': "Country dial code required"})
    phone_number = forms.IntegerField(label='Phone', error_messages={'required': "Phone number required"})

    class Meta:
        model = Phone
        fields = ['country_code', 'phone_number']


class AddressForm(ModelForm):
    address_info = forms.CharField(label='Address info', error_messages={'required': "Street address required"})
    city = forms.ModelChoiceField(queryset=Territory.objects.filter(active=True), label='City',
                                  error_messages={'required': "City info required"})
    country = forms.ModelChoiceField(queryset=Country.objects.filter(active=True), label='Country',
                                     error_messages={'required': "Country info required"})

    class Meta:
        model = Country
        fields = ['address_info', 'city', 'country']


class ContactPersonForm(ModelForm):
    first_name = forms.CharField(label='First Name', error_messages={'required': "First Name is required"})
    last_name = forms.CharField(label='Last Name', error_messages={'required': "Last Name is required"})
    # email = forms.EmailField(label='Email', error_messages={'required': "Contact person email is required"})
    # gender = forms.ChoiceField(choices=GENDER, label='Gender',
    #                            error_messages={'required': "Contact person gender is required"})

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name']


class AccountProfileForm(ModelForm):
    name = forms.CharField(label='Company Name', error_messages={'required': "Company Name is required"})
    company_email = forms.EmailField(label='Company Email', required=False)
    industry = forms.ModelChoiceField(queryset=Industry.objects.filter(active=True), label='Industry',
                                      error_messages={'required': "Company Industry is required"})
    referred_by = forms.CharField(label='Referred By', required=False)

    class Meta:
        model = AccountProfile
        fields = ['name', 'company_email', 'industry']


class SiteEnquiryForm(ModelForm):
    name = forms.CharField(label='Full Name', error_messages={'required': "Please provide Full name"})
    email = forms.EmailField(label='Email',
                             error_messages={'required': 'Please provide your email so we can get back to you.'})
    phone = forms.CharField(label='Phone No.',
                               error_messages={'required': "Please provide your phone number so we can reach you."})
    business_name = forms.CharField(label='Business Name', required=False)
    enquiry_message = forms.CharField(label='Enquiry', error_messages={'required': 'Please supply enquiry detail.'})

    class Meta:
        model = SiteEnquiry
        fields = ['name', 'email', 'phone', 'business_name', 'enquiry_message']



