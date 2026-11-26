---
name: eeclass-exam-generator
description: >-
  自動化生成與轉換符合 TronClass / 智園 ee-class 線上測驗系統匯入規範的 CSV 與 TXT 題庫與模擬考題。支援題目 100% 獨立性（防隨機抽題斷鏈）、Python 程式碼縮排 (&nbsp;)、精確換行 (<br>)、全特殊字元防護轉義（雙引號、中括號、大括號、大小於、錢字號、AND、反引號清除防 ASCIIMath 數學公式誤判）、27 欄標準結構與 UTF-8 with BOM (utf-8-sig) 編碼。
---

# ee-class / TronClass 線上測驗題庫生成與轉換技能

## 1. 概述 (Overview)

本技能旨在提供高等教育與技術認證（如 Certiport ITS Python、APCS、IPA、TQC 等）在 **TronClass（暢課）** 與 **智園 ee-class** 線上學習平台上的題庫生成、格式轉換、同觀念模擬題改寫與排版防護。

由於 TronClass / ee-class 的測驗引擎採用 Web HTML 渲染、內建 MathJax (ASCIIMath / LaTeX) 引擎與專用 CSV 解析器，若直接匯入一般純文字或含 Markdown 語法的 CSV，常會引發：
1. **排版崩潰**：純文字換行（`\n`）與程式碼縮排（空格）被瀏覽器壓縮成單一行。
2. **符號遺失**：雙引號 `""` 造成 HTML 屬性斷裂、中括號 `[]` 被誤判為克漏字標籤（Cloze Token）而整段抹除、大括號 `{}` 被誤判為範本變數、`<class>` 被當成 HTML 標籤隱藏、錢字號 `$` 觸發 LaTeX 數學公式亂碼。
3. **ASCIIMath 數學公式劫持（重大陷阱）**：TronClass 內建的 MathJax 引擎開啟了 **ASCIIMath**，並將**反引號（`` ` ``）**作為預設公式定界符！若題目或解說中使用 Markdown 行內程式碼反引號（如 `` `int()` ``、`` `bool()` ``、`` `string` ``、`` `ValueError` ``），即使轉成 HTML 實體 `&#96;`，瀏覽器 DOM 解析後仍會還原為反引號並被 MathJax 攔截，導致：
   - `int()` 被當成積分符號渲染為 **`∫()`**
   - `bool()` 中的 `oo` 被當成無限大渲染為 **`b∞l()`**
   - `string` 中的 `in` 被當成屬於符號渲染為 **`str∈g`**
   - `ValueError` 中的 `or` 被當成邏輯或拆裂為 **`ValueErr or`**
4. **隨機抽題斷鏈**：若題目包含「承上題」，在開啟題庫隨機亂序時學生將無法作答。

本技能完整規範了 27 欄位標準格式、全字元 HTML 安全實體轉義、**反引號強制清零原則**、100% 獨立題型原則以及自動化 Python 生成與轉換工具。

---

## 2. CSV 標準格式規範 (27 欄位規格)

TronClass / ee-class 題庫匯入必須遵循嚴格的 27 欄位結構，且編碼必須為 **`utf-8-sig`（帶 BOM 的 UTF-8）**，否則 Excel 或後端系統解析時會產生亂碼。

### 欄位結構定義

* **第 0 列 (Row 0)**：`version: 4`，後方緊跟 26 個空欄位（共 27 欄）。
* **第 1 列 (Row 1)**：標準表頭（共 27 欄）：
  1. `題組`
  2. `類別 \n(格式相容欄位，匯入線上測驗時不支援)`
  3. `題型: \n(1)是非\n(2)單選  \n(3)複選  \n(4)填充 \n(5)問答\n(6)說明\n(7)題組`
  4. `題目`
  5. `答案\n若為是非題: \n(1)答案為是\n(2)答案為否`
  6. `解說\n(說明沒有解說)`
  7. `難易度:\n(1)容易\n(2)適中\n(3)困難`
  8. `選項1\n若為填充題: \n(1)不區分英文大小寫\n(2)區分英文大小寫`
  9. `選項2 \n若為填充題: \n(1)不需考慮順序\n(2)需考慮順序 `
  10. `選項3 `
  11. `選項4`
  12. `選項5` ~ 27. `選項20`
* **資料列 (Data Rows)**：每一題一列，必須剛好 27 欄。

### 題型代碼與答案填寫規則

