#!/usr/bin/python3

import json
from tests.helper import BaseTestCase
from mock import Mock, ANY
from searchguard.rolesmapping import create_rolemapping
from searchguard.exceptions import CreateRoleMappingException, RoleMappingException, CheckRoleExistsException


class TestCreateRoleMapping(BaseTestCase):

    def setUp(self):
        self.role = "DummyRole"

        self.properties_arg = {"users": ["DummyUser"], "hosts": ["127.0.0.1"], "backendroles": ["DummyBackendRole"]}
        self.properties_invalid = {"dummykey": ["dummyvalue"]}

        self.api_url = "fake_api_url/rolesmapping/"
        self.set_up_patch('searchguard.settings.SEARCHGUARD_API_URL', "fake_api_url")

        self.mocked_requests_put = self.set_up_patch('searchguard.rolesmapping.requests.put')
        self.mocked_requests_put.return_value = Mock(status_code=201)

        self.mocked_check_role_exists = self.set_up_patch('searchguard.rolesmapping.check_role_exists')
        self.mocked_check_role_exists.return_value = True

    def test_create_rolemapping_returns_none_when_successfully_created_role(self):
        self.assertIsNone(create_rolemapping(self.role, self.properties_arg))

    def test_create_rolemapping_raises_create_exception_when_role_does_not_exists(self):
        self.mocked_check_role_exists.return_value = False

        with self.assertRaises(CheckRoleExistsException):
            create_rolemapping(self.role, self.properties_arg)

    def test_create_rolemapping_raises_exception_when_requests_return_code_not_201(self):
        self.mocked_requests_put.return_value = Mock(status_code=999)

        with self.assertRaises(RoleMappingException):
            create_rolemapping(self.role, self.properties_arg)

    def test_create_rolemapping_calls_check_role_exist(self):
        create_rolemapping(self.role, self.properties_arg)
        self.mocked_check_role_exists.assert_called_once_with(self.role)

    def test_create_rolemapping_raises_exception_when_essential_keys_missing_in_properties(self):

        with self.assertRaises(CreateRoleMappingException):
            create_rolemapping(self.role, self.properties_invalid)

    def test_create_rolemapping_calls_requests_put_with_correct_arguments(self):
        create_rolemapping(self.role, self.properties_arg)
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                         auth=(ANY, ANY),
                                                         data=json.dumps(self.properties_arg),
                                                         headers={'content-type': 'application/json'})
