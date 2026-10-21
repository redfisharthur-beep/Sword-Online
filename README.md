# 軒轅劍網路版畫面重製

以使用者提供的兩張原作遊戲截圖作為目前視覺基準：4:3 遊戲畫面、第三人稱草地戰場、左側技能欄、右上狀態與雷達地圖、左下聊天、右下角色數值、底部綠色卷紋功能列。畫面改用高解析場景和透明角色素材，Canvas 依裝置像素比繪製並啟用高品質影像縮放。

目前程式包含登入／伺服器／角色欄位／建角流程、點地移動、選怪、靠近後自動攻擊、Q 攻擊、R 走跑切換、Tab 地圖，以及 1–8 技能列。技能名稱和人物初始數值，優先依提供的截圖可辨識內容重建。這是單機瀏覽器重製，沒有連上原作伺服器。

## 本機預覽

在專案根目錄執行 `python -m http.server 8080`，再開啟 `http://localhost:8080`。

## Cloudflare Workers

這是無建置步驟的靜態瀏覽器遊戲，使用 Cloudflare Workers Static Assets 部署。Workers Builds 設定：

- Production branch：`main`
- Root directory：`/`
- Build command：留空
- Deploy command：`npx wrangler deploy`

`wrangler.toml` 已指向專案根目錄的靜態檔案。推送到 `main` 後，Workers Builds 會部署至 `sword-online.workers.dev`（若已啟用 workers.dev 網域）。

## 待依原作資料校準

目前角色、猴子和場景是依截圖重製的高解析素材，不是原作客戶端模型／貼圖；行走與攻擊動畫、精確職業資料、完整任務故事、各地圖與怪物行為仍需逐項依原作影片、截圖或可用資料校對。聊天區、數值面板的已知內容已參照截圖，未提供的故事台詞不會自行補寫。
