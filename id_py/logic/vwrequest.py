import requests
import logging
import json
import os
from logging import info, debug, basicConfig
from datetime import datetime, timezone

from .consts import HtmlConsts, UrlConsts, PrefixConsts
from ..models import Token
from .util import Util
from .commissionnumber import CommissionNumber


# class to receive a token from vw
# better do not touch this class if it's working fine and you do not know what you do.
class TokenReceiver:

    # Vocabulary
    SESSION         = 'SESSION'
    VCAP_JOURNEY    = 'vcap_journey'
    COOKIE          = 'Cookie'


    # self explanatory. used for extracting some tokens. returns a dictionary containing the 
    # intermediate tokens.
    @staticmethod
    def extract_keys_values_from_html(text: str) -> dict:
        sandwich = Util.sandwich
        dictionary = {}
        csrf_token = sandwich(text, 'name="_csrf" value="', '"')
        dictionary.setdefault('_csrf', csrf_token)
        relay_state = sandwich(text, 'name="relayState" value="', '"')
        dictionary.setdefault('relayState', relay_state)
        hmac = sandwich(text, 'name="hmac" value="', '"')
        dictionary.setdefault('hmac', hmac)
        return dictionary


    # constructor. sets the credentials via environment variables.
    def __init__(self):
        self.EMAIL = os.getenv('VW_LOGIN_EMAIL')
        self.PASSWORD = os.getenv('VW_LOGIN_PASSWORD')
        if self.EMAIL == None or self.PASSWORD == None:
            raise Exception('bad credentials')


    # the main method which returns the Bearer token
    def main(self) -> Token:

        # constants
        ENTRY_POINT = UrlConsts.ENTRY_POINT
        SESSION = self.SESSION
        VCAP_JOURNEY = self.VCAP_JOURNEY
        COOKIE = self.COOKIE
        LOGIN_FORM_MAIL_ENTRY_POINT = UrlConsts.LOGIN_FORM_MAIL_ENTRY_POINT
        EMAIL = self.EMAIL
        PASSWORD = self.PASSWORD
        LOGIN_FORM_PASSWORD_ENTRY_POINT = UrlConsts.LOGIN_FORM_PASSWORD_ENTRY_POINT
        TOKEN_URL = UrlConsts.TOKEN_URL

        # for using the static methods without class prefix
        sandwich = Util.sandwich
        extract_keys_values_from_html = TokenReceiver.extract_keys_values_from_html

        # create html session that performs the same actions as done by a human being via browser
        s = requests.Session()

        # calling entrypoint
        info(f'calling entrypoint {ENTRY_POINT}')
        entrypoint_response = s.get(ENTRY_POINT)
        debug(f'got status {entrypoint_response.status_code}')

        # extract tokens (csrf, ...) and stuff from plain html
        text = entrypoint_response.text
        keys_values = extract_keys_values_from_html(text)
        debug(f'extracted keys and values are {keys_values}')

        # add email to the keys/values to pass it to the login form
        keys_values.setdefault('email', EMAIL)

        # obtain session id
        session = entrypoint_response.cookies.get(SESSION)
        debug(f'extracted session id is {session}')

        # extract vcap_journey
        vcap_journey = entrypoint_response.request.headers.get(COOKIE).split('vcap_journey=')[1]
        debug(f'extracted vcap_journey is {vcap_journey}.')

        # define cookies for new request
        new_request_cookies = {SESSION: session, VCAP_JOURNEY: vcap_journey}

        # save keys and values as pairs just like $key=$value
        keys_values_as_pairs = []
        for key in keys_values.keys():
            keys_values_as_pairs.append(f'{key}={keys_values.get(key)}')
        
        # join the keys and values to construct a payload
        payload_for_login_form_mail = '&'.join(keys_values_as_pairs)
        debug(f'new payload is {payload_for_login_form_mail}')

        # calling the login form as a human being would do
        info(f'calling {LOGIN_FORM_MAIL_ENTRY_POINT}')
        login_form_mail_response = s.post(LOGIN_FORM_MAIL_ENTRY_POINT, \
                                        data=payload_for_login_form_mail, \
                                        cookies=new_request_cookies)
        debug(f'status code is {login_form_mail_response.status_code}')

        # append the password to the key/value map to pass it to the next login form
        keys_values.setdefault('password', PASSWORD)

        # append new hmac value for the next form
        new_hmac = sandwich(login_form_mail_response.text, '"hmac":"', '"')
        keys_values.update({'hmac': new_hmac})

        # construct next payload for the password form
        keys_values_as_pairs = []
        for key in keys_values.keys():
            keys_values_as_pairs.append(f'{key}={keys_values.get(key)}')
        payload_for_password_form_mail = '&'.join(keys_values_as_pairs)

        debug(f'new payload is {payload_for_password_form_mail}')

        # do the call
        password_form_mail_response = \
            s.post(LOGIN_FORM_PASSWORD_ENTRY_POINT, payload_for_password_form_mail)

        # extract the final csrf token that is needed to obtain the Bearer token to put it into the 
        # header as X-CSRF-TOKEN.
        final_csrf_token = password_form_mail_response.request.headers\
                                .get('Cookie')\
                                .split('token=')[1]

        # perform the call to the token endpoint
        tokens = s.get(TOKEN_URL, headers={'X-CSRF-TOKEN': final_csrf_token})

        # get the access token
        access_token = sandwich(tokens.text, '"access_token":"', '"')

        # get the id token (currently not in use as not needed)
        id_token = sandwich(tokens.text, '"id_token":"', '"')

        return_token = Token()
        return_token.token = access_token
        return_token.date = datetime.now().astimezone(timezone.utc)
        return return_token

