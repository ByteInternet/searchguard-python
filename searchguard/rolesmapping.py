#!/usr/bin/python3

import requests
import json
import searchguard.settings as settings
from searchguard.exceptions import RoleMappingException, CheckRoleMappingExistsException, ViewRoleMappingException, \
    DeleteRoleMappingException, CreateRoleMappingException, ModifyRoleMappingException, CheckRoleExistsException
from searchguard.roles import check_role_exists


PROPERTIES_KEYS = {"users", "backendroles", "hosts"}


def _send_api_request(role, properties):
    """Private function to process API calls for the rolemapping module"""
    create_sg_rolemapping = requests.put('{}/rolesmapping/{}'.format(settings.SEARCHGUARD_API_URL, role),
                                         data=json.dumps(properties),
                                         headers=settings.HEADER,
                                         auth=settings.SEARCHGUARD_API_AUTH)

    if create_sg_rolemapping.status_code in (200, 201):
        # Role mapping created or updated successfully
        return

    # Error when creating/updating the role mapping
    raise RoleMappingException('Error creating/updating the mapping for role {} - msg {}'.format(
        role, create_sg_rolemapping.text))


def check_rolemapping_exists(role):
    """Returns True of False depending on whether the requested role mapping exists in Search Guard"""
    rolemapping_exists_check = requests.get('{}/rolesmapping/{}'.format(settings.SEARCHGUARD_API_URL, role),
                                            auth=settings.SEARCHGUARD_API_AUTH)

    if rolemapping_exists_check.status_code == 200:
        # Role mapping exists in SearchGuard
        return True
    elif rolemapping_exists_check.status_code == 404:
        # Role mapping does not exist in SearchGuard
        return False
    else:
        # Could not fetch valid output
        raise CheckRoleMappingExistsException('Unknown error checking whether role mapping for {} exists'.format(role))


def view_rolemapping(role):
    """Returns the properties for the requested role mapping if it exists"""
    view_sg_rolemapping = requests.get('{}/rolesmapping/{}'.format(settings.SEARCHGUARD_API_URL, role),
                                       auth=settings.SEARCHGUARD_API_AUTH)

    if view_sg_rolemapping.status_code == 200:
        return json.loads(view_sg_rolemapping.text)
    elif view_sg_rolemapping.status_code == 404:
        # Raise exception because the role mapping does not exist
        raise ViewRoleMappingException('Error viewing the role mapping for {}, does not exist'.format(role))
    else:
        # Could not fetch valid output
        raise ViewRoleMappingException('Unknown error checking whether role mapping for {} exists'.format(role))


def delete_rolemapping(role):
    """Deletes a Search Guard role mapping. Returns when successfully deleted"""
    if check_rolemapping_exists(role):
        # The role mapping does exist, let's delete it
        delete_sg_rolemapping = requests.delete('{}/rolesmapping/{}'.format(settings.SEARCHGUARD_API_URL, role),
                                                auth=settings.SEARCHGUARD_API_AUTH)

        if delete_sg_rolemapping.status_code == 200:
            # Role mapping deleted successfully
            return
        else:
            # Raise exception because we could not delete the role mapping
            raise DeleteRoleMappingException('Error deleting the role mapping for role {} '
                                             '- msg: {}'.format(role, delete_sg_rolemapping.text))
    else:
        # Raise exception because the role mapping does not exist
        raise DeleteRoleMappingException('Error deleting the role mapping for role {}, does not exist'.format(role))


def create_rolemapping(role, properties):
    """Creates a Search Guard role mapping. Returns when successfully created
    It is required to specify at least one of: users, backendroles or hosts in the properties argument.
    We do not use the PATCH endpoint for backwards compatibility with Elasticsearch before 6.4.0

    :param str role: Name of the role mapping to create in Search Guard
    :param dict properties: Search Guard role mapping fields (users, backendroles and/or hosts)
    :raises: CreateRoleMappingException, CheckRoleExistsException
    """
    if not check_role_exists(role):
        raise CheckRoleExistsException('Role {} does not exist'.format(role))

    if not any(key in properties for key in PROPERTIES_KEYS):
        # Raise exception because we did not receive valid properties
        raise CreateRoleMappingException('Error creating mapping for role {} - Include at least one of: users, '
                                         'backendroles or hosts keys in the properties argument'.format(role))

    _send_api_request(role, properties)
    return


def modify_rolemapping(role, properties, action="replace"):
    """Modifies a Search Guard role mapping. Returns when successfully modified
    It is required to specify at least one of: users, backendroles or hosts in the properties argument.
    We do not use the PATCH endpoint for backwards compatibility with Elasticsearch before 6.4.0

    :param str role: Name of the role mapping to create in Search Guard
    :param dict properties: Search Guard role mapping fields (users, backendroles and/or hosts)
    :param boolean action: Defines what to do with the properties. Defaults to replace (overwrites existing
    properties). Other options are merge (combine the properties with existing ones) or split
    (removes the properties from existing ones)
    :raises: ModifyRoleMappingException
    """
    if not check_rolemapping_exists(role):
        raise ModifyRoleMappingException('Mapping for role {} does not exist'.format(role))

    if not any(key in properties for key in PROPERTIES_KEYS):
        # Raise exception because we did not receive valid properties
        raise ValueError('Error modifying mapping for role {} - Include at least one of: users, '
                         'backendroles or hosts keys in the properties argument'.format(role))

    # Retrieve existing properties of the role mapping:
    rolemapping = view_rolemapping(role)
    for property in PROPERTIES_KEYS:
        if property not in rolemapping[role]:
            rolemapping[role][property] = list()

    if action is "merge":
        # Merge the requested properties with existing properties in the role mapping.

        rolemapping[role]['users'] = \
            sorted(set(rolemapping[role]['users'] + properties.get('users', [])))
        rolemapping[role]['backendroles'] = \
            sorted(set(rolemapping[role]['backendroles'] + properties.get('backendroles', [])))
        rolemapping[role]['hosts'] = \
            sorted(set(rolemapping[role]['hosts'] + properties.get('hosts', [])))

        _send_api_request(role, rolemapping[role])
        return

    if action is "split":
        # Remove the requested properties from existing properties in the role mapping.

        rolemapping[role]['users'] = [item for item in rolemapping[role]['users']
                                      if item not in properties['users']]
        rolemapping[role]['backendroles'] = [item for item in rolemapping[role]['backendroles']
                                             if item not in properties['backendroles']]
        rolemapping[role]['hosts'] = [item for item in rolemapping[role]['hosts']
                                      if item not in properties['hosts']]

        _send_api_request(role, rolemapping[role])
        return

    # No merge or split action, overwrite existing properties:
    _send_api_request(role, properties)
