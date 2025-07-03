import json
from PIL import Image
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

def decode_data(encoded_bits, tree, total_pixels):
    decoded_data = []
    current = tree
    for bit in encoded_bits:
        current = current.left if bit == '0' else current.right
        if current.symbol is not None:
            decoded_data.append(current.symbol)
            current = tree
            if len(decoded_data) == total_pixels:
                break
    return decoded_data

def huffman_decompress_image(huff_file, meta_file, output_image):
    # Load metadata
    with open(meta_file, 'r') as f:
        meta = json.load(f)
    freq_dict = {int(k): v for k, v in meta['freq'].items()}
    width, height = meta['size']
    total_pixels = width * height

    tree = build_huffman_tree(freq_dict)

    # Read bit stream
    with open(huff_file, 'rb') as f:
        byte = f.read(1)
        bits = ""
        while byte:
            bits += f"{ord(byte):08b}"
            byte = f.read(1)

    extra_padding = int(bits[:8], 2)
    bits = bits[8:]  # remove padding info
    bits = bits[:-extra_padding] if extra_padding else bits

    decoded_data = decode_data(bits, tree, total_pixels)
    image = Image.new('L', (width, height))
    image.putdata(decoded_data)
    image.save(output_image)
    print(f"Decompressed image saved as {output_image}")

# Example usage
huffman_decompress_image("compressed.huff", "compressed_meta.json", "decompressed.png")
