# 原版角色動作矩陣檢視器

此檢視器不是重繪的人物；它直接顯示 `MODEL/CHR00001.PLY` 已解壓區塊中的 44×60 組 4×4 變換矩陣。

## 本機使用

```sh
python3 scripts/extract_character_rig.py --model-zip /path/to/MODEL.zip --out tools/original-character-viewer/rig_frames.json
python3 -m http.server 8000
```

開啟 `http://localhost:8000/tools/original-character-viewer/`。瀏覽器須能連線載入 Three.js。原始 `MODEL.zip` 不放進公開儲存庫；產出的 `rig_frames.json` 不自動提交。

已驗證矩陣從解壓後偏移 `19916` 開始，44 個節點，每節點 16 個 float32，連續 60 組姿態。已檢查姿態間有實際變化、變換矩陣末元素約為 1。

**仍未驗證**：骨架父子階層、每個節點的語義、原始幀率、頂點、三角面、UV、蒙皮權重、角色材質與骨骼對應。檢視器的連接線是基於距離與穩定性推估的鄰接圖，並非已解碼的原始骨架。只有完成網格及蒙皮關係驗證後才能輸出忠實角色 GLB。
