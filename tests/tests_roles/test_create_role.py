#!/usr/bin/python3

import json
import unittest.mock as mock
from tests.helper import BaseTestCase
from unittest.mock import Mock
from searchguard.roles import create_role
from searchguard.exceptions import CreateRoleException


class TestCreateRole(BaseTestCase):

    def setUp(self):
        self.role = "DummyRole"
        self.permissions = {"cluster": ["dummyperm"], "indices": {"dummyindice": {"dummytype": ["READ"]}}}
        self.defaultperms = {"cluster": ["indices:data/read/mget", "indices:data/read/msearch"]}
        self.api_url = "fake_api_url/roles/"
        self.set_up_patch('searchguard.roles.SGAPI', "fake_api_url")

        self.mocked_requests_put = self.set_up_patch('searchguard.roles.requests.put')
        self.mocked_requests_put.return_value = Mock(status_code=201)
        self.mocked_check_role_exists = self.set_up_patch('searchguard.roles.check_role_exists')
        self.mocked_check_role_exists.return_value = False

    def test_create_role_returns_when_successfully_created_role(self):
        self.assertIsNone(create_role(self.role, self.permissions))

    def test_create_role_returns_exception_when_role_already_exists(self):
        self.mocked_check_role_exists.return_value = True

        with self.assertRaises(CreateRoleException):
            create_role(self.role, self.permissions)

    def test_create_role_returns_exception_when_requests_return_code_not_201(self):
        self.mocked_requests_put.return_value = Mock(status_code=999)

        with self.assertRaises(CreateRoleException):
            create_role(self.role, self.permissions)

    def test_create_role_calls_check_role_exist(self):
        create_role(self.role)
        self.mocked_check_role_exists.assert_called_once_with(self.role)

    def test_create_role_wo_perms_calls_requests_put_with_correct_arguments(self):
        create_role(self.role)
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                         auth=(mock.ANY, mock.ANY),
                                                         data=json.dumps(self.defaultperms),
                                                         headers={'content-type': 'application/json'})

    def test_create_role_with_perms_calls_requests_put_with_correct_arguments(self):
        create_role(self.role, self.permissions)
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                         auth=(mock.ANY, mock.ANY),
                                                         data=json.dumps(self.permissions),
                                                         headers={'content-type': 'application/json'})
