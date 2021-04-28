import abc

class Abstract_Huffman(abc.ABC):
    def __init__(self, path, read_bit_size=8):
        self.path = path
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}
        self.read_bit_size = read_bit_size
        
