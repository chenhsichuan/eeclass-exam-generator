# -*- coding: utf-8 -*-
"""
eeclass_builder.py - Utility CLI & library for TronClass / ee-class question bank generation and conversion.
Features:
1. Backtick (`) complete removal to prevent MathJax ASCIIMath from corrupting code identifiers
   (e.g. `int()` -> ∫(), `bool()` -> b∞l(), `string` -> str∈g, `ValueError` -> ValueErr or).
2. Full HTML entity escaping (&, <, >, ", ', [, ], {, }, $) to prevent LMS stripping or formatting corruption.
3. Monospace & table whitespace preservation (&nbsp;) and linebreaks (<br>).
4. 27-column standard format with UTF-8 BOM (utf-8-sig).
5. TXT-to-CSV direct converter and comprehensive validator.
"""
import os
import sys
import csv
import re
import argparse

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HEADER_ROW_0 = ['version: 4'] + [''] * 26
HEADER_ROW_1 = [
    '題組',
    '類別 \n(格式相容欄位，匯入線上測驗時不支援)',
    '題型: \n(1)是非\n(2)單選  \n(3)複選  \n(4)填充 \n(5)問答\n(6)說明\n(7)題組',
    '題目',
    '答案\n若為是非題: \n(1)答案為是\n(2)答案為否',
    '解說\n(說明沒有解說)',
    '難易度:\n(1)容易\n(2)適中\n(3)困難',
    '選項1\n若為填充題: \n(1)不區分英文大小寫\n(2)區分英文大小寫',
    '選項2 \n若為填充題: \n(1)不需考慮順序\n(2)需考慮順序 ',
    '選項3 ',
    '選項4',
    '選項5',
    '選項6',
    '選項7',
    '選項8',
    '選項9',
    '選項10',
    '選項11',
    '選項12',
    '選項13',
    '選項14',
    '選項15',
    '選項16',
    '選項17',
    '選項18',
    '選項19',
    '選項20'
]

def format_for_tronclass(text: str) -> str:
    """Convert text into TronClass/ee-class compatible HTML entities and tags."""
    if not text:
        return ''
    text = str(text)
    
    # 0. Strip all backticks ` completely (never keep ` or &#96;, as browser DOM decoding
    #    still triggers MathJax ASCIIMath formula parsing!)
    text = text.replace('`', '')
    
    # 1. Escape &
    text = text.replace('&', '&amp;')
    
    # 2. Escape HTML tag delimiters & quotes
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    
    # 3. Escape LMS / Cloze / MathJax reserved characters
    text = text.replace('[', '&#91;')
    text = text.replace(']', '&#93;')
    text = text.replace('{', '&#123;')
    text = text.replace('}', '&#125;')
    text = text.replace('$', '&#36;')
    
    # 4. Preserve spaces in indentation and tables
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
        
    return '<br>'.join(formatted_lines)

def make_item(group='', category='', qtype=2, question='', answer='1', explanation='', difficulty=1, options=None):
    return {
        'group': group,
        'category': category,
        'qtype': qtype,
        'question': question.replace('`', ''),
        'answer': answer,
        'explanation': explanation.replace('`', ''),
        'difficulty': difficulty,
        'options': [str(o).replace('`', '') for o in (options or [])]
    }

