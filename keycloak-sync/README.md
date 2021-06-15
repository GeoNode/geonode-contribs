# Geonode KeyCloak Sync
-------------

keycloak-sync is a geonode app to synchronise users, groups and roles between Keycloak and GeoNode.

## Quick start
1. Docker
  ```
  RUN cd /usr/src; git clone https://github.com/GeoNode/geonode-contribs.git -b master
  RUN cd /usr/src/geonode-contribs/keycloaksync/src; pip install --upgrade  -e .
  ```
2. Add the following to your `settings.py` file:
    ```
    if 'keycloaksync' not in INSTALLED_APPS:
        INSTALLED_APPS += ('keycloaksync',)
        
    KEYCLOAK_URL=os.getenv('KEYCLOAK_URL', None)
    KEYCLOAK_CLIENT=os.getenv('KEYCLOAK_CLIENT', None)
    KEYCLOAK_CLIENT_ID=os.getenv('KEYCLOAK_CLIENT_ID', None)
    KEYCLOAK_CLIENT_SECRET=os.getenv('KEYCLOAK_CLIENT_SECRET', None)
    KEYCLOAK_REALM=os.getenv('KEYCLOAK_REALM', None)
    KEYCLOAK_USER=os.getenv('KEYCLOAK_USER', None)
    KEYCLOAK_PASSWORD=os.getenv('KEYCLOAK_PASSWORD', None)
    KEYCLOAK_USER_REALM=os.getenv('KEYCLOAK_USER_REALM', None)
    ```

3. Add the urls to your `urls.py` file:
    ```
    urlpatterns += [
        url(r'^keycloaksync/', include('keycloaksync.urls', namespace='keycloaksync'))
    ]
    ```

4. Test your synchronization:
    To initiate synchronization, go to: `/keycloaksync/synchronize_all`. It will return a summary of what actions it performed per table that was affected.

    You can validate that the following models were affected via the Admin page:
    - Groups: `/en/admin/auth/group/`
    - GroupProfiles: `/en/admin/groups/groupprofile/`
    - Users: `/en/admin/people/profile/`
    - SocialAccounts: `/en/admin/socialaccount/socialaccount/`

    You can also use the GeoNode interface to validate:
    - Users: `/people/`
    - Groups: `/groups/`

## Documentation

The idea behind this contrib app is to synchronize users from Keycloak to GeoNode's models.

It fetches the users from Keycloak's users and groups API endpoints, e.g.
- <keycloak_auth_url>/admin/realms/<keycloak_realm>/users?max=6000
- <keycloak_auth_url>/admin/realms/<keycloak_realm>/groups?max=6000

It then adds, deletes or updates:
- SocialAccounts, including associated Profiles per account
- GroupProfiles, including Groups per group profile

Social Accounts are added with `keycloak` as their provider.

The `/keycloaksync/synchronize_all` url will return information in the following:
```
{
  "group_profiles": {
    "new": [],
    "deleted": []
  },
  "groups": {
    "new": [],
    "deleted": []
  },
  "profiles": {
    "new": [],
    "updated": [
      {
        "model": "people.profile",
        "pk": 1,
        "fields": {
          "password": "sha1$somesha1",
          "last_login": "2021-06-09T10:58:01.009Z",
          "is_superuser": true,
          "username": "username",
          "first_name": "user",
          "last_name": "name",
          "email": "my@mail.com",
          "is_staff": true,
          "is_active": true,
          "date_joined": "2021-06-09T10:51:38.704Z",
          "organization": null,
          "profile": null,
          "position": null,
          "voice": null,
          "fax": null,
          "delivery": null,
          "city": null,
          "area": null,
          "zipcode": null,
          "country": null,
          "language": "en",
          "timezone": "",
          "groups": [],
          "user_permissions": []
        }
      },
      ...
    ],
    "deleted": []
  },
  "social_accounts": {
    "new": [],
    "deleted": []
  }
}
```
## Development

1. To get get the project up and running:

- Make sure you've got an `.env` file with the contents of `.env.example`
- Start the sync script
    ```
    docker-compose run --rm sync bash
    python keycloaksync/controller.py
    ```
- You can reuse this method to test your changes

2. Important files:
- `src/keycloaksync/controller.py` handles all of the sync logic
- `src/keycloaksync/settings.py` is where we set some settings variables
- `src/keycloaksync/urls.py` is where we create the url endpoints for the app
- `src/keycloaksync/views.py` is where we create the handlers for the url endpoints

3. If your testing is done, you can test it integrated in a sample GeoNode project
- Make sure you've got an `test.env` file with the contents of `test.env.example`
- Start up the services
    ```
    COMPOSE_HTTP_TIMEOUT=240 docker-compose -f test.yml up --build
    ```
- Wait for the following log from the `django_1` log that indicates all has loaded:
  ```
  [uWSGI] getting INI configuration from /usr/src/my_geonode/uwsgi.ini
  ```
- You can thus test with http://localhost:9999/keycloaksync/synchronize_all
  - Username: admin
  - Password: admin
- Use the same validation logic as provided in Quick Start's point 4