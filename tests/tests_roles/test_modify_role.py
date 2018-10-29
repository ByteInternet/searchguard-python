#!/usr/bin/python3

import json
import unittest.mock as mock
from unittest.mock import Mock
from tests.helper import BaseTestCase
from searchguard.roles import modify_role
from searchguard.exceptions import ModifyRoleException


class TestModifyRole(BaseTestCase):

    def setUp(self):
        self.role = "DummyRole"
        self.permissions = {"cluster": ["dummyperm"], "indices": {"dummyindice": {"dummytype": ["READ"]}}}
        self.api_url = "fake_api_url/roles/"
        self.set_up_patch('searchguard.roles.SGAPI', "fake_api_url")

        self.mocked_requests_put = self.set_up_patch('searchguard.roles.requests.put')
        self.mocked_requests_put.return_value = Mock(status_code=200)
        self.mocked_check_role_exists = self.set_up_patch('searchguard.roles.check_role_exists')
        self.mocked_check_role_exists.return_value = True

    def test_modify_role_returns_when_successfully_modified_role(self):
        self.assertIsNone(modify_role(self.role, self.permissions))

    def test_modify_role_returns_exception_when_role_does_not_exist(self):
        self.mocked_check_role_exists.return_value = False

        with self.assertRaises(ModifyRoleException):
            modify_role(self.role, self.permissions)

    def test_modify_role_returns_exception_when_requests_return_code_not_200(self):
        self.mocked_requests_put.return_value = Mock(status_code=999)

        with self.assertRaises(ModifyRoleException):
            modify_role(self.role, self.permissions)

    def test_modify_role_calls_check_role_exist(self):
        modify_role(self.role, self.permissions)
        self.mocked_check_role_exists.assert_called_once_with(self.role)

    def test_modify_role_calls_requests_with_correct_arguments(self):
        modify_role(self.role, self.permissions)
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                         auth=(mock.ANY, mock.ANY),
                                                         data=json.dumps(self.permissions),
                                                         headers={'content-type': 'application/json'})

    def test_modify_role_returns_error_when_permissions_argument_missing(self):
        with self.assertRaises(TypeError):
            modify_role(self.role)
