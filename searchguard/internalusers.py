#!/usr/bin/python3

import requests
import warnings
import json
import random
import string
import searchguard.settings as settings
from searchguard.exceptions import *


def password_generator(size=25, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    """Returns a random 25 character password"""
    return ''.join(random.choice(chars) for _ in range(size))


def check_user_exists(username):
    """Returns True of False depending on whether the requested user exists in Search Guard"""
    user_exists_check = requests.get('{}/internalusers/{}'.format(settings.SEARCHGUARD_API_URL, username), auth=settings.SEARCHGUARD_API_AUTH)

    if user_exists_check.status_code == 200:
        # Username exists in SearchGuard
        return True
    elif user_exists_check.status_code == 404:
        # Username does not exist in SearchGuard
        return False
    else:
        # Could not fetch valid output
        raise CheckUserExistsException('Unknown error checking whether user {} exists'.format(username))


def create_user(username, password=None, properties=None):
    """Creates a new Search Guard user and returns the generated password

    :param str username: the username
    :param str password: the password (by default will generate a password)
    :param dict properties: dict of user properties (roles, attributes, hash, etc), matching
    the API request body. Following the API, if "hash" is specified the password
    won't be used, then the return value is empty string.
    If password is passed both explicitly and as a property,
    mismatching passwords would raise a ValueError.

    :raises: UserAlreadyExistsException, CreateUserException, ValueError
    :return str: password, or if hash is used empty string
    """
    if check_user_exists(username):
        raise UserAlreadyExistsException('User {} already exists'.format(username))

    # The username does not exist, let's create it
    if not properties:
        properties = dict()

    if 'password' in properties and password and (password != properties['password']):
        raise ValueError("Password argument is different than 'password' property")

    # decide returned password value and request body password according to arguments
    if 'hash' in properties:
        password = ''  # password is not effective, return empty string
    elif 'password' in properties:
        password = properties['password']  # return the effective password
    else:
        password = password or password_generator()
        properties['password'] = password

    create_sg_user = requests.put('{}/internalusers/{}'.format(settings.SEARCHGUARD_API_URL, username),
                                  data=json.dumps(properties), headers=settings.HEADER, auth=settings.SEARCHGUARD_API_AUTH)

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
        modify_sg_user = requests.put('{}/internalusers/{}'.format(settings.SEARCHGUARD_API_URL, user),
                                      data=json.dumps(properties), headers=settings.HEADER, auth=settings.SEARCHGUARD_API_AUTH)

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
    delete_sg_user = requests.delete('{}/internalusers/{}'.format(settings.SEARCHGUARD_API_URL, username), auth=settings.SEARCHGUARD_API_AUTH)

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
        view_sg_user = requests.get('{}/internalusers/{}'.format(settings.SEARCHGUARD_API_URL, user), auth=settings.SEARCHGUARD_API_AUTH)

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
    response = requests.get('{}/internalusers/'.format(settings.SEARCHGUARD_API_URL), auth=settings.SEARCHGUARD_API_AUTH)

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
