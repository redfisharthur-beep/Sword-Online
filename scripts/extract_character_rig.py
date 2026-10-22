#!/usr/bin/env python3
"""Extract original CHR00001.PLY animation transforms to browser-readable JSON.

The identified contiguous section contains 60 poses of 44 row-major 4x4
matrices. This tool deliberately DOES NOT claim to decode mesh geometry,
skin weights, joint names, or original frame rate.
"""
import argparse
import json
import math
import struct
from pathlib import Path
from decode_original_assets import unpack
import zipfile

JOINTS=44
FRAMES=60
MATRIX_SIZE=64
KNOWN_OFFSET=19916

def extract(data,offset=KNOWN_OFFSET):
    needed=FRAMES*JOINTS*MATRIX_SIZE
    if len(data)<offset+needed:
        raise ValueError("PLY data too short for known CHR00001 matrix block")
    frames=[]
    for frame in range(FRAMES):
        pose=[]
        for joint in range(JOINTS):
            m=struct.unpack_from("<16f",data,offset+(frame*JOINTS+joint)*MATRIX_SIZE)
            if not all(math.isfinite(v) for v in m):
                raise ValueError(f"Non-finite transform at frame {frame}, joint {joint}")
            if abs(m[15]-1)>0.01:
                raise ValueError(f"Not a homogeneous transform: frame {frame}, joint {joint}")
            pose.append([round(m[3],5),round(m[7],5),round(m[11],5)])
        frames.append(pose)
    return frames

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-zip",type=Path)
    ap.add_argument("--ply",type=Path)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    if bool(args.model_zip)==bool(args.ply):
        ap.error("Provide exactly one of --model-zip or --ply")
    if args.model_zip:
        with zipfile.ZipFile(args.model_zip) as z:
            data=unpack(z.read("MODEL/CHR00001.PLY"))
    else:
        data=args.ply.read_bytes()
    frames=extract(data)
    output={"source":"MODEL/CHR00001.PLY","matrix_offset":KNOWN_OFFSET,
        "joint_count":JOINTS,"frame_count":FRAMES,
        "frame_rate":"unknown (preview uses 12 fps only as a display assumption)",
        "geometry_status":"not decoded","skin_weights_status":"not decoded",
        "frames":frames}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print(f"Validated {FRAMES} original poses with {JOINTS} transforms each:",args.out)

if __name__=="__main__":
    main()
