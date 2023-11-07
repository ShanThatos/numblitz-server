from functools import cache

from jinja2 import Environment, PackageLoader, select_autoescape

from src import config

jinja_env = Environment(loader=PackageLoader("src.utils.jinja"), autoescape=select_autoescape())

CACHE_TEMPLATES = config.get("CACHE_TEMPLATES", "yes") == "yes"


def get_template(name: str):
    return jinja_env.get_template(name)


def get_macro(name: str):
    name, macro = name.split(":", 1)
    return getattr(get_template(name).module, macro)


if CACHE_TEMPLATES:
    get_template = cache(get_template)
    get_macro = cache(get_macro)


def render_template(name: str, **kwargs):
    return get_template(name).render(**kwargs)


def render_macro(name: str, *args, **kwargs):
    return get_macro(name)(*args, **kwargs)
