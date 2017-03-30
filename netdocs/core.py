from six.moves.urllib import parse
import base64
import requests
from netdocs.errors import (
    NDRefreshTokenError,
    NDAccessTokenError
)

# Can have multiple scopes separated by spaces
VALID_SCOPES = [
    'read', 'edit', 'organize', 'lookup', 'delete_doc',
    'delete_container', 'full'
    ]


AUTH_URL = 'https://vault.netvoyage.com/neWeb2/OAuth.aspx'
REFRESH_URL = 'https://api.vault.netvoyage.com/v1/OAuth'
BASE_URL = 'https://api.vault.netvoyage.com'


class NetDocs():

    def __init__(self, client_id, client_secret):
        """ Create object and initialise client settings. """
        # Load Settings
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = ""
        self.refresh_token = ""
        self.scope = ""
        self.configure_urls()

    def configure_urls(
            self,
            redirect_url="http://localhost",
            auth_url=AUTH_URL,
            refresh_url=REFRESH_URL,
            base_url=BASE_URL
    ):
        """ Initialise URLs """
        self.auth_url = auth_url
        self.redirect_url = redirect_url
        self.refresh_url = refresh_url
        self.base_url = base_url

    def auth_headers(self):
        """ Get headers for authentication. """
        b64string = base64.b64encode(
            ":".join([self.client_id, self.client_secret]).encode()
            )
        return {
            "Authorization": "Basic {0}".format(b64string.decode()),
            "Accept": "application/json",
            "Accept-Encoding": "utf-8",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Content-Length": "29"
            }

    def get_auth_url(self):
        """ Build authentication URL. """
        # Encode URL parameters...
        params = parse.urlencode({
            'client_id': self.client_id,
            'scope': parse.quote(self.scope, safe=''),
            'response_type': 'code'
            })
        # ...apart from redirect_uri (server doesn't like this encoded)
        redirect_url = "=".join(['redirect_uri', self.redirect_url])
        params = "&".join([params, redirect_url])

        return "?".join([self.auth_url, params])

    def get_refresh_token(self, authcode):
        self.authcode = authcode

        # Encode URL parameters
        params = {
            'grant_type': 'authorization_code',
            'code': authcode,
            'redirect_uri': self.redirect_url
            }
        # ...apart from redirect_uri (server doesn't like this encoded)
        # redirect_url = "=".join(['redirect_uri', self.redirect_uri])
        # params = "&".join([params, redirect_url])

        r = requests.post(self.refresh_url, headers=self.auth_headers(), data=params)

        if r.status_code == 200:
            params_dict = r.json()
            self.access_token = params_dict.get('access_token')
            self.refresh_token = params_dict.get('refresh_token')
            return self.refresh_token
        else:
            print(r.status_code, r.text)
            raise NDRefreshTokenError

    def get_new_access_token(self):
        # Encode URL parameters
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
            }

        r = requests.post(self.refresh_url, headers=self.headers(), data=params)

        if r.status_code == 200:
            params_dict = r.json()
            self.access_token = params_dict['access_token']
            return self.access_token
        else:
            print(r)
            raise NDAccessTokenError

    def create_user_instance(self):
        """ Create a NetDocs instance for a user. """
        pass

    def build_request(self, url_portion):
        headers = {
            "Authorization": "Bearer {0}".format(self.access_token),
            "Accept": "application/json"
            }

        url = "".join([self.base_url, url_portion])
        return url, headers

    def make_query(
        self,
        url_portion,
        params=None,
        method='GET',
        retry=False
    ):
        """
        Function to make a (get) query and return json or statuscode / text
        """
        url, headers = self.build_request(url_portion)

        if method == 'GET':
            r = requests.get(url, headers=headers, params=params)
        else:
            r = requests.post(url, headers=headers, params=params)

        if r.status_code == 200:
            return r.json()

        if r.status_code == 401:
            if not retry:
                self.get_new_access_token()
                return self.make_query(url_portion, params, method, retry=True)
        else:
            print(r.status_code)

    def get_user_data(self):
        object_type = "/v1/User/info"
        response = self.make_query(object_type)
        return response

    def get_savedsearch(self, ssid, params=None):
        object_type = "/v1/SavedSearch"
        url_portion = "/".join([object_type, ssid])
        response = self.make_query(url_portion)
        return response

    def get_homepage_searches(self):
        # Get ids of homepage searches
        object_type = "/v1/User/homePage"
        status_code, response = self.make_query(object_type)
        if status_code == 200:
            return [entry['envId'] for entry in response[0]['list']]
        else:
            return status_code, response

    def get_cabinets(self):
        object_type = "/v1/User/cabinets"
        response = self.make_query(object_type)
        return response

    def get_folder_id(self, cabinet_id, caseref, foldername):
        object_type = "/v1/Search"
        urlportion = "{ot}/{c_id}".format(ot=object_type, c_id=cabinet_id)
        # Get folder id
        querystring = """
            =3({{{f}}}) =1033({{{c}}}) =11( ndfld )
            """.format(f=foldername, c=caseref)
        # params = urllib.urlencode(
        # {'q': querystring, '$select': 'standardAttributes'}
        # )
        params = {'q': querystring}
        status_code, response = self.make_query(urlportion, params)
        if status_code == 200 and len(response['list']) == 1:
            return response['list'][0]['envId']
        else:
            return status_code, response

    def get_ids_from_querystring(self, cabinet_id, caseref, querystring):
        object_type = "/v1/Search"
        urlportion = "{ot}/{c_id}".format(ot=object_type, c_id=cabinet_id)
        caseref_stem = caseref.rsplit('.', 1)[0]
        params = {
                'q': querystring.format(
                    caseref_stem=caseref_stem,
                    caseref=caseref
                    )
            }

        status_code, response = self.make_query(urlportion, params)
        if status_code == 200:
            return [
                result['envId']
                for result in response['list']
                ]
        else:
            return status_code, response

    def get_doc_info(self, docid):
        object_type = "/v1/Document/{id}/info".format(id=docid)
        response = self.make_query(object_type)
        return response

    def get_folder_info(self, folderid):
        object_type = "/v1/Folder/{id}/info".format(id=folderid)
        response = self.make_query(object_type)
        return response

    def folder_content(self, folderid, attributes=True):
        """Function to get folder content given an ID."""
        object_type = "/v1/Folder/{id}".format(id=folderid)
        if attributes:
            params = {'$select': 'standardAttributes'}
        else:
            params = ""
        response = self.make_query(object_type, params)
        return response

    def folder_content_by_querystring(self, cabinet_id, caseref, querystring):
        """ Get ID:name list based on a folder search. """
        folder_ids = self.get_ids_from_querystring(
                                        cabinet_id,
                                        caseref,
                                        querystring
                                    )
        print(folder_ids)
        files = []
        for folder_id in folder_ids:
            folder_content = self.folder_content(folder_id)
            print(folder_content)
            if folder_content:
                new_files = [
                    {
                        'name': entry['name'],
                        'envId': entry['envId'],
                        'extension': entry['extension']
                    }
                    for entry in folder_content[1]['standardList']
                    ]
                files = files + new_files
        return files

    def create_folder(self, parent_id, folder_name):
        """ Create a new folder under the folder with parent_id. """
        url = "/v1/Folder"
        data = {
            'name': folder_name,
            'parent-id': parent_id
        }
        response = self.post_query(url, data)
        print(response)
        #try:

            #return self.post_query(url, params)
        #except:
            #return None

    def copy_file(self, file_id, to_folder_id, newname=None):
        """ Copy a file to a folder with an optional newname. """
        url = "/v1/Document"
        params = {
            'action': 'copy',
            'id': file_id,
            'destination': to_folder_id,
        }

        if newname:
            params['name'] = newname

        # params = parse.urlencode(params)

        try:
            return self.post_query(url, params)
        except:
            return None

    def get_uploads(self, userstring, withindays=None):
        """
        Get recent uploads to NetDocs for a user.

        :param userstring: user name in format 'Joe Blogs'
        :type userstring: str
        :param withindays: return results created within this many days
        :type withindays: int
        :return: runninglist of files
        """
        object_type = "/v1/Search"
        # Ignore emails, saved searches, discussions and folders
        ignore_string = "NOT =11( msg OR ndsq OR nddis OR ndfld ))"

        # Generate query string for GET parameters
        querystring = "=6({uploader}) ={fe_code}({user}) {ig}".format(
            uploader=self.uploader_name,
            fe_code=self.fe_code,
            user=userstring,
            ig=ignore_string
            )

        if withindays:
            querystring = " ".join([
                querystring,
                "=5(^-{w}-+0)".format(w=str(withindays))
                ])
        # =5(^-30) restricts to last 30 days

        # Iterate through cabinets associated with user
        status_code, cabinets = self.get_cabinets()
        if status_code != 200:
            return "Error"

        runninglist = []

        for cabinet in cabinets:
            # Build search url and params for cabinet
            urlportion = "{ot}/{c_id}".format(
                                            ot=object_type,
                                            c_id=cabinet['id']
                                            )

            # Set search patameters
            params = parse.urlencode({
                            'q': querystring,
                            '$select': 'standardAttributes',
                            '$orderby': 'lastMod desc'
                        })

            moreresults = True
            while moreresults:
                status_code, response = self.make_query(urlportion, params)

                if status_code == 200:
                    # response['standardList'] provides a list of dicts
                    runninglist = runninglist + response['standardList']
                    # If there are more results...
                    if 'next' in response.keys():
                        # response['next'] provides url
                        urlportion = response['next']
                        params = None
                        moreresults = True
                    else:
                        moreresults = False
                else:
                    moreresults = False
                    print (status_code, response)

        return runninglist
