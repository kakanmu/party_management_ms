import json
import json
from decimal import Decimal
from datetime import datetime


class Fakefloat(float):

    def __init__(self, value):
        self._value = value
    def __repr__(self):
        return str(self._value)


def defaultencode(o):
    if isinstance(o, Decimal):
        # Subclass float with custom repr?
        return Fakefloat(o)
    raise TypeError(repr(o) + " is not JSON serializable")


class DecimalEncoder2(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            #return '{:20,.2f}'.format(o)
            return float("{0:.2f}".format(o))
        return super(DecimalEncoder, self).default(o)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super(DateTimeEncoder, self).default(o)


class Response(object):
    """
    The ResponseModel Class encapsulates the request response in JSON format.
    """
    def __init__(self):
        """
        Constructor
        """
        super(Response, self).__init__()
        self.query_response = {}
        self.data = {}
        self.status_code = 0
        self.message = ""

    def add_param(self, key_str, value_str):
        """
        Adds a key/value pair to the Response dict payload
        """
        # print("Adding %s as key for %s" % (key_str, value_str))
        self.data[key_str] = value_str

    def add_message(self, msgtxt, title=None):
        """
        Used to pass a message to the response. A wrapper for resp.add_param('message', 'message text goes here')
        :param msgtxt:
        :param title:
        :return:
        """
        self.message = msgtxt
        if title:
            self.data['message_title'] = title

    def passed(self):
        """
        Set the status of the response as success i.e. HTTP200
        """
        self.query_response['status'] = 'success'
        self.status_code = 200

    def failed(self):
        """
        Set the status of the response to failed i.e. HTTP200 but failed
        attempt at the response result.
        :return:
        """
        self.query_response['status'] = 'fail'
        self.status_code = 400

    def error(self):
        """
        Set the status of the response to failed i.e. HTTP404
        :return:
        """
        self.query_response['status'] = 'error'
        self.status_code = 500

    def no_params(self, message=None):
        """
        Set the status of the response to failed i.e. HTTP404
        :return:
        """
        self.query_response['status'] = 'fail'
        self.status_code = 400
        if message:
            self.data['message'] = message
        else:
            self.data['message'] = 'No parameters was sent or the construct of the parameter is invalid. Please verify.'
        self.data['message_title'] = 'No Parameters'

    def unsuccessful(self):
        self.query_response['status'] = 'fail'
        self.status_code = 400

    def successful(self):
        self.query_response['status'] = 'success'
        self.status_code = 200

    def no_token(self):
        """
        No token was found or given
        :return:
        """
        self.query_response['status'] = 'error'
        self.data['message'] = "No Request Token was found or the Request Token sent was invalid. " \
                               "You probably have not logged in"

    def missing_params(self, message=None):
        """
        Set the status of the response to failed i.e. HTTP404
        :return:
        """
        self.query_response['status'] = 'error'
        if message:
            self.data['message'] = message
        else:
            self.data['message'] = 'There are missing parameters in your request. Please verify.'

    def failed_api_call(self, message=None):
        """
        If a call to an external API fails, this method is a
        response wrapper to the API Consumer (Web UI, Postman etc.)
        :return:
        """
        self.query_response['status'] = 'error'
        if message:
            self.data['message'] = message
        else:
            self.data['message'] = 'Call to the API failed. Check your paramters and try again.'

    def set_error_message(self, mssg_string):
        """
        set error messages
        :param mssg_string:
        :return:
        """
        self.query_response['message'] = mssg_string

    def get_response(self, isdecimal=True):
        """
        send back response as json
        :param isdecimal:
        :return:
        """
        self.query_response['data'] = self.data
        self.query_response['status_code'] = self.status_code
        self.query_response['message'] = self.message
        if isdecimal:
            json_resp = json.dumps(self.query_response, cls=DecimalEncoder)
        else:
            json_resp = json.dumps(self.query_response)
        return json_resp

    def print_result(self):
        """
        print the json response to the console
        :return:
        """
        json_resp = json.dumps(self.query_response)
        print('--> JSON Response', json_resp)
