#!/usr/bin/python3

import json
import unittest.mock as mock
from unittest.mock import Mock
from tests.helper import BaseTestCase
from searchguard.internalusers import modify_user
from searchguard.exceptions import ModifyUserException


class TestModifyUser(BaseTestCase):

    def setUp(self):
        self.user = "DummyUser"
        self.properties = {"hash": "$2a$1234", "roles": ["DummyRole"]}
        self.api_url = "fake_api_url/internalusers/"
        self.set_up_patch('searchguard.internalusers.SGAPI', "fake_api_url")

        self.mocked_requests_put = self.set_up_patch('searchguard.internalusers.requests.put')
        self.mocked_requests_put.return_value = Mock(status_code=200)
        self.mocked_check_user_exists = self.set_up_patch('searchguard.internalusers.check_user_exists')
        self.mocked_check_user_exists.return_value = True

    def test_modify_user_returns_when_successfully_modified_user(self):
        self.assertIsNone(modify_user(self.user, self.properties))

    def test_modify_user_returns_exception_when_user_does_not_exist(self):
        self.mocked_check_user_exists.return_value = False

        with self.assertRaises(ModifyUserException):
            modify_user(self.user, self.properties)

    def test_modify_user_returns_exception_when_requests_return_code_not_200(self):
        self.mocked_requests_put.return_value = Mock(status_code=999)

        with self.assertRaises(ModifyUserException):
            modify_user(self.user, self.properties)

    def test_modify_user_calls_check_user_exist(self):
        modify_user(self.user, self.properties)
        self.mocked_check_user_exists.assert_called_once_with(self.user)

    def test_modify_user_calls_requests_with_correct_arguments(self):
        modify_user(self.user, self.properties)
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.user),
                                                         auth=(mock.ANY, mock.ANY),
                                                         data=json.dumps(self.properties),
                                                         headers={'content-type': 'application/json'})

    def test_modify_user_returns_error_when_properties_argument_missing(self):
        with self.assertRaises(TypeError):
            modify_user(self.user)
