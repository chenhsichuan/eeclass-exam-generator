# 🎓 eeclass-exam-generator
> **TronClass（暢課）與 智園 ee-class 線上測驗題庫生成、模擬題改寫與 CSV 轉換 AI Agent 技能 (Skill)**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB.svg)](https://www.python.org/)
[![Agent Skill](https://img.shields.io/badge/AI_Agent-Skill-10B981.svg)](#🚀-各大-ai-agent-匯入與安裝指南)

**`eeclass-exam-generator`** 是一套專為大專院校教師與助教設計的 AI Agent 技能包。它能讓各種 AI 程式助手（如 **Google Antigravity (AGY)**、**Claude Code**、**Cursor**、**OpenAI Codex CLI**、**Windsurf**、**Cline** 等）自動將教材、題庫或純文字題目轉換為 **100% 符合 TronClass / 智園 ee-class 線上測驗匯入規格的 27 欄位 CSV 檔案**，並完美解決線上測驗系統常見的排版崩潰、符號消失與數學公式誤判問題！

---

## ✨ 為什麼需要這個技能？（解決痛點）

當您將程式設計（Python、C++、Java 等）或理工科考題匯入 **TronClass / 智園 ee-class** 時，若使用一般 CSV 往往會遭遇以下四大災難，本技能皆已內建自動化防禦機制：

| 常見系統災難 | 發生原因 | 本技能自動化解決方案 |
| :--- | :--- | :--- |
| **1. `int()` 變成積分 `∫()`、`bool()` 變成無限 `b∞l()`、`string` 變成 `str∈g`** | 系統內建 MathJax 開啟了 **ASCIIMath**，將反引號 `` ` `` 當成數學公式定界符（即使轉成 `&#96;` 也會在瀏覽器 DOM 解碼後被攔截！） | **反引號強制清零機制**：在寫入前徹底清除所有 Markdown 反引號 `` ` ``，100% 阻斷 ASCIIMath 公式劫持。 |
| **2. 答案與題目中的 `""` 與 `[]` 內容整段憑空消失** | 雙引號 `""` 破壞前端 HTML 屬性；中括號 `[]` 被 LMS 誤判為克漏字填空標籤（Cloze Token）而整段抹除；`<class>` 被當作 HTML 標籤隱藏。 | **全特殊字元 HTML 安全實體轉義**：自動將 `"` 轉為 `&quot;`、`[` 轉為 `&#91;`、`]` 轉為 `&#93;`、`{}` 轉為 `&#123;&#125;`、`<` 轉為 `&lt;`、`$` 轉為 `&#36;`。 |
| **3. Python 程式碼縮排消失、多行程式碼全部擠成同一行** | 瀏覽器 HTML 渲染器會自動忽略純文字換行 `\n` 並將連續空白壓縮為單一空白。 | **精確縮排與換行保護**：自動將行首 4 格縮排與連續空格轉為 `&nbsp;`，並將換行符轉為 `<br>`。 |
| **4. 隨機抽題時出現「承上題」導致學生無法作答** | 原始題庫常有「承上題程式碼...」，當系統開啟隨機排序時題目順序被打亂。 | **100% 獨立題型規範與檢查器**：強制每一題皆包含完整情境與完整程式碼，並透過驗證器攔截任何「承上題」字眼。 |

---

## 📂 專案目錄結構

```text
eeclass-exam-generator/
├── README.md                  # 完整安裝、跨平台 AI Agent 匯入與使用說明書（本檔案）
├── SKILL.md                   # AI Agent 核心技能定義檔（包含 YAML Frontmatter 與完整轉換規範）
├── .gitignore                 # Git 忽略清單
└── scripts/
    └── eeclass_builder.py     # 內建 Python 自動化建構、TXT 轉 CSV 與 27 欄格式驗證工具
```

---

## 🚀 各大 AI Agent 匯入與安裝指南

本技能採用標準 `SKILL.md` 格式設計，可無縫匯入至目前主流的 AI Coding Agents 中。請依據您使用的工具選擇以下安裝方式：

### 方式一：Google Antigravity (AGY 2.0 / CLI / IDE)
將本專案直接複製（Clone）到您的 Antigravity 全域技能目錄或專案技能目錄中：

* **全域安裝（所有專案皆可使用，推薦）**：
  ```bash
  # Windows (PowerShell)
  git clone https://github.com/chenhsichuan/eeclass-exam-generator.git "$HOME\.gemini\config\skills\eeclass-exam-generator"

  # macOS / Linux
  git clone https://github.com/chenhsichuan/eeclass-exam-generator.git ~/.gemini/config/skills/eeclass-exam-generator
  ```
* **單一專案安裝**：
  ```bash
  git clone https://github.com/chenhsichuan/eeclass-exam-generator.git .agents/skills/eeclass-exam-generator
  ```
* **呼叫方式**：在 Antigravity 對話框輸入 `/eeclass-exam-generator` 或直接口頭告訴 AI：「請依照 eeclass 測驗技能幫我轉換成 CSV」。

---

### 方式二：Claude Code (Anthropic CLI)
Claude Code 支援自訂技能與專案指令：
```bash
# 安裝至專案的 .claude/skills 或直接放到專案目錄
git clone https://github.com/chenhsichuan/eeclass-exam-generator.git .claude/skills/eeclass-exam-generator
```
或者在對話中輸入：
> `請先閱讀 @SKILL.md 的規範，並使用 scripts/eeclass_builder.py 幫我將題庫轉換為 ee-class CSV 格式。`

---

### 方式三：Cursor / Windsurf / Cline / GitHub Copilot
您可以將本技能放到專案資料夾中，或將 `SKILL.md` 加入您的 Rules 中：
1. 下載或 Clone 本倉庫至您的題庫工作資料夾：
   ```bash
   git clone https://github.com/chenhsichuan/eeclass-exam-generator.git
   ```
2. 在對話框使用 `@SKILL.md` 引用此技能檔，即可讓 AI 自動遵循所有 27 欄位與轉義規範並呼叫 `scripts/eeclass_builder.py`！

---

## 💬 AI 提示詞（Prompts）使用範例

匯入技能後，您可以直接對 AI 這樣下達指令：

### 範例 1：將現有文字題庫轉成 ee-class CSV
> 「請使用 `eeclass-exam-generator` 技能，將資料夾內的 `期中考題庫.txt` 轉換成可以匯入 ee-class 的 CSV 檔案。」

### 範例 2：根據原有題目自動改寫出「同觀念模擬考題」
> 「請依照 `eeclass-exam-generator` 技能，將第一章到第四章的考題改寫成類似但情境與數值不同的模擬考題，每一題都要獨立包含完整程式碼（不要有承上題），並加上詳細解析，最後同時輸出 `.txt` 與 `.csv` 檔案。」

### 範例 3：雙語或多語言詳解考題生成
> 「請幫我把這份 Python 考題的每一題【詳細解析】加上詳細的教學推導與越南文（或英文）對照翻譯，並轉成 ee-class 的 CSV 題庫檔。」

---

## 🛠️ 命令列工具 (`eeclass_builder.py`) 獨立使用說明

除了讓 AI 自動呼叫外，您也可以直接在終端機使用內建的 Python 腳本進行**一鍵轉檔**與**格式驗證**（僅需標準 Python 3 環境，無須安裝任何第三方套件）：

### 1. 將標準 `.txt` 題庫直接轉換為 ee-class `.csv`
```bash
python scripts/eeclass_builder.py --convert "期中考複習測驗題.txt" --output "期中考複習測驗題.csv"
```

### 2. 驗證 `.csv` 檔案是否 100% 符合 ee-class 匯入規範
自動檢查是否符合 **27 欄位**、**`version: 4` 標頭**、**無殘留反引號 `` ` ``**、**無「承上題」相依字眼**：
```bash
python scripts/eeclass_builder.py --validate "期中考複習測驗題.csv"
```
驗證通過時會顯示：
```text
[PASS] 期中考複習測驗題.csv is completely valid! (80 questions, 0 backticks)
```

---

## 📝 標準 `.txt` 題庫輸入格式範例

若您要準備 `.txt` 交給 `eeclass_builder.py --convert` 轉檔，格式如下（每題以 40 個以上的減號 `----` 分隔）：

```text
[第 1 題]
【章節】第一章：變數與資料型態 (CH01)
【類別】變數與資料型態
【題型】單選題 (難易度: 1)
【題目】
在 Python 資料類型的課程中創建以下程式碼片段：

x1 = "5"
y1 = 4
a = x1 * y1

請問執行程式碼片段後，變數 a 的資料類型為何？

【選項】
  (A) str
  (B) int
  (C) float
  (D) bool

【參考解答】A
【詳細解析】
1. 核心考點：字串重複運算子（*）。
2. 解題推導："5" * 4 代表將字串重複 4 次得到 "5555"，資料型態仍為 str。
--------------------------------------------------------------------------------
```

* 支援題型：
  * `是非題`（答案填 `是` 或 `否`）
  * `單選題`（答案填 `A`、`B`、`C`、`D`）
  * `複選題`（答案填 `B, D` 或 `A, B, C`）

---

## 📋 匯入智園 ee-class / TronClass 系統步驟

1. 登入您的 **ee-class** 或 **TronClass** 課程管理後台。
2. 進入 **「測驗 / 題庫」** ➔ 點選 **「匯入」**。
3. 選擇由本技能生成的 `.csv` 檔案（本技能自動採用 `utf-8-sig` 帶 BOM 編碼，Windows Excel 直接雙擊打開也不會亂碼，但**請勿用 Excel 另存覆蓋**以免遺失格式，請直接將產出的 CSV 匯入系統）。
4. 匯入完成後，預覽題目即可看到完美的程式碼縮排、完整保留的 `""` 與 `[]` 符號，且不會有任何數學公式亂碼！

---

## 📄 授權條款 (License)

本專案採用 [MIT License](https://opensource.org/licenses/MIT) 開源授權，歡迎各位老師、助教與開發者自由下載、分享、修改與散佈。
