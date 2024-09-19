import re
from itertools import groupby
import hashlib
import numpy as np

def simhash(content):
    content = content.lower()
    reg = r'[\w\u4e00-\u9fcc]+'
    content = ''.join(re.findall(reg, content))
    width = 3
    tokens = [content[i:i + width] for i in range(max(len(content) - width + 1, 1))]
    print(tokens)

    features = {k:sum(1 for _ in g) for k, g in groupby(sorted(tokens))}
    print(features)
    features = features.items()

    count = 0
    sums = []
    for f in features:
        f, w = f
        count += w
        h =  hashlib.md5(f.encode('utf-8')).digest()[-64 // 8:]
        print(h)
        print(np.frombuffer(h, dtype='>B'))
        print(np.unpackbits(np.frombuffer(h, dtype='>B')))
        #gettting binary values
        sums.append(np.unpackbits(np.frombuffer(h, dtype='>B')) * w)
        if len(sums) >= 200:
            #sum all bits
            sums = [np.sum(sums, 0)]

    sums = np.sum(sums, 0)
    print(sums)
    print(sums > count / 2)
    print(np.packbits(sums > count / 2))
    #keep bits with sum > count/2 (more 1s than 0s)
    value = int.from_bytes((np.packbits(sums > count / 2).tobytes()), 'big')
    return value

def distance(s1, s2):
    #diff with xor
    x = (s1 ^ s2)
    print(np.unpackbits(np.frombuffer(((1 << 64) -1).to_bytes(8, 'big'), dtype='>B')))
    print(np.unpackbits(np.frombuffer(x.to_bytes(8, 'big'), dtype='>B')))
    ans = 0
    while x:
        ans += 1
        #x-1 > switch rightmost 1 bit to 0
        #increment counter and then redo xor to find next diff bit
        x &= x - 1
        print(np.unpackbits(np.frombuffer(x.to_bytes(8, 'big'), dtype='>B')))
    return ans

def main():    
    print(distance(simhash('hello world'), simhash('hello world')))
    print(distance(simhash('hello world'), simhash('hello world2')))


if __name__ == "__main__":
    main()