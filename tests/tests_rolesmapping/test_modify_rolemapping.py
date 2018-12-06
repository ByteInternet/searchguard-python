#!/usr/bin/python3

import json
from mock import Mock, ANY
from tests.helper import BaseTestCase
from searchguard.rolesmapping import modify_rolemapping
from searchguard.exceptions import ModifyRoleMappingException, RoleMappingException


class TestModifyRoleMapping(BaseTestCase):

    def setUp(self):
        self.role = "DummyRole"

        self.properties_arg = {"users": ["DummyUser"], "hosts": ["127.0.0.1"], "backendroles": ["DummyBackendRole"]}
        self.properties_cur = {"DummyRole": {"users": ["DummyUser1", "DummyUser2"],
                                             "hosts": ["127.0.0.1"], "backendroles": []}}
        self.properties_invalid = {"dummykey": ["dummyvalue"]}

        self.api_url = "fake_api_url/rolesmapping/"
        self.set_up_patch('searchguard.settings.SEARCHGUARD_API_URL', "fake_api_url")

        self.mocked_requests_put = self.set_up_patch('searchguard.rolesmapping.requests.put')
        self.mocked_requests_put.return_value = Mock(status_code=200)

        self.mocked_check_role_exists = self.set_up_patch('searchguard.rolesmapping.check_role_exists')
        self.mocked_check_role_exists.return_value = True

        self.mocked_check_rolemapping_exists = self.set_up_patch('searchguard.rolesmapping.check_rolemapping_exists')
        self.mocked_check_rolemapping_exists.return_value = True

        self.mocked_view_rolemapping = self.set_up_patch('searchguard.rolesmapping.view_rolemapping')
        self.mocked_view_rolemapping.return_value = self.properties_cur

    def test_modify_rolemapping_returns_none_when_successfully_modified_role(self):
        self.assertIsNone(modify_rolemapping(self.role, self.properties_arg))

    def test_modify_rolemapping_raises_create_exception_when_rolemapping_does_not_exists(self):
        self.mocked_check_rolemapping_exists.return_value = False

        with self.assertRaises(ModifyRoleMappingException):
            modify_rolemapping(self.role, self.properties_arg)

    def test_modify_rolemapping_raises_exception_when_requests_return_code_not_200(self):
        self.mocked_requests_put.return_value = Mock(status_code=999)

        with self.assertRaises(RoleMappingException):
            modify_rolemapping(self.role, self.properties_arg)

    def test_modify_rolemapping_calls_check_rolemapping_exist(self):
        modify_rolemapping(self.role, self.properties_arg)
        self.mocked_check_rolemapping_exists.assert_called_once_with(self.role)

    def test_modify_rolemapping_raises_exception_when_essential_keys_missing_in_properties(self):

        with self.assertRaises(ModifyRoleMappingException):
            modify_rolemapping(self.role, self.properties_invalid)

    def test_modify_rolemapping_creates_empty_lists_for_non_existent_properties(self):
        self.properties_cur = {"DummyRole": {"users": ["DummyUser1"], "hosts": ["127.0.0.1"]}}
        self.mocked_view_rolemapping.return_value = self.properties_cur

        modify_rolemapping(self.role, self.properties_arg)

    def test_modify_rolemapping_with_action_replace_calls_requests_put_with_correct_arguments(self):
        modify_rolemapping(self.role, self.properties_arg)
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                         auth=(ANY, ANY),
                                                         data=json.dumps(self.properties_arg),
                                                         headers={'content-type': 'application/json'})

    def test_modify_rolemapping_with_action_merge_calls_requests_put_with_correct_arguments(self):
        self.properties_merged = {"users": ["DummyUser", "DummyUser1", "DummyUser2"],
                                  "hosts": ["127.0.0.1"], "backendroles": ["DummyBackendRole"]}

        modify_rolemapping(self.role, self.properties_arg, "merge")
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                         auth=(ANY, ANY),
                                                         data=json.dumps(self.properties_merged),
                                                         headers={'content-type': 'application/json'})

    def test_modify_rolemapping_with_action_split_calls_requests_put_with_correct_arguments(self):
        self.properties_split = {"users": ["DummyUser1", "DummyUser2"], "hosts": [], "backendroles": []}

        modify_rolemapping(self.role, self.properties_arg, "split")
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                         auth=(ANY, ANY),
                                                         data=json.dumps(self.properties_split),
                                                         headers={'content-type': 'application/json'})
