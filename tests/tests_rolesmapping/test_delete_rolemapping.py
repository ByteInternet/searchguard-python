#!/usr/bin/python3

from mock import Mock, ANY
from tests.helper import BaseTestCase
from searchguard.rolesmapping import delete_rolemapping
from searchguard.exceptions import DeleteRoleMappingException


class TestDeleteRoleMapping(BaseTestCase):

    def setUp(self):
        self.role = "DummyRole"
        self.api_url = "fake_api_url/rolesmapping/"
        self.set_up_patch('searchguard.settings.SEARCHGUARD_API_URL', "fake_api_url")

        self.mocked_requests_delete = self.set_up_patch('searchguard.rolesmapping.requests.delete')
        self.mocked_requests_delete.return_value = Mock(status_code=200)
        self.mocked_check_rolemapping_exists = self.set_up_patch('searchguard.rolesmapping.check_rolemapping_exists')
        self.mocked_check_rolemapping_exists.return_value = True

    def test_delete_rolemapping_returns_when_successfully_deleted_role(self):
        self.assertIsNone(delete_rolemapping(self.role))

    def test_delete_rolemapping_raises_exception_when_user_does_not_exist(self):
        self.mocked_check_rolemapping_exists.return_value = False

        with self.assertRaises(DeleteRoleMappingException):
            delete_rolemapping(self.role)

    def test_delete_rolemapping_returns_exception_when_requests_return_code_not_200(self):
        self.mocked_requests_delete.return_value = Mock(status_code=999)

        with self.assertRaises(DeleteRoleMappingException):
            delete_rolemapping(self.role)

    def test_delete_role_calls_requests_with_correct_arguments(self):
        delete_rolemapping(self.role)
        self.mocked_requests_delete.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                            auth=(ANY, ANY))
