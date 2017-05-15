phpipam-api-pythonclient
=================

Python Library for PHPIPAM API 

Tested on API v1.3

#### Installation
```
pip install git+https://github.com/adzhurinskij/phpipam-api-pythonclient
```

#### Usage
```python
from phpipam_api_pythonclient.phpipam import PHPIPAM

ipam = PHPIPAM("phpipam.example.com", "api_id", "api_key")

print ipam.read_devices()
print ipam.read_devices(id=20)

print ipam.generic(
    controller="vlans",
    method="GET"
)
```