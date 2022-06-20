from typing import Literal
from pathlib import Path
from matplotlib.font_manager import FontProperties

# import fontawesome
import fontawesomefree

from matplotlib.offsetbox import (
    TextArea,
)


class FontAwesome:
    root = Path(fontawesomefree.__path__[0])
    fontname_dict = dict(regular="fa-regular-400.ttf",
                         solid="fa-solid-900.ttf")
    ymlpath = (root / "static" / "fontawesomefree" / "metadata"
               / "icons.yml")
    icons = {}

    @classmethod
    def get_fontprop(cls, family="solid", size=11):
        fontname = cls.fontname_dict[family]
        fontpath = (cls.root / "static" / "fontawesomefree" / "webfonts"
                    / fontname)

        fontprop = FontProperties(fname=fontpath, size=size)

        return fontprop

    @classmethod
    def load_icons_yaml(cls):
        import yaml

        with open(cls.ymlpath) as f:

            data = yaml.load(f, Loader=yaml.CLoader)
            icons = dict((k, chr(int(v["unicode"], 16)))
                         for k, v in data.items())

        return icons

    @classmethod
    def load_icons_ryml(cls):
        # pyyaml seems quite slow. We try rapidyaml.
        import ryml

        with open(cls.ymlpath, "rb") as buf:
            tree = ryml.parse_in_place(bytearray(buf.read()))
            icons = {}
            kk = ""  # key
            for n, indentation_level in ryml.walk(tree):
                if indentation_level == 1:
                    kk = str(tree.key(n), "utf8")
                elif indentation_level == 2 and tree.key(n) == b"unicode":
                    v = str(tree.val(n), "utf8")
                    icons[kk] = chr(int(v, 16))
        return icons

FontAwesome.icons.update(FontAwesome.load_icons_ryml())


def get_fa_textarea(icon_name: str,
                    color="k",
                    size: int = 10,
                    family: Literal["regular", "solid"] = "solid",
                    ):

    fontprop = FontAwesome.get_fontprop(family=family,
                                        size=size)

    button = TextArea(FontAwesome.icons[icon_name],
                      textprops=dict(fontproperties=fontprop,
                                      color=color))
    return button
