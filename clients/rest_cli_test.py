#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rest_cli
import unittest

class TestRestCli(unittest.TestCase):

    def test_clean_filename_with_ascii(self):
        result = rest_cli.clean_filename("abc")
        self.assertEqual(result, "abc", "result")

    def test_clean_filename_with_colon_no_space(self):
        result = rest_cli.clean_filename("a:b")
        self.assertEqual(result, "a, b", "result")

    def test_clean_filename_with_colon_space(self):
        result = rest_cli.clean_filename("a: b")
        self.assertEqual(result, "a, b", "result")

    def test_clean_filename_with_pound_symbol_no_space(self):
        result = rest_cli.clean_filename("£10")
        #print "result: " + result
        self.assertEqual(result, "GBP 10", "result")

    def test_clean_filename_with_pound_symbol_space(self):
        result = rest_cli.clean_filename("£ 10")
        #print "result: " + result
        self.assertEqual(result, "GBP 10", "result")

if __name__ == '__main__':
    unittest.main()
