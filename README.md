phpipam-api-pythonclient
=================

Python Library for PHPIPAM API 

Tested on API v1.3

<h4>Usage</h4>

<pre>
ipam = PHPIPAM("phpipam.example.com", "api_id", "api_key")

print ipam.read_devices()
print ipam.read_devices(id=20)

print ipam.generic(
    controller="vlans",
    method="GET"
)
</pre>
