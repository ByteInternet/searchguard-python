#!/usr/bin/python3
from searchguard import ViewRoleMappingException
from searchguard.rolesmapping import list_rolemappings_for_user
from tests.helper import BaseTestCase


class TestListRolemappingsForUser(BaseTestCase):

    def setUp(self):
        self.user = 'username'
        self.roles = ['role1', 'role2', 'role3']

        self.mock_view_rolemapping = self.set_up_patch('searchguard.rolesmapping.view_rolemapping')
        self.mock_view_rolemapping.side_effect = [{self.roles[0]: {'users': [self.user]}},
                                                  {self.roles[1]: {'users': ['differentUser']}},
                                                  {self.roles[2]: {'users': [self.user, 'differentUser']}}]

    def test_list_rolemappings_for_user_returns_list_of_rolemappings_that_contain_user(self):

        ret = list_rolemappings_for_user(self.user, self.roles)
        self.assertEqual(ret, ['role1', 'role3'])

    def test_list_rolemappings_for_user_returns_empty_list_if_no_matches_occur(self):
        self.mock_view_rolemapping.side_effect = [{self.roles[0]: {'users': ['differentUser']}},
                                                  {self.roles[1]: {'users': ['differentUser']}},
                                                  {self.roles[2]: {'users': ['only', 'differentUser']}}]

        ret = list_rolemappings_for_user(self.user, self.roles)
        self.assertEqual(ret, [])

    def test_list_rolemappings_for_user_raises_exception_when_role_does_not_exist(self):
        self.mock_view_rolemapping.side_effect = [{self.roles[0]: {'users': [self.user]}},
                                                  ViewRoleMappingException,
                                                  {self.roles[2]: {'users': [self.user, 'differentUser']}}]

        with self.assertRaises(ViewRoleMappingException):
            list_rolemappings_for_user(self.user, self.roles)
