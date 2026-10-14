#!/usr/bin/env python3
"""Собирает site/index.html из ../concept.md, src/intro.html и иллюстраций из src/slides/.

Запуск: python3 site/build.py
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(ROOT, '..', 'concept.md')
SLIDES = os.path.join(ROOT, 'src', 'slides')
INTRO = os.path.join(ROOT, 'src', 'intro.html')
OUT = os.path.join(ROOT, 'index.html')
OUT_SLIDES = os.path.join(ROOT, 'slides.html')

# ---------------------------------------------------------------- figures

FIGS = {
    'hero': dict(slide='cover', crop=(1032, 230, 760, 620), remove=[('width:860px', 'div')], cap=None),
    'inertia': dict(slide='inertia', crop=(820, 330, 980, 270), remove=[('left:128px;top:320px;width:640px', 'div'), ('left:860px;top:660px', 'div')],
                    cap='Ось времени: знать скорость в момент 4 — значит помнить положение в момент 3.'),
    'honey': dict(slide='honey', crop=(128, 280, 1664, 520), remove=[('top:860px', 'p')],
                  cap='Без инерции пространство состояний одномерно; с инерцией — двумерно, и пути «туда» и «обратно» могут различаться.'),
    'wave': dict(slide='wave', crop=(128, 262, 1664, 800), remove=[],
                 cap='Одиночная волна хемоаттрактанта проходит мимо нейтрофила. Внизу — смещение клетки к источнику во времени.'),
    'loops': dict(slide='loops', crop=(128, 280, 1664, 540), remove=[('top:830px', 'p')], cap='Петля как свидетель памяти.'),
    'plan': dict(slide='plan', crop=(128, 250, 1664, 780), remove=[],
                 cap='План сверху, масштаб 110 пикселей на метр. Кольцо обхода и порог — из модели (раздел 4).'),
    'section': dict(slide='section', crop=(128, 250, 1664, 740), remove=[],
                    cap='Разрез: лидар между тумбой и столешницей, плоскость сканирования на уровне корпуса зрителя. Выноска с клеткой увеличена.'),
    'corridor': dict(slide='corridor', crop=(128, 262, 1664, 520), remove=[('top:800px', 'p')],
                     cap='Шаг 0: кукла из пяти несцепленных сегментов за прозрачным занавесом.'),
    'alive': dict(slide='alive', crop=(128, 270, 980, 640), remove=[('left:1150px', 'div')],
                  cap='Шаг 1: набросок вида из проёма — мерцание изнутри и медленное «дыхание» мембраны.'),
    'pass1': dict(slide='pass1', crop=(128, 262, 1664, 640), remove=[('top:924px', 'p')],
                  cap='Шаг 2, симуляция модели: зритель обходит стол по кругу r = 1 м и выходит; рука отстаёт от направления на зрителя, справа рисуется её след (в 1.5 раза быстрее реального времени).'),
    'vestibule': dict(slide='vestibule', crop=(128, 262, 1664, 540), remove=[('top:850px', 'p')],
                      cap='Шаг 3, по симуляции: зритель стоит в предбаннике; рука увеличена в 4 раза.'),
    'pass2': dict(slide='pass2', crop=(128, 262, 1664, 640), remove=[('top:924px', 'p')],
                  cap='Шаг 4, тот же маршрут: без памяти рука на длине R смотрит точно на зрителя, её след — копия маршрута.'),
    'simfull': dict(slide='simfull', crop=(128, 250, 1664, 700), remove=[],
                    cap='Весь цикл — живая симуляция модели из раздела 4 (в 1.5 раза быстрее реального времени).'),
    'signal': dict(slide='signal', crop=(128, 270, 840, 420), remove=[('left:900px;top:290px', 'div')],
                   cap='Градиент сигнала в центре клетки направлен на зрителя.'),
    'decay': dict(slide='decay', crop=(128, 290, 800, 400), remove=[('left:960px;top:300px', 'div')],
                  cap='Длина руки после ухода зрителя: только экспоненциальное затухание (пунктир) и с постоянным членом γ (сплошная) — ноль за конечное время t* ≈ 7.5 с.'),
    'threshold': dict(slide='threshold', crop=(128, 240, 1664, 720), remove=[],
                      cap='Равновесная длина руки в зависимости от расстояния до зрителя и соответствующие зоны вокруг стола.'),
    'params': dict(slide='params', crop=(128, 270, 1664, 660), remove=[],
                   cap='Параметры, с которыми посчитаны все траектории на этой странице. Это точка отсчёта для прототипа, а не финальные значения.'),
    'routes': dict(slide='routes', crop=(128, 90, 1664, 850), remove=[],
                   cap='Траектории для четырёх маршрутов зрителя (симуляция). Вверху — маршрут в зале, внизу — плоскость поляризации.'),
    'mech': dict(slide='mech', crop=(128, 262, 1664, 700), remove=[],
                 cap='Механика клетки: вид сверху в покое и с вытянутой рукой; схематичный разрез.'),
    'membrane': dict(slide='membrane', crop=(128, 262, 1664, 640), remove=[],
                     cap='Мембрана: разнесённая сборка и сравнение кандидатов.'),
    'corridortech': dict(slide='corridortech', crop=(128, 262, 1664, 640), remove=[],
                         cap='Коридор: лебёдки, нити, кукла, занавес.'),
    'receipt': dict(slide='receipt', crop=(120, 236, 560, 730), remove=[('left:700px;top:270px', 'div')],
                    cap='Макет чека. Траектория — результат симуляции для маршрута «круг с остановкой».'),
    'lidar': dict(slide='lidar', crop=(128, 285, 1664, 640), remove=[],
                  cap='К вопросу 4: два варианта размещения лидара; тёмные клинья — слепые секторы.'),
    'room': dict(slide='room', crop=(128, 262, 1664, 680), remove=[], cap='К вопросу 5: три способа построить зал.'),
    'light': dict(slide='light', crop=(128, 270, 1664, 730), remove=[], cap='К вопросу 6: свет по шагам сценария.'),
}


def remove_el(s, sub, tag):
    i = s.find(sub)
    if i < 0:
        raise ValueError('not found: %s' % sub)
    start = s.rfind('<' + tag, 0, i)
    depth, j = 0, start
    pat = re.compile(r'<(/?)%s\b' % tag)
    for m in pat.finditer(s, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            j = s.index('>', m.end()) + 1
            break
    return s[:start] + s[j:]


def load_figure(key, f=None, keep_headings=False):
    f = f or FIGS[key]
    src = open(os.path.join(SLIDES, f['slide'] + '.html'), encoding='utf-8').read()
    m = re.match(r'\s*<section[^>]*style="([^"]*)"[^>]*>(.*)</section>\s*$', src, re.S)
    style, inner = m.group(1), m.group(2)
    inner = re.sub(r'<aside>.*?</aside>', '', inner, flags=re.S)
    if not keep_headings:
        inner = re.sub(r'<p style="[^"]*text-transform:uppercase[^"]*">.*?</p>', '', inner, count=1, flags=re.S)
        inner = re.sub(r'<h2 .*?</h2>', '', inner, count=1, flags=re.S)
    for sub, tag in f['remove']:
        inner = remove_el(inner, sub, tag)

    def to_iframe(mm):
        return '<iframe title="анимация" style="%s;border:0" sandbox="allow-scripts" srcdoc="%s"></iframe>' % (
            mm.group(1), html.escape(mm.group(2), quote=True))
    inner = re.sub(r'<x-embed style="([^"]*)">(.*?)</x-embed>', to_iframe, inner, flags=re.S)
    for i in sorted(set(re.findall(r'\bid="([^"]+)"', inner)), key=len, reverse=True):
        inner = (inner.replace('id="%s"' % i, 'id="%s-%s"' % (key, i))
                 .replace('"#%s"' % i, '"#%s-%s"' % (key, i))
                 .replace('url(#%s)' % i, 'url(#%s-%s)' % (key, i)))
    if key == 'signal':
        inner = inner.replace('width:700px;height:600px"', 'width:700px;height:600px;overflow:visible"', 1)
    x0, y0, w, h = f['crop']
    cap = '<figcaption>%s</figcaption>' % f['cap'] if f.get('cap') else ''
    return ('<figure class="fig" data-w="%d" data-h="%d" style="max-width:%dpx"><div class="box">'
            '<div class="stage" style="width:%dpx;height:%dpx">'
            '<div class="slide" style="%s;position:absolute;left:-%dpx;top:-%dpx;width:1920px;height:1080px;box-sizing:border-box">%s</div>'
            '</div></div>%s</figure>') % (w, h, w, w, h, style, x0, y0, inner, cap)


# ---------------------------------------------------------------- markdown

INLINE_MATH = [
    ('Зритель находится в точке **x**_v, в полярных координатах относительно центра стола (r, φ). Сигнал L(**x**) = ℓ(|**x** − **x**_v|), где ℓ',
     r'Зритель находится в точке \(\mathbf{x}_v\), в полярных координатах относительно центра стола \((r, \varphi)\). Сигнал \(L(\mathbf{x}) = \ell(|\mathbf{x} - \mathbf{x}_v|)\), где \(\ell\)'),
    ('при ℓ(r) = e^{−r/λ} получается |∇L| = e^{−r/λ}/λ. Конкретный вид ℓ',
     r'при \(\ell(r) = e^{-r/\lambda}\) получается \(|\nabla L| = e^{-r/\lambda}/\lambda\). Конкретный вид \(\ell\)'),
    ('p — двумерный вектор руки', r'\(\mathbf{p}\) — двумерный вектор руки'),
    ('- **κ∇L** — накопление', r'- **\(\kappa\nabla L\)** — накопление'),
    ('Пока зритель стоит на месте, p растёт', r'Пока зритель стоит на месте, \(\mathbf{p}\) растёт'),
    ('на |p\\*| = τ(κ|∇L| − γ) или не упрётся в R', r'на \(|\mathbf{p}^{\ast}| = \tau(\kappa|\nabla L| - \gamma)\) или не упрётся в \(R\)'),
    ('и p догоняет', r'и \(\mathbf{p}\) догоняет'),
    ('- **−p/τ** — экспоненциальное затухание, задаёт время памяти τ.', r'- **\(-\mathbf{p}/\tau\)** — экспоненциальное затухание, задаёт время памяти \(\tau\).'),
    ('- **−γ p̂** — затухание', r'- **\(-\gamma\,\hat{\mathbf{p}}\)** — затухание'),
    ('При p = 0 рука остаётся на месте, пока κ|∇L| ≤ γ.', r'При \(\mathbf{p} = 0\) рука остаётся на месте, пока \(\kappa|\nabla L| \le \gamma\).'),
    ('у стены κ|∇L(r_wall)| < γ:', r'у стены \(\kappa|\nabla L(r_{\text{wall}})| < \gamma\):'),
    ('- **R** — максимальный вылет', r'- **\(R\)** — максимальный вылет'),
    ('Значит, τ порядка', r'Значит, \(\tau\) порядка'),
    ('при τ → 0 и сильном насыщении (κτ|∇L| ≫ R): отклик мгновенный и сразу упирается в R,',
     r'при \(\tau \to 0\) и сильном насыщении (\(\kappa\tau|\nabla L| \gg R\)): отклик мгновенный и сразу упирается в \(R\),'),
    ('Траектория **p(t)** записывается', r'Траектория \(\mathbf{p}(t)\) записывается'),
    ('петля собственной формы внутри круга радиуса R.', r'петля собственной формы внутри круга радиуса \(R\).'),
    ('дуга окружности радиуса R по тем углам', r'дуга окружности радиуса \(R\) по тем углам'),
    ('дуга радиуса R только по тем углам', r'дуга радиуса \(R\) только по тем углам'),
]

PLACE = [  # (якорь в исходном тексте блока, фигуры после блока)
    ('- **Зритель** обходит стол', ['section']),
    ('**0. Коридор', ['corridor']),
    ('**1. У входа', ['alive']),
    ('**2. Первый проход', ['pass1']),
    ('**3. Выход в предбанник', ['vestibule']),
    ('**4. Второй проход', ['pass2']),
    ('**6. Сброс', ['simfull']),
    ('Он направлен **на зрителя**', ['signal']),
    ('- **Порог.**', ['decay', 'threshold']),
    ('Оценка масштабов', ['params']),
    ('**Без памяти:** дуга', ['routes']),
    ('| Узел |', ['mech', 'membrane', 'corridortech']),
    ('**QR-код**', ['receipt']),
    ('**Где стоит лидар.**', ['lidar', 'room', 'light']),
]


def inline(t):
    t = t.replace('\\*', '\x00')
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    return t.replace('\x00', '*')


LIST_RE = re.compile(r'^(\s*)([-*]|\d+\.)\s+(.*)$')


def render_list(lines):
    """lines: [(indent, marker|None, text)] -> nested html"""
    out, stack = [], []  # stack of (indent, tag)

    def open_list(ind, marker):
        tag = 'ol' if marker[0].isdigit() else 'ul'
        out.append('<%s>' % tag)
        stack.append((ind, tag))

    for ind, marker, text in lines:
        if marker is None:  # continuation / math
            out.append(text if text.startswith('<') else '<p>%s</p>' % inline(text))
            continue
        while stack and ind < stack[-1][0]:
            out.append('</li></%s>' % stack.pop()[1])
        if not stack or ind > stack[-1][0]:
            open_list(ind, marker)
        else:
            out.append('</li>')
        out.append('<li>%s' % inline(text))
    while stack:
        out.append('</li></%s>' % stack.pop()[1])
    return ''.join(out)


def md_blocks(md):
    lines = md.split('\n')
    blocks, i, n = [], 0, len(lines)  # (raw, html, kind)
    while i < n:
        ln = lines[i]
        s = ln.strip()
        if not s or s == '---':
            i += 1
            continue
        if s.startswith('# '):
            blocks.append((s, '', 'title')); i += 1; continue
        if s.startswith('## ') or s.startswith('### '):
            lvl = 2 if s.startswith('## ') else 3
            text = s[lvl + 1:].strip()
            slug = 's' + re.sub(r'\W+', '-', text.split(' ')[0]).strip('-')
            blocks.append((s, '<h%d id="%s">%s</h%d>' % (lvl, slug, inline(text), lvl), 'h%d' % lvl)); i += 1; continue
        if s.startswith('```'):
            j = i + 1
            while not lines[j].strip().startswith('```'):
                j += 1
            blocks.append(('\n'.join(lines[i:j + 1]), '<pre>%s</pre>' % html.escape('\n'.join(lines[i + 1:j])), 'code'))
            i = j + 1; continue
        if s == '$$':
            j = i + 1
            while lines[j].strip() != '$$':
                j += 1
            blocks.append(('', '<div class="math">$$%s$$</div>' % '\n'.join(lines[i + 1:j]), 'math'))
            i = j + 1; continue
        if s.startswith('|'):
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip()); i += 1
            cells = [[c.strip() for c in r.strip('|').split('|')] for r in rows if not re.match(r'^\|[-|\s]+\|$', r)]
            h = '<div class="tablewrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
                ''.join('<th>%s</th>' % inline(c) for c in cells[0]),
                ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r) for r in cells[1:]))
            blocks.append(('\n'.join(rows), h, 'table')); continue
        if LIST_RE.match(ln):
            items, raw = [], []
            while i < n:
                ln = lines[i]
                m = LIST_RE.match(ln)
                if m:
                    items.append((len(m.group(1)), m.group(2), m.group(3))); raw.append(ln); i += 1; continue
                if not ln.strip():
                    k = i
                    while k < n and not lines[k].strip():
                        k += 1
                    if k < n and (LIST_RE.match(lines[k]) or lines[k].startswith(' ') or lines[k].strip() == '$$'):
                        i = k; continue
                    break
                if ln.strip() == '$$':
                    j = i + 1
                    while lines[j].strip() != '$$':
                        j += 1
                    items.append((99, None, '<div class="math">$$%s$$</div>' % '\n'.join(lines[i + 1:j])))
                    i = j + 1; continue
                if ln.startswith(' '):
                    items.append((len(ln) - len(ln.lstrip()), None, ln.strip())); raw.append(ln); i += 1; continue
                break
            blocks.append(('\n'.join(raw), render_list(items), 'list')); continue
        para = []
        while i < n and lines[i].strip() and not LIST_RE.match(lines[i]) and not lines[i].strip().startswith(('#', '|', '$$', '```')):
            para.append(lines[i].strip()); i += 1
        text = ' '.join(para)
        if text.startswith('*') and text.endswith('*') and not text.startswith('**'):
            blocks.append((text, '<p class="lede">%s</p>' % inline(text.strip('*')), 'lede'))
        else:
            blocks.append((text, '<p>%s</p>' % inline(text), 'p'))
    return blocks


# ---------------------------------------------------------------- page

def build():
    md = open(MD, encoding='utf-8').read()
    for a, b in INLINE_MATH:
        if a not in md:
            print('warning: inline-math anchor not found:', a[:60])
        md = md.replace(a, b)
    blocks = md_blocks(md)
    body, toc, lede = [], [], ''
    used = set()
    for raw, h, kind in blocks:
        if kind == 'title':
            continue
        if kind == 'lede':
            lede = h.replace(' Документ для совместной правки.', ''); continue
        if kind == 'code':
            body.append(load_figure('plan')); continue
        if kind == 'h2':
            if body:
                body.append('</section>')
            m = re.search(r'id="([^"]+)">(.*?)</h2>', h)
            toc.append('<li><a href="#%s">%s</a></li>' % (m.group(1), m.group(2)))
            body.append('<section>')
        body.append(h)
        for anchor, figs in PLACE:
            if anchor in raw and anchor not in used:
                used.add(anchor)
                body.extend(load_figure(k) for k in figs)
    body.append('</section>')
    for anchor, _ in PLACE:
        if anchor not in used:
            print('warning: figure anchor not found:', anchor)

    intro = open(INTRO, encoding='utf-8').read()
    intro = re.sub(r'<!--FIG:(\w+)-->', lambda m: load_figure(m.group(1)), intro)
    toc.insert(0, '<li><a href="#intro">0. Научный сюжет</a></li>')

    page = TEMPLATE.format(lede=lede, hero=load_figure('hero'), toc=''.join(toc), intro=intro, body='\n'.join(body))
    open(OUT, 'w', encoding='utf-8').write(page)
    print('written', OUT, '%.0f KB' % (len(page.encode()) / 1024))


TEMPLATE = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Baal Zikaron · בַּעַל זִיכָּרוֹן</title>
<meta name="description" content="Концепция инсталляции для выставки «Архивы нечеловеческой памяти»: инерция как простейшая память, нейтрофилы и клетка с рукой.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Frank+Ruhl+Libre:wght@400;500&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<style>
:root {{ --bg:#111316; --card:#1B1E23; --ink:#ECE8E1; --text:#C9C3B8; --muted:#8E887E; --amber:#F2B252; --blue:#6E9FD8; --rule:#2A2D33; }}
* {{ box-sizing:border-box; }}
html {{ background:var(--bg); }}
body {{ margin:0; background:var(--bg); color:var(--text); font:400 19px/1.65 'IBM Plex Sans', Arial, sans-serif; -webkit-font-smoothing:antialiased; }}
main {{ max-width:900px; margin:0 auto; padding:0 16px 120px; }}
header.top {{ max-width:1100px; margin:0 auto; padding:64px 16px 24px; display:grid; grid-template-columns:1fr minmax(0,560px); gap:32px; align-items:center; }}
header.top .eyebrow {{ font:500 14px/1.4 'IBM Plex Mono', monospace; letter-spacing:.14em; text-transform:uppercase; color:var(--amber); margin:0 0 18px; }}
header.top h1 {{ font:500 clamp(48px,7vw,96px)/1 'Cormorant Garamond', Georgia, serif; color:var(--ink); margin:0 0 16px; }}
header.top h1 .he {{ font-family:'Frank Ruhl Libre', 'Times New Roman', serif; font-weight:500; display:block; text-align:left; }}
header.top h1 small {{ display:block; font:400 16px/1.4 'IBM Plex Mono', monospace; color:var(--muted); margin-top:12px; letter-spacing:.04em; }}
.lede {{ color:var(--text); font-size:20px; margin:0 0 8px; }}
.byline {{ font:400 15px/1.5 'IBM Plex Mono', monospace; color:var(--muted); }}
header.top .fig {{ left:0; transform:none; width:100%; margin:0; }}
nav.toc {{ max-width:900px; margin:8px auto 48px; padding:0 16px; }}
nav.toc ol {{ list-style:none; padding:20px 24px; margin:0; background:var(--card); border-radius:14px; columns:2; column-gap:32px; }}
nav.toc li {{ margin:4px 0; break-inside:avoid; }}
nav.toc a {{ color:var(--text); text-decoration:none; border-bottom:1px solid var(--rule); }}
nav.toc a:hover {{ color:var(--amber); border-color:var(--amber); }}
section {{ margin-top:72px; }}
h2 {{ font:500 clamp(36px,5vw,52px)/1.1 'Cormorant Garamond', Georgia, serif; color:var(--ink); margin:0 0 24px; padding-top:8px; border-top:1px solid var(--rule); padding-top:32px; }}
h3 {{ font:600 22px/1.3 'IBM Plex Sans', Arial, sans-serif; color:var(--ink); margin:40px 0 12px; }}
p {{ margin:0 0 18px; }}
strong {{ color:var(--ink); font-weight:600; }}
em {{ font-style:italic; }}
a {{ color:var(--amber); }}
ul, ol {{ padding-left:24px; margin:0 0 18px; }}
li {{ margin:6px 0; }}
li > p {{ margin:8px 0; }}
.math {{ overflow-x:auto; overflow-y:hidden; margin:8px 0 18px; color:var(--ink); }}
.katex {{ font-size:1.08em; }}
.math .katex {{ font-size:1.3em; }}
blockquote.thesis {{ margin:40px 0; padding:28px 32px; background:var(--amber); color:#17191C; border-radius:14px; font:500 clamp(26px,3.6vw,36px)/1.2 'Cormorant Garamond', Georgia, serif; }}
pre {{ background:var(--card); padding:16px; border-radius:10px; overflow-x:auto; font:13px/1.4 'IBM Plex Mono', monospace; }}
.tablewrap {{ overflow-x:auto; margin:8px 0 26px; position:relative; left:50%; transform:translateX(-50%); width:min(1000px, calc(100vw - 32px)); }}
table {{ border-collapse:collapse; font-size:16px; line-height:1.5; min-width:640px; }}
th, td {{ text-align:left; vertical-align:top; padding:10px 12px; border-bottom:1px solid var(--rule); }}
th {{ color:var(--amber); font-weight:600; }}
figure.fig {{ position:relative; left:50%; transform:translateX(-50%); width:min(1100px, calc(100vw - 32px)); margin:32px 0 40px; }}
figure.fig .box {{ position:relative; overflow:hidden; border-radius:14px; }}
figure.fig .stage {{ position:absolute; left:0; top:0; transform-origin:0 0; overflow:hidden; }}
figure.fig .slide {{ font-size:16px; line-height:normal; }}
figure.fig .slide p, figure.fig .slide h3 {{ margin:0; }}
figure.fig .slide table {{ min-width:0; border-collapse:collapse; }}
figure.fig .slide th, figure.fig .slide td {{ padding:0.35em 0.6em; border-bottom:1px solid #2A2D33; }}
figure.fig .slide ul {{ margin:0; }}
figcaption {{ font-size:15px; line-height:1.5; color:var(--muted); margin:10px auto 0; max-width:900px; padding:0 4px; }}
footer {{ max-width:900px; margin:0 auto; padding:24px 16px 64px; color:var(--muted); font-size:14px; border-top:1px solid var(--rule); }}
@media (max-width:820px) {{
  header.top {{ grid-template-columns:1fr; padding-top:40px; }}
  nav.toc ol {{ columns:1; }}
  body {{ font-size:17px; }}
}}
</style>
</head>
<body>
<header class="top">
<div>
<p class="eyebrow">Архивы нечеловеческой памяти · концепция</p>
<h1><span class="he" lang="he" dir="rtl">בַּעַל זִיכָּרוֹן</span><small>Baal Zikaron · рабочее название</small></h1>
{lede}
<p class="byline">Рома Гайдаров · черновик, октябрь 2026</p>
</div>
{hero}
</header>
<nav class="toc"><ol>{toc}</ol></nav>
<main>
{intro}
{body}
</main>
<footer>Черновик. Траектории и графики посчитаны по модели из раздела 4 с иллюстративными параметрами. Та же концепция в виде слайдов: <a href="slides.html">slides.html</a>.</footer>
<script>
function fitFigs() {{
  document.querySelectorAll('figure.fig').forEach(function (f) {{
    var w = +f.dataset.w, h = +f.dataset.h, box = f.querySelector('.box'), st = f.querySelector('.stage');
    var s = Math.min(1, box.clientWidth / w);
    st.style.transform = 'scale(' + s + ')';
    box.style.height = (h * s) + 'px';
  }});
}}
window.addEventListener('resize', fitFigs);
document.addEventListener('DOMContentLoaded', function () {{
  fitFigs();
  renderMathInElement(document.querySelector('main'), {{
    delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '\\\\(', right: '\\\\)', display: false}}],
    throwOnError: false
  }});
}});
</script>
</body>
</html>
'''

ORDER = ['cover', 'inertia', 'honey', 'wave', 'loops', 'statement', 'plan', 'section', 'overview', 'corridor', 'alive',
         'pass1', 'vestibule', 'pass2', 'receipt', 'simfull', 'signal', 'equation', 'decay', 'threshold', 'nomem', 'routes',
         'params', 'mech', 'components', 'membrane', 'lidar', 'corridortech', 'room', 'light', 'theme', 'viewer', 'questions', 'next']


def build_slides():
    parts = []
    for n, sid in enumerate(ORDER, 1):
        fig = load_figure('s%d' % n, dict(slide=sid, crop=(0, 0, 1920, 1080), remove=[]), keep_headings=True)
        parts.append('<div class="sl" id="%s">%s<p class="num">%d / %d</p></div>' % (sid, fig, n, len(ORDER)))
    page = SLIDES_TEMPLATE.replace('{slides}', '\n'.join(parts))
    open(OUT_SLIDES, 'w', encoding='utf-8').write(page)
    print('written', OUT_SLIDES, '%.0f KB' % (len(page.encode()) / 1024))


SLIDES_TEMPLATE = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Baal Zikaron · слайды</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Frank+Ruhl+Libre:wght@400;500&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap">
<style>
* { box-sizing:border-box; }
html, body { margin:0; background:#08090B; color:#8E887E; font:14px/1.4 'IBM Plex Mono', monospace; }
.bar { max-width:1600px; margin:0 auto; padding:20px 16px 4px; display:flex; justify-content:space-between; gap:16px; }
.bar a { color:#F2B252; }
.sl { max-width:1600px; margin:0 auto; padding:12px 16px 20px; }
figure.fig { margin:0; }
figure.fig .box { position:relative; overflow:hidden; border-radius:10px; box-shadow:0 10px 40px rgba(0,0,0,.5); }
figure.fig .stage { position:absolute; left:0; top:0; transform-origin:0 0; overflow:hidden; }
figure.fig .slide p, figure.fig .slide h1, figure.fig .slide h2, figure.fig .slide h3 { margin:0; }
figure.fig .slide ul { margin:0; }
figure.fig .slide table { border-collapse:collapse; }
figure.fig .slide th, figure.fig .slide td { padding:0.35em 0.6em; border-bottom:1px solid #2A2D33; text-align:left; }
.num { text-align:right; margin:6px 4px 0; }
</style>
</head>
<body>
<div class="bar"><span>Baal Zikaron · слайды · ← → или PgUp/PgDn</span><a href="./">связный текст</a></div>
{slides}
<script>
function fitFigs() {
  document.querySelectorAll('figure.fig').forEach(function (f) {
    var w = +f.dataset.w, h = +f.dataset.h, box = f.querySelector('.box'), st = f.querySelector('.stage');
    var s = box.clientWidth / w;
    st.style.transform = 'scale(' + s + ')';
    box.style.height = (h * s) + 'px';
  });
}
window.addEventListener('resize', fitFigs);
document.addEventListener('DOMContentLoaded', fitFigs);
document.addEventListener('keydown', function (e) {
  var d = {ArrowRight: 1, ArrowDown: 1, PageDown: 1, ' ': 1, ArrowLeft: -1, ArrowUp: -1, PageUp: -1}[e.key];
  if (!d) return;
  e.preventDefault();
  var sl = Array.from(document.querySelectorAll('.sl')), y = window.scrollY + 10;
  var i = sl.findIndex(function (s) { return s.offsetTop > y; });
  i = i < 0 ? sl.length : i;
  var t = d > 0 ? sl[i] : sl[Math.max(0, i - 2)];
  if (t) window.scrollTo({top: t.offsetTop, behavior: 'smooth'});
});
</script>
</body>
</html>
'''

if __name__ == '__main__':
    build()
    build_slides()
