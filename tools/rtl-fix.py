# Fix right-to-left / left-to-right display of the Hebrew markdown on GitHub.
# Run after adding or editing Hebrew pages:  python3 tools/rtl-fix.py .
# - wraps tables and blockquotes in <div dir="rtl"> (GitHub gives them no direction)
# - adds an invisible RLM to Hebrew paragraphs/list items/headings that start with English
# - adds an invisible LRM *outside* inline code that starts/ends with a symbol (Switch>, .1, /24)
# - adds an LRM to table cells with no Hebrew (IPs, VLAN lists) so they read as typed
# - sets dir="rtl" on <details>
# Fenced code blocks and the text inside backticks are never changed.
# A code block inside an answer (<details>) must be wrapped in <div dir="ltr"> by hand.
import sys, re, os
RLM, LRM = "‏", "‎"
HEB = re.compile(r"[֐-׿]")
def first_strong(text):
    """First strong bidi char of rendered text: 'R', 'L' or None. Markdown syntax stripped, code text kept."""
    t = re.sub(r"\]\([^)]*\)", "]", text)         # drop link URLs
    t = re.sub(r"<[^>]+>", "", t)                  # drop html tags
    for ch in t:
        if ch == RLM or HEB.match(ch): return "R"
        if ch == LRM or ch.isascii() and ch.isalpha(): return "L"
    return None
def fix_code_spans(s):
    return _fix_code_spans(fix_arrows(s))
def _fix_code_spans(s):
    """LRM outside inline code spans whose ends are not letters (so >, #, ., / stay in place)."""
    out, i = [], 0
    for m in re.finditer(r"(?<!`)`([^`\n]+)`(?!`)", s):
        a, b = m.span(); code = m.group(1)
        pre = s[i:a]; out.append(pre)
        need_before = not (code[0].isascii() and code[0].isalpha())
        need_after = not (code[-1].isascii() and code[-1].isalnum())
        if need_before and not (pre.endswith(LRM)): out.append(LRM)
        out.append(m.group(0))
        if need_after and not s[b:b+1] == LRM: out.append(LRM)
        i = b
    out.append(s[i:]); return "".join(out)
def fix_arrows(s):
    """A Hebrew-flow arrow between two English words would join their left-to-right run and point
    backwards. Strong RTL marks on both sides keep it in the right-to-left flow."""
    parts = re.split(r"(`[^`\n]+`)", s)
    for k in range(0, len(parts), 2):
        parts[k] = re.sub("\u200f?←\u200f?", RLM + "←" + RLM, parts[k])
    return "".join(parts)
def fix_cell(c):
    inner = c.strip()
    if not inner or set(inner) <= set("-: "): return c
    if not HEB.search(inner) and not inner.startswith(LRM):
        inner = LRM + inner
    return " " + fix_code_spans(inner) + " "
def split_row(line):
    # split on | not escaped and not inside code
    cells, cur, code, k = [], "", False, 0
    while k < len(line):
        ch = line[k]
        if ch == "`": code = not code
        if ch == "\\" and k + 1 < len(line): cur += line[k:k+2]; k += 2; continue
        if ch == "|" and not code: cells.append(cur); cur = ""
        else: cur += ch
        k += 1
    cells.append(cur); return cells
def process(text, stats):
    lines = text.split("\n"); out = []; i = 0; fence = False
    while i < len(lines):
        ln = lines[i]
        if ln.lstrip().startswith("```"):
            fence = not fence; out.append(ln); i += 1; continue
        if fence: out.append(ln); i += 1; continue
        # table block
        if ln.startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"): j += 1
            block = lines[i:j]
            wrapped = len(out) >= 2 and out[-2] == '<div dir="rtl">'
            new = []
            for row in block:
                cells = split_row(row)
                new.append("|".join([cells[0]] + [fix_cell(c) if not re.fullmatch(r"\s*:?-+:?\s*", c) else c for c in cells[1:-1]] + [cells[-1]]))
            if not wrapped:
                if out and out[-1] != "": out.append("")
                out += ['<div dir="rtl">', ""] + new + ["", "</div>"]; stats["tables"] += 1
                if j < len(lines) and lines[j] != "": out.append("")
            else: out += new
            stats["cells"] += sum(1 for a, b in zip(block, new) if a != b)
            i = j; continue
        # blockquote block
        if ln.startswith(">"):
            j = i
            while j < len(lines) and lines[j].startswith(">"): j += 1
            block = lines[i:j]; new = []
            for k, q in enumerate(block):
                body = fix_code_spans(q[1:].lstrip(" "))
                if k == 0 or block[k-1].strip() == ">":   # first line of a paragraph inside the quote
                    if HEB.search(" ".join(b[1:] for b in block)) and first_strong(body) == "L":
                        body = RLM + body; stats["rlm"] += 1
                new.append("> " + body if body else ">")
            wrapped = len(out) >= 2 and out[-2] == '<div dir="rtl">'
            if not wrapped:
                if out and out[-1] != "": out.append("")
                out += ['<div dir="rtl">', ""] + new + ["", "</div>"]; stats["quotes"] += 1
                if j < len(lines) and lines[j] != "": out.append("")
            else: out += new
            i = j; continue
        if ln.startswith("<details>"):
            ln = ln.replace("<details>", '<details dir="rtl">', 1); stats["details"] += 1
        # headings, list items, paragraph starts
        if HEB.search(ln) or re.match(r"^(#{1,6} |\s*[-*] |\s*\d+\. )", ln):
            ln2 = fix_code_spans(ln)
            if ln2 != ln: stats["code"] += 1
            ln = ln2
        m = re.match(r"^(#{1,6} |\s*[-*] (?:\[[ x]\] )?|\s*\d+\. )(.*)$", ln)
        prev = out[-1] if out else ""
        para_start = ln.strip() and not m and (prev.strip() == "" or prev.startswith("<") or prev.startswith("#")) and not ln.startswith("<")
        if m:
            head, body = m.group(1), m.group(2)
            if first_strong(body) == "L" and not body.startswith(RLM):
                body = RLM + body; stats["rlm"] += 1
            ln = head + body
        elif para_start and HEB.search(ln + " " + " ".join(lines[i+1:i+4])) and first_strong(ln) == "L" and not ln.startswith(RLM):
            ln = RLM + ln; stats["rlm"] += 1
        out.append(ln); i += 1
    return "\n".join(out)
root = sys.argv[1]; dry = len(sys.argv) > 2
tot = {}
for dp, _, fs in os.walk(root):
    if ".git" in dp: continue
    for f in fs:
        if not f.endswith(".md"): continue
        p = os.path.join(dp, f); s = open(p, encoding="utf-8").read()
        st = dict(tables=0, cells=0, quotes=0, details=0, rlm=0, code=0)
        new = process(s, st)
        print(f"{os.path.relpath(p, root):45s} " + " ".join(f"{k}={v}" for k, v in st.items()))
        if not dry and new != s: open(p, "w", encoding="utf-8").write(new)
