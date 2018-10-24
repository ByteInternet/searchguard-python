#!/usr/bin/python3

import unittest.mock as mock
from unittest.mock import Mock
from tests.helper import BaseTestCase
from searchguard.searchguard import view_user
from searchguard.exceptions import ViewUserException


class TestViewUser(BaseTestCase):

    def setUp(self):
        self.user = "DummyUser"
        self.api_url = "fake_api_url/internalusers/"
        self.user_data = {"DummyUser": {"roles": ["BackendRole"], "hash": "hash1234"}}
        self.set_up_patch('searchguard.searchguard.SGAPI', "fake_api_url")

        self.mocked_requests_get = self.set_up_patch('searchguard.searchguard.requests.get')
        self.mocked_requests_get.return_value = Mock(status_code=200)
        self.mocked_check_user_exists = self.set_up_patch('searchguard.searchguard.check_user_exists')
        self.mocked_check_user_exists.return_value = True

    def test_view_user_returns_user_information_when_correctly_called(self):
        self.mocked_requests_get.return_value = Mock(status_code=200, text=self.user_data)

        ret = view_user(self.user)
        assert ret == self.user_data

    def test_view_user_returns_exception_when_user_does_not_exist(self):
        self.mocked_check_user_exists.return_value = False

        with self.assertRaises(ViewUserException):
            view_user(self.user)

    def test_view_user_returns_exception_when_requests_return_code_not_200(self):
        self.mocked_requests_get.return_value = Mock(status_code=999)

        with self.assertRaises(ViewUserException):
            view_user(self.user)

    def test_view_user_calls_check_user_exist(self):
        view_user(self.user)
        self.mocked_check_user_exists.assert_called_once_with(self.user)

    def test_view_user_calls_requests_with_correct_arguments(self):
        view_user(self.user)
        self.mocked_requests_get.assert_called_once_with('{}{}'.format(self.api_url, self.user),
                                                         auth=(mock.ANY, mock.ANY))
