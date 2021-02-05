import json

from django.db import IntegrityError

from party_base.models import Country, Industry, Territory, Address, AccountType
from party_base.entry_validation_forms import AccountProfileForm, AddressForm, ContactPersonForm, PhoneNumberForm, \
    Phone, UserProfile, AccountProfile
from utils import compile_form_errors, fetch_locale_data


def compose_account_creation_params(location=None, resp=None):
    countries = Country.objects.filter(active=True)
    locations = [{'id': x.id, 'label': str.capitalize(str.lower(x.name)), 'dial_code': x.dial_code,
                  'default': False if location is None or location != str(x.country_code_2).upper() else True}
                 for x in countries]

    industries = Industry.objects.filter(active=True)
    ind_list = [{'id': d.id, 'label': str.capitalize(d.name)} for d in industries]
    profiles = UserProfile.objects.filter(active=True, account_manager=True)
    managers = [{'id': x.id, 'label': x.profile_ref_code} for x in profiles]

    resp.add_param('countries', locations)
    resp.add_param('industries', ind_list)
    resp.add_param('account_officers', managers)

    return resp


def fetch_country_cities(country_id=None, resp=None):
    if country_id:
        territories = Territory.objects.filter(country_id=country_id)
        terr_lst = [{'id': p.id, 'label': str.capitalize(p.name)} for p in territories]

        resp.add_param('cities', terr_lst)

    return resp


def validate_signup_composite(submitted_data=None, resp=None):
    # Validate Company Data
    company_form = AccountProfileForm(submitted_data)
    if not company_form.is_valid():
        resp.add_param('errors', compile_form_errors(company_form))
        resp.error()
        return False

    # Validate Company Address
    address_form = AddressForm(submitted_data.get('company_address', {}))
    if not address_form.is_valid():
        resp.add_param('errors', compile_form_errors(address_form))
        resp.error()
        return False

    # Validate Contact person
    c_person_form = ContactPersonForm(submitted_data.get('contact_person', {}))
    if not c_person_form.is_valid():
        resp.add_param('errors', compile_form_errors(c_person_form))
        resp.error()
        return False

    return True


def update_client_account(submitted_data=None, resp=None):
    try:
        # Fetch the Account Profile record
        record_id = submitted_data.get('id', None)
        account_form = AccountProfileForm(submitted_data)
        if account_form.is_valid():
            if record_id:
                account_profile = AccountProfile.objects.get(id=record_id)
                account_profile.name = account_form.cleaned_data['name']
                account_profile.displayString = account_form.cleaned_data['name']
                account_profile.industry = account_form.cleaned_data['industry']
                account_profile.company_email = str(account_form.cleaned_data['company_email']).lower()
                account_profile.save()

                # Update Phone
                accnt_phone = account_profile.company_phone
                data = submitted_data.get('company_phone', None)
                if data:
                    accnt_phone.country_code = data.get('country_code', 0)
                    accnt_phone.phone_number = data.get('phone_number', 0)
                    accnt_phone.save()

                # Update Contact Person
                accnt_prsn = account_profile.contact_person
                data = submitted_data.get('contact_person', None)
                if data:
                    accnt_prsn.first_name = data.get('first_name', '-')
                    accnt_prsn.last_name = data.get('last_name', '-')
                    accnt_prsn.name = ''.join([accnt_prsn.first_name, ' ', accnt_prsn.last_name])
                    accnt_prsn.save()

                # Update Address
                accnt_addy = account_profile.company_address
                data = submitted_data.get('company_address', None)
                c_address_form = AddressForm(data)
                if c_address_form.is_valid():
                    if data:
                        accnt_addy.address_info = c_address_form.cleaned_data['address_info']
                        accnt_addy.country = c_address_form.cleaned_data['country']
                        accnt_addy.city = c_address_form.cleaned_data['city']
                        accnt_addy.save()

                resp.passed()
                resp.add_message('Update successful')

            else:
                resp.failed()
                resp.add_message('Missing parameter: ID')

        else:
            resp.failed()
            resp.add_param('errors', compile_form_errors(account_form))

    except Exception as err:
        resp.failed()
        resp.add_message(str(err))


def create_signup_composite(submitted_data=None, accnt_type='regular', resp=None):
    try:
        c_address = None
        c_phone_obj = None
        c_person_obj = None

        # Create Company Address
        c_addy = submitted_data.get('company_address', None)
        if c_addy:
            c_address_form = AddressForm(c_addy)
            if c_address_form.is_valid():
                c_address = Address()
                c_address.address_info = c_address_form.cleaned_data['address_info']
                c_address.country = c_address_form.cleaned_data['country']
                c_address.city = c_address_form.cleaned_data['city']
                c_address.save()

        # Create Company Phone
        c_phone = submitted_data.get('company_phone', None)
        if c_phone:
            c_phone_obj = Phone.objects.create(**c_phone)

        # Create Contact Person details
        c_person = submitted_data.get('contact_person', None)

        if c_person:
            c_person_frm = ContactPersonForm(c_person)
            if c_person_frm.is_valid():
                try:
                    c_person_obj = UserProfile()
                    c_person_obj.first_name = c_person_frm.cleaned_data['first_name']
                    c_person_obj.last_name = c_person_frm.cleaned_data['last_name']
                    c_person_obj.name = ''.join([c_person_obj.first_name, ' ', c_person_obj.last_name])
                    c_person_obj.email = str(submitted_data.get('company_email', None)).lower()
                    c_person_obj.save()

                except IntegrityError as err:
                    resp.error()
                    resp.add_param('errors',
                                   [{'field': 'company_email', 'error': 'An account with this email already exists.'}])
                    resp.add_message('An account with this email already exists.')
                    return

                except Exception as err:
                    resp.failed
                    resp.add_message(str(err))
                    return

        # Create Account Profile
        account_form = AccountProfileForm(submitted_data)
        if account_form.is_valid():
            account_prof_obj = AccountProfile()
            account_prof_obj.name = account_form.cleaned_data['name']
            account_prof_obj.displayString = account_form.cleaned_data['name']
            account_prof_obj.industry = account_form.cleaned_data['industry']
            account_prof_obj.company_email = str(account_form.cleaned_data['company_email']).lower()
            account_prof_obj.company_phone = c_phone_obj
            account_prof_obj.company_address = c_address
            addy_strng = str(c_address.address_info)
            if c_address.city:
                addy_strng = addy_strng + ', ' + str(c_address.city.name)
            if c_address.country:
                addy_strng = addy_strng + ', ' + str(c_address.country.name)

            account_prof_obj.account_address = addy_strng
            account_prof_obj.contact_person = c_person_obj

            # Set referral id
            referral_id = submitted_data.get('referred_by', None)
            if referral_id:
                account_prof_obj.account_officer = UserProfile.objects.get(id=referral_id)

            # Set account officer
            accnt_ofcr_mail = submitted_data.get('booked_by', None)
            if accnt_ofcr_mail:
                account_prof_obj.account_officer = UserProfile.objects.get(email__iexact=accnt_ofcr_mail)

            # Specify the Account type
            account_prof_obj.account_type = AccountType.objects.get(name__iexact=accnt_type)
            account_prof_obj.save()

        resp.passed()
        resp.add_message('Account creation successful')

    except Exception as err:
        resp.failed()
        resp.add_message(str(err))
