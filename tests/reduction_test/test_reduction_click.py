import unittest
import pygame
import numpy as np

from npvis.problem import ThreeSATProblem, IndependentSetProblem
from npvis.reduction.reduction import Reduction
from npvis.element import Variable, Node

class TestInputMethods(unittest.TestCase):
    def setUp(self):
        # Set up the object and any initial states
        p1 = ThreeSATProblem()
        p2 = IndependentSetProblem()
        self.obj = Reduction(p1,p2) 
        self.obj.input1_to_input2_dict = {}  # Initialize empty dictionary
        self.obj.highlighted = []

    def test_add_input1_to_input2_by_pair(self):
        # Test when the input1 doesn't exist
        input1 = Variable("var1", False, 0, 0)
        input2 = Node(0, "node1")
        input3 = Node(0, "node2")

        self.obj.add_input1_to_input2_by_pair(input1, input2)
        self.assertIn(input1, self.obj.input1_to_input2_dict)
        self.assertEqual(self.obj.input1_to_input2_dict[input1], {input2})

        # Test when the input1 already exists
        self.obj.add_input1_to_input2_by_pair(input1, input3)
        self.assertIn(input1, self.obj.input1_to_input2_dict)
        self.assertEqual(self.obj.input1_to_input2_dict[input1], {input2,input3})

    def test_add_input1_to_input2_by_set(self):
        # Test when the input1 doesn't exist
        input1 = Variable("var1", False, 0, 0)  # Assuming Variable is a class
        input2 = Node(0, "node1")  # Assuming Node is a class
        input3 = Node(0, "node2")
        input4 = Node(0, "node3")

        # Add a set of nodes to input1
        self.obj.add_input1_to_input2_by_set(input1, {input2, input3})
        self.assertIn(input1, self.obj.input1_to_input2_dict)
        self.assertEqual(self.obj.input1_to_input2_dict[input1], {input2, input3})

        # Test when the input1 already exists
        self.obj.add_input1_to_input2_by_set(input1, {input2, input4})
        self.assertEqual(self.obj.input1_to_input2_dict[input1], {input2, input3, input4})

    def test_display_input_to_input(self):
        # Create actual elements for input1 and input2
        input1 = Variable("var1", False, 0, 0) 
        input2 = Node(0, "node1")  # Assuming Node is a class
        input3 = Node(0, "node2")  # Assuming Node is a class
        self.obj.add_input1_to_input2_by_set(input1, {input2, input3})

        # Test with one element in p1
        self.obj.display_input_to_input({input1})
        self.assertIn(input1, self.obj.highlighted)  # input1 should be highlighted
        self.assertIn(input2, self.obj.highlighted)
        self.assertIn(input3, self.obj.highlighted)

        # Test with one element in p2
        self.obj.display_input_to_input({input2})
        self.assertNotIn(input1, self.obj.highlighted)  # input1 should not be highlighted
        self.assertIn(input2, self.obj.highlighted)  # input2 should be highlighted
        self.assertNotIn(input3, self.obj.highlighted)

        # Test with all elements that is needed to light p1 input1
        self.obj.display_input_to_input({input2,input3})
        self.assertIn(input1, self.obj.highlighted)  # input1 should be highlighted
        self.assertIn(input2, self.obj.highlighted)
        self.assertIn(input3, self.obj.highlighted)


    def test_reset_highlighted(self):
        # Simulate adding highlighted elements
        self.obj.highlighted = [Node(0, "node1"), Node(0, "node2")]
        
        # Mocking reset function
        self.obj.reset_highlighted()
        self.assertEqual(self.obj.highlighted, [])  # Should reset to empty list

if __name__ == '__main__':
    unittest.main()