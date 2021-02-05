from django.urls import path
from party_base.views import InitializeSignUpForm, SubmitSignUpForm, FetchCountryCities, LookupClient, \
    SubmitSiteEnquiry, LookUpAccount, SubcsriberView, LookupAccountManager, VerifyAccount

# router = DefaultRouter()
# router.register(r'addresses', AddressViewSet)
# router.register(r'user-profile', UserProfileViewSet)
# router.register(r'user-phones', PhoneViewSet)
# router.register(r'companies', CompanyViewSet)
# router.register(r'company-branches', CompanyBranchViewSet)
# router.register(r'industries', IndustryViewSet)
# router.register(r'cities', CityViewSet)
# router.register(r'countries', CountryViewSet)

urlpatterns = [
    path('initialize-signup-form/', InitializeSignUpForm.as_view()),
    path('fetch-cities/', FetchCountryCities.as_view()),
    path('accounts/signup/<str:accnt_type>/', SubmitSignUpForm.as_view()),
    path('add-subscriber/', SubcsriberView.as_view()),
    path('client-lookup/', LookupClient.as_view()),
    path('manager-lookup/', LookupAccountManager.as_view()),
    path('contact-us/', SubmitSiteEnquiry.as_view()),

    # Interservice endpoints
    path('get_account_details_byID/', LookUpAccount.as_view(), {'qry_type': 'id'}),
    path('get_account_details_byEmail/', LookUpAccount.as_view(), {'qry_type': 'email'}),
    path('verifyAccountId/', VerifyAccount.as_view()),

]


