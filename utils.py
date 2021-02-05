import json
from party_data_management_ms.settings import (
    TRAKIT_URL,
    ENQUIRY_ICON,
    ENQUIRIES_SLACK_CHANNEL,
)
import requests
from jsa_utils.assets import (
    compile_form_errors,
    get_modifier,
    build_query_filter,
    build_pagination_markers,
    get_contents,
    generate_serial_number,
    generate_client_location_code,
    get_broker_channel,
    publish_event_topic,
    publish_event_broadcast,
    publish_direct_message,
    send_email_notification,
    fetch_locale_data,
)


def generate_party_code(party_prefix=None, location=""):
    return generate_client_location_code(client_prefix=party_prefix, location=location)


# def synchronize_on_trakit(account_profile=None):
#
#     print(">>> Inside SYNCHRONIZER: ", account_profile)
#     print(">>> Inside SYNCHRONIZER: ", account_profile.account_type.account_type_code)
#
#     if account_profile and account_profile.account_type.account_type_code in [
#         "IE",
#         "FF",
#     ]:
#         print(">>>> Synchronizing with TRAKIT")
#         trakit_token = None
#         # Login to get token.
#         login_params = {
#             "UserID": "OKA",
#             "Pass": "@Ucapital1",
#             "DeviceType": "Linux",
#             "DeviceName": "CloudServer",
#             "DeviceID": "jsa-platformcore-centos",
#             "Zone": 0,
#         }
#         req = requests.post(TRAKIT_URL + "/api/mobile/Login", data=login_params)
#         if req.status_code == 200:
#             response = req.json()
#             if response.get("Code", None) == 1:
#                 trakit_token = response.get("Info", None)
#                 print(">>>> Fetched TRAKIT token successfully", trakit_token)
#
#             # Create Customer account
#             if trakit_token and account_profile:
#                 print(">>>>> Creating Customer Record on TRAKIT <<<<<")
#                 payload = {
#                     "Code": str(account_profile.account_code),
#                     "Name": str(account_profile.name),
#                     "Type": "Customer",
#                     "Country": str(
#                         account_profile.company_address.country.country_code_2
#                     ),
#                     "Address": str(account_profile.account_address),
#                     "Phone": str(account_profile.company_phone),
#                     "Email": str(account_profile.company_email),
#                 }
#
#                 url_end = "/api/mobile/CreateEntity?Token=" + str(trakit_token)
#                 proc = requests.post(TRAKIT_URL + url_end, data=payload)
#                 if proc.status_code == 200:
#                     response = proc.json()
#                     print(">>> Request Returned", response)
#                     if response.get("Code", None) == 1:
#                         print(">> Account Synchronized Successfully")
#                 else:
#                     print(">> Account TrakIT synchronization failed")


def publish_slack_enquiry_channel(enquiry=None):

    if enquiry:
        message = {
            "blocks": [
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "image",
                            "image_url": "{}".format(ENQUIRY_ICON),
                            "alt_text": "images",
                        },
                        {"type": "mrkdwn", "text": "*New Website Enquiry*"},
                    ],
                },
                {"type": "divider", "block_id": "divider1"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Name:* {} - {}".format(
                            enquiry.name, enquiry.business_name
                        ),
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Email:* {}".format(enquiry.email),
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Phone:* {}".format(enquiry.phone),
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Enquiry:* {}".format(enquiry.enquiry_message),
                    },
                },
                {"type": "divider", "block_id": "divide2"},
            ]
        }

        # Post request
        try:
            postman = requests.post(ENQUIRIES_SLACK_CHANNEL, data=json.dumps(message))
            if postman.status_code == 200:
                print(">>>> Slack Message Posted successfully !!")
            else:
                print(">>>> Message Posting Failed")

        except Exception as err:
            print(">>>> Slack message posting failed.")
            print(str(err))
