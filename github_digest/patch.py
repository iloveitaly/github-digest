"""
https://github.com/nedbat/dinghy/blob/9d8136983a566304793e3e773c97e1ee5f9ae74c/src/dinghy/jinja_helpers.py#L53
"""

import colorsys
import datetime
from pathlib import Path

import aiofiles
import dinghy.jinja_helpers
import emoji
import jinja2

from github_digest.svg import svg_url_to_base64_png


def custom_render_jinja(template_filename, **variables):
    """Render a template file, with variables."""
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            [
                Path("."),
                Path(__file__).parent / "templates",
            ]
        ),
        autoescape=True,
    )
    jenv.filters["datetime"] = dinghy.jinja_helpers.datetime_format
    jenv.filters["label_color_css"] = dinghy.jinja_helpers.label_color_css

    # NOTE this is the main addition!
    jenv.globals["inline_svg"] = svg_url_to_base64_png

    template = jenv.get_template(template_filename)
    html = template.render(**variables)

    return html


# Monkey patch the original function
dinghy.jinja_helpers = custom_render_jinja
