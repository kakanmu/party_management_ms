from django.db.models.signals import pre_save, post_save
from django_fsm.signals import post_transition
from django.dispatch import receiver
from party_base.models import AccountProfile, UserProfile, SiteEnquiry
from utils import generate_party_code, publish_event_topic
from utils import generate_serial_number, publish_slack_enquiry_channel
import uuid


@receiver(pre_save, sender=AccountProfile)
def set_account_code(sender, **kwargs):
    account_prof = kwargs.get('instance')

    if account_prof and account_prof.account_code is None:
        account_prof.account_code = generate_party_code(str(account_prof.account_type.account_type_code),
                                                        account_prof.company_address.country.country_code_2)


@receiver(post_transition, sender=AccountProfile)
def dispatch_account_welcome_email(sender, **kwargs):
    print('>>>> Account Profile Transition PostConsequence <<<<<<')
    account = kwargs.get('instance')
    t_status = kwargs.get('target')
    print(account, t_status)

    if t_status == 'Completed':
        print('>>>>>> SYNCHRONIZING ACCOUNT TO TRAKIT <<<<<<<', str(account.id))
        #synchronize_on_trakit(account)
        # print('>>> Sending Welcome Email <<')
        # mail_cntxt = {'price_quote_url': PRICE_QUOTE_URL}
        # if account.name:
        #     mail_cntxt['full_name'] = account.name
        #
        # recepients = []
        # if account.company_email:
        #     print('>> Company Email', account.company_email)
        #     recepients.append(account.company_email)
        # elif account.contact_person.email:
        #     print(">>> Contact Person Email:", account.contact_person.email)
        #     recepients.append(account.contact_person.email)
        #
        # print("Context:", mail_cntxt)
        # print(" Recepients:", recepients)
        # print('From Email: ',DEFAULT_FROM_EMAIL)
        # # Send Email
        # send_email_notification(recepients, DEFAULT_FROM_EMAIL, 'Welcome to Jetstream', mail_cntxt,
        #                         'emails/account_welcome.html')


@receiver(pre_save, sender=UserProfile)
def set_party_code(sender, **kwargs):
    usr_prof = kwargs.get('instance')

    if usr_prof and usr_prof.party_code is None:
        # Set party code
        usr_prof.party_code = generate_party_code('U', '')
        # Set profile ref code
        usr_prof.profile_ref_code = ''.join([str(usr_prof.first_name).upper(), generate_serial_number()])

    usr_prof.name = ''.join([usr_prof.first_name, ' ', usr_prof.last_name])



@receiver(post_save, sender=AccountProfile)
def post_account_signup_event(sender, **kwargs):
    print('Post saving stuff')
    accnt_prof = kwargs.get('instance')
    new_entry = kwargs.get('created')
    print(accnt_prof, new_entry)
    info = kwargs
    print(info)
    if accnt_prof and new_entry:
        try:
            topic = 'party_base.companyprofile.signup'
            task_id = uuid.uuid4().int
            task_name = 'process_inter_service_message'
            data = {'message_key': topic,
                    'person_id': accnt_prof.contact_person.id,
                    'person_fname': accnt_prof.name,
                    'person_lname': '.',
                    'person_email': accnt_prof.contact_person.email,
                    'person_phone': str(accnt_prof.company_phone),
                    'app_role_code': accnt_prof.account_type.mapped_app_role_code
                    }
            #print(data['person_fname'])

            # Send message to Exchange
            publish_event_topic(topic, {'id': task_id, 'task': task_name, 'kwargs': data})

        except Exception as err:
            print('>> Error on Event Publish <<<')
            print(str(err))


@receiver(post_save, sender=SiteEnquiry)
def post_enquiry_notitfications(sender, **kwargs):
    enquiry = kwargs.get('instance')
    new_entry = kwargs.get('created')

    if enquiry and new_entry:
        # Post Slack Notification
        publish_slack_enquiry_channel(enquiry)


