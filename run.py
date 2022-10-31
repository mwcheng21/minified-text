import chunk
from typing import List, Optional

from dahuffman import load_shakespeare, HuffmanCodec
from bitstring import Bits
import numpy as np
from english_words import english_words_set
import math
import random
import requests
import pickle
import json
import nltk
nltk.download('words')
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.corpus import words as nltk_words
from nltk.corpus import wordnet

# -----------------------------------------------------------------------------
#   Codec
# -----------------------------------------------------------------------------

class Huffman:

    def __init__(
            self,
            dictionary: Optional[List[str]] = None
    ) -> None:
        if dictionary is not None:
            try:
                self.codec = HuffmanCodec.from_data(''.join(dictionary))
            except:
                self.codec = HuffmanCodec.from_frequencies(dictionary)
        else:
            self.codec = load_shakespeare()

    def _add_padding(self, msg: Bits, padding_len: int) -> Bits:

        padding_bits = '{0:b}'.format(0).zfill(padding_len) if padding_len > 0 else ''
        padded_msg_bin = '0b{}{}'.format(padding_bits, msg.bin)

        padded_msg = Bits(bin=padded_msg_bin)
        return padded_msg

    def _remove_padding(self, msg: Bits, padding_len: int) -> Bits:
        original_encoding = Bits(bin=f'0b{msg.bin[padding_len:]}')


        return original_encoding

    def encode(
            self,
            msg: str,
            padding_len: int = 5
    ) -> Bits:
        bytes = self.codec.encode(msg)
        bits = Bits(bytes=bytes)
        padded_bits = self._add_padding(bits, padding_len)

        return padded_bits

    def decode(
            self,
            bits: Bits,
            padding_len: int = 5
    ) -> str:
        bits = self._remove_padding(bits, padding_len)
        decoded = self.codec.decode(bits.tobytes())

        return decoded
# -----------------------------------------------------------------------------
#   Unit Tests
# -----------------------------------------------------------------------------

def test_huffman_codec():
    # Note: shakespeare codec doesn't seem to be able to handle punctuations
    cases = ['group 3', 'magic code']

    huffman = Huffman()
    for tc in cases:
        orig = tc
        encoded = huffman.encode(orig)
        decoded = huffman.decode(encoded)

        assert type(encoded) == Bits, 'error: encoded message is not of type Bits!'
        assert orig == decoded, 'error: decoded message is not the same as the original'

    print('PASSED: Huffman codec using pre-traind shakespeare text')

    cases = ['group 3', 'magic code', 'hi!']
    huffman = Huffman(dictionary=cases)
    for tc in cases:
        orig = tc
        encoded = huffman.encode(orig)
        decoded = huffman.decode(encoded)

        assert type(encoded) == Bits, 'error: encoded message is not of type Bits!'
        assert orig == decoded, 'error: decoded message is not the same as the original'

    print('PASSED: Huffman codec using dictionary')

def get_bit_chunk_freq(words):
    letter_freq = {}

    for word in words:
        for letter in word:
            if letter in letter_freq:
                letter_freq[letter] += 1
            else:
                letter_freq[letter] = 1

    print("Letter frequency: ", letter_freq)

    # huffman = Huffman(letter_freq)
    # frequency = {}

    # chunk_size = 5
    # a = 0
    # for word in words:
    #     bit_len = len(huffman.encode(word, padding_len=0).bin)
    #     padding =  (chunk_size - (bit_len % chunk_size)) % chunk_size
    #     encoded = huffman.encode(word, padding_len=padding).bin
    #     parts = [str(encoded)[i:i+chunk_size] for i in range(0, len(str(encoded)), chunk_size)]
    #     for part in parts:
    #         if part not in frequency:
    #             frequency[part] = 0
    #         frequency[part] += 1
    #     a += bit_len


def minify_list():
    try:
        # might need to apt-get install --reinstall wamerican
        with open('/usr/share/dict/american-english', 'r') as f:
            words = f.read().splitlines()
    except:
        print("might need to run apt-get install --reinstall wamerican")
        words = []

    words += nltk_words.words() + list(wordnet.words() )
    words = list(set(words))

    print(len(words))
    cutoff = 2


    abrev2word = {word:word for word in words if len(word) <= cutoff}
    words = [word for word in words if len(word) > cutoff]
    
    # sort words by word len 
    # TODO: sort by frequency
    words = sorted(words, key=len)

    letters_by_freq = ['e', 't', 'a', 'o', 'i', 'n', 's', 'h', 'r', 'd', 'l', 'c', 'u', 'm', 'w', 'f', 'g', 'y', 'p', 'b', 'v', 'k', 'j', 'x', 'q', 'z']
    letters_by_freq.reverse()
    letters_by_freq = letters_by_freq[:4]
    letters_by_freq = []

    random.seed(1)
    words_seen = set()
    for word in words:
        if word in words_seen:
            continue
        words_seen.add(word)

        modified_word = word
        while modified_word not in abrev2word:
            actual_modified_word = modified_word
            # remove random letter from word
            if len(modified_word) <= 1:
                break
            # for letter in letters_by_freq:
            #     idx = modified_word.find(letter)
            #     if idx != -1:
            #         modified_word = modified_word[:idx] + modified_word[idx+1:]
            #         break
            for letter_idx in range(1, len(modified_word)-1):
                if modified_word[letter_idx] in letters_by_freq:
                    modified_word = modified_word[:letter_idx] + modified_word[letter_idx+1:]
                    break
            else:
                index = random.randint(1, len(modified_word)-1)
                modified_word = modified_word[:index] + modified_word[index+1:]
        abrev2word[actual_modified_word] = word


    print("average word length")
    print(f"before {sum([len(word) for word in abrev2word.values()])/len(abrev2word.values())}")
    print(f"after {sum([len(word) for word in abrev2word.keys()])/len(abrev2word.keys())}")

    word2abrev = {val:key for key, val in abrev2word.items()}

    print("writing to file ./minified.txt, json dumps in minifiedDicts")
    with open('minifiedDicts', 'wb') as f:
        pickle.dump([abrev2word, word2abrev], f)

    # To load    
    # with open('minifiedDicts', 'rb') as f:
    #     abrev2word, word2abrev = pickle.load(f)
    #     print(abrev2word['ys'])

    with open('minified.txt', 'w') as f:
        for key, val in abrev2word.items():
            f.write(f"{key} {val}\n")
    print(word2abrev["name"])
    return abrev2word

mini = minify_list()
get_bit_chunk_freq(mini.keys())