#!/usr/bin/env python3

from PIL import Image
import math
import struct

out_cols = 191

image = Image.open("flag17.png")
in_cols, in_rows = image.size
out_rows = round(out_cols * in_rows / in_cols)

image = image.rotate(180)
image = image.resize((out_cols, out_rows), Image.ANTIALIAS)
image = image.convert('L')
pixels = list(image.getdata())

with open('paint-mask.raw', 'wb') as f:
    for r in range(out_rows):
        row = pixels[r * out_cols:(r+1) * out_cols]
        for i in range(0, out_cols, 19):
            row[i] = 192
        row = [math.pow(10, (p / 255) * 0.8 - 0.4) for p in row]
        row = ([0] * 478) + row + ([0] * 711) + row + ([0] * 477)
        print(len(row))
        for _ in range(20):
            for i in range(2048):
                f.write(struct.pack('ff', row[i], 0))
