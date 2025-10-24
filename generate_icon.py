#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont

# Create a 64x64 image with transparent background
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw nametag body (rounded rectangle badge shape)
draw.rounded_rectangle([(6, 14), (58, 50)], radius=6, fill='#E74C3C', outline='#C0392B', width=2)

# Draw pin/clip at top
draw.ellipse([(28, 8), (36, 16)], fill='#95A5A6', outline='#7F8C8D', width=1)
draw.rectangle([(30, 12), (34, 18)], fill='#95A5A6')

# Draw name lines (simulating text)
draw.rectangle([(12, 22), (52, 26)], fill='#FFFFFF')
draw.rectangle([(12, 30), (45, 34)], fill='#FFFFFF')
draw.rectangle([(12, 38), (42, 42)], fill='#FFFFFF')

# Save to res/mipmap-mdpi directory
img.save('res/mipmap-mdpi/icon_64x64.png', 'PNG', optimize=True)
print("Icon saved as res/mipmap-mdpi/icon_64x64.png")