| 題型名稱 | 題型代碼 (欄位 2) | 答案格式 (欄位 4) | 選項填寫方式 (欄位 7~26) |
| :--- | :---: | :--- | :--- |
| **是非題** | `1` | `1` 代表「是 (Yes)」，`2` 代表「否 (No)」 | 選項 1~20 留空 |
| **單選題** | `2` | 填寫正確選項的數字編號（例如 `1` 代表選項 1，`3` 代表選項 3） | 依序填入選項 1、選項 2、選項 3、選項 4... |
| **複選題** | `3` | 以半形逗號分隔多個正確選項編號（例如 `1,3,4`） | 依序填入選項 1~選項 N |
| **填充題** | `4` | 填寫標準答案字串 | 選項 1: `1` (不分大小寫)/`2` (分大小寫)；選項 2: `1` (不限順序)/`2` (依順序) |
| **問答題** | `5` | 填寫參考答案 | 選項 1~20 留空 |

---

## 3. 核心規範 1：100% 獨立題型原則 (防隨機抽題斷鏈)

在線上測驗中，系統通常會開啟**「隨機亂序抽題」**。因此：

1. **嚴禁任何相依詞**：題目中**絕不能出現**「承上題」、「承上題程式碼」、「如前所述」、「接續上題」等字眼。
2. **完整情境重複**：若同一個背景程式碼包含多個空格（如空格 1、2、3）或多個敘述判斷，**每一題都必須完整包含「情境描述」+「完整程式碼片段」+「明確提問」**。
   * *範例提問*：「...（完整情境與程式碼）...\n\n請問程式碼中的空格 (2) 應填入下列哪一個函式？」

---

## 4. 核心規範 2：全特殊字元 HTML 安全實體轉義與反引號清除

所有寫入 CSV 的文字欄位（包含 **`題目`**、**`選項1~20`**、**`解說`**），均必須經過專用的 `format_for_tronclass()` 處理：

| 原始符號 | 容易引發的系統問題 | 處理 / 轉義方式 | 前端還原效果 |
| :---: | :--- | :---: | :---: |
| **`` ` ``**<br>(反引號) | **致命陷阱**：瀏覽器 DOM 解碼後會觸發 MathJax ASCIIMath 數學引擎（即使轉成 `&#96;` 也無效！），導致 `int()` 變成 `∫()`、`bool()` 變成 `b∞l()`、`string` 變成 `str∈g`、`ValueError` 變成 `ValueErr or` | **直接移除 (`''`)**<br>嚴禁使用反引號或 `&#96;` | 純淨顯示原程式碼字元 |
| **`&`** | 與 HTML 實體解析衝突 | `&amp;` | `&` |
| **`<`** | 被瀏覽器當成 HTML 標籤（如 `<class>`）而整段隱藏 | `&lt;` | `<` |
| **`>`** | HTML 標籤結束符 | `&gt;` | `>` |
| **`"`** | 破壞 HTML 屬性（如 `<input value="...">`）導致文字截斷消失 | `&quot;` | `"` |
| **`'`** | 在部分系統引發 JavaScript 字串解析錯誤 | `&#39;` | `'` |
| **`[`** | 被 LMS 誤判為克漏字填空標籤（Cloze Token）或 BBCode 而抹除 | `&#91;` | `[` |
| **`]`** | 被 LMS 誤判為克漏字填空標籤而抹除 | `&#93;` | `]` |
| **`{`** | 被 LMS 誤判為範本變數（Template Variable）或格式化標籤而吃掉 | `&#123;` | `{` |
| **`}`** | 被 LMS 誤判為範本變數結束符 | `&#125;` | `}` |
| **`$`** | 觸發 LMS 的 MathJax / LaTeX 數學公式引擎，導致字體變斜體或亂碼 | `&#36;` | `$` |
| **`    `**<br>(4空格縮排) | 瀏覽器 HTML 自動合併連續空格，導致 Python 縮排消失 | `&nbsp;&nbsp;&nbsp;&nbsp;` | 4 格空格縮排 |
| **`\n`**<br>(換行) | 瀏覽器 HTML 忽略純文字換行，導致多行程式碼黏成一行 | `<br>` | 精確換行 |

### 標準轉義函式實作 (Python)

