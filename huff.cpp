#include <iostream>
#include <fstream>
#include <vector>
#include <unordered_map>
#include <queue>
#include <bitset>

struct Node {
    unsigned char pixel;
    int freq;
    Node *left, *right;

    Node(unsigned char p, int f) : pixel(p), freq(f), left(nullptr), right(nullptr) {}
};

// Comparator for min-heap
struct Compare {
    bool operator()(Node* a, Node* b) {
        return a->freq > b->freq;
    }
};

// Build frequency map
std::unordered_map<unsigned char, int> buildFrequency(const std::vector<unsigned char>& data) {
    std::unordered_map<unsigned char, int> freq;
    for (auto pixel : data)
        freq[pixel]++;
    return freq;
}

// Build Huffman tree
Node* buildHuffmanTree(const std::unordered_map<unsigned char, int>& freq) {
    std::priority_queue<Node*, std::vector<Node*>, Compare> pq;
    for (const auto& pair : freq)
        pq.push(new Node(pair.first, pair.second));

    while (pq.size() > 1) {
        Node* left = pq.top(); pq.pop();
        Node* right = pq.top(); pq.pop();
        Node* merged = new Node(0, left->freq + right->freq);
        merged->left = left;
        merged->right = right;
        pq.push(merged);
    }
    return pq.top();
}

// Generate Huffman codes
void generateCodes(Node* root, std::string code,
                   std::unordered_map<unsigned char, std::string>& codes) {
    if (!root) return;
    if (!root->left && !root->right)
        codes[root->pixel] = code;
    generateCodes(root->left, code + "0", codes);
    generateCodes(root->right, code + "1", codes);
}

// Encode data
std::string encodeData(const std::vector<unsigned char>& data,
                       const std::unordered_map<unsigned char, std::string>& codes) {
    std::string encoded;
    for (auto pixel : data)
        encoded += codes.at(pixel);
    return encoded;
}

// Pad to byte boundary
std::string padEncodedData(std::string encoded) {
    int extraBits = 8 - (encoded.size() % 8);
    if (extraBits == 8) extraBits = 0;
    encoded.append(extraBits, '0');
    return std::bitset<8>(extraBits).to_string() + encoded; // first 8 bits store padding
}

// Write binary file
void writeBinaryFile(const std::string& filename, const std::string& bits) {
    std::ofstream out(filename, std::ios::binary);
    for (size_t i = 0; i < bits.size(); i += 8) {
        std::bitset<8> byte(bits.substr(i, 8));
        out.put(static_cast<unsigned char>(byte.to_ulong()));
    }
}

int main() {
    // Load PGM file (assumes P5 binary format)
    std::ifstream in("image.pgm", std::ios::binary);
    std::string line;
    getline(in, line); // P5
    getline(in, line); // skip comment or width height
    while (line[0] == '#') getline(in, line);
    int width, height, maxval;
    std::istringstream(line) >> width >> height;
    in >> maxval;
    in.get(); // consume newline

    std::vector<unsigned char> data(width * height);
    in.read(reinterpret_cast<char*>(data.data()), data.size());

    // Build frequency & Huffman tree
    auto freq = buildFrequency(data);
    Node* root = buildHuffmanTree(freq);

    // Generate codes
    std::unordered_map<unsigned char, std::string> codes;
    generateCodes(root, "", codes);

    // Encode
    std::string encoded = encodeData(data, codes);
    std::string padded = padEncodedData(encoded);

    // Write to file
    writeBinaryFile("compressed.huff", padded);

    std::cout << "Compressed image to compressed.huff\n";
    return 0;
}
