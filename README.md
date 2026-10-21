# 軒轅劍網路版・瀏覽器重製

可直接部署到 Cloudflare 的單機瀏覽器遊戲。經典 4:3 綠金 HUD、青綠登入場景、角色建立、探索戰鬥、技能熟練、商店補給與本機存檔。這是持續製作中的重製版，尚未達到原版全部內容一致；多人、真正帳號、交易和公會尚未實作。[內容來源與完成範圍](docs/REMAKE-SOURCES.md)。

## 本機執行

需要 Python 3，遊戲本身不需要 npm 套件、資料庫或 API 金鑰。

```sh
python3 scripts/build.py
python3 -m http.server 8080 --directory public
```

在瀏覽器開啟本機伺服器，點「訪客登入」→「進入遊戲」。可先建立自己的人物，再找港口嚮導查看操作及前往雜貨舖。進度儲存在目前瀏覽器；系統設定可匯出/匯入 JSON 存檔。登入名稱僅供本機展示，不是線上帳號，不收集密碼。

## Cloudflare Workers 部署（建議）

在 Cloudflare Workers 連接此 GitHub 儲存庫，設定：

| 設定 | 值 |
| --- | --- |
| Production branch | `main` |
| Root directory | 儲存庫根目錄 |
| Build command | 留空（Wrangler 自動執行建置） |
| Deploy command | `npx wrangler deploy` |

`wrangler.toml` 的 `[build]` 會在部署前自動執行 `python3 scripts/build.py`，產生 `public/`；只複製遊戲必需的公開檔案。部署成功後即可由 Cloudflare 提供的網址遊玩。若已連接 Workers Builds，推送至 `main` 會觸發部署；須以 Cloudflare 的實際部署結果為準。

若使用 **Cloudflare Pages**：Framework preset 選 None，Build command 設為 `python3 scripts/build.py`，Build output directory 設為 `public`，不需 Workers deploy command。

不要將原始儲存庫根目錄直接作為公開目錄。`public/` 為生成檔，不提交 Git；每次由 Wrangler 自動重建。既有 Workers 設定只需保留 `npx wrangler deploy`，Build command 可留空。

## 操作

- 左鍵點地或 WASD／方向鍵移動；點擊妖物選取，Q 普攻，1–8 使用技能。
- R / NumLock 自動奔跑；PageUp / PageDown 縮放；右鍵對目標行動。
- Tab 開地圖；空白鍵或 `/sit` 打坐；F1–F4 開人物、技能、任務、包裹。
- 港口嚮導提供入門說明；雜貨舖購買藥草、靈泉水、包裹與招魂號角。
- 包裹中點選物品使用/裝備；廣靈鎮為安全區，沒有戰鬥目標。

## 驗證

```sh
node --check src/game.js
python3 scripts/build.py
python3 scripts/smoke_test.py
```

瀏覽器測試需 Python `playwright` 套件與 `/usr/bin/chromium`，雲端開發環境已具備。測試使用暫時的本機HTTP伺服器與全新瀏覽器，不接觸玩家存檔；驗證角色、商店、安全區、戰鬥、存檔備份還原及手機介面。
