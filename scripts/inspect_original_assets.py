#!/usr/bin/env python3
"""Read-only investigation of original Sword Online asset archives.
Never treats proprietary PLY as Stanford PLY or proprietary TEX as an image.
Usage: python3 scripts/inspect_original_assets.py MODEL.zip TEX.zip --out original-audit
"""
from __future__ import annotations
import argparse
import csv
import json
import struct
import zipfile
from collections import Counter
from pathlib import Path

def inspect_archive(path: Path, output: Path):
    with zipfile.ZipFile(path) as archive:
        rows = []
        counts = Counter()
        signature_samples = {}
        anomalies = []
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            suffix = Path(entry.filename).suffix.lower()
            counts[suffix or "(none)"] += 1
            with archive.open(entry) as stream:
                header = stream.read(32)
            magic = header[:4]
            kind = "unknown"
            if magic == b"SS3D":
                kind = "s3d-container"
            elif magic == b"WLD\x00":
                kind = "wld-container"
            elif magic == b"RIFF" and header[8:12] == b"WAVE":
                kind = "wav"
            elif header[:3] == b"ID3" or header[:2] in (b"\xff\xfb", b"\xff\xf3"):
                kind = "mp3"
            elif header[:7] == b"IDX_PLY":
                kind = "index"
            elif suffix in (".ply", ".tex") and len(header) >= 8:
                unpacked, packed = struct.unpack_from("<II", header)
                if packed == entry.file_size - 8 and unpacked >= packed:
                    kind = "custom-packed"
                else:
                    anomalies.append({"file":entry.filename,"reason":"Unexpected proprietary header"})
            rows.append({"path":entry.filename,"extension":suffix,"bytes":entry.file_size,
                         "kind":kind,"header_hex":header[:16].hex(),
                         "crc32":f"{entry.CRC:08x}"})
            if kind not in signature_samples:
                signature_samples[kind] = entry.filename
        output.mkdir(parents=True, exist_ok=True)
        with (output / f"{path.stem}_manifest.csv").open("w",newline="",encoding="utf-8-sig") as f:
            writer=csv.DictWriter(f,fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return {"archive":path.name,"files":len(rows),"extensions":dict(counts),
                "signature_samples":signature_samples,"anomalies":anomalies[:30]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("archives",type=Path,nargs="+")
    p.add_argument("--out",type=Path,default=Path("original-audit"))
    args=p.parse_args()
    result=[inspect_archive(path,args.out) for path in args.archives]
    (args.out/"summary.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    for row in result:
        print(f"{row['archive']}: {row['files']} files; kinds: {row['signature_samples']}")
    print("Saved to",args.out)

if __name__=="__main__":
    main()
