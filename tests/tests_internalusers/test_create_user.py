#!/usr/bin/python3

import json
import mock as mock
from tests.helper import BaseTestCase
from mock import patch, Mock
from searchguard.internalusers import create_user, password_generator
from searchguard.exceptions import CreateUserException, UserAlreadyExistsException


class TestCreateUser(BaseTestCase):

    def setUp(self):
        self.user = "DummyUser"
        self.api_url = "fake_api_url/internalusers/"
        self.set_up_patch('searchguard.internalusers.SGAPI', "fake_api_url")

        self.mocked_requests_put = self.set_up_patch('searchguard.internalusers.requests.put')
        self.mocked_requests_put.return_value = Mock(status_code=201)
        self.mocked_check_user_exists = self.set_up_patch('searchguard.internalusers.check_user_exists')
        self.mocked_check_user_exists.return_value = False

    @patch('searchguard.internalusers.password_generator')
    def test_create_user_returns_correct_password_when_successfully_created_user(self, mock_password_generator):
        mock_password_generator.return_value = "abc1234"

        ret = create_user(self.user)
        self.assertEqual(ret, "abc1234")

    def test_create_user_returns_25_char_password_when_successfully_created_user(self):
        ret = create_user(self.user)
        self.assertEqual(len(ret), 25)

    def test_create_user_accepts_optional_password(self):
        ret = create_user(self.user, 'sample_password')
        self.assertEqual(ret, 'sample_password')

    @patch('searchguard.internalusers.password_generator')
    def test_create_user_wont_generate_password_if_its_passed_in(self, mock_password_generator):
        ret = create_user(self.user, 'sample_password')
        mock_password_generator.assert_not_called()

    def test_create_user_raises_create_exception_when_user_already_exists(self):
        self.mocked_check_user_exists.return_value = True

        with self.assertRaises(CreateUserException):
            create_user(self.user)

    def test_create_user_raises_specific_exception_when_user_already_exists(self):
        self.mocked_check_user_exists.return_value = True

        with self.assertRaises(UserAlreadyExistsException):
            create_user(self.user)

    def test_create_user_raises_exception_when_requests_return_code_not_201(self):
        self.mocked_requests_put.return_value = Mock(status_code=999)

        with self.assertRaises(CreateUserException):
            create_user(self.user)

    def test_create_user_calls_check_user_exist(self):
        create_user(self.user)
        self.mocked_check_user_exists.assert_called_once_with(self.user)

    def test_create_user_calls_password_generator(self):
        create_user(self.user)
        self.assertTrue(password_generator())

    @patch('searchguard.internalusers.password_generator')
    def test_create_user_calls_requests_with_correct_arguments(self, mock_password_generator):
        mock_password_generator.return_value = "abc1234"

        create_user(self.user)
        data = {"password": "abc1234"}
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.user),
                                                         auth=(mock.ANY, mock.ANY),
                                                         data=json.dumps(data),
                                                         headers={'content-type': 'application/json'})
