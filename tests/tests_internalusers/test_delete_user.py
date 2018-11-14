#!/usr/bin/python3

import mock as mock
from mock import Mock
from tests.helper import BaseTestCase
from searchguard.internalusers import delete_user
from searchguard.exceptions import DeleteUserException


class TestDeleteUser(BaseTestCase):

    def setUp(self):
        self.user = "DummyUser"
        self.api_url = "fake_api_url/internalusers/"
        self.set_up_patch('searchguard.internalusers.SGAPI', "fake_api_url")

        self.mocked_requests_delete = self.set_up_patch('searchguard.internalusers.requests.delete')
        self.mocked_requests_delete.return_value = Mock(status_code=200)
        self.mocked_check_user_exists = self.set_up_patch('searchguard.internalusers.check_user_exists')
        self.mocked_check_user_exists.return_value = True

    def test_delete_user_returns_when_successfully_deleted_user(self):
        self.assertIsNone(delete_user(self.user))

    def test_delete_user_returns_exception_when_user_does_not_exist(self):
        self.mocked_check_user_exists.return_value = False

        with self.assertRaises(DeleteUserException):
            delete_user(self.user)

    def test_delete_user_returns_exception_when_requests_return_code_not_200(self):
        self.mocked_requests_delete.return_value = Mock(status_code=999)

        with self.assertRaises(DeleteUserException):
            delete_user(self.user)

    def test_delete_user_calls_check_user_exist(self):
        delete_user(self.user)
        self.mocked_check_user_exists.assert_called_once_with(self.user)

    def test_delete_user_calls_requests_with_correct_arguments(self):
        delete_user(self.user)
        self.mocked_requests_delete.assert_called_once_with('{}{}'.format(self.api_url, self.user),
                                                            auth=(mock.ANY, mock.ANY))
