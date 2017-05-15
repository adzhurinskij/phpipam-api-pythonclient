# -*- coding: utf-8 -*-
import requests
import urllib
import base64
import rijndael
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

KEY_SIZE = 16
BLOCK_SIZE = 32


def encrypt(key, plaintext):
    padded_key = key.ljust(KEY_SIZE, '\0')
    padded_text = plaintext + (BLOCK_SIZE - len(plaintext) % BLOCK_SIZE) * '\0'

    r = rijndael.rijndael(padded_key, BLOCK_SIZE)

    ciphertext = ''
    for start in range(0, len(padded_text), BLOCK_SIZE):
        ciphertext += r.encrypt(padded_text[start:start+BLOCK_SIZE])

    encoded = base64.b64encode(ciphertext)

    return encoded


def decrypt(key, encoded):
    padded_key = key.ljust(KEY_SIZE, '\0')

    ciphertext = base64.b64decode(encoded)

    r = rijndael.rijndael(padded_key, BLOCK_SIZE)

    padded_text = ''
    for start in range(0, len(ciphertext), BLOCK_SIZE):
        padded_text += r.decrypt(ciphertext[start:start+BLOCK_SIZE])

    plaintext = padded_text.split('\x00', 1)[0]

    return plaintext


class PHPIPAM:
    def __init__(self, url, api_id, api_key):
        """Constructor

        Parameters
            url - string base url to phpipam server
            api_id - string phpipam api id
            api_key - string phpipam api key
        """
        self.url = url
        self.api_id = api_id
        self.api_key = api_key

    def query_phpipam(self, method, **kwargs):
        """Query PHPIPAM API

        Sends HTTP query to PHPIPAM

        Parameters
            kwargs - dictionary
        Returns
            JSON
            {
                "success":true,
                "data": [{...}, ...]
            }
        """
        data = {
            'enc_request': encrypt(self.api_key, json.dumps(kwargs)),
            'app_id': self.api_id
        }

        url = '%s/?%s' % (self.url, urllib.urlencode(data, True))

        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, verify=False, allow_redirects=False)
            elif method == 'POST':
                response = requests.post(url, headers=headers, verify=False, allow_redirects=False)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, verify=False, allow_redirects=False)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, verify=False, allow_redirects=False)
            else:
                print "Wrong method"
                return None
        except Exception as error:
            print error
            return None

        return json.loads(response.text.encode('utf8'))

    def generic(self, controller, method, **kwargs):
        """Query PHPIPAM 

        Parameters
            controller - string controller name
               valid controller values = ["sections", "subnets", "addresses", "vlans", "users", "groups", "requests"] 
            method - string method name
                valid method values = ["GET", "POST", "PATCH", "DELETE"]
        Returns
            JSON
            {
                "success":true,
                "data": [{...}, ...]
            }                            
        """
        data = {"controller": controller}
        data.update(kwargs)

        return self.query_phpipam(method, **data)

    """
    Manage devices.
    """

    def create_devices(self, **kwargs):
        """
        Create device.

        Database fields:
        +----------------+-----------------------+------+-----+---------+-----------------------------+
        | Field          | Type                  | Null | Key | Default | Extra                       |
        +----------------+-----------------------+------+-----+---------+-----------------------------+
        | id             | int(11) unsigned      | NO   | PRI | NULL    | auto_increment              |
        | hostname       | varchar(32)           | YES  | MUL | NULL    |                             |
        | ip_addr        | varchar(100)          | YES  |     | NULL    |                             |
        | type           | int(2)                | YES  |     | 0       |                             |
        | vendor         | varchar(156)          | YES  |     | NULL    |                             |
        | model          | varchar(124)          | YES  |     | NULL    |                             |
        | description    | varchar(256)          | YES  |     | NULL    |                             |
        | sections       | varchar(1024)         | YES  |     | NULL    |                             |
        | editDate       | timestamp             | YES  |     | NULL    | on update CURRENT_TIMESTAMP |
        | snmp_community | varchar(100)          | YES  |     | NULL    |                             |
        | snmp_version   | set('0','1','2')      | YES  |     | 0       |                             |
        | snmp_port      | mediumint(5) unsigned | YES  |     | 161     |                             |
        | snmp_timeout   | mediumint(5) unsigned | YES  |     | 1000000 |                             |
        | snmp_queries   | varchar(128)          | YES  |     | NULL    |                             |
        | rack           | int(11) unsigned      | YES  |     | NULL    |                             |
        | rack_start     | int(11) unsigned      | YES  |     | NULL    |                             |
        | rack_size      | int(11) unsigned      | YES  |     | NULL    |                             |
        | location       | int(11) unsigned      | YES  |     | NULL    |                             |
        +----------------+-----------------------+------+-----+---------+-----------------------------+

        """
        data = {
            "controller": "tools",
            "id": "devices",
        }

        data.update(kwargs)

        return self.query_phpipam(method='POST', **data)

    def read_devices(self, id=None):
        """Read devices"""
        data = {
            "controller": "tools",
            "id": "devices"
        }

        if id is not None:
            data.update({"id2": id})

        return self.query_phpipam(method='GET', **data)

    def update_devices(self, id, **kwargs):
        data = {
            "controller": "tools",
            "id": "devices",

            "id2": id
        }

        data.update(kwargs)

        return self.query_phpipam(method='PATCH', **data)

    def delete_devices(self, id):
        """Delete devices"""
        data = {
            "controller": "tools",
            "id": "devices",
            "id2": id
        }

        return self.query_phpipam(method='DELETE', **data)

    """
    Manage locations

    Locations fields:
    +-------------+------------------+------+-----+---------+----------------+
    | Field       | Type             | Null | Key | Default | Extra          |
    +-------------+------------------+------+-----+---------+----------------+
    | id          | int(11) unsigned | NO   | PRI | NULL    | auto_increment |
    | name        | varchar(128)     | NO   |     |         |                |
    | description | text             | YES  |     | NULL    |                |
    | lat         | varchar(12)      | YES  |     | NULL    |                |
    | long        | varchar(12)      | YES  |     | NULL    |                |
    | address     | varchar(128)     | YES  |     | NULL    |                |
    +-------------+------------------+------+-----+---------+----------------+

    """

    def create_locations(self, **kwargs):
        """Create locations"""
        data = {
            "controller": "tools",
            "id": "locations",
        }

        data.update(kwargs)

        return self.query_phpipam(method='POST', **data)

    def read_locations(self, id=None):
        """Read locations"""
        data = {
            "controller": "tools",
            "id": "locations"
        }

        if id is not None:
            data.update({"id2": id})

        return self.query_phpipam(method='GET', **data)

    def update_locations(self, id, **kwargs):
        """Update locations"""
        data = {
            "controller": "tools",
            "id": "locations",
            "id2": id
        }

        data.update(kwargs)

        return self.query_phpipam(method='PATCH', **data)

    def delete_locations(self, id):
        """Delete locations"""
        data = {
            "controller": "tools",
            "id": "locations",
            "id2": id
        }

        return self.query_phpipam(method='DELETE', **data)
