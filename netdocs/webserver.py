# Import flask dependencies
from flask import Flask, request, render_template, \
                  flash, g, session, redirect, url_for

import os          
                  
# Import netdocs module for authentication
from netdocs import NetDocs

# Self-signed certificate and key for SSL
context = (os.path.join(os.path.expanduser('~'), 'domain.crt'), os.path.join(os.path.expanduser('~'),'domain.key'))

app = Flask(__name__)

def get_urlparams(request, param):
    return request.args.to_dict().get(param, None)

@app.route('/ndsetup', methods=['GET'])
def netdocs_auth():
    nd = NetDocs()
    return redirect(nd.get_auth_url())

@app.route('/gettoken', methods=['GET'])
def get_netdocs_authcode():
    authcode = get_urlparams(request, 'code')
    if authcode:
        nd = NetDocs()
        return nd.get_refresh_token(authcode)
    else:
        return "Error getting token"
        
def main():
    app.run(host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", 3000)), debug=True, ssl_context=context)

if __name__ == '__main__':
    main()