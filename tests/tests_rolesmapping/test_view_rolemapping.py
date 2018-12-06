#!/usr/bin/python3

import json
from mock import Mock, ANY
from searchguard.rolesmapping import view_rolemapping
from searchguard.exceptions import ViewRoleMappingException
from tests.helper import BaseTestCase


class TestViewRoleMapping(BaseTestCase):

    def setUp(self):
        self.role = "DummyRole"
        self.permissions = {"users": ["worf"]}
        self.api_url = "fake_api_url/rolesmapping/"
        self.set_up_patch('searchguard.settings.SEARCHGUARD_API_URL', "fake_api_url")

        self.mocked_requests_get = self.set_up_patch('searchguard.rolesmapping.requests.get')
        self.mocked_requests_get.return_value = Mock(status_code=200, text=json.dumps(self.permissions))
        self.mocked_check_rolemapping_exists = self.set_up_patch('searchguard.rolesmapping.check_rolemapping_exists')
        self.mocked_check_rolemapping_exists.return_value = True

    def test_view_rolemapping_returns_role_information_when_correctly_called(self):

        ret = view_rolemapping(self.role)
        assert ret == self.permissions

    def test_view_rolemapping_returns_exception_when_role_does_not_exist(self):
        self.mocked_check_rolemapping_exists.return_value = False

        with self.assertRaises(ViewRoleMappingException):
            view_rolemapping(self.role)

    def test_view_rolemapping_returns_exception_when_requests_return_code_not_200(self):
        self.mocked_requests_get.return_value = Mock(status_code=999)

        with self.assertRaises(ViewRoleMappingException):
            view_rolemapping(self.role)

    def test_view_rolemapping_calls_check_role_exist(self):
        view_rolemapping(self.role)
        self.mocked_check_rolemapping_exists.assert_called_once_with(self.role)

    def test_view_rolemapping_calls_requests_with_correct_arguments(self):
        view_rolemapping(self.role)
        self.mocked_requests_get.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                         auth=(ANY, ANY))
