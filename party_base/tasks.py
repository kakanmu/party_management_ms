from __future__ import absolute_import, unicode_literals
from party_data_management_ms.celery import pdms_app
from party_data_management_ms.settings import TRAKIT_URL
from party_base.models import AccountProfile
import requests
from .interservice_callbacks import assign_authprofile


@pdms_app.task(name='process_inter_service_message')
def process_interservice_message(**kwargs):
    print('>>>>>> PDMS received IS-Message: ', kwargs)

    route = kwargs.get('message_key', None)

    # Event subscription handlers
    if str(route).lower() == 'accounts.userprofile.setup':
        print('>>>> Message Handler Found: ', route)
        assign_authprofile(kwargs)

    else:
        print('>>>> Message Handler Undefined: Message dropped', route)
