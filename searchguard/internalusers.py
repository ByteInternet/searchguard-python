#!/usr/bin/python3

import requests
import warnings
import json
import random
import string
from searchguard.exceptions import *
from searchguard.settings import HEADER, SGAPI, TOKEN


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


def create_user(username):
    """Creates a new Search Guard user and returns the generated password

    :param str username: the username
    :raises: UserAlreadyExistsException, CreateUserException
    """
    if check_user_exists(username):
        raise UserAlreadyExistsException('User {} already exists'.format(username))

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


def modify_user(user, properties):
    """Modifies a Search Guard user. Returns when successfully modified"""
    if check_user_exists(user):
        # The user does exist, let's modify it
        modify_sg_user = requests.put('{}/internalusers/{}'.format(SGAPI, user),
                                      data=json.dumps(properties), headers=HEADER, auth=TOKEN)

        if modify_sg_user.status_code == 200:
            # User modified successfully
            return
        else:
            # Raise exception because we received an error when modifying the user
            raise ModifyUserException('Error modifying user {} - msg: {}'.format(user, modify_sg_user.text))
    else:
        # Raise exception because the user does not exist
        raise ModifyUserException('User {} does not exist'.format(user))


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


def view_user(user):
    """Returns information about a Search Guard user (when the user exists)
    The returned information contains the password hash and if present an array of the user's backend roles.
    :param str user: Name of the user to view in Search Guard
    """
    if check_user_exists(user):
        # The user does exist, let's view it
        view_sg_user = requests.get('{}/internalusers/{}'.format(SGAPI, user), auth=TOKEN)

        if view_sg_user.status_code == 200:
            return view_sg_user.text
        else:
            # Raise exception because we could not view the user
            raise ViewUserException('Error viewing the user {} - msg {}'.format(user, view_sg_user.text))
    else:
        # Raise exception because the user does not exist
        raise ViewUserException('Error viewing the user {}, does not exist'.format(user))


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
