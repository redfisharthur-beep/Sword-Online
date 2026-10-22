#!/usr/bin/env python3
"""Extract original LZO1X game assets without substituting modern artwork.

Requires Python 3 and liblzo2 (Linux package liblzo2-2).
Optional Pillow for --png. Original TEX files are 16-bit RGB555 with
six bytes of row overhead. Uncompressed PLY is a proprietary binary model,
NOT Stanford PLY; no false conversion to GLB is attempted.
"""
import argparse
import ctypes
import ctypes.util
import struct
import zipfile
from pathlib import Path

def unpack(data):
    if len(data)<8: raise ValueError("Missing size header")
    raw_size, compressed_size=struct.unpack_from("<II",data)
    if compressed_size != len(data)-8 or raw_size>128*1024*1024:
        raise ValueError("Unexpected packed length")
    path=ctypes.util.find_library("lzo2")
    if not path: raise RuntimeError("liblzo2 is required")
    lib=ctypes.CDLL(path)
    lib.lzo1x_decompress_safe.argtypes=[
        ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_size_t),ctypes.c_void_p]
    lib.lzo1x_decompress_safe.restype=ctypes.c_int
    output=ctypes.create_string_buffer(raw_size)
    length=ctypes.c_size_t(raw_size)
    packed=ctypes.create_string_buffer(data[8:])
    rc=lib.lzo1x_decompress_safe(packed,compressed_size,output,ctypes.byref(length),None)
    if rc!=0 or length.value!=raw_size:
        raise ValueError(f"LZO1X decode failed: {rc}, {length.value}/{raw_size}")
    return output.raw

def tex_to_png(data,dest,transparent=False):
    from PIL import Image
    if data[:2]!=b"\xff\xff": raise ValueError("Unsupported TEX marker")
    w,h=struct.unpack_from("<HH",data,2)
    if not 1<=w<=8192 or not 1<=h<=8192: raise ValueError("Invalid dimensions")
    # Row: 6-byte original engine metadata, followed by width 16-bit pixels.
    if len(data)!=6+h*(6+w*2):
        raise ValueError(f"Unsupported TEX layout: {len(data)} bytes for {w}x{h}")
    rgba=bytearray(w*h*4)
    for y in range(h):
        start=12+y*(w*2+6)
        for x in range(w):
            v=struct.unpack_from("<H",data,start+x*2)[0]
            p=(y*w+x)*4
            rgba[p:p+4]=bytes(((v>>10&31)*255//31,(v>>5&31)*255//31,(v&31)*255//31,
                                  0 if transparent and v==0 else 255))
    im=Image.frombytes("RGBA",(w,h),bytes(rgba))
    dest.parent.mkdir(parents=True,exist_ok=True)
    im.save(dest)
    return (w,h)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archive",type=Path)
    ap.add_argument("member",help="Exact case-sensitive path inside ZIP")
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--png",action="store_true",help="Decode RGB555 TEX to PNG")
    ap.add_argument("--transparent-zero",action="store_true",help="Make RGB555 zero transparent")
    args=ap.parse_args()
    with zipfile.ZipFile(args.archive) as z:
        data=unpack(z.read(args.member))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    if args.png:
        print("Original texture decoded:",tex_to_png(data,args.out,args.transparent_zero))
    else:
        args.out.write_bytes(data)
        print("Original binary decompressed:",len(data),"bytes",args.out)

if __name__=="__main__":
    main()
