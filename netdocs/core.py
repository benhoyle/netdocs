# -*- coding: utf-8 -*-

import configparser
import urllib
import base64
from datetime import datetime
import os
import requests

# Can have multiple scopes separated by spaces
VALID_SCOPES = ['read', 'edit', 'organize', 'lookup', 'delete_doc', 'delete_container', 'full']

RESPONSE_TYPE = "code" # For authorization code flow
#auth parameters are client_id, scope, response_type, and redirect_uri

def check_list(listvar):
    if not isinstance(listvar, list):
        listvar = [listvar]
    return listvar
    
def filter_name(name, whitelist, blacklist):
    """ If a string name contains one or more words from whitelist but
    no words from blacklist return true else return false. """
    return any(word.lower() in name.lower() for word in whitelist) and not any(word.lower() in name.lower() for word in blacklist)

class NetDocs():
    
    def __init__(self, path_to_config=""):
        """ Initialise object and load settings. """

        parser = configparser.SafeConfigParser()
        if not path_to_config:
            # Default to user home directory and ".netdocs" file
            self.path_to_config = os.path.join(os.path.expanduser('~'), ".netdocs")
        else:
            self.path_to_config = path_to_config
        parser.read(self.path_to_config)
        self.client_id = parser.get('Client Parameters', 'C_ID')
        self.client_secret = parser.get('Client Parameters', 'C_SECRET')
        self.scope = parser.get('Client Parameters', 'SCOPE')
        
        # Initialise URLs
        self.auth_url = parser.get('URLs', 'AUTH_URL')
        self.redirect_uri = parser.get('URLs', 'REDIRECT_URI')
        self.refresh_url = parser.get('URLs', 'REFRESH_URL')
        self.base_url = parser.get('URLs', 'BASE_URL')
        
        # See if an access or refresh token has been saved
        try:
            self.refresh_token = parser.get('Client Parameters', 'REFRESH_TOKEN')
        except:
            self.refresh_token = None
        
        try:
            self.access_token = parser.get('Client Parameters', 'ACCESS_TOKEN')
        except:
            if self.refresh_token:
                self.get_new_access_token()
            else:
                self.access_token = None     
    
    def get_auth_url(self):
        # Encode URL parameters...
        params = urllib.parse.urlencode({
            'client_id' : self.client_id,
            'scope' : urllib.parse.quote(self.scope, safe=''),
            'response_type' : RESPONSE_TYPE
            })
        #...apart from redirect_uri (server doesn't like this encoded)
        redirect_url = "=".join(['redirect_uri', self.redirect_uri])
        params = "&".join([params, redirect_url])
            
        return "?".join([self.auth_url, params])
        
    def get_refresh_token(self, authcode):
        self.authcode = authcode
        
        # Encode URL parameters
        params = urllib.parse.urlencode({
            'grant_type' : 'authorization_code',
            'code' : authcode
            })
        #...apart from redirect_uri (server doesn't like this encoded)
        redirect_url = "=".join(['redirect_uri', self.redirect_uri])
        params = "&".join([params, redirect_url])
        
        url = self.refresh_url
        
        r = requests.post(url, headers=self.get_auth_headers(), data=params)
        
        #print r.text
        #try:
        params_dict = r.json()
        access_token = params_dict.get('access_token', None)
        refresh_token = params_dict.get('refresh_token', None)
        if access_token and refresh_token:
            self.access_token = access_token
            self.refresh_token = refresh_token
            
            # Store retrieved tokens in persistent storage
            config = configparser.SafeConfigParser()
            config.read(self.path_to_config)
            config.set('Client Parameters', 'ACCESS_TOKEN', self.access_token)
            config.set('Client Parameters', 'REFRESH_TOKEN', self.refresh_token)
            # Write config to file 
            with open(self.path_to_config, 'w') as configfile:
                config.write(configfile)
            return "Success > tokens stored"
        else:
            return str(r.status_code) + r.text
            
    def get_auth_headers(self):
        """ Generate headers needed for authorisation requests. """
        string_to_encode = ":".join([self.client_id, self.client_secret])
        b64string = base64.b64encode(bytes(string_to_encode, 'utf-8'))
        headers = {
            "Authorization" : "Basic {0}".format(b64string.decode('utf-8')),
            "Accept" : "application/json",
            "Accept-Encoding": "utf-8",
            "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",
            "Content-Length": "29"
            }
        return headers
    
    def get_new_access_token(self):
         # Encode URL parameters
        params = urllib.parse.urlencode({
            'grant_type' : 'refresh_token',
            'refresh_token' : self.refresh_token
            })
        
        url = self.refresh_url
        
        r = requests.post(url, headers=self.get_auth_headers(), data=params)
        
        try:
            params_dict = r.json()
            self.access_token = params_dict['access_token']
            
            # Store retrieved access token in persistent storage
            config = configparser.SafeConfigParser()
            config.read(self.path_to_config)
            config.set('Client Parameters', 'ACCESS_TOKEN', self.access_token)
            # Write config to file 
            with open(self.path_to_config, 'w') as configfile:
                config.write(configfile)
            return "Success > token stored"
        except:
            return str(r.status_code)      
    
    def build_request(self, object_type, object_id=""):
        headers = {
            "Authorization" : "Bearer %s" % self.access_token,
            "Accept" : "application/json"
            }
            
        url = "".join([self.base_url, object_type])
        return url, headers
    
    def make_query(self, url_portion, params=None):
        #Function to make a query and return json or statuscode / text
        url, headers = self.build_request(url_portion)
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 401:
            # Get new access token
            self.get_new_access_token()
            # Rebuild headers
            url, headers = self.build_request(url_portion)
            # Repeat request
            r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            return r.status_code, r.json()
        else:
            return r.status_code, r.text
    
    def get_user_data(self):
        object_type = "/v1/User/info"
        response = self.make_query(object_type)
        return response
    
    def get_savedsearch(self, ssid, params=None):
        object_type = "/v1/SavedSearch"
        url_portion = "/".join([object_type,ssid])
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
        #Gets folder id
        querystring = "=3({{{f}}}) =1033({{{c}}}) =11( ndfld )".format(f=foldername, c=caseref)
        #params = urllib.parse.urlencode({'q':querystring, '$select':'standardAttributes'})
        params = urllib.parse.urlencode({'q':querystring})
        status_code, response = self.make_query(urlportion, params)
        if status_code == 200 and len(response['list']) == 1:
            return response['list'][0]['envId']
        else:
            return status_code, response
      
    def get_doc_info(self, docid):
        object_type = "/v1/Document/{id}/info".format(id=docid)
        response = self.make_query(object_type)
        return response
    
    def get_folder_info(self, folderid):
        object_type =  "/v1/Folder/{id}/info".format(id=folderid)
        response = self.make_query(object_type)
        return response
        
    def folder_content(self, folderid, attributes=True):
        """Function to get folder content given an ID."""
        object_type= "/v1/Folder/{id}".format(id=folderid)
        if attributes:
            params = urllib.parse.urlencode({'$select': 'standardAttributes'})
        else:
            params = ""
        response = nd.make_query(object_type, params)
        return response
        
    def get_uploads(self, withindays=30):
        # withindays is an integer that only returns results created within last 'withindays' days
        object_type = "/v1/Search"
        # Ignore emails, saved searches, discussions and folders
        ignore_string = "NOT =11( msg OR ndsq OR nddis OR ndfld ))"
        
        # Generate query string for GET parameters
        querystring = "{ig}".format(ig=ignore_string)
        
        if withindays:
           querystring = " ".join([querystring, "=5(^-{w}-+0)".format(w=str(withindays))])
        # =5(^-30) restricts to last 30 days > assume anything older has been dealt with
        
        # Iterate through cabinets associated with user
        status_code, cabinets = self.get_cabinets()
        if status_code != 200:
            return "Error"

        runninglist = []
        
        for cabinet in cabinets:
            # Build search url and params for cabinet
            urlportion = "{ot}/{c_id}".format(ot=object_type, c_id=cabinet['id'])
            
            # Set search patameters
            params = urllib.parse.urlencode({'q':querystring, '$select':'standardAttributes', '$orderby':'lastMod desc'})
            
            moreresults = True
            while moreresults:
                status_code, response = self.make_query(urlportion, params)
                
                if status_code == 200:
                    #response['standardList'] provides a list of dicts
                    runninglist = runninglist + response['standardList']
                    # If there are more results...
                    if 'next' in response.keys():
                        #response['next'] provides url
                        urlportion = response['next']
                        params = None
                        moreresults = True
                    else:
                        moreresults = False
                else:
                    moreresults = False
                    print (status_code, response)

        return runninglist
            
        
    

