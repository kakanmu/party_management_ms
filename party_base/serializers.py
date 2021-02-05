from rest_framework import serializers
from party_base.models import (
    UserProfile, AccountProfile, CompanyBranch, Address, Phone, 
    Industry, City, Country, NewsLetterSubscribers)

class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ['id', 'name']


class CityIDSerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ['id', ]


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ['id', 'name']


class CountryIDSerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ['id',]


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = [
            'id', 'address_info','state', 'country', 
            'active', 'activated', 
            'creation_date', 'last_modified_date']


class AddressOutputSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Address
        fields = [
            'id', 'address_info','state', 'country', 
            'active', 'activated', 
            'creation_date', 'last_modified_date']

class ShortPhoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Phone
        fields = ['id', 'country_code', 'phone_number']


class UserProfileSerializer(serializers.ModelSerializer):
    phones = ShortPhoneSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'first_name', 'last_name', 'email', 'party_code', 
            'party_role', 'dob', 'gender', 'phones'
        ]
    
    def create(self, validated_data):
        phones = validated_data.pop('phones')
        user_profile = UserProfile.objects.create(**validated_data)
        for phone in phones:
            Phone.objects.create(owner=user_profile, **phone)
        return user_profile


class FullUserProfileSerializer(serializers.ModelSerializer):
    phones = ShortPhoneSerializer(many=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'first_name', 'last_name', 'party_code', 
            'party_role', 'phones', 'dob', 'avatar', 'gender', 'active', 
            'activated', 'creation_date', 'last_modified_date']


class PhoneSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer(read_only=True)

    class Meta:
        model = Phone
        fields = ['id', 'country_code', 'phone_number', 'owner']


class ShortUserProfile(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = UserProfile.objects.get(email=value)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError('User Profile does not exist with that email')
        return value


class IndustrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Industry
        fields = ['id', 'name']


class CompanyProfileSerializer(serializers.ModelSerializer):
    contact_person = UserProfileSerializer()
    address = AddressSerializer()
    # industry = IndustrySerializer()
    # back_office_personel = UserProfileSerializer(read_only=True)
    # back_office_email = ShortUserProfile(write_only=True, allow_null=True,)

    class Meta:
        model = AccountProfile
        fields = [
            'id', 'name', 'description', 'email', 'address', 'industry', 
            'contact_person',]
    
    def create(self, validated_data):
        contact = validated_data.pop('contact_person')
        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        phone_data = contact.pop('phones')
        industry_data = validated_data.pop('industry')
        user_profile = UserProfile.objects.create(**contact)
        for phone in phone_data:
            Phone.objects.create(owner=user_profile, **phone)
        if 'back_office_email' in validated_data:
            back_office_data = validated_data.pop('back_office_email')
            try:
                personel_profile = UserProfile.objects.get(email=back_office_data['email'])
                company_profile = AccountProfile.objects.create(contact_person=user_profile, industry=industry, back_office_personel=personel_profile, **validated_data)
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError('No profile exists with this email')
        else:
            company_profile = AccountProfile.objects.create(contact_person=user_profile, industry=industry, address=address, **validated_data)
        return company_profile


class ShortCompanySerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            company = AccountProfile.objects.get(email=value)
        except AccountProfile.DoesNotExist:
            raise serializers.ValidationError('Company with that email does not exist')
        return value


class CompanyBranchSerializer(serializers.ModelSerializer):
    company = CompanyProfileSerializer(read_only=True)
    company_email = ShortCompanySerializer(write_only=True)
    contact_person = UserProfileSerializer(read_only=True)
    contact_email = ShortUserProfile(write_only=True)
    address = AddressSerializer()

    class Meta:
        model = CompanyBranch
        fields = ['id', 'company', 'company_email', 'address', 'contact_person', 'contact_email', 'is_head_office']

    def create(self, validated_data):
        contact_email_data = validated_data.pop('contact_email')
        try:
            user = UserProfile.objects.get(email=contact_email_data['email'])
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError('No user profile with that email')
        company_email_data = validated_data.pop('company_email')
        print(company_email_data['email'])
        try:
            company = AccountProfile.objects.get(email=company_email_data['email'])
        except AccountProfile.DoesNotExist:
            raise serializers.ValidationError('No company profile with that email')
        address_data = validated_data.pop('address')
        address_instance = Address.objects.create(**address_data)
        company_branch = CompanyBranch.objects.create(company=company, contact_person=user, address=address_instance, **validated_data)
        return company_branch


class ShortCompanyBranchSerializer(serializers.ModelSerializer):
    company = ShortCompanySerializer()
    address = AddressSerializer()
    contact_person = UserProfileSerializer()

    class Meta:
        model = CompanyBranch
        fields = ['id', 'company', 'address', 'contact_person', 'is_head_office']


class CompanyBranchesSerializer(serializers.ModelSerializer):
    branches = ShortCompanyBranchSerializer(many=True)

    class Meta:
        model = AccountProfile
        fields = ['id', 'name','branches']


class GenderSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    name = serializers.CharField()
    symbol = serializers.CharField()


class DataCountrySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField()

class SignupInitializtionSerializer(serializers.Serializer):
    cities = CitySerializer(many=True)
    gender = GenderSerializer(many=True)


class SubscriberSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsLetterSubscribers
        fields = ['email', 'creation_date']


class SubscriberInput(serializers.Serializer):
    email = serializers.EmailField()