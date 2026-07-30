import struct
import zlib

def create_png(width, height, color_r, color_g, color_b):
    """Create a minimal PNG with a colored circle background"""
    def write_chunk(chunk_type, data):
        chunk = chunk_type + data
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
    
    # PNG signature
    signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = write_chunk(b'IHDR', ihdr_data)
    
    # IDAT - raw image data
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # filter byte
        for x in range(width):
            # Simple circle
            cx, cy = width//2, height//2
            r = min(width, height)//2 - 4
            dx, dy = x - cx, y - cy
            if dx*dx + dy*dy <= r*r:
                raw_data += bytes([color_r, color_g, color_b])
            else:
                raw_data += bytes([255, 255, 255])
    
    compressed = zlib.compress(raw_data)
    idat = write_chunk(b'IDAT', compressed)
    
    # IEND
    iend = write_chunk(b'IEND', b'')
    
    return signature + ihdr + idat + iend

# Create icons
png64 = create_png(64, 64, 79, 70, 229)
with open('fpk/app/ui/images/icon.png', 'wb') as f:
    f.write(png64)
print('icon.png (64x64) created')

png256 = create_png(256, 256, 79, 70, 229)
with open('fpk/app/ui/images/icon_256.png', 'wb') as f:
    f.write(png256)
print('icon_256.png (256x256) created')
