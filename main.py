import re
from itertools import groupby
import hashlib
import numpy as np
import collections

def simhash(content):
    content = content.lower()
    reg = r'[\w\u4e00-\u9fcc]+'
    content = ''.join(re.findall(reg, content))
    width = 3
    tokens = [content[i:i + width] for i in range(max(len(content) - width + 1, 1))]
    #print(tokens)

    features = {k:sum(1 for _ in g) for k, g in groupby(sorted(tokens))}
    #print(features)
    features = features.items()

    count = 0
    sums = []
    for f in features:
        f, w = f
        count += w
        h =  hashlib.md5(f.encode('utf-8')).digest()[-64 // 8:]
        #print(h)
        #print(np.frombuffer(h, dtype='>B'))
        #print(np.unpackbits(np.frombuffer(h, dtype='>B')))
        #gettting binary values
        sums.append(np.unpackbits(np.frombuffer(h, dtype='>B')) * w)
        if len(sums) >= 200:
            #sum all bits
            sums = [np.sum(sums, 0)]

    sums = np.sum(sums, 0)
    #print(sums)
    #print(sums > count / 2)
    #print(np.packbits(sums > count / 2))
    #keep bits with sum > count/2 (more 1s than 0s)
    value = int.from_bytes((np.packbits(sums > count / 2).tobytes()), 'big')
    return value

def distance(s1, s2):
    #diff with xor
    x = (s1 ^ s2)
    #print(np.unpackbits(np.frombuffer(((1 << 64) -1).to_bytes(8, 'big'), dtype='>B')))
    #print(np.unpackbits(np.frombuffer(x.to_bytes(8, 'big'), dtype='>B')))
    ans = 0
    while x:
        ans += 1
        #x-1 > switch rightmost 1 bit to 0
        #increment counter and then redo xor to find next diff bit
        x &= x - 1
        #print(np.unpackbits(np.frombuffer(x.to_bytes(8, 'big'), dtype='>B')))
    return ans

def get_keys(simhash):
    #number of offsets according to precision, here precision = 3
    offsets = [64 // (2 + 1) * i for i in range(2 + 1)]
    #print(offsets)

    for i, offset in enumerate(offsets):
        #m = mask => size computed from step between offsets
        if i == (len(offsets) - 1):
            m = 2 ** (64 - offset) - 1
        else:
            m = 2 ** (offsets[i + 1] - offset) - 1
        #print(offset)
        #print(simhash >> offset)
        #print(m)
        #take into account a "window" of bits of simhash value => rightmost bits then shift bits to the right to have a look at the bits to the left for next iteration etc.
        c = simhash >> offset & m
        #print(c)
        yield '%x:%x' % (c, i)


def main():    
    simhash1 = simhash('hello world')
    simhash2 = simhash('hello world2')
    simhash3 = simhash('nope')

    bucket = collections.defaultdict(set)

    #add docs
    for key in get_keys(simhash1):
        v = '%x,%s' % (simhash1, '1')
        bucket[key].add(v)

    for key in get_keys(simhash2):
        v = '%x,%s' % (simhash2, '2')
        bucket[key].add(v)

    for key in get_keys(simhash3):
        v = '%x,%s' % (simhash3, '3')
        bucket[key].add(v)

    search = simhash('hello worldT')
    #print(f'distance : {distance(simhash1, search)}')

    #search near duplicates
    ans = set()
    for key in get_keys(search):
        dups = bucket[key]
        for dup in dups:
            sim2, obj_id = dup.split(',', 1)
            d = distance(search, int(sim2, 16))
            print(f'distance : {d} obj id : {obj_id}')
            if d <= 3:
                ans.add(obj_id)

    print(f'found id: {list(ans)}')

if __name__ == "__main__":
    main()

