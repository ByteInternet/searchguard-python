#!/usr/bin/python3

from mock import Mock, ANY
from tests.helper import BaseTestCase
from searchguard.rolesmapping import check_rolemapping_exists
from searchguard.exceptions import CheckRoleMappingExistsException


class TestCheckRoleMappingExists(BaseTestCase):

    def setUp(self):
        self.role = "DummyRole"
        self.api_url = "fake_api_url/rolesmapping/"
        self.set_up_patch('searchguard.settings.SEARCHGUARD_API_URL', "fake_api_url")

        self.mocked_requests_get = self.set_up_patch('searchguard.rolesmapping.requests.get')
        self.mocked_requests_get.return_value = Mock(status_code=200)

    def test_check_rolemapping_exists_calls_requests_with_correct_arguments(self):
        check_rolemapping_exists(self.role)
        self.mocked_requests_get.assert_called_once_with('{}{}'.format(self.api_url, self.role),
                                                         auth=(ANY, ANY))

    def test_check_rolemapping_exists_returns_true_when_role_exists(self):
        ret = check_rolemapping_exists(self.role)
        self.assertTrue(ret)

    def test_check_rolemapping_exists_returns_false_when_role_does_not_exist(self):
        self.mocked_requests_get.return_value = Mock(status_code=404)

        ret = check_rolemapping_exists(self.role)
        self.assertFalse(ret)

    def test_check_rolemapping_exists_returns_exception_when_unknown_status_code(self):
        self.mocked_requests_get.return_value = Mock(status_code=999)

        with self.assertRaises(CheckRoleMappingExistsException):
            check_rolemapping_exists(self.role)
