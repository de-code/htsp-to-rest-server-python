import dict_utils
import unittest

class TestExtract(unittest.TestCase):
    def test_extract_two_out_of_three_keys(self):
        result = dict_utils.extract({'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}, ['key1', 'key3'])
        self.assertEqual(result, {'key1': 'value1', 'key3': 'value3'}, "result")

    def test_extract_with_non_existing_key(self):
        result = dict_utils.extract({'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}, ['key1', 'key4'])
        self.assertEqual(result, {'key1': 'value1'}, "result")

class TestExtractAndMapKeys(unittest.TestCase):
    def test_extract_and_map_keys_one_out_of_three(self):
        result = dict_utils.extract_and_map_keys({'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}, {'key1': 'key1.new'})
        self.assertEqual(result, {'key1.new': 'value1'}, "result")

class TestMerge(unittest.TestCase):
    def test_merge_with_none_none(self):
        result = dict_utils.merge(None, None)
        self.assertEqual(result, {}, "result")

    def test_merge_with_default_but_no_override(self):
        result = dict_utils.merge({'key1': 'value1'}, None)
        self.assertEqual(result, {'key1': 'value1'}, "result")

    def test_merge_with_no_default_but_override(self):
        result = dict_utils.merge(None, {'key1': 'value1'})
        self.assertEqual(result, {'key1': 'value1'}, "result")

    def test_merge_with_distinct_keys(self):
        result = dict_utils.merge({'key1': 'value1'}, {'key2': 'value2'})
        self.assertEqual(result, {'key1': 'value1', 'key2': 'value2'}, "result")

    def test_merge_with_distinct_and_overlapping_keys(self):
        result = dict_utils.merge({'key1': 'value1', 'keyx': 'valuex1'}, {'key2': 'value2', 'keyx': 'valuex2'})
        self.assertEqual(result, {'key1': 'value1', 'key2': 'value2', 'keyx': 'valuex2'}, "result")

if __name__ == '__main__':
    unittest.main()