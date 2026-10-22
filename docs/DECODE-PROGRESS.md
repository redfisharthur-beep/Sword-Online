# 原版角色與貼圖還原：首次成功解壓（2026-10-22）

## 已驗證的突破

**原始 PLY / TEX 檔案的 8-byte header 是兩個 little-endian u32：解壓後大小、壓縮資料大小。**
其後是 **LZO1X** 壓縮資料，透過 `liblzo2.so.2` 的 `lzo1x_decompress_safe` 驗證：
- `MODEL/CHR00001.PLY`：112,107 壓縮資料 bytes → **202,484 解壓 bytes**，回傳 0。
- `TEX/ALL00000.TEX`：26,513 → **132,622 bytes**，回傳 0。
- `TEX/ALL00001.TEX`：436,170 → **963,610 bytes**，回傳 0。

**貼圖格式也已驗證**：解壓後開頭是 `FF FF`、寬高各 16-bit little endian，接著每列六位元組的原引擎資訊，再接每像素 16-bit RGB555。實測 `ALL00001.TEX` 能解出**真正的 800×600 原版遊戲截圖**；`ALL00000.TEX` 解出 **256×256 彩虹光效**。不是 AI 生成，也不是臨時替代圖。

## 重現

```bash
python3 -m pip install pillow
# Ubuntu/Debian: sudo apt-get install liblzo2-2
python3 scripts/decode_original_assets.py MODEL.zip MODEL/CHR00001.PLY --out decoded/CHR00001.bin
python3 scripts/decode_original_assets.py TEX.zip TEX/ALL00001.TEX --out decoded/ALL00001.png --png
python3 scripts/decode_original_assets.py TEX.zip TEX/ALL00000.TEX --out decoded/ALL00000.png --png --transparent-zero
```

## 仍待完成
- `CHR00001.PLY` 解壓成功，但其內部**仍是專有 3D 網格資料**，不是標準 PLY。尚未解析頂點、三角面、UV、骨架與動畫。
- `ALL00001.TEX` 是原版畫面截圖，不代表它是 `CHR00001.PLY` 的角色材質。角色貼圖需要用 IDX / TSW 對應。
- `Act/all_char.act` 尚未解析為可用的動作曲線。
- 因此**尚未生成可信的原版角色 GLB、貼圖綁定或可播放動作**。目前沒有替換遊戲中的角色模型，避免錯誤復刻。
