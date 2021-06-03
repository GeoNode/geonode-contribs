# **GeoNode extension Keycloak-Role Django Application**
## **Purpose**
The goal of this application is to synchronize Keycloak roles with GeoNode group profiles.

The application creates a connection with Keycloak. Using client credentials the roles are retrieved from Keycloak. Each role is then assigned a group.

The synchronize button can be found in Django Administration page, Home -> Keycloak -> Keycloak roles and right next to add Keycloak role button.
## **SetUp**
### **Django-Allauth**
Django-allauth is already installed with GeoNode.

Django-allauth tutorial-> https://number1.co.za/using-keycloak-as-the-identity-provider-for-users-on-django-and-django-admin/

From the tutorial add these points to your code: 
1. Add 'allauth.socialaccount.providers.keycloak' to INSTALLED_APPS.
2. Add to the SOCIALACCOUNT_PROVIDERS.

When creating your private client following these points from the tutorial:
1. Create the client.
2. Do not add the provided redirect uri.
3. Add this redirect uri:  http://localhost:8000/account/keycloak/login/callback/
4. Set the access type.
5. Turn on: Authorization, Direct Access Grant.
6. Under Service Account Roles tab select **admin** and added it to assigned roles.

When creating your public client:
1. Create the client.
2. set access type to public.
3. Turn on: Standard Flow, Implicit Flow, Direct Access.
4. Add these two redirect uris: http://localhost:8000/account/keycloak/login/callback/, http://localhost:8000/*
5. Add the following web origin: *
### **Inside your web-app**
The following files required to be modified before configuration of geonode:

#### **> settings.py**
Add the app to INSTALLED_APPS above 'geonode'
```python
INSTALLED_APPS = (
    ...
    'keycloakrole',
    ...
)
```
And make sure the following installed apps are below 'geonode' so that the template functionality of django-allauth is not overwritten by geonode
```python
INSTALLED_APPS = (
    ...
    'geonode',

     # login with external providers
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Django-Allauth
    'allauth.socialaccount.providers.keycloak',
)


```
Add the keycloak variables
```python
# Keycloak client data
KEYCLOAK_CLIENT = '[client name]'
KEYCLOAK_PUB_CLIENT = '[client name]'
KEYCLOAK_CLIENT_ID = '[{Keycloak url}/[client_id/uuid ]]'
KEYCLOAK_CLIENT_SECRET = '[client secret]'
KEYCLOAK_GRANT_TYPE = 'client_credentials'
KEYCLOAK_SCOPE = 'openid roles'
KEYCLOAK_REALM = '[realm name]'
KEYCLOAK_HOST_URL = '[http://localhost:8080 or host url that you will be using]'

Example:
# Keycloak client data
KEYCLOAK_CLIENT = 'geonode-client'
KEYCLOAK_PUB_CLIENT = 'geonode-pub-client'
KEYCLOAK_CLIENT_ID = 'NDJKSDu3939320ndndJSJEWjj33333'
KEYCLOAK_CLIENT_SECRET = 'dhdhJSJSU673JDSHShddd88hhd883'
KEYCLOAK_GRANT_TYPE = 'client_credentials'
KEYCLOAK_SCOPE = 'openid roles'
KEYCLOAK_REALM = 'master'
KEYCLOAK_HOST_URL = 'http://localhost:8080'
```
Comment out DIRS within TEMPLATES
```python
TEMPLATES = [
    ...
    # 'DIRS': [os.path.join(PROJECT_ROOT, "templates")],
    ...
]
```
#### **> url.py**
Add the app to INSTALLED_APPS
```python
urlpatterns += (
    ...
    # Keycloakrole views
    url(r'^keycloakrole/', include('keycloakrole.urls', namespace='keycloakrole')),
    ...
)
```
## **Test**
Create a virtual environment within your repository using the following commands:
```bash
python3 -m venv venv

. ./venv/bin/activate/ 
```
### **Test with GeoNode**
The following command runs the tests:
```bash
./manage.py test keycloakrole
```
### **Test as a stand alone Django application**
Make sure requirements.txt has a compatible version of GDAL with your version of GeoNode (version 3.0.4 is being tested against).
 
Install all the requirements with the following command within your virtual environment:
```bash
pip install -r requirements.txt
```
The following command runs the tests:
```bash
python runtests.py test keycloakrole  
```