#!/usr/bin/python3

import requests
import json
import searchguard.settings as settings
from searchguard.exceptions import *
from searchguard.roles import check_role_exists


def __process_data(role, properties):
    """Private function to process API calls for the rolemapping module"""
    create_sg_rolemapping = requests.put('{}/rolesmapping/{}'.format(settings.SEARCHGUARD_API_URL, role),
                                         data=json.dumps(properties),
                                         headers=settings.HEADER,
                                         auth=settings.SEARCHGUARD_API_AUTH)

    if create_sg_rolemapping.status_code == 201 or create_sg_rolemapping.status_code == 200:
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
    if check_rolemapping_exists(role):
        # The role mapping does exist, let's view it
        view_sg_rolemapping = requests.get('{}/rolesmapping/{}'.format(settings.SEARCHGUARD_API_URL, role),
                                           auth=settings.SEARCHGUARD_API_AUTH)

        if view_sg_rolemapping.status_code == 200:
            return json.loads(view_sg_rolemapping.text)
        else:
            # Raise exception because we could not view the role mapping
            raise ViewRoleMappingException('Error viewing the role mapping for {} - msg {}'.format(
                role, view_sg_rolemapping.text))
    else:
        # Raise exception because the role mapping does not exist
        raise ViewRoleMappingException('Error viewing the role mapping for {}, does not exist'.format(role))


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

    properties_keys = {"users", "backendroles", "hosts"}

    if not any(key in properties for key in properties_keys):
        # Raise exception because we did not receive valid properties
        raise CreateRoleMappingException('Error creating mapping for role {} - Include at least one of: users, '
                                         'backendroles or hosts keys in the properties argument'.format(role))

    __process_data(role, properties)
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

    properties_keys = {"users", "backendroles", "hosts"}

    if not any(key in properties for key in properties_keys):
        # Raise exception because we did not receive valid properties
        raise ModifyRoleMappingException('Error modifying mapping for role {} - Include at least one of: users, '
                                         'backendroles or hosts keys in the properties argument'.format(role))

    # Retrieve existing properties of the role mapping:
    rolemapping = view_rolemapping(role)
    for property in properties_keys:
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

        __process_data(role, rolemapping[role])
        return

    if action is "split":
        # Remove the requested properties from existing properties in the role mapping.

        rolemapping[role]['users'] = [item for item in rolemapping[role]['users']
                                      if item not in properties['users']]
        rolemapping[role]['backendroles'] = [item for item in rolemapping[role]['backendroles']
                                             if item not in properties['backendroles']]
        rolemapping[role]['hosts'] = [item for item in rolemapping[role]['hosts']
                                      if item not in properties['hosts']]

        __process_data(role, rolemapping[role])
        return

    # No merge or split action, overwrite existing properties:
    __process_data(role, properties)
