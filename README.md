# 軒轅劍網路版｜高解析度重製底稿

本專案目標是保留《軒轅劍網路版》的早期 3D MMORPG 操作與介面結構，並以高解析度場景圖和縮放友善的畫面呈現。目前已重整登入、伺服器選擇、雙角色欄位、建角、遊戲 HUD，以及點擊移動、選擇目標、即時攻擊和 1–8 快捷技能等基本流程。這是可在瀏覽器執行的單機重製底稿，尚未接上原作伺服器或多人連線。

## 操作

- 點擊地面移動；點擊怪物選取並接近目標。
- `Q` 攻擊目前目標；`R` 切換走路／跑步；`Tab` 開啟地圖。
- `1`–`8` 使用側邊快捷技能。其他功能按鈕會開啟對應的介面面板。
- 角色資料儲存在目前瀏覽器的 localStorage。

## 本機預覽

在專案根目錄執行 `python -m http.server 8080`，再瀏覽 `http://localhost:8080`。

## Cloudflare Pages

這是無建置步驟的靜態網站。將 GitHub 儲存庫 `redfisharthur-beep/Sword-Online` 連接至 Cloudflare Pages，Production branch 設為 `main`，Build command 留空，Build output directory 設為 `.`。部署設定已記錄在 `wrangler.toml`。推送至 `main` 後，Cloudflare Pages 可依專案設定自動部署；目前尚未建立 Cloudflare 專案或發布網址。

## 後續重製範圍

目前畫面美術為重製用新素材，並非從原版客戶端提取；角色、地圖、職業、怪物和動畫還需依可核對的原版畫面與資料逐項校準。多人即時連線、帳號、伺服器存檔、完整技能／職業資料和更多場景尚未實作。
