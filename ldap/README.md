# Geonode auth via LDAP

This package provides utilities for using LDAP as an authentication and 
authorization backend for geonode.

The [django_auth_ldap][1] package is a very capable way to add LDAP integration 
with django projects. It provides a lot of flexibility in mapping LDAP users to 
geonode users and is able to manage user authentication.

However, in order to provide full support for mapping LDAP groups with 
geonode's and enforce group permissions on resources, a custom geonode 
authentication backend  is required. This contrib package provides such a 
backend, based on django_auth_ldap.


## Installation


Installing this contrib package is a matter of:

1. [Installing geonode](http://geonode.org/#install)
2. Installing system LDAP libraries (development packages needed)
3. Cloning this repository locally
4. Change to the `ldap` directory and install this contrib package

```sh
# 1. install geonode (not shwn here for brevity)
# 2. install systemwide LDAP libraries
sudo apt install \
    libldap2-dev \
    libsasl2-dev
    
# 3. get geonode/contribs code
git clone https://github.com/GeoNode/geonode-contribs.git

# 4. install geonode ldap contrib package
cd geonode-contribs/ldap
pip install .
```


## Configuration

1. Add `geonode_ldap.backend.GeonodeLdapBackend` as an additional auth
   backend (see example configuration below).

   You may use additional auth backends, the django authentication framework
   tries them all according to the order listed in the settings. This means that
   geonode can be setup in such a way as to permit internal organization users
   to login with their LDAP credentials, while at the same time allowing for
   casual users to use their facebook login (as long as you enable facebook
   social auth provider).

   Note that django's `django.contrib.auth.backends.ModelBackend` must also
   be used in order to provide full geonode integration with LDAP.

2. Set some additional configuration values. Some of these variables are
   prefixed with `AUTH_LDAP` (these are used directly by `django_auth_ldap`)
   while others are prefixed with `GEONODE_LDAP` (these are used by
   `geonode_ldap`). The geonode custom variables are:

   * `GEONODE_LDAP_GROUP_PROFILE_FILTERSTR` - This is an LDAP search fragment
     with the filter that allows querying for existing groups. See example below

   * `GEONODE_LDAP_GROUP_NAME_ATTRIBUTE` - This is the name of the LDAP
     attribute that will be used for deriving the geonode group name. If not
     specified it will default to `cn`, which means that the LDAP object's
     `common name` will be used for generating the name of the geonode group

   * `GEONODE_LDAP_GROUP_PROFILE_MEMBER_ATTR` - This is the name of the LDAP
     attribute that will be used for deriving the geonode membership. If not
     specified it will default to `member`


Example configuration:

```python
# add these import lines to the top of your geonode settings file
from django_auth_ldap import config as ldap_config
from geonode_ldap.config import GeonodeNestedGroupOfNamesType
import ldap

# add both standard ModelBackend auth and geonode.contrib.ldap auth
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'geonode_ldap.backend.GeonodeLdapBackend',
)

# django_auth_ldap configuration
AUTH_LDAP_SERVER_URI = 'ldap://example.com'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=com'
AUTH_LDAP_BIND_PASSWORD = 'something-secret'
AUTH_LDAP_USER_SEARCH = ldap_config.LDAPSearch(
    'ou=people,dc=example,dc=com',
    ldap.SCOPE_SUBTREE,
    '(cn=%(user)s)'
)
AUTH_LDAP_GROUP_SEARCH = ldap_config.LDAPSearch(
    'ou=groups,dc=example,dc=com',
    ldap.SCOPE_SUBTREE,
)
AUTH_LDAP_GROUP_TYPE = GeonodeNestedGroupOfNamesType()
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'cn',
    'last_name': 'sn'
}
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_MIRROR_GROUPS_EXCEPT = [
    'test_group'
]

# geonode.contrib.ldap configuration
GEONODE_LDAP_GROUP_NAME_ATTRIBUTE = 'cn'
GEONODE_LDAP_GROUP_PROFILE_FILTERSTR = '(ou=research group)'
GEONODE_LDAP_GROUP_PROFILE_MEMBER_ATTR = 'uniqueMember'
```

The configuration seen in the example above will allow LDAP users to login to
geonode with their LDAP credentials.

On first login, a geonode user is created from the LDAP user and its LDAP
attributes `cn` and `sn` are used to populate the geonode user's
`first_name` and `last_name` profile fields.

Any groups that the user is a member of in LDAP (under the
`ou=groups,dc=example,dc=com` search base and with an
`(ou=research group)` attribute) will be mapped to the corresponding
geonode groups, even creating these groups in geonode in case they do not
exist yet. The geonode user is also made a member of these geonode groups.

Upon each login, the user's geonode group memberships are re-evaluated
according to the information extracted from LDAP. The
`AUTH_LDAP_MIRROR_GROUPS_EXCEPT` setting can be used to specify groups
whose memberships will not be re-evaluated.

You may also manually generate the geonode groups in advance, before users
login. In this case, when a user logs in and the mapped LDAP group already
exists, the user is merely added to the geonode group

Be sure to check out [django_auth_ldap][1] for more information on the various
configuration options.


[1]: https://django-auth-ldap.readthedocs.io/en/latest/
