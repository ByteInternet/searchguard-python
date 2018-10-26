#!/usr/bin/python3

import requests
import warnings
import json
import random
import string
import os
from searchguard.exceptions import *

warnings.filterwarnings("ignore")

HEADER = {'content-type': 'application/json'}
SGAPI = os.environ['SEARCHGUARD_API_URL']
TOKEN = (os.environ['SEARCHGUARD_API_USER'], os.environ['SEARCHGUARD_API_PASS'])


def password_generator(size=25, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    """Returns a random 25 character password"""
    return ''.join(random.choice(chars) for _ in range(size))


def check_user_exists(username):
    """Returns True of False depending on whether the requested user exists in Search Guard"""
    user_exists_check = requests.get('{}/internalusers/{}'.format(SGAPI, username), auth=TOKEN)

    if user_exists_check.status_code == 200:
        # Username exists in SearchGuard
        return True
    elif user_exists_check.status_code == 404:
        # Username does not exist in SearchGuard
        return False
    else:
        # Could not fetch valid output
        raise CheckUserExistsException('Unknown error checking whether user {} exists'.format(username))


def check_role_exists(role):
    """Returns True of False depending on whether the requested role exists in Search Guard"""
    role_exists_check = requests.get('{}/roles/{}'.format(SGAPI, role), auth=TOKEN)

    if role_exists_check.status_code == 200:
        # Role exists in SearchGuard
        return True
    elif role_exists_check.status_code == 404:
        # Role does not exist in SearchGuard
        return False
    else:
        # Could not fetch valid output
        raise CheckRoleExistsException('Unknown error checking whether role{} exists'.format(role))


def create_user(username):
    """Creates a new Search Guard user and returns the generated password"""
    if check_user_exists(username):
        # Raise exception because the user already exists
        raise CreateUserException('User {} already exists'.format(username))

    # The username does not exist, let's create it
    password = password_generator()
    payload = {'password': password}
    create_sg_user = requests.put('{}/internalusers/{}'.format(SGAPI, username),
                                  data=json.dumps(payload), headers=HEADER, auth=TOKEN)

    if create_sg_user.status_code == 201:
        # User created successfully
        return password
    else:
        # Raise exception because we received an error when creating the user
        raise CreateUserException('Error creating user {} - msg: {}'.format(username, create_sg_user.text))


def delete_user(username):
    """Deletes a Search Guard user. Returns when successfully deleted"""
    if not check_user_exists(username):
        # Raise exception because the user does not exist
        raise DeleteUserException('Error deleting the user {}, does not exist'.format(username))

    # The user does exist, let's delete it
    delete_sg_user = requests.delete('{}/internalusers/{}'.format(SGAPI, username), auth=TOKEN)

    if delete_sg_user.status_code != 200:
        # Raise exception because we could not delete the user
        raise DeleteUserException('Error deleting the user {} - msg: {}'.format(username, delete_sg_user.text))


def create_role(role, permissions=None):
    """Creates a Search Guard role. Returns when successfully created
    When no permissions are specified, we use some default cluster permissions.
    :param str role: Name of the role to create in Search Guard
    :param dict permissions: Search Guard role permissions (default is read access to cluster)
    """
    if not check_role_exists(role):
        # The role does not exist, let's create it
        # When no permissions are requested, we only add basic cluster perms, no indice perms.
        payload = {'cluster': ["indices:data/read/mget", "indices:data/read/msearch"]}
        if permissions:
            payload = permissions
        create_sg_role = requests.put('{}/roles/{}'.format(SGAPI, role),
                                      data=json.dumps(payload), headers=HEADER, auth=TOKEN)

        if create_sg_role.status_code == 201:
            # Role created successfully
            return
        else:
            # Raise exception because we received an error when creating the role
            raise CreateRoleException('Error creating role {} - msg: {}'.format(role, create_sg_role.text))
    else:
        # Raise exception because the role already exists
        raise CreateRoleException('Role {} already exists'.format(role))


def modify_role(role, permissions):
    """Modifies a Search Guard role. Returns when successfully modified"""
    if check_role_exists(role):
        # The role does exist, let's modify it
        modify_sg_role = requests.put('{}/roles/{}'.format(SGAPI, role),
                                      data=json.dumps(permissions), headers=HEADER, auth=TOKEN)

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
        delete_sg_role = requests.delete('{}/roles/{}'.format(SGAPI, role), auth=TOKEN)

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
        view_sg_role = requests.get('{}/roles/{}'.format(SGAPI, role), auth=TOKEN)

        if view_sg_role.status_code == 200:
            return view_sg_role.text
        else:
            # Raise exception because we could not view the role
            raise ViewRoleException('Error viewing the role {} - msg {}'.format(role, view_sg_role.text))
    else:
        # Raise exception because the role does not exist
        raise ViewRoleException('Error viewing the role {}, does not exist'.format(role))


def list_users(prefix=None, search=None):
    """Returns the existing Search Guard users that match the filter criteria
    When no filters are specified, all users are returned.
    :param str prefix: Return only users that match this prefix (underscore is used as delimiter)
    :param str search: Return only users that contain this search string
    """
    response = requests.get('{}/internalusers/'.format(SGAPI), auth=TOKEN)

    if response.status_code == 200:
        list_sg_users = json.loads(response.text)
        # The API returned a list of existing users
        if prefix and search:
            # Return list of users filtered on prefix and search string
            return {k: v for (k, v) in list_sg_users.items() if k.split('_')[0] == prefix and search in k}
        if prefix:
            # Return list of users filtered on prefix
            return {k: v for (k, v) in list_sg_users.items() if k.split('_')[0] == prefix}
        if search:
            # Return list of users filtered on search string
            return {k: v for (k, v) in list_sg_users.items() if search in k}

        # Return all existing users (unfiltered)
        return list_sg_users
    else:
        # Raise exception because the API did not return code 200
        raise ListUsersException('Error listing users. status: {} - body: {}'.format(response.status_code, response.text))
