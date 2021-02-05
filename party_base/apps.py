from django.apps import AppConfig
import pika


class PartyBaseConfig(AppConfig):
    name = 'party_base'

    def ready(self):
        from party_base import model_actions

        print('-- Initializing Messaging Infrastructure : {} >>>'.format(self.name))
        from party_data_management_ms.settings import MESSAGING_USERNAME, MESSAGING_PWORD, BROKER_IP, BROKER_PORT, \
            BROKER_VHOST, BROKER_CONNECTION, EVENT_SUBSCRIPTIONS, ROUTING_EXCHANGES, DATABASES

        # Channel
        broker_channel = None

        def setup_service_messaging(xchanges=None):
            print('---> Setting up Routing Exchange(s) on VHOST: {}'.format(BROKER_VHOST))
            for xch in xchanges:
                # Confirm/Setup routing exchanges
                print('>>>>>>>> ', xch['description'])
                broker_channel.exchange_declare(str(xch['id']).upper(), str(xch['type']).lower(), False, True)

                # Create queues & bindings
                if str(xch['type']).lower() == 'fanout':
                    print('=== Declaring Queue:', '{}_inbox'.format(str(self.name)))
                    q_res = broker_channel.queue_declare(str('{}_inbox'.format(str(self.name))).upper(), False, True)
                    print('=== Declaring Queue Binding:', q_res.method.queue)
                    broker_channel.queue_bind(q_res.method.queue, str(xch['id']).upper(), '')

                elif str(xch['type']).lower() == 'direct':
                    print('=== Declaring Queue:', '{}_inbox'.format(str(self.name)))
                    q_res = broker_channel.queue_declare(str('{}_inbox'.format(str(self.name))).upper(), False, True)
                    print('=== Declaring Queue Binding:', q_res.method.queue)
                    broker_channel.queue_bind(q_res.method.queue, str(xch['id']).upper(),
                                              str(q_res.method.queue).lower())

                elif str(xch['type']).lower() == 'topic':
                    print('=== Declaring Queue:', '{}_inbox'.format(str(self.name)))
                    q_res = broker_channel.queue_declare(str('{}_inbox'.format(str(self.name))).upper(), False, True)
                    for topic in EVENT_SUBSCRIPTIONS:
                        print('==== Declaring Topic Subscriptions:', topic.get('description'))
                        broker_channel.queue_bind(q_res.method.queue, str(xch['id']).upper(),
                                                  str(topic.get('topic', '')).lower())

        try:
            if BROKER_CONNECTION is None:
                print('---> Establishing broker connection & channel')
                creds = pika.PlainCredentials(MESSAGING_USERNAME, MESSAGING_PWORD)
                params = pika.ConnectionParameters(BROKER_IP, BROKER_PORT, BROKER_VHOST, creds)
                BROKER_CONNECTION = pika.BlockingConnection(params)
                broker_channel = BROKER_CONNECTION.channel()
            else:
                broker_channel = BROKER_CONNECTION.channel()

            print('==>> Check DB Settings')
            print(DATABASES.get('default'))

            # Setup service messaging
            setup_service_messaging(ROUTING_EXCHANGES)

            print('-- Closing Channel')
            broker_channel.close()

        except Exception as err:
            print('>> EXCEPTION: ', str(err))