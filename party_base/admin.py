from django.contrib import admin
from party_base.models import Address, AccountProfile, CompanyBranch, Phone, UserProfile, Industry, City, Country, \
    AccountType, Territory, NewsLetterSubscribers, SiteEnquiry


class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_type_code', 'mapped_app_role_code')


class AccountProfileAdmin(admin.ModelAdmin):
    list_display = ('account_code', 'name', 'account_type', 'account_status', 'account_officer')
    readonly_fields = ('account_code', 'account_status', 'contact_person')
    exclude = ('displayString', 'activated')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('party_code', 'first_name', 'last_name', 'email', 'profile_ref_code', 'profile_status')
    readonly_fields = ('party_code', 'auth_profile_id', 'profile_status', 'email', 'phone')
    exclude = ('name', 'displayString', 'activated')


class SiteEnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_name', 'email')
    readonly_fields = ('enquiry_message',)


class TerritoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')


# Register your models here.
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(AccountProfile, AccountProfileAdmin)
admin.site.register(CompanyBranch)
admin.site.register(Address)
admin.site.register(AccountType, AccountTypeAdmin)
admin.site.register(Phone)
admin.site.register(Industry)
admin.site.register(City)
admin.site.register(Country)
admin.site.register(NewsLetterSubscribers)
admin.site.register(Territory, TerritoryAdmin)
admin.site.register(SiteEnquiry, SiteEnquiryAdmin)

