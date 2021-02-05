from collections import namedtuple
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from party_base.models import (
    Address, UserProfile, Phone, AccountProfile, 
    CompanyBranch, Industry, City, Country, NewsLetterSubscribers)
from party_base import utils as u
from party_base.serializers import (
    AddressSerializer, UserProfileSerializer, PhoneSerializer, CompanyProfileSerializer, 
    CompanyBranchSerializer, CompanyBranchesSerializer, IndustrySerializer, CitySerializer, 
    CountrySerializer, AddressOutputSerializer, SignupInitializtionSerializer, SubscriberSerializer, SubscriberInput)

from party_base.entry_validation_forms import SiteEnquiryForm

from party_base.function import compose_account_creation_params, fetch_country_cities, validate_signup_composite, \
    create_signup_composite, update_client_account, fetch_locale_data
from django.views.generic import View
from jsa_auth_middleware.query_response import Response
from utils import get_contents, compile_form_errors, build_pagination_markers, build_query_filter
import json


# Create your views here.


class CityViewSet(ModelViewSet):

    queryset = City.objects.all()
    serializer_class = CitySerializer


class CountryViewSet(ModelViewSet):

    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def get_countries(self, request):
        country_data = u.get_countries()
        for country in country_data:
            Country.objects.create(name=country)
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        return Response(
            {
                'status': 'success',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    

    @action(detail=False, methods=['POST'], url_path='get-all-countries')
    def get_all_countries(self, request):
        with open('countries.json', 'r') as myfile:
            data = myfile.read()
        country_data = json.loads(data)
        return Response(
            {
                'status': 'success',
                'data': country_data
            },
            status=status.HTTP_200_OK
        )



class AddressViewSet(ModelViewSet):

    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            address = serializer.save()
            output_serializer = AddressOutputSerializer(address)
            return Response(
                {
                    "status": "success",
                    "data": output_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "status": "fail",
                "data": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def list(self, request):
        addresses = self.queryset
        serializer = AddressOutputSerializer(addresses, many=True)
        return Response(
            {
                "status": "success",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        try:
            address = Address.objects.get(id=pk)
            serializer = self.serializer_class(address)
            return Response(
                {
                    "status": "success",
                    "data": serializer.data
                }
            )
        except Address.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Address does not exist"
                }
            )

        

class UserProfileViewSet(ModelViewSet):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED                
            )
        return Response(
            {
                "status": "fail",
                "data": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def list(self, request):
        user_profiles = self.queryset
        serializer = self.serializer_class(user_profiles, many=True)
        return Response(
            {
                "status": "success",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class PhoneViewSet(ModelViewSet):

    queryset = Phone.objects.all()
    serializer_class = PhoneSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "status": "fail",
                "data": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def list(self, request):
        phones = self.queryset
        serializer = self.serializer_class(phones, many=True)
        return Response(
            {
                "status": "success",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class CompanyViewSet(ModelViewSet):

    queryset = AccountProfile.objects.all()
    serializer_class = CompanyProfileSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "status": "fail",
                "data": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def list(self, request):
        companies = self.queryset
        serializer = self.serializer_class(companies, many=True)
        return Response(
            {
                "status": "success",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


    @action(detail=False, methods=['POST'], url_path='get-branches')
    def get_company_branches(self, request):
        company_email = request.data.get('email')
        company = AccountProfile.objects.get(email=company_email)
        serializer = CompanyBranchesSerializer(company)
        return Response(
            {
                'data': serializer.data,
                'status': 'success'
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['GET'], url_path='initial-data')
    def get_initial_data(self, request):
        Datapoints = namedtuple('initial_data', ('cities', 'gender'))
        countries = u.get_all_countries()
        industries = u.get_industries()
        gender = [
            {
                "code": 1,
                "name": "Male",
                "symbol": "M"
            },
            {
                "code": 2,
                "name": "Female",
                "symbol": "F"
            }
        ]
            
        data_points = Datapoints(
            cities=City.objects.all(),
            gender=gender
        )
        serializer = SignupInitializtionSerializer(data_points)
        data = serializer.data
        data.update(industries)
        data.update(countries['data'])
        return Response(
            {
                "status": "success",
                "data": data
            },
            status=status.HTTP_200_OK
        )
    

    @action(detail=False, methods=['GET'], url_path='get-states')
    def get_states(self, request):
        country_data = request.query_params.get('id')
        country_id = int(country_data)
        states = u.get_states_of_country(country_id)
        return Response(
            {
                'status': 'success',
                'data': states
            },
            status=status.HTTP_200_OK
        )


class CompanyBranchViewSet(ModelViewSet):

    queryset = CompanyBranch.objects.all()
    serializer_class = CompanyBranchSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "status": "fail",
                "data": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def list(self, request):
        branches = self.queryset
        serializer = self.serializer_class(branches, many=True)
        return Response(
            {
                "status": "success",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class IndustryViewSet(ModelViewSet):

    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "status": "fail",
                "data": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def list(self, request):
        industries = self.queryset
        serializer = self.serializer_class(industries, many=True)
        return Response(
            {
                "status": "success",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


# Class based Views - kakanmu ######


class InitializeSignUpForm(View):

    @staticmethod
    def get(request):
        resp = Response()
        country_code = request.GET.get('location', None)
        if not country_code:
            ip_addr = request.META.get('REMOTE_ADDR')
            locale_data = fetch_locale_data(ip_addr)
            country_code = locale_data.get('country')

        try:
            compose_account_creation_params(country_code, resp)
            resp.passed()

        except Exception as err:
            resp.failed()
            resp.add_message(str(err))

        return HttpResponse(resp.get_response(), content_type="application/json")


class FetchCountryCities(View):

    @staticmethod
    def get(request):
        resp = Response()
        country_code = request.GET.get('country_id', None)
        try:
            fetch_country_cities(country_code, resp)
            resp.passed()

        except Exception as err:
            resp.failed()
            resp.add_message(str(err))

        return HttpResponse(resp.get_response(), content_type="application/json")


class SubmitSignUpForm(View):

    @staticmethod
    def post(request, accnt_type):
        resp = Response()
        contents = get_contents(request)
        validation = validate_signup_composite(contents, resp)
        if validation:
            # Create signup composite
            create_signup_composite(contents, accnt_type, resp)

        return HttpResponse(resp.get_response(), content_type="application/json")


class SubcsriberView(APIView):

    def post(self, request):
        resp = Response()
        email = request.data.get('email', None)
        valid_email = SubscriberInput(data={'email': email})
        if valid_email.is_valid():
            try:
                subscriber = NewsLetterSubscribers.objects.create(email=email)
                serializer = SubscriberSerializer(instance=subscriber)
                resp.data = serializer.data
                resp.add_message('Successs')
                resp.passed()
                return HttpResponse(resp.get_response(), content_type='application/json')

            except Exception as err:
                resp.add_message('Email already exists')
                resp.failed()
                return HttpResponse(resp.get_response(), content_type='application/json')
        else:
            resp.add_message('Invalid Email')
            resp.failed()
            return HttpResponse(resp.get_response(), content_type='application/json')
            
        
class LookupClient(View):

    @staticmethod
    def get(request):
        resp = Response()
        contents = get_contents(request)
        if contents:
            search_string = contents.get('pattern', None)
            if search_string:
                try:
                    results = AccountProfile.objects.filter(name__icontains=search_string, active=True).order_by('id')\
                        .values('id', 'name', 'account_code', 'account_address')
                    matches = [x for x in results]
                    resp.passed()
                    resp.add_param('matches', matches)

                except Exception as err:
                    resp.failed()
                    resp.add_message(str(err))
        else:
            resp.failed()
            resp.add_message('Missing request parameters.')

        return HttpResponse(resp.get_response(), content_type="application/json")


class LookupAccountManager(View):

    @staticmethod
    def get(request):
        resp = Response()
        contents = get_contents(request)
        contents = get_contents(request)
        if contents:
            search_string = contents.get('pattern', None)
            if search_string:
                try:
                    results = UserProfile.objects.filter(active=True, account_manager=True,
                                                         name__icontains=search_string).order_by('id').values('id', 'name')
                    matches = [x for x in results]
                    resp.passed()
                    resp.add_param('matches', matches)

                except Exception as err:
                    resp.failed()
                    resp.add_message(str(err))
        else:
            resp.failed()
            resp.add_message('Missing request parameters.')

        return HttpResponse(resp.get_response(), content_type="application/json")


class SubmitSiteEnquiry(View):

    @staticmethod
    def post(request):
        resp = Response()
        contents = get_contents(request)
        enquiry_form = SiteEnquiryForm(contents)
        if enquiry_form.is_valid():
            enquiry_form.save()
            resp.passed()
            resp.add_message("Thank you. We received your enquiry and we'll get in touch soonest.")
        else:
            resp.failed()
            resp.add_param('errors', compile_form_errors(enquiry_form))

        return HttpResponse(resp.get_response(), content_type="application/json")


class LookUpAccount(View):

    @staticmethod
    def get(request, qry_type):
        resp = Response()
        contents = get_contents(request)
        if contents:
            qry_id = contents.get('id', None)
            qry_email = contents.get('email', None)
            try:
                accnt = None
                if qry_type == 'id':
                    accnt = AccountProfile.objects.get(id=qry_id)
                elif qry_type == 'email':
                    accnt = AccountProfile.objects.get(company_email__icontains=qry_email)

                a_obj = {'id': accnt.id, 'name': accnt.name, 'email': accnt.company_email,
                         'mobile': str(accnt.company_phone), 'address_info': accnt.company_address.address_info,
                         'country': accnt.company_address.country.name, 'city': accnt.company_address.city.name}

                resp.passed()
                resp.add_param('result', a_obj)

            except AccountProfile.DoesNotExist:
                resp.failed()
                resp.add_message('AccountProfile with ID/Email does not exist')

            except AccountProfile.MultipleObjectsReturned:
                resp.failed()
                resp.add_message('Multiple AccountProfiles matches the Id/Email')

        return HttpResponse(resp.get_response(), content_type="application/json")


class VerifyAccount(View):
    @staticmethod
    def get(request):
        resp = Response()
        contents = get_contents(request)
        if contents:
            acct_id = contents.get('id', None)
            acct_email = contents.get('email', None)
            try:
                if acct_id:
                    AccountProfile.objects.get(id=acct_id)
                    resp.passed()
                    resp.add_param('result', True)
                elif acct_email:
                    AccountProfile.objects.get(company_email__icontains=acct_email)
                    resp.passed()
                    resp.add_param('result', True)

            except AccountProfile.DoesNotExist:
                resp.passed()
                resp.add_param('result', False)

            except AccountProfile.MultipleObjectsReturned:
                resp.passed()
                resp.add_param('result', False)
        else:
            resp.failed()
            resp.add_message('Missing parameters!')

        return HttpResponse(resp.get_response(), content_type="application/json")


class ReadCustomerAccounts(View):

    def get(self, request, **kwargs):
        customer_type = kwargs.get('account_type', None)
        contents = get_contents(request)
        resp = Response()
        if contents:
            _pageSize = contents.get('pageSize', 10)
            _pageIndex = contents.get('pageIndex', 1)
            _filter = contents.get('filters', [])
            _sort = contents.get('sort', None)

            kwargs = build_query_filter(_filter)
            pager = build_pagination_markers(_pageIndex, _pageSize)

            # Run Query
            accounts = None
            if customer_type == 'pod':
                kwargs['account_type__name__iexact'] = 'pod'
            elif customer_type == 'streamz':
                kwargs['account_type__name__iexact'] = 'streamz'

            result_size = AccountProfile.objects.filter(**kwargs).count()
            results = AccountProfile.objects.filter(**kwargs)[pager['lm']:pager['um']]

            try:
                accounts = [{'id': x.id, 'name': x.name, 'account_code': x.account_code,
                             'company_email': x.company_email,
                             'account_officer': {'id': x.account_officer.id, 'label': x.account_officer.name}
                             if x.account_officer is not None else {'id': "",'label': ""},
                             'industry': {'id': x.industry.id, 'label': x.industry.name},
                             'company_address': {'address_info': x.company_address.address_info,
                                                 'city': {'id': x.company_address.city.id,
                                                          'label': x.company_address.city.name},
                                                 'country': {'id': x.company_address.country.id,
                                                             'label': x.company_address.country.name}
                                                   },
                             'company_phone': {'country_code': x.company_phone.country_code,
                                               'phone_number': x.company_phone.phone_number},
                             'contact_person': {'first_name': x.contact_person.first_name,
                                                'last_name': x.contact_person.last_name}} for x in results]

                resp.passed()
                resp.add_param('result', accounts)
                resp.add_param('result_size', result_size)

            except Exception as err:
                resp.failed()
                resp.add_message(str(err))

        return HttpResponse(resp.get_response(), content_type="application/json")

    def post(self, request, **kwargs):
        customer_type = kwargs.get('account_type', None)
        contents = get_contents(request)
        resp = Response()
        if contents:
            _pageSize = contents.get('pageSize', 10)
            _pageIndex = contents.get('pageIndex', 1)
            _filter = contents.get('filters', [])
            _sort = contents.get('sort', None)

            kwargs = build_query_filter(_filter)
            pager = build_pagination_markers(_pageIndex, _pageSize)

            # Run Query
            accounts = None
            if customer_type == 'pod':
                kwargs['account_type__name__iexact'] = 'pod'
            elif customer_type == 'streamz':
                kwargs['account_type__name__iexact'] = 'streamz'

            result_size = AccountProfile.objects.filter(**kwargs).count()
            results = AccountProfile.objects.filter(**kwargs)[pager['lm']:pager['um']]

            try:
                accounts = [{'id': x.id, 'name': x.name, 'account_code': x.account_code,
                             'company_email': x.company_email,
                             'account_officer': {'id': x.account_officer.id, 'label': x.account_officer.name}
                             if x.account_officer is not None else {'id': "",'label': ""},
                             'industry': {'id': x.industry.id, 'label': x.industry.name},
                             'company_address': {'address_info': x.company_address.address_info,
                                                 'city': {'id': x.company_address.city.id,
                                                          'label': x.company_address.city.name},
                                                 'country': {'id': x.company_address.country.id,
                                                             'label': x.company_address.country.name}
                                                 },
                             'company_phone': {'country_code': x.company_phone.country_code,
                                               'phone_number': x.company_phone.phone_number},
                             'contact_person': {'first_name': x.contact_person.first_name,
                                                'last_name': x.contact_person.last_name}} for x in results]

                resp.passed()
                resp.add_param('result', accounts)
                resp.add_param('result_size', result_size)

            except Exception as err:
                resp.failed()
                resp.add_message(str(err))

        return HttpResponse(resp.get_response(), content_type="application/json")


class UpdateCustomerAccounts(View):

    @staticmethod
    def post(request):
        resp = Response()
        contents = get_contents(request)
        validation = validate_signup_composite(contents, resp)
        if validation:
            # Update Account
            update_client_account(contents, resp)

        return HttpResponse(resp.get_response(), content_type="application/json")
