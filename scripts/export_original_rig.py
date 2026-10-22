#!/usr/bin/env python3
"""Extract empirically identified animation transforms from original CHR00001.PLY.

Original LZO1X-decompressed file, not standard Stanford PLY.
Observed: 44 homogeneous 4x4 row-major matrices per pose,
60 contiguous complete poses starting at offset 19916.
Joint labels/hierarchy, original FPS, mesh/UV/skin weights are unknown.
"""
import argparse
import json
import math
import struct
from pathlib import Path

OFFSET=19916
JOINTS=44
FRAMES=60
MATRIX_BYTES=64

def extract(data):
    required=OFFSET+JOINTS*FRAMES*MATRIX_BYTES
    if len(data)<required:
        raise ValueError(f"Need {required} bytes, found {len(data)}")
    frames=[]
    for frame in range(FRAMES):
        pose=[]
        for joint in range(JOINTS):
            at=OFFSET+(frame*JOINTS+joint)*MATRIX_BYTES
            m=struct.unpack_from("<16f",data,at)
            if not all(math.isfinite(v) for v in m):
                raise ValueError(f"Nonfinite matrix: frame={frame}, joint={joint}")
            if any(abs(a-b)>0.0001 for a,b in zip(m[12:],(0,0,0,1))):
                raise ValueError(f"Not homogeneous matrix: frame={frame}, joint={joint}")
            pose.append([round(m[3],4),round(m[7],4),round(m[11],4)])
        frames.append(pose)
    return {"source":"MODEL/CHR00001.PLY","matrix_offset":OFFSET,
            "matrix_stride":MATRIX_BYTES,"joint_count":JOINTS,
            "frame_count":FRAMES,"fps":"unknown","positions":frames}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decompressed_ply",type=Path)
    parser.add_argument("--out",type=Path,default=Path("CHR00001_rig_frames.json"))
    args=parser.parse_args()
    result=extract(args.decompressed_ply.read_bytes())
    args.out.write_text(json.dumps(result,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print(f"Exported {FRAMES} poses x {JOINTS} original joint transforms to {args.out}")

if __name__=="__main__":
    main()
