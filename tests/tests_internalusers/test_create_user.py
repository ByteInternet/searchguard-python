#!/usr/bin/python3

import json
from tests.helper import BaseTestCase
from mock import patch, Mock, ANY
from searchguard.internalusers import create_user, password_generator
from searchguard.exceptions import CreateUserException, UserAlreadyExistsException


class TestCreateUser(BaseTestCase):

    def setUp(self):
        self.user = "DummyUser"
        self.properties = {
            "password": "abcd1234",
            "roles": ["testrole"],
            "attributes": {
                "attr1": "value1",
                "attr2": "value2",
            }
        }
        self.api_url = "fake_api_url/internalusers/"
        self.set_up_patch('searchguard.settings.SEARCHGUARD_API_URL', "fake_api_url")

        self.mocked_requests_put = self.set_up_patch('searchguard.internalusers.requests.put')
        self.mocked_requests_put.return_value = Mock(status_code=201)
        self.mocked_check_user_exists = self.set_up_patch('searchguard.internalusers.check_user_exists')
        self.mocked_check_user_exists.return_value = False

    @patch('searchguard.internalusers.password_generator')
    def test_create_user_returns_correct_password_when_successfully_created_user(self, mock_password_generator):
        mock_password_generator.return_value = "abc1234"

        ret = create_user(self.user)
        self.assertEqual(ret, "abc1234")

    def test_create_user_returns_25_char_password_when_generated_a_password(self):
        ret = create_user(self.user)
        self.assertEqual(len(ret), 25)

    def test_create_user_accepts_optional_password_and_returns_it(self):
        ret = create_user(self.user, 'sample_password')
        self.assertEqual(ret, 'sample_password')

    @patch('searchguard.internalusers.password_generator')
    def test_create_user_wont_generate_password_if_its_passed_in(self, mock_password_generator):
        ret = create_user(self.user, 'sample_password')
        mock_password_generator.assert_not_called()

    def test_create_user_returns_password_in_properties_if_set(self):
        ret = create_user(self.user, None, dict(password='password_in_properties'))
        self.assertEqual(ret, 'password_in_properties')

    @patch('searchguard.internalusers.password_generator')
    def test_create_user_wont_generate_password_if_properties_contain_password(self, mock_password_generator):
        ret = create_user(self.user, None, dict(password='password_in_properties'))
        mock_password_generator.assert_not_called()

    def test_create_user_returns_empty_string_if_properties_contain_hash(self):
        ret = create_user(self.user, None, {'hash': 'buYQkJcKxsz4JO50X8SqbJE9Cth5dJI'})
        self.assertEqual(ret, '')

    @patch('searchguard.internalusers.password_generator')
    def test_create_user_wont_generate_password_if_properties_contain_hash(self, mock_password_generator):
        ret = create_user(self.user, None, {'hash': 'buYQkJcKxsz4JO50X8SqbJE9Cth5dJI'})
        mock_password_generator.assert_not_called()

    @patch('searchguard.internalusers.password_generator')
    def test_create_user_wont_generate_password_if_its_passed_in(self, mock_password_generator):
        ret = create_user(self.user, 'sample_password')
        mock_password_generator.assert_not_called()

    def test_create_user_raises_value_error_when_password_does_not_match_properties_password(self):
        with self.assertRaises(ValueError):
            create_user(self.user, 'efgh5678', self.properties)
        self.mocked_requests_put.assert_not_called()

    def test_create_user_raises_value_error_when_password_does_not_match_properties_password_with_hash(self):
        self.properties['hash'] = 'buYQkJcKxsz4JO50X8SqbJE9Cth5dJI'
        with self.assertRaises(ValueError):
            create_user(self.user, 'efgh5678', self.properties)
        self.mocked_requests_put.assert_not_called()

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
    def test_create_user_calls_api_with_correct_arguments_when_generating_password(self, mock_password_generator):
        mock_password_generator.return_value = "abc1234"

        create_user(self.user)
        data = {"password": "abc1234"}
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.user),
                                                         auth=(ANY, ANY),
                                                         data=json.dumps(data),
                                                         headers={'content-type': 'application/json'})

    def test_create_user_calls_api_with_correct_arguments_when_explicit_password(self):
        create_user(self.user, "efg5678")
        data = {"password": "efg5678"}
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.user),
                                                         auth=(ANY, ANY),
                                                         data=json.dumps(data),
                                                         headers={'content-type': 'application/json'})

    def test_create_user_calls_api_with_correct_arguments_when_properties_has_hash(self):
        self.properties['hash'] = 'buYQkJcKxsz4JO50X8SqbJE9Cth5dJI'
        create_user(self.user, properties=self.properties)
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.user),
                                                         auth=(ANY, ANY),
                                                         data=json.dumps(self.properties),
                                                         headers={'content-type': 'application/json'})

    def test_create_user_calls_api_with_correct_arguments_when_properties_has_hash_only(self):
        self.properties['hash'] = 'buYQkJcKxsz4JO50X8SqbJE9Cth5dJI'
        del self.properties['password']
        create_user(self.user, properties=self.properties)
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.user),
                                                         auth=(ANY, ANY),
                                                         data=json.dumps(self.properties),
                                                         headers={'content-type': 'application/json'})

    def test_create_user_calls_api_with_correct_arguments_when_properties_has_password_only(self):
        create_user(self.user, properties=self.properties)
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.user),
                                                         auth=(ANY, ANY),
                                                         data=json.dumps(self.properties),
                                                         headers={'content-type': 'application/json'})

    def test_create_user_calls_api_with_correct_arguments_when_password_matches_properties(self):
        create_user(self.user, 'abcd1234', self.properties)
        self.mocked_requests_put.assert_called_once_with('{}{}'.format(self.api_url, self.user),
                                                         auth=(ANY, ANY),
                                                         data=json.dumps(self.properties),
                                                         headers={'content-type': 'application/json'})
