#!/usr/bin/python3

import json
import unittest.mock as mock
from unittest.mock import Mock
from tests.helper import BaseTestCase
from searchguard.searchguard import list_users
from searchguard.exceptions import ListUsersException


class TestListUsers(BaseTestCase):

    def setUp(self):
        self.api_url = "fake_api_url/internalusers/"
        self.set_up_patch('searchguard.searchguard.SGAPI', "fake_api_url")

        self.user_list_pt1 = {"dummyuser1": {"hash": "123"}}
        self.user_list_pt2 = {"999_dummyuser2": {"hash": "456", "roles": ["dummyrole2"]}}
        self.user_list_pt3 = {"999_someuser3": {"hash": "789", "username": "dummy.user3"}}

        # To maintain Python 3.4 compatibility:
        self.user_list = {}
        self.user_list.update(self.user_list_pt1, **dict(self.user_list_pt2, **self.user_list_pt3))

        self.mocked_requests_get = self.set_up_patch('searchguard.searchguard.requests.get')
        self.mocked_requests_get.return_value = Mock(status_code=200, text=json.dumps(self.user_list))

    def test_list_users_returns_all_users_when_called_without_filters(self):
        ret = list_users()

        self.assertEqual(ret, self.user_list)

    def test_list_users_returns_only_matching_users_when_prefix_is_used(self):
        user_list_filtered = dict(self.user_list_pt2, **self.user_list_pt3)

        ret = list_users(prefix='999')

        self.assertEqual(ret, user_list_filtered)

    def test_list_users_returns_only_matching_users_when_search_is_used(self):
        user_list_filtered = dict(self.user_list_pt1, **self.user_list_pt2)

        ret = list_users(search='dummyuser')

        self.assertEqual(ret, user_list_filtered)

    def test_list_users_returns_only_matching_users_when_both_prefix_and_search_are_used(self):
        ret = list_users(prefix='999', search='dummyuser')

        self.assertEqual(ret, self.user_list_pt2)

    def test_list_users_returns_exception_when_requests_return_code_not_200(self):
        self.mocked_requests_get.return_value = Mock(status_code=999)

        with self.assertRaises(ListUsersException):
            list_users()

    def test_list_users_calls_requests_with_correct_arguments(self):
        list_users()

        self.mocked_requests_get.assert_called_once_with('{}'.format(self.api_url), auth=(mock.ANY, mock.ANY))