# class end


# class to retrieve properties from the volkswagen api
class PropertyGetter:

    # url constants
    VEHICLE_DETAILS_BASE_URL: str
    VEHICLE_DATA_BASE_URL: str

    # dicts for properties
    data: dict = {}
    details: dict = {}

    # boolean flag to show if a token is ok
    success = False


    # constructor: takes token and commssion number.
    def __init__(self, token: Token, number: CommissionNumber):
        self.token = token
        self.number = number

        # prefix defaults to 2022 to prefer newer commission numbers
        # there is at least one known case where a 2022 and 2021 commission number exists: AH0021
        # TODO: find out the 2023 prefix. maybe 1852023? i don't know.
        self.prefix = PrefixConsts.PREFIX_2022
        self.data: dict = {}
        self.details: dict = {}
        self.VEHICLE_DATA_BASE_URL = \
            'https://myvw-gvf-proxy.apps.emea.vwapps.io/vehicleData/de-DE/'
        self.VEHICLE_DETAILS_BASE_URL = \
            'https://myvw-gvf-proxy.apps.emea.vwapps.io/vehicleDetails/de-DE/'


    # method to load all properties from the vw api.
    # if not successful, then the success flag is set to False
    def load(self):
        res = self.make_request(self.VEHICLE_DATA_BASE_URL)
        # if request was not successful, try again with 2021 token
        if (res.status_code != 200):
            self.prefix = PrefixConsts.PREFIX_2021
            res = self.make_request(self.VEHICLE_DATA_BASE_URL)
        self.data: dict = json.loads(res.text)
        res = self.make_request(self.VEHICLE_DETAILS_BASE_URL)
        self.details: dict = json.loads(res.text)
        self.success = res.status_code == 200


    def make_request(self, base_url: str) -> requests.Response:
        response = requests.get(base_url +  f'{self.prefix}{self.number.number}',
            headers={'Authorization': f'Bearer {self.token.token}'})
        return response


    # method to return the text to show (vin if present, subs otherwise)
    def show(self) -> str:
        vin = self.data.get('vin')
        if not self.success:
            return HtmlConsts.NO_CAR_FOUND
        if vin != None:
            return vin
        else:
            return HtmlConsts.SAD_MESSAGE


    # extracts a value from specifications. takes a string.
    # the first spec that includes the string is returned.
    # example: string = "Softwareverbund"
    def extract_from_specs(self, string: str):
        filter_lambda = lambda x : string in x.get('codeText')
        specs_dict: dict = self.details.get('specifications')
        try:
            return list(filter(filter_lambda, specs_dict))[0].get('codeText')
        except:
            return None

# class end


# class to test if the token is valid
class TokenTester:

    URL = UrlConsts.TOKEN_TEST_URL

    def __init__(self, token: Token):
        self.token = token

    def test(self) -> bool:
        response: requests.Response = requests.get(self.URL, headers={
            'Authorization': f'Bearer {self.token.token}'})
        return response.status_code == 200

# class end