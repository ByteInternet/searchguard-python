import unittest
from unittest.mock import Mock, patch


class BaseTestCase(unittest.TestCase):
    def set_up_patch(self, topatch, themock=None, **kwargs):
        """
        Patch a function or class
        :param topatch: string The class to patch
        :param themock: optional object to use as mock
        :return: mocked object
        """
        if themock is None:
            themock = Mock(**kwargs)

        patcher = patch(topatch, themock)
        self.addCleanup(patcher.stop)
        return patcher.start()
