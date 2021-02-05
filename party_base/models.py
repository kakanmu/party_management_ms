from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django_fsm import FSMField, transition
from utils import generate_party_code

# Create your models here.

GENDER = (('M', 'Male'), ('F', 'Female'))


class PartyManagementServiceBaseModel(models.Model):
    name = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    displayString = models.CharField(max_length=200, null=True, blank=True)
    active = models.BooleanField(default=True)
    activated = models.BooleanField(default=True)

    # Audit properties
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, null=True)
    last_modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    history = AuditlogHistoryField()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Country(PartyManagementServiceBaseModel):
    country_code_2 = models.CharField(max_length=3, blank=True, null=True)
    country_code_3 = models.CharField(max_length=3, blank=True, null=True)
    dial_code = models.CharField(max_length=10, blank=True, null=True)
    currency = models.CharField(max_length=50, blank=True, null=True)
    currency_code = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'


class Territory(PartyManagementServiceBaseModel):
    country = models.ForeignKey('Country', related_name='territories', on_delete=models.SET_NULL, null=True)
    territory_code = models.CharField(max_length=3, blank=True,  null=True)

    def __str__(self):
        return self.name

    def get_city_digest(self):
        pass

    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'Territory'
        verbose_name_plural = 'Territories'


class City(PartyManagementServiceBaseModel):
    territory = models.ForeignKey('Territory', related_name='cities', on_delete=models.SET_NULL, null=True)
    city_code = models.CharField(max_length=3, blank=True, null=True)

    def __str__(self):
        return self.territory.name + ', ' + self.name

    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'City'
        verbose_name_plural = 'Cities'


class Address(PartyManagementServiceBaseModel):
    address_info = models.CharField('Address', max_length=200, null=True)
    city = models.ForeignKey(Territory, on_delete=models.SET_NULL, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.address_info

    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'


class UserProfile(PartyManagementServiceBaseModel):
    party_code = models.CharField(max_length=100, db_index=True, unique=True, null=True)
    auth_profile_id = models.IntegerField(default=0)
    first_name = models.CharField('First Name', max_length=20)
    last_name = models.CharField('Last Name', max_length=20)
    email = models.EmailField('Contact Email', unique=True)
    phone = models.ForeignKey('Phone', on_delete=models.SET_NULL, null=True, blank=True)
    dob = models.DateField('DOB', null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    gender = models.CharField('Gender', max_length=10, choices=GENDER, blank=True)
    profile_status = FSMField(protected=True, default='Un-synced')
    account_manager = models.BooleanField('Designate as Account Manager', default=False)
    profile_ref_code = models.CharField('User Referral Code', max_length=100, null=True, blank=True)

    def __str__(self):
        return self.email

    @transition(field=profile_status, source='Un-synced', target='Synced')
    def synchronize_userprofile(self, auth_profile_id):
        print('>> Synchronizing UserProfile: ', auth_profile_id)
        self.auth_profile_id = auth_profile_id # attach auth profile

    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class Phone(PartyManagementServiceBaseModel):
    country_code = models.IntegerField('Country Code', blank=True, null=True)
    phone_number = models.BigIntegerField('Phone', blank=True, null=True)

    def __str__(self):
        return str(self.country_code) + '' + str(self.phone_number)

    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'Company Phone Number'
        verbose_name_plural = 'Company Phone Numbers'


class Industry(PartyManagementServiceBaseModel):
    description = models.TextField('Description', blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'Company Industry'
        verbose_name_plural = 'Company Industries'


class AccountProfile(PartyManagementServiceBaseModel):
    account_code = models.CharField('Account Code', max_length=100, null=True)
    company_email = models.EmailField('Company Email', null=True, blank=True)
    description = models.TextField('Company Description', blank=True)
    company_address = models.ForeignKey(Address, on_delete=models.SET_NULL, related_name='company_addresses', null=True)
    account_address = models.CharField('Address', max_length=3000, null=True, default='-')
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True)
    company_phone = models.ForeignKey(Phone, on_delete=models.SET_NULL, null=True, blank=True)
    contact_person = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, related_name='linked_company',
                                       null=True)
    account_officer = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True)

    # Freight forwarder account related fields
    default_commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    account_type = models.ForeignKey('AccountType', related_name='accounts', null=True, on_delete=models.SET_NULL)
    account_status = FSMField(protected=True, default='Pending')
    
    def __str__(self):
        return self.name

    @transition(field=account_status, source='Pending', target='Completed')
    def finalize_account_opening(self):
        print('doing nothing here for now...')

    class Meta:
        ordering = ['name']
        verbose_name = 'Account Profile'
        verbose_name_plural = 'Account Profiles'


class CompanyBranch(PartyManagementServiceBaseModel):
    company = models.ForeignKey(AccountProfile, on_delete=models.DO_NOTHING, related_name='branches')
    address = models.ForeignKey(Address, on_delete=models.DO_NOTHING,)
    contact_person = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING)
    is_head_office = models.BooleanField('Head Office', default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'Company Branch Office'
        verbose_name_plural = 'Company Branch Offices'


class AccountType(PartyManagementServiceBaseModel):
    account_type_code = models.CharField('Account Code', unique=True, db_index=True, max_length=5)
    mapped_app_role_code = models.CharField('Application Role Code', max_length=5, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'Account Type'
        verbose_name_plural = 'Account Types'


class NewsLetterSubscribers(PartyManagementServiceBaseModel):
    email = models.EmailField('Email', unique=True, max_length=80)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'


class SiteEnquiry(PartyManagementServiceBaseModel):
    email = models.EmailField('Enquirer Email', null=True, blank=True)
    phone = models.CharField('Enquirer Phone', default=0, blank=True, max_length=100)
    business_name = models.CharField('Business Name', null=True, blank=True, max_length=200)
    enquiry_message = models.CharField('Enquiry', max_length=3000, null=True, blank=True)
    enquiry_status = FSMField(protected=True, default='Pending')
    enquiry_response = models.CharField('Enquiry response', max_length=3000, null=True, blank=True)

    def __str__(self):
        return self.name+"'s Enquiry"

    @transition(field=enquiry_status, source='Pending', target='Responded')
    def despatch_response(self, response_message):
        self.enquiry_response = response_message

    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'Site Enquiry'
        verbose_name_plural = 'Site Enquiries'


auditlog.register(UserProfile)
auditlog.register(AccountProfile)
auditlog.register(CompanyBranch)
auditlog.register(Address)
auditlog.register(Phone)
auditlog.register(Industry)
auditlog.register(AccountType)
auditlog.register(NewsLetterSubscribers)
auditlog.register(SiteEnquiry)

