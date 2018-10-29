#!/usr/bin/python3

import unittest.mock as mock
from unittest.mock import Mock
from tests.helper import BaseTestCase
from searchguard.roles import delete_role
from searchguard.exceptions import DeleteRoleException


class TestDeleteRole(BaseTestCase):

    def setUp(self):
        self.role = "DummyRole"
        self.api_url = "fake_api_url/roles/"
        self.set_up_patch('searchguard.roles.SGAPI', "fake_api_url")

        self.mocked_requests_delete = self.set_up_patch('searchguard.roles.requests.delete')
        self.mocked_requests_delete.return_value = Mock(status_code=200)
        self.mocked_check_role_exists = self.set_up_patch('searchguard.roles.check_role_exists')
        self.mocked_check_role_exists.return_value = True

    def test_delete_role_returns_when_successfully_deleted_role(self):
        self.assertIsNone(delete_role(self.role))

    def test_delete_role_returns_exception_when_user_does_not_exist(self):
        self.mocked_check_role_exists.return_value = False

        with self.assertRaises(DeleteRoleException):
            delete_role(self.role)

    def test_delete_role_returns_exception_when_requests_return_code_not_200(self):
        self.mocked_requests_delete.return_value = Mock(status_code=999)

        with self.assertRaises(DeleteRoleException):
            delete_role(self.role)

    def test_delete_role_calls_check_role_exist(self):
        delete_role(self.role)
        self.mocked_check_role_exists.assert_called_once_with(self.role)

    def test_delete_role_calls_requests_with_correct_arguments(self):
        delete_role(self.role)
        self.mocked_requests_delete.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                            auth=(mock.ANY, mock.ANY))
