import heapq
import os
from tqdm import tqdm 
import numpy as np
import hashlib

import resource, sys
resource.setrlimit(resource.RLIMIT_STACK, (2**29,-1))
sys.setrecursionlimit(10**6)

class HuffmanCoding:
    def __init__(self, path, read_bit_size=8):
        self.path = path
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}
        self.read_bit_size = read_bit_size

    class HeapNode:
        def __init__(self, char, freq):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None

        # defining comparators less_than and equals
        def __lt__(self, other):
            return self.freq < other.freq

        def __eq__(self, other):
            if(other == None):
                return False
            if(not isinstance(other, HeapNode)):
                return False
            return self.freq == other.freq

    # functions for compression:

    def make_frequency_dict(self, text):
        frequency = {}
        N = len(text)
        
        if self.read_bit_size == 8:
            _text = np.zeros(N//2, dtype=int)

            for j, i in tqdm(enumerate(range(1, N, 2))):
                ext_char = int(str(text[i-1]) + str(text[i]))
                _text[j] = ext_char
            for ext_char in tqdm(np.unique(_text)):
                frequency[ext_char] = (_text == ext_char).sum()
        else:
            # 32 + 32 = 64 codeword
            step = 32//4
            _text = []

            for j, i in tqdm(enumerate(range(step, N, step)), desc='count'):
#                 code = ''.join([str(f) for f in text[i-step:i]]) 
                code = str(text[i-step:i])
                if code not in frequency:
                    frequency[code] = 1
                    _text.append(code)
                else:
                    frequency[code] += 1
        self._text = _text
        
        return frequency

    def make_heap(self, frequency):
        for key in frequency:
            node = self.HeapNode(key, frequency[key])
            heapq.heappush(self.heap, node)

    def merge_nodes(self):
        while(len(self.heap)>1):
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)

            merged = self.HeapNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2

            heapq.heappush(self.heap, merged)


    def make_codes_helper(self, root, current_code):
        if(root == None):
            return

        if(root.char != None):
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return

        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")


    def make_codes(self):
        root = heapq.heappop(self.heap)
        current_code = ""
        self.make_codes_helper(root, current_code)


#     def get_encoded_text(self, text):
#         encoded_text = ""
#         for character in tqdm(text):
#             encoded_text += self.codes[character]
#         return encoded_text


#     def pad_encoded_text(self, encoded_text):
#         extra_padding = 8 - len(encoded_text) % 8
#         for i in tqdm(range(extra_padding)):
#             encoded_text += "0"

#         padded_info = "{0:08b}".format(extra_padding)
#         encoded_text = padded_info + encoded_text
#         return encoded_text


    def get_byte_array(self, padded_encoded_text):
        if(len(padded_encoded_text) % 8 != 0):
            print("Encoded text not padded properly")
            exit(0)

        b = bytearray()
        for i in tqdm(range(0, len(padded_encoded_text), 8)):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b

    def compress(self):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + ".bin"
        print('Reading...')
        with open(self.path, 'rb+') as file, open(output_path, 'wb') as output:
            text = file.read()
            text = text.rstrip()
            print('Freq dict...')
            frequency = self.make_frequency_dict(text)
            print('Make heap...')
            self.make_heap(frequency)
            print('Merge nodes')
            self.merge_nodes()
            print('Make codes')
            self.make_codes()
            
            '''<GARBAGE>'''
            import csv
#             w = csv.writer(open("freq.csv", "w"))
#             for key, val in frequency.items():
#                 w.writerow([key, val])
            w = csv.writer(open("ext_codes.csv", "w"))
            for key, val in self.codes.items():
                w.writerow([key, val])
            '''<\GARBAGE>'''
            
            print('Encoding...')
            self.write2file(output, self._text)
#             encoded_text = self.get_encoded_text(self._text)
#             padded_encoded_text = self.pad_encoded_text(encoded_text)

#             b = self.get_byte_array(padded_encoded_text)
#             output.write(bytes(b))

        print("Compressed")
        return output_path

    def write2file(self, file, text):
        current_bstr = bytearray()
        tail2 = ''
        
        for i in tqdm(range(1, len(text), 2), desc='main'):
#         for i in range(1, len(text), 2):
            ch1 = text[i-1]
            ch2 = text[i]
            
            encod1 = self.codes[ch1]
            encod2 = self.codes[ch2]
            
#             print()
#             print(encod1, encod2)
            
            # full part 
            encod1 = tail2 + encod1
#             for e in tqdm(range(0,(len(encod1)//8)), leave=False, desc='E1'):
            k = 0
            for e in range(0,len(encod1)//8):
                encod = encod1[e*8:(e+1)*8]
                current_bstr.append(int(encod,2))
                k += 1
            
            idx = len(encod1) % 8
            if idx == 0:
                tail1 = ''
            else:
                tail1 = encod1[-idx:]

            encod2 = tail1 + encod2

#             for e in tqdm(range(0,(len(encod2)//8)),leave=False,desc='E2'):
            for e in range(0,len(encod2)//8):
                encod = encod2[e*8:(e+1)*8]
                current_bstr.append(int(encod,2))
            
            tail2 = len(encod2) % 8
            tail2 = encod2[-tail2:]
#           
#             print(current_bstr)
#             print(tail2)
        
            # Write 64 bytes to file and drop them
#             print('BSTR_LEN:\t',len(current_bstr))
#             print('TAIL1:\t',len(tail1))
#             print('TAIL2:\t',len(tail2))
            
            for i in range(len(current_bstr)//64):
                b_str = current_bstr[:64]
                file.write(bytes(b_str))
                current_bstr = current_bstr[64:]
            if len(current_bstr) > 64:
                print(len(current_bstr))

        # After 
        for i in range(len(tail2)//8):
                b_str = tail2[:8]
                file.write(bytes(b_str))
                tail2 = tail2[8:]
        if len(tail2) < 8:
            extra_padding = 8 - len(tail2) % 8
            tail2 += "0"*extra_padding
        file.write(bytes(int(tail2,2)))


    """ functions for decompression: """


    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)

        padded_encoded_text = padded_encoded_text[8:] 
        encoded_text = padded_encoded_text[:-1*extra_padding]

        return encoded_text

    def decode_text(self, encoded_text):
        current_code = ""
        decoded_text = ""

        for bit in encoded_text:
            current_code += bit
            if(current_code in self.reverse_mapping):
                character = self.reverse_mapping[current_code]
                decoded_text += chr(character)
                current_code = ""

        return decoded_text


    def decompress(self, input_path):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + "_decompressed" + ".txt"

        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ""

            byte = file.read(1)
            while(len(byte) > 0):
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)

            encoded_text = self.remove_padding(bit_string)

            decompressed_text = self.decode_text(encoded_text)
            
            output.write(decompressed_text)

        print("Decompressed")
        return output_path

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