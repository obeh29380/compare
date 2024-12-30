import os
import sys
import unittest
sys.path.append("../compress")

from compress.compressor import compress, decompress



class TestMethods(unittest.TestCase):

    INPUT_DIR = os.path.join(os.path.dirname(__file__), 'input')

    def _test_base(self, input_file):
        input_file = os.path.join(self.INPUT_DIR, input_file)
        with open(input_file, 'r', encoding="utf-8") as f:
            data = f.read()
        compressed_data = compress(data)
        decompressed_data = decompress(compressed_data)
        assert data == decompressed_data
        print(f"Compressed {len(data.encode('utf-8'))} -> {len(compressed_data)} (bytes)")

    def _test_base_byte(self, input_file):
        input_file = os.path.join(self.INPUT_DIR, input_file)
        with open(input_file, 'rb') as f:
            data = f.read()
        compressed_data = compress(data)
        decompressed_data = decompress(compressed_data)
        assert data == decompressed_data
        print(f"Compressed {len(data)} -> {len(compressed_data)} (bytes)")

    def test_txt_01(self):
        self._test_base('test_simple.txt')

    def test_txt_02(self):
        self._test_base('test.txt')

    def test_jpg(self):
        self._test_base_byte('cat.jpg')


if __name__ == '__main__':
    unittest.main()
