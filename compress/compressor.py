"""Huffman圧縮を行うモジュール"""
from enum import Enum
import json


# Size for info of data length
DATATYPEINFO_LENGTH_BYTE = 1
DATA_LENGTHINFO_BYTE = 4

class DATATYPE(Enum):
    DATATYPE_STR = 0
    DATATYPE_BYTES = 1

    @staticmethod
    def get_datatype_byte(data):
        if isinstance(data, str):
            return DATATYPE.DATATYPE_STR.value.to_bytes(DATATYPEINFO_LENGTH_BYTE)
        elif isinstance(data, bytes):
            return DATATYPE.DATATYPE_BYTES.value.to_bytes(DATATYPEINFO_LENGTH_BYTE)
        else:
            raise ValueError("Data type is not supported")


def _huffman_decompress(data):

    class reader:
        def __init__(self, data):
            self.data = data
            self.current = 0

        def read(self, length):
            if length > 0:
                ret = self.data[self.current:self.current+length]
                self.current += length
            elif length == -1:
                ret = self.data[self.current:]
                self.current = len(self.data)
            return ret

    # 逆引き情報を作る
    # {byte: symbol}
    # return table_length_info b_symbole_table data_length_info compressed_data
    r = reader(data)
    data_type = int.from_bytes(r.read(DATATYPEINFO_LENGTH_BYTE))
    symbol_table_length = int.from_bytes(r.read(DATA_LENGTHINFO_BYTE))
    json_data = r.read(symbol_table_length).decode('utf-8')
    symbol_table = json.loads(json_data)
    symbol_table_rev = {path: symbol for symbol, path in symbol_table.items()}

    # データ長を取得
    data_length = int.from_bytes(r.read(DATA_LENGTHINFO_BYTE))
    data_main = r.read(-1)

    bitlike_str = ''.join(
        format(byte, '08b') for byte in data_main
    )
    if DATATYPE.DATATYPE_STR.value == data_type:

        decompressed_data = ''
        current = ''
        for bit_str in bitlike_str[:data_length]:
            current += bit_str
            symbol = symbol_table_rev.get(current)
            if symbol is not None:
                decompressed_data += symbol
                current = ''

    elif DATATYPE.DATATYPE_BYTES.value == data_type:

        decompressed_data = b''
        current = ''
        for bit_str in bitlike_str[:data_length]:
            current += bit_str
            symbol = symbol_table_rev.get(current)
            if symbol is not None:
                decompressed_data += int(symbol).to_bytes(1)
                current = ''

    return decompressed_data


def _huffman_compress(data):

    LEFT_PATH = '0'
    RIGHT_PATH = '1'

    class __Node:
        def __init__(self):
            self.left = None
            self.right = None
            self.symbol = None
            self.frequency = None

    def _get_path(node: __Node, path: str = ""):
        """子ノードを探索する
        子ノードが葉ノードであれば、そのノードまでのパスと記号を返す。
        それ以外の場合、再帰的に探索を続ける。

        Args:
            node (__Node): ノード
            path (str): ノードまでのパス
        Returns:
            dict: {symbol: path} pathはstr型(個別にByte変換すると、結局圧縮にならない)
        """
        if node.symbol is not None:
            # 葉に到達したら、そこまでのパスを返す
            return {node.symbol: path}
        else:
            # 葉ノード以外は、必ず子ノードが２つある
            left = _get_path(node.left, path + LEFT_PATH)
            right = _get_path(node.right, path + RIGHT_PATH)
            return {**left, **right}

    symbols = {}  # {symbol: frequency}
    for byte in data:
        if byte in symbols:
            symbols[byte] += 1
        else:
            symbols[byte] = 1
    # Sort symbols by frequency
    symbols = dict(sorted(symbols.items(), key=lambda x: x[1], reverse=True))

    # Create leaf nodes
    nodes = []
    for symbol, frequency in symbols.items():
        node = __Node()
        node.symbol = symbol
        node.frequency = frequency
        nodes.append(node)

    # Create internal nodes
    # 最終的にnodesの中身が１つ＝rootノードまで作成
    while len(nodes) > 1:
        node = __Node()
        node.left = nodes.pop()
        node.right = nodes.pop()
        node.frequency = node.left.frequency + node.right.frequency
        nodes.append(node)
        nodes = sorted(nodes, key=lambda x: x.frequency, reverse=True)

    root = nodes[0]

    # 符号化情報を作成する
    symbol_table = _get_path(root)

    # 符号化情報を用いて圧縮
    compressed_data = ''.join(symbol_table[byte] for byte in data)

    # 圧縮データをバイト列に変換
    # ここでデータ量が減る
    # 8bitごとに分割して、intに変換するが、最後の分割は8bitに満たない場合があるので、その場合末尾を0埋めする
    # 0埋め分は「0」に割り当てた文字に変換されてしまうため、圧縮情報としてバイト長を格納し、解凍時にトリムする
    # [圧縮情報][圧縮データバイト列]
    data_length_info = len(compressed_data)
    data_length_info = data_length_info.to_bytes(DATA_LENGTHINFO_BYTE)
    # '0' * (len(compressed_data) % 8) とするのは誤り。余りの数を足すのではなく、足りない分を足す。
    compressed_data += '0' * (8 - len(compressed_data) % 8)
    compressed_data = bytes(
        int(compressed_data[i: i + 8], 2) for i in range(0, len(compressed_data), 8))
    b_symbole_table = json.dumps(symbol_table).encode('utf-8')
    table_length_info = len(b_symbole_table)
    table_length_info = table_length_info.to_bytes(DATA_LENGTHINFO_BYTE)

    return DATATYPE.get_datatype_byte(data)+table_length_info+b_symbole_table+data_length_info+compressed_data


def compress(data: [str, bytes]) -> bytes:

    compressed_data = _huffman_compress(data)
    return compressed_data


def decompress(data):
    decompressed_data = _huffman_decompress(data)
    return decompressed_data
