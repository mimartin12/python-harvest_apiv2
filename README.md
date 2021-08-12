

[![Build](https://travis-ci.org/bradbase/python-harvest_apiv2.png?branch=master)](https://travis-ci.org/bradbase/python-harvest_apiv2)
[![Coverage Status](https://coveralls.io/repos/github/bradbase/python-harvest_apiv2/badge.svg?branch=master)](https://coveralls.io/github/bradbase/python-harvest_apiv2?branch=master)
![Version](https://img.shields.io/pypi/v/python-harvest_apiv2.svg?style=flat)
![License](https://img.shields.io/pypi/l/python-harvest_apiv2.svg?style=flat)
![Versions](https://img.shields.io/pypi/pyversions/python-harvest_apiv2.svg?style=flat)

Version 1.11.0 will be the last freely availalbe build. The source will still be available but not for free.

Version 1.13.0 and above will be sold on the following e-commerce website:-
https://dachshund-turbot-6p52.squarespace.com/

Documentation is also available on the squrespace website. It's free but currently distributed as a zipfile through the store.


### Installation

Python 3.7 and above:

```
pip install "python-harvest_apiv2"
```

### Usage

#### Personal Access Token

Create a Personal Access Token in the Developers page on Harvest as documented in the Harvest documentation https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/

```python
import harvest
from harvest.harvestdataclasses import *

personal_access_token = PersonalAccessToken("ACCOUNT ID", "PERSONAL TOKEN")
client = harvest.Harvest("https://api.harvestapp.com/api/v2", personal_access_token)

client.get_currently_authenticated_user()
```

#### For Server Side Applications

Create an OAuth2 application in the Developers page on Harvest as documented in the Harvest documentation https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/

Authentication needs to occur before you make your Harvest client.

```python
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import WebApplicationClient
from dacite import from_dict

import harvest
from harvest.harvestdataclasses import *

webclient = WebApplicationClient(client_id="CLIENT ID")
oauth = OAuth2Session(client=webclient)

authorization_url, state = oauth.authorization_url("https://id.getharvest.com/oauth2/authorize")
print("Browse to here in your web browser and authenticate: ", authorization_url)
response_uri = input("Please copy the resulting URL from your browser and paste here:")

harv = OAuth2Session("CLIENT ID", state=state)
token = harv.fetch_token("https://id.getharvest.com/api/v2/oauth2/token", client_secret="CLIENT SECRET", authorization_response=response_uri, include_client_id=True, state=state)
oauth2_serverside_token = from_dict(data_class=OAuth2_ServerSide_Token, data=token)
oauth2_serverside = OAuth2_ServerSide(client_id="CLIENT ID", client_secret="CLIENT SECRET", token=oauth2_serverside_token, refresh_url="https://id.getharvest.com/api/v2/oauth2/token")

client = harvest.Harvest("https://api.harvestapp.com/api/v2", oauth2_serverside)

client.get_currently_authenticated_user()
```

#### For Client Side Applications

Create an OAuth2 application in the Developers page on Harvest as documented in the Harvest documentation https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/

Authentication needs to occur before you make your Harvest client.

```python
from oauthlib.oauth2 import MobileApplicationClient
from dacite import from_dict

import harvest
from harvest.harvestdataclasses import *

mobileclient = MobileApplicationClient(client_id="CLIENT ID")

url = mobileclient.prepare_request_uri("https://id.getharvest.com/oauth2/authorize")
print("Browse to here in your web browser and authenticate: ", url)
response_uri = input("Please copy the resulting URL from your browser and paste here:")

response_uri = response_uri.replace('callback?', 'callback#')
token = mobileclient.parse_request_uri_response(response_uri)
oauth2_clientside_token = from_dict(data_class=OAuth2_ClientSide_Token, data=token)

client = harvest.Harvest("https://api.harvestapp.com/api/v2", oauth2_clientside_token)

client.get_currently_authenticated_user()
```

### Run tests
From the root python-harvest_apiv2 directory
```
tox
```

### Contributions

Contributions are welcome. Including tests helps decide on whether to merge the PR.

### TODOs
* Write API doco for the Python client. The tests demonstrate how to use the library but that's not clear from this page.
* Support Detailed Reports page functionality in the module detailedreports

### License

python-harvest_apiv2 is licensed under MIT style licence. See [LICENSE](LICENSE) for more details.
