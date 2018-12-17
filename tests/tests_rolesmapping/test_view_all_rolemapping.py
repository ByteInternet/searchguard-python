#!/usr/bin/python3

import json

from mock import Mock, ANY

from searchguard.exceptions import ViewAllRoleMappingException
from searchguard.rolesmapping import view_all_rolemappings
from tests.helper import BaseTestCase


class TestViewAllRoleMapping(BaseTestCase):

    def setUp(self):
        self.permissions = {"role1": {"users": ["john"]},
                            "role2": {"users": ["doe"]}}

        self.set_up_patch('searchguard.settings.SEARCHGUARD_API_URL', "fake_api_url")
        self.mocked_requests_get = self.set_up_patch('searchguard.rolesmapping.requests.get')
        self.mocked_requests_get.return_value = Mock(status_code=200, text=json.dumps(self.permissions))

    def test_view_rolemapping_returns_role_information_when_correctly_called(self):

        ret = view_all_rolemappings()
        self.assertEqual(ret, self.permissions)

    def test_view_rolemapping_returns_exception_when_requests_return_code_not_200(self):
        self.mocked_requests_get.return_value = Mock(status_code=999)

        with self.assertRaises(ViewAllRoleMappingException):
            view_all_rolemappings()

    def test_view_rolemapping_calls_requests_with_correct_arguments(self):
        view_all_rolemappings()
        self.mocked_requests_get.assert_called_once_with("fake_api_url/rolesmapping/", auth=(ANY, ANY))
