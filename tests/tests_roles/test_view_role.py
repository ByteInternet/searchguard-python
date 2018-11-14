#!/usr/bin/python3

import mock as mock
from mock import Mock
from searchguard.roles import view_role
from searchguard.exceptions import ViewRoleException
from tests.helper import BaseTestCase


class TestViewRole(BaseTestCase):

    def setUp(self):
        self.role = "DummyRole"
        self.permissions = {"cluster": ["dummyperm"], "indices": {"dummyindice": {"dummytype": ["READ"]}}}
        self.api_url = "fake_api_url/roles/"
        self.set_up_patch('searchguard.roles.SGAPI', "fake_api_url")

        self.mocked_requests_get = self.set_up_patch('searchguard.roles.requests.get')
        self.mocked_requests_get.return_value = Mock(status_code=200)
        self.mocked_check_role_exists = self.set_up_patch('searchguard.roles.check_role_exists')
        self.mocked_check_role_exists.return_value = True

    def test_view_role_returns_role_information_when_correctly_called(self):
        self.mocked_requests_get.return_value = Mock(status_code=200, text=self.permissions)

        ret = view_role(self.role)
        assert ret == self.permissions

    def test_view_role_returns_exception_when_role_does_not_exist(self):
        self.mocked_check_role_exists.return_value = False

        with self.assertRaises(ViewRoleException):
            view_role(self.role)

    def test_view_role_returns_exception_when_requests_return_code_not_200(self):
        self.mocked_requests_get.return_value = Mock(status_code=999)

        with self.assertRaises(ViewRoleException):
            view_role(self.role)

    def test_view_role_calls_check_role_exist(self):
        view_role(self.role)
        self.mocked_check_role_exists.assert_called_once_with(self.role)

    def test_view_role_calls_requests_with_correct_arguments(self):
        view_role(self.role)
        self.mocked_requests_get.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                         auth=(mock.ANY, mock.ANY))
