from unittest import TestCase

from data_transform.foo.node import Node
from data_transform.foo.link import Link



class TestLink(TestCase):
    n_1 = Node("test123", 2022)
    n_2 = Node("test321", 2022)

    def generate_test_link(self) -> Link:
        test_link = Link(self.n_1, self.n_2, 1)
        return test_link

    def test_get_source(self):
        self.assertEqual(self.generate_test_link().get_source(), self.n_1)

    def test_get_target(self):
        self.assertEqual(self.generate_test_link().get_target(), self.n_2)

    def test_get_value(self):
        self.assertEqual(self.generate_test_link().get_value(), 1)

    def test_set_value(self):
        link = self.generate_test_link()
        new_value = 5
        link.set_value(new_value)
        self.assertEqual(new_value, link.get_value())

    def test_eq(self):
        n_3 = Node("test213", 2022)

        l1 = self.generate_test_link()
        # value is ignored when comparing equality
        l2_equal = Link(self.n_1, self.n_2, 1)
        l3_equal = Link(self.n_2, self.n_1, 2)
        l4_unequal = Link(self.n_2, n_3, 1)

        self.assertEqual(l1, l2_equal)
        self.assertEqual(l1, l3_equal)
        self.assertNotEqual(l1, l4_unequal)