def save_exam_bank(output_dir: str, filename_base: str, title: str, items: list):
    os.makedirs(output_dir, exist_ok=True)
    csv_file = os.path.join(output_dir, f"{filename_base}.csv")
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER_ROW_0)
        writer.writerow(HEADER_ROW_1)
        for it in items:
            row = [''] * 27
            row[0] = it.get('group', '')
            row[1] = it.get('category', '')
            row[2] = str(it.get('qtype', 2))
            row[3] = format_for_tronclass(it.get('question', ''))
            row[4] = str(it.get('answer', '1'))
            row[5] = format_for_tronclass(it.get('explanation', ''))
            row[6] = str(it.get('difficulty', 1))
            for idx, opt in enumerate(it.get('options', [])):
                if idx < 20:
                    row[7 + idx] = format_for_tronclass(opt)
            writer.writerow(row)

    txt_file = os.path.join(output_dir, f"{filename_base}.txt")
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"{title} ({filename_base.upper()})\n")
        f.write("=" * 80 + "\n\n")
        for idx, it in enumerate(items, 1):
            f.write(f"[第 {idx} 題]\n")
            if it.get('group'):
                f.write(f"【章節】{it['group']}\n")
            if it.get('category'):
                f.write(f"【類別】{it['category']}\n")
            qtype_map = {1: "是非題", 2: "單選題", 3: "複選題", 4: "填充題", 5: "問答題"}
            f.write(f"【題型】{qtype_map.get(it.get('qtype', 2), '選擇題')} (難易度: {it.get('difficulty', 1)})\n")
            f.write(f"【題目】\n{it.get('question', '').replace('`', '')}\n\n")
            if it.get('options'):
                f.write("【選項】\n")
                for o_i, opt in enumerate(it['options']):
                    f.write(f"  ({chr(65 + o_i)}) {str(opt).replace('`', '')}\n")
                f.write("\n")
            ans_val = str(it.get('answer', '1'))
            ans_str = "是 (Yes)" if it.get('qtype') == 1 and ans_val == '1' else ("否 (No)" if it.get('qtype') == 1 else ans_val)
            f.write(f"【參考解答】{ans_str}\n")
            if it.get('explanation'):
                f.write(f"【詳細解析】\n{it['explanation'].replace('`', '')}\n")
            f.write("-" * 80 + "\n\n")

    print(f"Successfully generated: {filename_base}.csv & {filename_base}.txt ({len(items)} questions)")

def parse_txt_to_items(txt_path: str):
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read().replace('`', '')

    raw_blocks = re.split(r'-{40,}', content)
    items = []

    for block in raw_blocks:
        block = block.strip()
        if not block or '[第 ' not in block:
            continue
        
        m_qnum = re.search(r'\[第\s*(\d+)\s*題\]', block)
        qnum = int(m_qnum.group(1)) if m_qnum else len(items) + 1
        
        group = ''
        m_chap = re.search(r'【章節】(.*)', block)
        if m_chap:
            group = m_chap.group(1).strip()
            
        category = ''
        m_cat = re.search(r'【類別】(.*)', block)
        if m_cat:
            category = m_cat.group(1).strip()
            
        difficulty = 1
        m_type = re.search(r'【題型】(.*)', block)
        if m_type:
            type_line = m_type.group(1).strip()
            m_diff = re.search(r'難易度[:：]\s*(\d+)', type_line)
            if m_diff:
                difficulty = int(m_diff.group(1))
            if '是非' in type_line:
                qtype = 1
            elif '複選' in type_line:
                qtype = 3
            elif '填充' in type_line:
                qtype = 4
            elif '問答' in type_line:
                qtype = 5
            else:
                qtype = 2
        else:
            qtype = 2

        m_qtext = re.search(r'【題目】\s*\n(.*?)(?=\n【(?:選項|參考解答|答案)】)', block, re.DOTALL)
        question_text = m_qtext.group(1).strip() if m_qtext else ""

        options = []
        m_opts = re.search(r'【選項】\s*\n(.*?)(?=\n【(?:參考解答|答案)】)', block, re.DOTALL)
        if m_opts:
            opt_block = m_opts.group(1).strip()
            opt_matches = list(re.finditer(r'^\s*\(([A-Z0-9]+)\)\s*(.*?)(?=\n\s*\([A-Z0-9]+\)|\Z)', opt_block, re.DOTALL | re.MULTILINE))
            if opt_matches:
                for om in opt_matches:
                    options.append(om.group(2).strip())
            else:
                for line in opt_block.splitlines():
                    line = line.strip()
                    if line:
                        clean_line = re.sub(r'^\([A-Za-z0-9]+\)\s*', '', line)
                        options.append(clean_line)

        m_ans = re.search(r'【(?:參考解答|答案)】\s*(.*)', block)
        raw_ans = m_ans.group(1).strip() if m_ans else ''
        
        if qtype == 1:
            if '是' in raw_ans or '1' in raw_ans or 'Yes' in raw_ans or 'True' in raw_ans:
                answer_code = '1'
            else:
                answer_code = '2'
        elif qtype == 2:
            ans_letter = raw_ans.strip().upper()
            if ans_letter and ans_letter[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                answer_code = str(ord(ans_letter[0]) - ord('A') + 1)
            elif ans_letter and ans_letter[0].isdigit():
                answer_code = ans_letter[0]
            else:
                answer_code = '1'
        elif qtype == 3:
            letters = re.findall(r'[A-Za-z0-9]', raw_ans)
            ans_nums = []
            for l in letters:
                l_up = l.upper()
                if 'A' <= l_up <= 'Z':
                    ans_nums.append(str(ord(l_up) - ord('A') + 1))
                elif l_up.isdigit():
                    ans_nums.append(l_up)
            answer_code = ','.join(ans_nums)
        else:
            answer_code = raw_ans

        m_exp = re.search(r'【(?:詳細解析|解說)】\s*\n?(.*)', block, re.DOTALL)
        explanation = m_exp.group(1).strip() if m_exp else ''

        items.append({
            'qnum': qnum,
            'group': group,
            'category': category,
            'qtype': qtype,
            'question': question_text,
            'options': options,
            'answer': answer_code,
            'explanation': explanation,
            'difficulty': difficulty
        })

    return items

def convert_txt_to_csv(txt_path: str, csv_path: str):
    items = parse_txt_to_items(txt_path)
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER_ROW_0)
        writer.writerow(HEADER_ROW_1)
        for it in items:
            row = [''] * 27
            row[0] = it['group']
            row[1] = it['category']
            row[2] = str(it['qtype'])
            row[3] = format_for_tronclass(it['question'])
            row[4] = str(it['answer'])
            row[5] = format_for_tronclass(it['explanation'])
            row[6] = str(it['difficulty'])
            for idx, opt in enumerate(it['options']):
                if idx < 20:
                    row[7 + idx] = format_for_tronclass(opt)
            writer.writerow(row)
    print(f"Converted {len(items)} questions from '{txt_path}' -> '{csv_path}'")
    validate_csv(csv_path)

