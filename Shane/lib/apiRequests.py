##################################################################################################
#
# Store Adobe Audience Manager REST API credentials in object
# Issue API calls with Request class
#
##################################################################################################
__author__ = "Shane Nielson"
__email__ = "shnielso@adobe.com"

# Imports
import base64
import requests
import logging

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Credentials:
    def __init__(self):
        """
        Stores information to make REST API calls for Adobe Audience Manager

        :_client_id: API client ID : string
        :_client_secret: API client secret : string
        :_username: Demdex username : string
        :_password: Demdex password : string
        :_enoced_auth: client_id and client_secret combined and base64 encoded : string
        :_access_token: Bearer access token from the demdex ouath domain : string
        :_domain: API domain address for oauth tokens: string
        """
        self._client_id = None
        self._client_secret = None
        self._username = None
        self._password = None
        self._encoded_auth = None
        self._access_token = None
        self._domain = "https://api.demdex.com/oauth/token"

    @property
    def client_id(self):
        return self._client_id

    @property
    def client_secret(self):
        return self._client_secret

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def encoded_auth(self):
        return self._encoded_auth

    @property
    def access_token(self):
        return self._access_token

    @client_id.setter
    def client_id(self, value):
        self._client_id = value

    @client_secret.setter
    def client_secret(self, value):
        self._client_secret = value

    @username.setter
    def username(self, value):
        self._username = value

    @password.setter
    def password(self, value):
        self._password = value

    @encoded_auth.setter
    def encoded_auth(self, value):
        self._encoded_auth = value

    @access_token.setter
    def access_token(self, value):
        self._access_token = value


    def encode(self):
        if self.client_id is None or self.client_secret is None:
            logger.error("Empty client id or client secret")
            logger.debug("client_id: %s | client_secret: %s" % (self.client_id, self.client_secret))
            return
        logger.info("Encoding %s:%s" % (self.client_id, self.client_secret))
        data_string = "%s:%s" % (self.client_id, self.client_secret)
        self._encoded_auth = base64.urlsafe_b64encode(data_string.encode('utf-8')).decode('utf-8')
        logger.debug("Encoded value: %s" % self.encoded_auth)

    def get_token(self):
        if self.username is None or self.password is None:
            logger.error("Empty username or password")
            return

        if self.encoded_auth is None:
            logger.error("Empty encoded api credentials")
            return

        payload = "grant_type=password&username=%s&password=%s" % (self.username, self.password)
        headers = {
            'Accept': "application/json",
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': "Basic %s" % self.encoded_auth,
            'cache-control': "no-cache",
        }
        logger.debug("Payload: %s" % payload)
        logger.debug("Headers: %s" % headers)
        logger.info("Sending request to %s" % self._domain)
        response = requests.request("POST", self._domain, data=payload, headers=headers)
        if response.status_code is 200:
            try:
                self._access_token = response.json()['access_token']
            except Exception:
                logger.error("%s: Failed to get token" % response.reason, exc_info=True)
        else:
            logger.error("%s : Unable to connect, please check inputs/network settings" % response.reason)

class Request():
    def __init__(self, token):
        """
        :_domain: API url for all API calls : string
        :_version: version for API calls : string
        :_header: Header to pass in during API requests. Stores access token : string
        """
        self._domain = "https://api.demdex.com"
        self._version = "v1"
        self._header = {
            'Accept': "application/json",
            'Content-Type': "application/json",
            'Authorization': "Bearer %s" % token,
            'cache-control': "no-cache",
        }

    def get_traits_by_dpid(self, dpid):
        url = "%s/%s/traits/" % (self._domain, self._version)
        querystring = {"dataSourceId": dpid}

        logger.info("Sending request to %s" % url)
        return requests.request("GET", url, headers=self._header, params=querystring)

    def get_destination_by_segment(self, segment):
        url = "%s/%s/destinations/" % (self._domain, self._version)
        querystring = {"containsSegment": segment}

        logger.info("Sending request to %s" % url)
        return requests.request("GET", url, headers=self._header, params=querystring)
    
    def put_destination_mapping(self, payload):
        if payload['destinationId']:
            destinationId = payload['destinationId']
            del payload['destinationId']
        else:
            logger.error("No destinationId found")
            return

        if payload['destinationMappingId']:
            destinationMappingId = payload['destinationMappingId']
            del payload['destinationMappingId']
        else:
            logger.error("No destinationMappingId found")
            return

        url = "%s/%s/destinations/%s/mappings/%s" % (self._domain, self._version, destinationId, destinationMappingId)

        logger.info("Sending request to %s" % url)
        logger.debug(payload)
        return requests.put(url, data=json.dumps(payload), headers=self._header)    

    def get_data_sources(self):
        url = "%s/%s/datasources/" % (self._domain, self._version)

        logger.info("Sending request to %s" % url)
        return requests.request("GET", url, headers=self._header)
    
    def get_destination_mapping(self, orderId):
        url = "https://api.demdex.com/v1/destinations/%s/mappings" % (orderId)

        logger.info("Sending request to %s" % url)
        return requests.request("GET", url, headers=self._header)