```python
import re

def format_for_tronclass(text: str) -> str:
    """將題目、選項或解說文字轉換為相容 TronClass / ee-class 的 HTML 安全格式"""
    if not text:
        return ''
    text = str(text)
    
    # 0. 強制移除所有反引號 ` (嚴禁保留或轉為 &#96;，防止瀏覽器 DOM 解碼後觸發 MathJax ASCIIMath 公式引擎)
    text = text.replace('`', '')
    
    # 1. 優先跳脫 & (避免後續實體的 & 被二次轉義)
    text = text.replace('&', '&amp;')
    
    # 2. 跳脫 HTML 標籤與引號
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    
    # 3. 跳脫 LMS / Cloze / MathJax 保留字元
    text = text.replace('[', '&#91;')
    text = text.replace(']', '&#93;')
    text = text.replace('{', '&#123;')
    text = text.replace('}', '&#125;')
    text = text.replace('$', '&#36;')
    
    # 4. 保留程式碼 4 格縮排與表格連續空格
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        stripped_l = line.lstrip(' ')
        leading_spaces = len(line) - len(stripped_l)
        if leading_spaces > 0:
            line_body = stripped_l
            line_body = re.sub(r'  +', lambda m: '&nbsp;' * len(m.group(0)), line_body)
            line = ('&nbsp;' * leading_spaces) + line_body
        else:
            line = re.sub(r'  +', lambda m: '&nbsp;' * len(m.group(0)), line)
        formatted_lines.append(line)
        
    # 5. 將換行替換為 <br>
    return '<br>'.join(formatted_lines)
```

---

## 5. 核心規範 3：同觀念模擬題改寫原則 (Isomorphic Questions)

當使用者要求「改寫成類似考題、不要一模一樣」時，遵循以下原則：
1. **同考點、同語法層次**：嚴格保留原題考核的知識點（如型態轉換、切片、運算子優先級、迴圈中斷、自訂函式作用域、模組使用、例外捕捉）。
2. **更換應用情境**：將運動 App 改為車輛行車電腦、學生考績改為氣溫警報、寵物店收費改為水電計費等。
3. **更換數值與條件臨界點**：調整運算數值、比較條件、字串內容，確保答案需要重新運算推導。
4. **另存新檔**：檔名建議加上 `_mock` 或版本號（如 `ch01_mock.csv`、`_V3.csv`），並同時輸出易於閱讀的純文字檔（且純文字檔內同樣不應使用反引號 `` ` ``）。

---

## 6. 工具腳本與自動化使用 (Utility Scripts)

本技能內置專用題庫生成、TXT 轉 CSV 與驗證工具：
`scripts/eeclass_builder.py`（位於本技能資料夾內）

### 終端機調用範例：
```powershell
# 驗證 CSV 題庫是否符合 27 欄、無反引號、無相依詞規範
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; python "<SKILL_DIR>/scripts/eeclass_builder.py" --validate "path/to/exam.csv"

# 將標準格式 TXT 題庫直接轉換為 ee-class CSV 題庫
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; python "<SKILL_DIR>/scripts/eeclass_builder.py" --convert "path/to/exam.txt" --output "path/to/exam.csv"
```

---

## 7. 常見錯誤與自我檢查清單 (Checklist)

* [ ] **欄位數量檢查**：每一列的欄位數是否嚴格等於 **27** 欄？
* [ ] **首列版本宣告**：第 0 列首格是否為 `version: 4`？
* [ ] **檔案編碼檢查**：是否使用 `encoding='utf-8-sig'` 寫入？（使用標準 utf-8 會在 Excel 開啟時產生亂碼）。
* [ ] **獨立性檢查**：是否使用 `grep "承上"` 確認過題目中完全沒有「承上題」關聯詞？
* [ ] **反引號清零檢查（關鍵）**：是否確認 CSV 與 TXT 中完全沒有 `` ` `` 與 `&#96;`？（數量必須為 `0`，防止 `int()` 變 `∫()`、`bool()` 變 `b∞l()`、`string` 變 `str∈g`）。
* [ ] **符號轉義檢查**：中括號 `[]` 是否轉為 `&#91;&#93;`？雙引號 `""` 是否轉為 `&quot;`？`<class>` 是否轉為 `&lt;class&gt;`？
* [ ] **縮排與換行檢查**：Python 程式碼是否以 `&nbsp;&nbsp;&nbsp;&nbsp;` 縮排、多行文字是否包含 `<br>`？
* [ ] **答案格式檢查**：是非題是否為 `1` 或 `2`、單選題是否為 `1`~`20` 數字、複選題是否為逗號分隔數字（如 `1,3`）？
