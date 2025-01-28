# -*- coding: utf-8 -*-
# tests/test_star_path_svg.py
import os
import base64
import re
from core.star_path import get_diagram


test_input = {"year": -2000, "month": 3, "day": 1, "lat": 40, "lng": 116, "tz_id": "Asia/Shanghai", "name": "jupiter"}
reference_svg_filename = 'example-matplotlib-3.9.1.post1.svg'


def normalize_svg_content(svg_content: str) -> str:
    """Normalizes SVG content by replacing specified elements and attributes."""
    # Ignore these elements
    svg_content = re.sub(r'<dc:date>[^<]+</dc:date>', '<dc:date> DATE </dc:date>', svg_content)
    svg_content = re.sub(r'<dc:title>[^<]+</dc:title>', '<dc:title> TITLE </dc:title>', svg_content)
    svg_content = re.sub(r'url\(#[a-z0-9]+\)', 'url(#URL)', svg_content)
    svg_content = re.sub(r'id="[a-z0-9]+"', 'id="ID"', svg_content)
    svg_content = re.sub(r'xlink:href="#[a-z0-9]+"', 'xlink:href="#HREF"', svg_content)
    svg_content = re.sub(r'(xlink:href="#DejaVuSans-.+") x="([^"]+)"', r'\1 transform="translate(\2 0)"', svg_content)
    # Remove extra whitespace and normalize line endings
    svg_content = '\n'.join(line.strip() for line in svg_content.splitlines())

    return svg_content


def test_get_svg():
    """Tests the SVG generated by `get_diagram` by comparing it with a reference SVG file."""
    res = get_diagram(**test_input)['svg_data']
    generated_svg = base64.b64decode(res).decode('utf-8')

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), reference_svg_filename), encoding='utf-8') as f:
        reference_svg = f.read()

    normalized_generated = normalize_svg_content(generated_svg)
    normalized_reference = normalize_svg_content(reference_svg)

    assert normalized_generated == normalized_reference
