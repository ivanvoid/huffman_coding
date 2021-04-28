from huffman import HuffmanCoding
import sys

def main(argv):
    filepath = argv[1]
    read_bit_size = 8
    
    if len(argv) > 2:
        read_bit_size = argv[2]
        print(read_bit_size)
        
    h = HuffmanCoding(filepath, read_bit_size)
    
    output_path = h.compress()
    print("Compressed file path: " + output_path)

    decom_path = h.decompress(output_path)
    print("Decompressed file path: " + decom_path)

if __name__ == '__main__':
    main(sys.argv)