from django.test import TestCase

from authtools.models import User
from nodemanager.models import CITreeInfo, ConceptNode


class CITreeInfoTests(TestCase):

    # def setup(self):

    #     test_admin = User.objects.create_superuser(email='admin@test.edu',
    #                                                password='password',
    #                                                name='test admin',)

    #     test_user = User.objects.create_superuser(email='user@test.edu',
    #                                               password='password',
    #                                               name='test user',)

    #     ci_tree_info_master = CITreeInfo(is_master=True)

    #     ci_tree_info_notmaster = CITreeInfo()


    #     root_node = ConceptNode()

    def simple_test(self):

        self.assertEqual(1+1,2)
