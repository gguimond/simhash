import re
from itertools import groupby
import hashlib
import numpy as np


def main():
    content = 'hello world'
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
        sums.append(np.unpackbits(np.frombuffer(h, dtype='>B')) * w)
        if len(sums) >= 200:
            sums = [np.sum(sums, 0)]

    sums = np.sum(sums, 0)
    print(sums)
    print(sums > count / 2)
    print(np.packbits(sums > count / 2))

    value = int.from_bytes((np.packbits(sums > count / 2).tobytes()), 'big')
    print(value)

if __name__ == "__main__":
    main()