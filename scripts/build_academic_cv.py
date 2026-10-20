#!/usr/bin/env python3
"""Generate the academic CV from the website's CV and publication data.

Requires Python with reportlab and Ruby's standard YAML/JSON libraries.
Run from any directory: python3 scripts/build_academic_cv.py
The separate one-page resume is authored in documents/Research_Resume.tex.
"""
from html import escape
from pathlib import Path
import json
import re
import subprocess

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://farbod-siahkali.github.io'
OUTPUT = ROOT / 'files/Farbod_Siahkali_CV.pdf'
NAVY = colors.HexColor('#003769')
GRAY = colors.HexColor('#555555')


def plain(text):
    return text.replace('–', '-').replace('—', '-').replace('’', "'").replace('“', '"').replace('”', '"').replace('\u00a0', ' ')


def markup(text):
    text = escape(plain(text))
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    def to_link(match):
        label, url = match.groups()
        if url.startswith('/'):
            url = SITE + url
        return f'<a href="{url}" color="#003769">{label}</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', to_link, text)


def register_fonts():
    folder = Path('/System/Library/Fonts/Supplemental')
    if (folder / 'Times New Roman.ttf').exists():
        for name, file in [('CVBody', 'Times New Roman.ttf'), ('CVBold', 'Times New Roman Bold.ttf'), ('CVItalic', 'Times New Roman Italic.ttf')]:
            pdfmetrics.registerFont(TTFont(name, str(folder / file)))
        pdfmetrics.registerFontFamily('CVBody', normal='CVBody', bold='CVBold', italic='CVItalic', boldItalic='CVBold')
        return 'CVBody', 'CVBold'
    return 'Times-Roman', 'Times-Bold'


def build():
    body_font, bold_font = register_fonts()
    styles = {
        'name': ParagraphStyle('Name', fontName=bold_font, fontSize=24, leading=27, textColor=NAVY, alignment=TA_CENTER, spaceAfter=5),
        'subtitle': ParagraphStyle('Subtitle', fontName=body_font, fontSize=11, leading=14, alignment=TA_CENTER, spaceAfter=3),
        'contact': ParagraphStyle('Contact', fontName=body_font, fontSize=9.5, leading=13, alignment=TA_CENTER, spaceAfter=3),
        'heading': ParagraphStyle('Heading', fontName=bold_font, fontSize=12.5, leading=16, textColor=NAVY, spaceBefore=12, spaceAfter=6, keepWithNext=True),
        'subheading': ParagraphStyle('Subheading', fontName=bold_font, fontSize=10.5, leading=13.5, spaceBefore=6, spaceAfter=4, keepWithNext=True),
        'body': ParagraphStyle('Body', fontName=body_font, fontSize=10.5, leading=13.5, spaceAfter=5),
        'bullet': ParagraphStyle('Bullet', fontName=body_font, fontSize=10.5, leading=13.5, leftIndent=12, firstLineIndent=0, bulletIndent=1, spaceAfter=3),
        'citation': ParagraphStyle('Citation', fontName=body_font, fontSize=10.5, leading=13.5, spaceAfter=3),
        'link': ParagraphStyle('ReferenceLink', fontName=body_font, fontSize=8.5, leading=10.5, textColor=NAVY, spaceAfter=7),
    }
    papers = json.loads(subprocess.check_output(['ruby', '-ryaml', '-rjson', '-e', 'puts JSON.generate(YAML.load_file(ARGV[0]))', str(ROOT / '_data/research_publications.yml')], text=True))
    source = (ROOT / '_pages/cv.md').read_text().split('---', 2)[2]
    story = [
        Paragraph('Farbod Siahkali', styles['name']),
        Paragraph('Curriculum Vitae | October 2026', styles['subtitle']),
        Paragraph('Electrical Engineering, Purdue University | West Lafayette, Indiana', styles['contact']),
        Paragraph('<a href="mailto:siahkali@purdue.edu">siahkali@purdue.edu</a> | <a href="' + SITE + '">farbod-siahkali.github.io</a> | <a href="https://scholar.google.com/citations?user=-99KSTsAAAAJ&amp;hl=en">Google Scholar</a> | <a href="https://www.linkedin.com/in/farbod-siahkali/">LinkedIn</a>', styles['contact']),
        Spacer(1, 6),
    ]
    started = False
    section = ''
    for line in source.splitlines():
        line = line.rstrip()
        if line.startswith('## Education'):
            started = True
        if not started or not line.strip():
            continue
        if line.startswith('## '):
            section = line[3:]
            if section in {'Peer-Reviewed Publications', 'Teaching Experience'}:
                story.append(PageBreak())
            story.append(Paragraph(markup(section), styles['heading']))
        elif line.startswith('{% include research-publications.html'):
            category = re.search(r'category="([a-z]+)"', line).group(1)
            for paper in papers:
                if paper['category'] != category:
                    continue
                authors = escape(plain(paper.get('authors', 'Farbod Siahkali (first author)'))).replace('Farbod Siahkali', '<b>Farbod Siahkali</b>')
                citation = authors + '. ' + '<b>' + escape(plain(paper['title'])) + '.</b> '
                venue = escape(plain(paper['venue']))
                if category == 'review':
                    citation += 'Under review at ' + venue + '.'
                elif category == 'preparation':
                    citation += 'In preparation for submission to ' + venue + '.'
                else:
                    citation += venue + '. ' + escape(paper['status'])
                if paper.get('note'):
                    citation += ' ' + escape(plain(paper['note']))
                entry = [Paragraph(citation, styles['citation'])]
                if paper.get('url'):
                    url = escape(paper['url'], quote=True)
                    entry.append(Paragraph(f'<a href="{url}" color="#003769">{url}</a>', styles['link']))
                else:
                    entry.append(Spacer(1, 6))
                story.append(KeepTogether(entry))
        elif line.startswith('[Publication details,'):
            continue
        elif line.startswith('  * '):
            story.append(Paragraph(markup(line[4:]), styles['bullet'], bulletText='-'))
        elif line.startswith('* '):
            if section == 'Research Experience':
                story.append(Paragraph(markup(line[2:]), styles['subheading']))
            else:
                story.append(Paragraph(markup(line[2:]), styles['body']))
        else:
            story.append(Paragraph(markup(line), styles['body']))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#BBBBBB'))
        canvas.setLineWidth(.4)
        canvas.line(47, 36, letter[0] - 47, 36)
        canvas.setFont(body_font, 8.5)
        canvas.setFillColor(GRAY)
        canvas.drawString(47, 23, 'Farbod Siahkali | Academic CV | October 2026')
        canvas.drawRightString(letter[0] - 47, 23, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=letter, leftMargin=47, rightMargin=47, topMargin=37, bottomMargin=48, title='Farbod Siahkali - Academic Curriculum Vitae', author='Farbod Siahkali', subject='Research, publications, education, teaching, mentoring, and academic service')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == '__main__':
    build()
