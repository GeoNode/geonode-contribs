import os, json
import logging

import requests

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    import django
    django.setup()
    from django.core.management import execute_from_command_line

    execute_from_command_line(['manage.py', 'migrate'])


from django.db.models import Q
from django.conf import settings
from django.core import serializers

from geonode.groups.models import GroupProfile
from django.contrib.auth.models import Group

from geonode.people.models import Profile
from allauth.socialaccount.models import SocialAccount

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%d-%b-%y %H:%M:%S') 
logger = logging.getLogger(__name__)

def get_token():
    url = f'{settings.KEYCLOAK_URL}/realms/master/protocol/openid-connect/token'
    if settings.KEYCLOAK_USER:
        rqdata = {
            'username': settings.KEYCLOAK_USER,
            'password': settings.KEYCLOAK_PASSWORD,
            'grant_type': 'password',
            'client_id': 'admin-cli'
        }
    else:
        rqdata = {
            'client_id': settings.KEYCLOAK_CLIENT,
            'client_secret': settings.KEYCLOAK_CLIENT_SECRET,
            'grant_type': settings.KEYCLOAK_GRANT_TYPE,
            'scope': settings.KEYCLOAK_SCOPE,
        }
    resp = requests.post(url=url, data=rqdata)
    data = resp.json()
    access_token = data.get('access_token', None)
    if not access_token:
        r = f'{resp.status_code}: {resp.text} for data {rqdata}'
        raise Exception(f'Access token not found in response: {r}')
    return access_token

def get_json(url):
    token = get_token()
    headers = {
        'Authorization': f'Bearer {token}',
    }
    resp = requests.get(url=url, headers=headers)
    return resp.json()

def get_users(max=5000):
    url = f'{settings.KEYCLOAK_URL}/admin/realms/{settings.KEYCLOAK_REALM}/users?max={max}'
    users = get_json(url)
    return users

def get_groups():
    url = f'{settings.KEYCLOAK_URL}/admin/realms/{settings.KEYCLOAK_REALM}/groups?max=5000'
    groups = get_json(url)
    return groups

def get_roles():
    url = f'{settings.KEYCLOAK_URL}/admin/realms/{settings.KEYCLOAK_REALM}/clients/{settings.KEYCLOAK_CLIENT}/roles'
    roles = get_json(url)
    return roles


def sync_users():
    kc_users = get_users()
    kc_accounts = [kcu for kcu in kc_users if kcu['enabled']]
    social_account_ids = [kcu['id'] for kcu in kc_accounts]
    
    existing_social_accounts = SocialAccount.objects.filter(provider='keycloak', uid__in=social_account_ids)
    existing_social_account_ids = [sa.uid for sa in existing_social_accounts]

    updated_profiles = []
    new_profiles = []
    new_social_accounts = []
    for kcu in kc_accounts:
        uid = kcu['id']
        username = kcu['username']
        email = kcu.get('email', '')
        firstName = kcu.get('firstName', '')
        lastName = kcu.get('lastName', '')
        groups = kcu.get('groups', [])
        if len(groups):
            logger.info(groups)

        profile = Profile.objects.filter(username=username).first()
        if profile:
            profile.email = email
            profile.first_name = firstName
            profile.last_name = lastName
            updated_profiles.append(profile)
        if uid not in existing_social_account_ids and not profile:
            profile = Profile(
                username=username,
                email=email,
                first_name=firstName,
                last_name=lastName
            )
            new_profiles.append(profile)
    
    deleted_social_accounts = SocialAccount.objects.filter(provider='keycloak').filter(~Q(uid__in=social_account_ids))
    deleted_profiles = Profile.objects.filter(username__in=[sa.user.username for sa in deleted_social_accounts])
  
    logging.info(f'Keycloak User Profile Bulk Create initiated')
    Profile.objects.bulk_create(new_profiles)

    for kcu in kc_accounts:
        uid = kcu['id']
        username = kcu['username']
        if uid not in existing_social_account_ids:
            profile = Profile.objects.filter(username=username).first()
            social_account = SocialAccount(
                uid=uid,
                provider='keycloak',
                user=profile
            )
            new_social_accounts.append(social_account)

    logging.info(f'Keycloak User SocialAccount Bulk Create initiated')
    SocialAccount.objects.bulk_create(new_social_accounts)

    logging.info(f'Keycloak User Profile Bulk Update initiated')
    Profile.objects.bulk_update(updated_profiles, ['email', 'first_name', 'last_name'])

    logging.info(f'Keycloak User SocialAccount Bulk Delete initiated')
    deleted_social_accounts.delete()
    logging.info(f'Keycloak User Profile Bulk Delete initiated')
    deleted_profiles.delete()

    logging.info(f'Keycloak User sync summary: {len(new_profiles)} New, {len(existing_social_account_ids)} Updated, {len(deleted_social_accounts)} Deleted')

    return {
        "profiles": {
            "new": new_profiles,
            "updated": updated_profiles,
            "deleted": deleted_profiles
        },
        "social_accounts": {
            "new": new_social_accounts,
            "deleted": deleted_social_accounts
        }
    }