def validate_csv(csv_path: str):
    if not os.path.exists(csv_path):
        print(f"Error: File not found {csv_path}")
        return False
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        raw_text = f.read()
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = list(csv.reader(f))
    if len(reader) < 2:
        print(f"Error: File {csv_path} has fewer than 2 header rows.")
        return False
    errors = 0
    if '`' in raw_text or '&#96;' in raw_text:
        print(f"Error: File contains backticks (` or &#96;) which trigger MathJax ASCIIMath corruption!")
        errors += 1
    for idx, row in enumerate(reader, start=1):
        if len(row) != 27:
            print(f"Row {idx} invalid column count: {len(row)} (expected 27)")
            errors += 1
        if idx > 2:
            q_text = row[3]
            if '承上' in q_text or '上題' in q_text:
                print(f"Row {idx} contains dependent reference: {q_text[:40]}")
                errors += 1
    if errors == 0:
        print(f"[PASS] {csv_path} is completely valid! ({len(reader)-2} questions, 0 backticks)")
        return True
    else:
        print(f"[FAIL] {csv_path} has {errors} error(s).")
        return False

def main():
    parser = argparse.ArgumentParser(description="ee-class / TronClass Question Bank Builder, Converter and Validator")
    parser.add_argument('--validate', '-v', type=str, help="Path to CSV file to validate")
    parser.add_argument('--convert', '-c', type=str, help="Path to source TXT file to convert to CSV")
    parser.add_argument('--output', '-o', type=str, help="Path to output CSV file (used with --convert)")
    args = parser.parse_args()
    if args.convert:
        out_csv = args.output or (os.path.splitext(args.convert)[0] + ".csv")
        convert_txt_to_csv(args.convert, out_csv)
    elif args.validate:
        validate_csv(args.validate)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
