import json
from party_base.models import UserProfile

# Callback functions


def assign_authprofile(payload=None):
    print('>>>> Assigning AuthProfile:', payload)

    if payload:

        try:
            party_profile = UserProfile.objects.get(id=payload.get('account_profile_id', None))
            print('>>>> UserProfile found: ', party_profile)
            party_profile.synchronize_userprofile(payload.get('auth_profile_id', None))

            if len(party_profile.linked_company.all()) > 0:
                comps = party_profile.linked_company.all()
                for c_prof in comps:
                    print('>>> Finalizing Account:', c_prof)
                    c_prof.finalize_account_opening()
                    c_prof.save()

            party_profile.save()
            print(">>>> Auth-profile Attached <<<")

        except Exception as err:
            print('>>> Error Assigning Auth Profile <<<<')
            print(str(err))