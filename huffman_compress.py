import json
from PIL import Image
from collections import Counter
import heapq

class Node:
    def __init__(self, symbol, freq):
        self.symbol = symbol
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(freq_dict):
    heap = [Node(symbol, freq) for symbol, freq in freq_dict.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    return heap[0]

def build_codes(node, current_code="", codes=None):
    if codes is None:
        codes = {}
    if node is not None:
        if node.symbol is not None:
            codes[node.symbol] = current_code
        build_codes(node.left, current_code + "0", codes)
        build_codes(node.right, current_code + "1", codes)
    return codes

def encode_data(data, codes):
    return ''.join(codes[pixel] for pixel in data)

def pad_encoded_data(encoded):
    extra_padding = 8 - len(encoded) % 8
    encoded += "0" * extra_padding
    padded_info = "{0:08b}".format(extra_padding)
    return padded_info + encoded

def get_byte_array(padded_encoded_data):
    byte_array = bytearray()
    for i in range(0, len(padded_encoded_data), 8):
        byte = padded_encoded_data[i:i+8]
        byte_array.append(int(byte, 2))
    return byte_array

def huffman_compress_image(image_path, output_path, meta_path):
    image = Image.open(image_path).convert('L')
    data = list(image.getdata())

    freq_dict = dict(Counter(data))
    tree = build_huffman_tree(freq_dict)
    codes = build_codes(tree)
    encoded_data = encode_data(data, codes)
    padded_encoded_data = pad_encoded_data(encoded_data)
    byte_array = get_byte_array(padded_encoded_data)

    # Save compressed binary
    with open(output_path, 'wb') as f:
        f.write(bytes(byte_array))

    # Save metadata (freq table + image size)
    meta = {'freq': freq_dict, 'size': image.size}
    with open(meta_path, 'w') as f:
        json.dump(meta, f)

    print(f"Compressed to {output_path} with metadata in {meta_path}")

# Example usage
huffman_compress_image("your_image.png", "compressed.huff", "compressed_meta.json")
