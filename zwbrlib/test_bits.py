import unittest

import zwbrlib.bits as bits

# To run tests: python3 -m unittest discover -s zwbrlib

class TestIsBitSet(unittest.TestCase):

    def test_each_bit_one_byte(self):
        bit_id = 1
        for i in range(0, 8):
            bit_field = bytes([1 << i])
            self.assertTrue(bits.is_id_set(bit_field, bit_id))
            bit_id += 1

    def test_each_bit_first_byte(self):
        bit_id = 1
        for i in range(0, 8):
            bit_field = bytes([1 << i, 0x00, 0x00])
            self.assertTrue(bits.is_id_set(bit_field, bit_id))
            bit_id += 1

    def test_each_bit_middle_byte(self):
        bit_id = 9
        for i in range(0, 8):
            bit_field = bytes([0x00, 1 << i, 0x00])
            self.assertTrue(bits.is_id_set(bit_field, bit_id))
            bit_id += 1

    def test_each_bit_last_byte(self):
        bit_id = 17
        for i in range(0, 8):
            bit_field = bytes([0x00, 0x00, 1 << i])
            self.assertTrue(bits.is_id_set(bit_field, bit_id))
            bit_id += 1

    def test_bit_not_set(self):
        self.assertFalse(bits.is_id_set(bytes([0xF7, 0xFF]), 4))
        self.assertFalse(bits.is_id_set(bytes([0xFE, 0xFF]), 1))

    def test_bit_not_set_last_byte(self):
        self.assertFalse(bits.is_id_set(bytes([0xFF, 0xEF]), 13))

    def test_bit_id_overflow(self):
        bit_field = bytes([0xFF, 0xFF])
        self.assertTrue(bits.is_id_set(bit_field, 9))
        self.assertTrue(bits.is_id_set(bit_field, 16))
        self.assertFalse(bits.is_id_set(bit_field, 17))
        self.assertFalse(bits.is_id_set(bit_field, 18))

if __name__ == '__main__':
    unittest.main()
