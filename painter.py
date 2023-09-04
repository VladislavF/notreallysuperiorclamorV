#!/usr/bin/env python3

from PIL import Image
import math
import struct


fftn = 768
out_cols = int(fftn/2)
lines = 6

image = Image.open("flag17.png")
#image = image.rotate(180)
image = image.transpose(Image.FLIP_LEFT_RIGHT)
in_cols, in_rows = image.size
out_rows = round(out_cols * in_rows / in_cols)

image = image.resize((out_cols, out_rows), Image.ANTIALIAS)
image = image.convert('L')
pixels = list(image.getdata())

with open('paint-mask.raw', 'wb') as f:
    for r in range(out_rows):
        row = pixels[r * out_cols:(r+1) * out_cols]
        for i in range(0, out_cols, lines-1):
            row[i] = 1
        row = [math.pow(10, (p / 255) * 0.99 - 0.5) for p in row]
        row = ([max(row)] * 1) + row[1:] + ([max(row)] * 1) + row[:0:-1]
        #print(len(row))
        for _ in range(lines):
            for i in range(fftn):
                f.write(struct.pack('ff', row[i]/100, 0))
