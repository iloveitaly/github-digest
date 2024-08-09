"""
https://github.com/nedbat/dinghy/blob/9d8136983a566304793e3e773c97e1ee5f9ae74c/src/dinghy/jinja_helpers.py#L53
"""

import colorsys
import datetime
import inspect
from pathlib import Path

import aiofiles
import dinghy.jinja_helpers
import emoji
import jinja2
import patchy
from dinghy.jinja_helpers import datetime_format, label_color_css


def custom_render_jinja(template_filename, **variables):
    """Render a template file, with variables."""
    from github_digest.svg import svg_url_to_base64_png

    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            [
                Path("."),
                Path(__file__).parent / "templates",
            ]
        ),
        autoescape=True,
    )
    jenv.filters["datetime"] = datetime_format
    jenv.filters["label_color_css"] = label_color_css

    # NOTE this is the main addition!
    jenv.globals["inline_svg"] = svg_url_to_base64_png

    template = jenv.get_template(template_filename)
    html = template.render(**variables)

    return html


# Monkey patch the original function
# dinghy.jinja_helpers = custom_render_jinja


def patch_me():
    print("unpatched")


def patched():
    print("patched")


import re


def replace_first_method_name(code, new_name):
    return re.sub(r"^def\s+\w+\(", f"def {new_name}(", code, count=1)


patchy.replace(
    patch_me,
    inspect.getsource(patch_me),
    replace_first_method_name(inspect.getsource(patched), patch_me.__name__),
)

patchy.replace(
    dinghy.jinja_helpers.render_jinja,
    inspect.getsource(dinghy.jinja_helpers.render_jinja),
    replace_first_method_name(
        inspect.getsource(custom_render_jinja),
        dinghy.jinja_helpers.render_jinja.__name__,
    ),
)