def sync_groups():
    kc_groups = get_groups()
    kc_roles = []

    group_ids = [f"keycloak_{kcu['id']}" for kcu in kc_groups]

    GroupProfiles = GroupProfile.objects.filter(description__startswith='keycloak_')
    Groups = Group.objects.filter(name__startswith='keycloak_')
    
    existing_group_profiles = GroupProfiles.filter(description__in=group_ids)
    existing_group_profile_ids = [sa.description for sa in existing_group_profiles]

    updated_groups = []
    new_groups = []
    new_group_profiles = []
    for kcu in kc_groups:
        uid = f'keycloak_{kcu["id"]}'
        subgroups = kcu.get('subGroups', [])

        group = Groups.filter(name=uid).first()
        if not group:
            group = Group(
                name=uid
            )
            new_groups.append(group)
    
    delete_group_profiles = GroupProfiles.filter(~Q(description__in=group_ids))
    delete_groups = Groups.filter(~Q(name__in=group_ids))
  
    logging.info(f'Keycloak Group Bulk Create initiated')
    Group.objects.bulk_create(new_groups)

    for kcu in kc_groups:
        description = f'keycloak_{kcu["id"]}'
        title = kcu.get('path', kcu.get('name', ''))
        if description not in existing_group_profile_ids:
            group = Groups.filter(name=description).first()
            social_account = GroupProfile(
                title=title,
                slug=title,
                description=description,
                group=group
            )
            new_group_profiles.append(social_account)

    logging.info(f'Keycloak GroupProfile Bulk Create initiated')
    GroupProfile.objects.bulk_create(new_group_profiles)

    # logging.info(f'Keycloak User Group Bulk Update initiated')
    # Group.objects.bulk_update(updated_groups, ['name'])

    logging.info(f'Keycloak GroupProfile Bulk Delete initiated')
    delete_group_profiles.delete()
    logging.info(f'Keycloak Group Bulk Delete initiated')
    delete_groups.delete()

    logging.info(f'Keycloak Group sync summary: {len(new_groups)} New, {len(existing_group_profile_ids)} Updated, {len(delete_group_profiles)} Deleted')
    return {
        "group_profiles": {
            "new": new_group_profiles,
            "deleted": delete_group_profiles
        },
        "groups": {
            "new": new_groups,
            "deleted": delete_groups
        }
    }

def sync_all():
    group_summary = sync_groups()
    user_summary = sync_users()

    full_summary = {**group_summary, **user_summary}
    return full_summary

def summary_to_json(summary):
    simplified = {}
    for model_key in summary:
        simplified[model_key] = {}
        for crud_key in summary[model_key]:
            data_list = summary[model_key][crud_key]
            simplified[model_key][crud_key] = json.loads(serializers.serialize("json", data_list))
    return simplified

if __name__ == '__main__':
    summary = sync_all()
    summary_json = summary_to_json(summary)
    logger.info(summary_json)