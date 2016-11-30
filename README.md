A Python wrapper for the NetDocuments API.

## Install and configuration

Requirements:
* Python 3+
* Requests
* Flask (for web server to retrieve the access token)

Install via pip:
```
pip install netdocs
```

### Setup Client Data

To access the API you'll need to register an app via the [Net Documents Developer Portal](https://www.netdocuments.com/en-gb/Developer/).

This will then give you a client id and secret. You will also need to register a redirect URI - set this as https://localhost:3000/gettoken.

Next create a file called ".netdocs". It's recommended to place this in your home directory (i.e. at "~/").
```
[Client Parameters]
c_id = [Paste your client id here]
c_secret = [Paste your client secret here]
scope = read [select from 'read', 'edit', 'organize', 'lookup', 'delete_doc', 'delete_container', 'full']
access_token = [Leave blank - will be retrieved]
refresh_token = [Leave blank - will be retrieved]

[URLs]
auth_url = https://vault.netvoyage.com/neWeb2/OAuth.aspx
redirect_uri = https://localhost:3000/gettoken [Register this in your App configuration - you can use a different uri if required]
refresh_url = https://api.vault.netvoyage.com/v1/OAuth
base_url = https://api.vault.netvoyage.com
```
If you use a service other than 'vault' (e.g. 'EU') change the urls accordingly.

### Getting an Access Token

The package provides a small webserver to enable you to connect to the Net Documents service and authorise the app.

Net Documents requires an SSL (https) connection. To provide this generate a self-signed certificate and key.
Make sure you have openssl installed then run from the terminal:
```
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout domain.key -out domain.crt
```
The webserver will look for the "domain.crt" and "domain.key" files in your home directory.

### Running the Webserver

To run the webserver and get an access token run the following after installing the package:
```
python -m netdocs.webserver
```
Then point your browser at [https://localhost:3000/ndsetup](https://localhost:3000/ndsetup).

You will probably get a warning about the self-signed certificate - click the advanced options and "Connect Anyway" option.

You will then be redirected to login to Net Documents and authorise the app with the scope set in 'Client Parameters' above.

After authorising the app you will be redirected to the webserver again. 
If all is successful this will be indicated with a message in the browser.

## Use

Once the steps above have been completed you can then use the Python NetDocs class.

Start by importing this class:
```
from netdocs import NetDocs
nd = NetDocs()
```
Example methods so far are:
```
# Get information on current user
info = nd.get_user_data()
# Get information on available cabinets
cabinets = nd.get_cabinents()
# Get information on a document with id [docid]
docinfo = nd.get_doc_info(docid)
# Get information on a folder with id [folderid]
folderinfo = nd.get_folder_info(folderid)
# Get contents of a folder with id [folderid]
foldercontents = folder_content(folderid)
```