"""Jinja2 テンプレート環境"""
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
env = Environment(
    loader=FileSystemLoader(str(ROOT / 'templates')),
    autoescape=select_autoescape(['html', 'xml']),
    auto_reload=True,
)
env.filters['tojson'] = lambda v: json.dumps(v, ensure_ascii=False)


def render(template_name: str, **context) -> str:
    return env.get_template(template_name).render(**context)
