#!/usr/bin/python3
from searchguard import ViewRoleMappingException
from searchguard.rolesmapping import list_rolemappings_for_user
from tests.helper import BaseTestCase


class TestListRolemappingsForUser(BaseTestCase):

    def setUp(self):
        self.user = 'username'
        self.roles = ['role0', 'role1', 'role2']

        self.mock_all_view_rolemapping = self.set_up_patch('searchguard.rolesmapping.view_all_rolemappings')
        self.mock_view_rolemapping = self.set_up_patch('searchguard.rolesmapping.view_rolemapping')

        self.all_roles = [{'role0': {'users': [self.user]}},
                          {'role1': {'users': ['differentUser']}},
                          {'role2': {'users': [self.user, 'differentUser']}},
                          {'role3': {'users': [self.user]}}]

        self.mock_view_rolemapping.side_effect = [self.all_roles[0], self.all_roles[1], self.all_roles[2]]

        self.mock_all_view_rolemapping.return_value = dict([(k, v) for element in self.all_roles
                                                            for k, v in element.items()])

    def test_list_rolemappings_for_user_returns_list_of_rolemappings_that_contain_user_for_provided_roles(self):
        ret = list_rolemappings_for_user(self.user, self.roles)
        self.assertEqual(ret, ['role0', 'role2'])

    def test_list_rolemappings_for_user_returns_list_of_rolemappings_that_contain_user_for_all_rolemappings(self):
        ret = list_rolemappings_for_user(self.user)
        self.assertListEqual(ret, ['role0', 'role2', 'role3'])

    def test_list_rolemappings_for_user_returns_empty_list_if_no_matches_occur(self):
        self.mock_view_rolemapping.side_effect = [{self.roles[0]: {'users': ['differentUser']}},
                                                  {self.roles[1]: {'users': ['differentUser']}},
                                                  {self.roles[2]: {'users': ['only', 'differentUser']}}]

        ret = list_rolemappings_for_user(self.user, self.roles)
        self.assertEqual(ret, [])

    def test_list_rolemappings_for_user_raises_exception_when_role_does_not_exist(self):
        self.mock_view_rolemapping.side_effect = [self.all_roles[0], ViewRoleMappingException, self.all_roles[2]]

        with self.assertRaises(ViewRoleMappingException):
            list_rolemappings_for_user(self.user, self.roles)
