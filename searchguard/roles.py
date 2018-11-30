#!/usr/bin/python3

import requests
import warnings
import json
from searchguard.exceptions import *
import searchguard.settings as settings


def check_role_exists(role):
    """Returns True of False depending on whether the requested role exists in Search Guard"""
    role_exists_check = requests.get('{}/roles/{}'.format(settings.SEARCHGUARD_API_URL, role), auth=settings.SEARCHGUARD_API_AUTH)

    if role_exists_check.status_code == 200:
        # Role exists in SearchGuard
        return True
    elif role_exists_check.status_code == 404:
        # Role does not exist in SearchGuard
        return False
    else:
        # Could not fetch valid output
        raise CheckRoleExistsException('Unknown error checking whether role{} exists'.format(role))


def create_role(role, permissions=None):
    """Creates a Search Guard role. Returns when successfully created
    When no permissions are specified, we use some default cluster permissions.

    :param str role: Name of the role to create in Search Guard
    :param dict permissions: Search Guard role permissions (default is read access to cluster)
    :raises: RoleAlreadyExistsException, CreateRoleException
    """
    if not check_role_exists(role):
        # The role does not exist, let's create it
        # When no permissions are requested, we only add basic cluster perms, no indice perms.
        payload = {'cluster': ["indices:data/read/mget", "indices:data/read/msearch"]}
        if permissions:
            payload = permissions
        create_sg_role = requests.put('{}/roles/{}'.format(settings.SEARCHGUARD_API_URL, role),
                                      data=json.dumps(payload), headers=settings.HEADER, auth=settings.SEARCHGUARD_API_AUTH)

        if create_sg_role.status_code == 201:
            # Role created successfully
            return
        else:
            # Raise exception because we received an error when creating the role
            raise CreateRoleException('Error creating role {} - msg: {}'.format(role, create_sg_role.text))
    else:
        raise RoleAlreadyExistsException('Role {} already exists'.format(role))


def modify_role(role, permissions):
    """Modifies a Search Guard role. Returns when successfully modified"""
    if check_role_exists(role):
        # The role does exist, let's modify it
        modify_sg_role = requests.put('{}/roles/{}'.format(settings.SEARCHGUARD_API_URL, role),
                                      data=json.dumps(permissions), headers=settings.HEADER, auth=settings.SEARCHGUARD_API_AUTH)

        if modify_sg_role.status_code == 200:
            # Role modified successfully
            return
        else:
            # Raise exception because we received an error when modifying the role
            raise ModifyRoleException('Error modifying role {} - msg: {}'.format(role, modify_sg_role.text))
    else:
        # Raise exception because the role does not exist
        raise ModifyRoleException('Role {} does not exist'.format(role))


def delete_role(role):
    """Deletes a Search Guard roles. Returns when successfully deleted"""
    if check_role_exists(role):
        # The role does exist, let's delete it
        delete_sg_role = requests.delete('{}/roles/{}'.format(settings.SEARCHGUARD_API_URL, role), auth=settings.SEARCHGUARD_API_AUTH)

        if delete_sg_role.status_code == 200:
            # Role deleted successfully
            return
        else:
            # Raise exception because we could not delete the role
            raise DeleteRoleException('Error deleting the role {} - msg: {}'.format(role, delete_sg_role.text))
    else:
        # Raise exception because the role does not exist
        raise DeleteRoleException('Error deleting the role {}, does not exist'.format(role))


def view_role(role):
    """Returns the permissions for the requested role if it exists"""
    if check_role_exists(role):
        # The role does exist, let's view it
        view_sg_role = requests.get('{}/roles/{}'.format(settings.SEARCHGUARD_API_URL, role), auth=settings.SEARCHGUARD_API_AUTH)

        if view_sg_role.status_code == 200:
            return view_sg_role.text
        else:
            # Raise exception because we could not view the role
            raise ViewRoleException('Error viewing the role {} - msg {}'.format(role, view_sg_role.text))
    else:
        # Raise exception because the role does not exist
        raise ViewRoleException('Error viewing the role {}, does not exist'.format(role))
