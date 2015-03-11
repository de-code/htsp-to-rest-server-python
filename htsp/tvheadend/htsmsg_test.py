import htsmsg
import unittest
from StringIO import StringIO

class TestHtsMsg(unittest.TestCase):

    def _serialize_deserialize(self, msg):
        serialized = htsmsg.serialize(msg)
        deserialized = htsmsg.deserialize(StringIO(serialized))
        return deserialized

    def test_serialize_deserialize_short_string(self):
        msg = {'s': '123'}
        deserialized = self._serialize_deserialize(msg)
        self.assertEqual(deserialized, msg, "deserialized == msg")

    def test_serialize_deserialize_long_string(self):
        msg = {'s': '123456789012345678901234567890123456789012345689012345678901234567890123456789012345678901234567890123456789012345689012345678901234567890'}
        deserialized = self._serialize_deserialize(msg)
        self.assertEqual(deserialized, msg, "deserialized == msg")

    def test_serialize_deserialize_complex_message(self):
        msg = {'username': 'tvrec', 'start': 1392339900, 'configName': 'tvbrowser', 'seq': 5, 'title': '12345678901234567890123456789012345678901234568901234567890123456789 [rec=2014-02-14-01-05]', 'channelId': 182, 'stop': 1392341700, 'method': 'addDvrEntry', 'digest': '\xeb\xad\xc3\xf3E\x01\x12\xd6\x1eiV\xc0\xc0\xf1\xa7e\x1c\xf4\x10\x03'}
        deserialized = self._serialize_deserialize(msg)
        self.assertEqual(deserialized, msg, "deserialized == msg")

    def test_int2bin_1(self):
        i = 1
        expected = chr(0) + chr(0) + chr(0) + chr(1)
        actual = htsmsg.int2bin(i)
        self.assertEqual(actual, expected, "actual = expected")

    def test_int2bin_256(self):
        i = 256
        expected = chr(0) + chr(0) + chr(1) + chr(0)
        actual = htsmsg.int2bin(i)
        self.assertEqual(actual, expected, "actual = expected")

if __name__ == '__main__':
    unittest.main()