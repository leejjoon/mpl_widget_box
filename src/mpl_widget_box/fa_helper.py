from pathlib import Path
from matplotlib.font_manager import FontManager, FontProperties

# import fontawesome
import fontawesomefree

from matplotlib.offsetbox import (
    TextArea,
)

__all__ = ["FontAwesome", "get_fa_textarea"]


class FontAwesome:
    root = Path(fontawesomefree.__path__[0])
    fontname_dict = dict(regular="fa-regular-400.ttf", solid="fa-solid-900.ttf")
    ymlpath = root / "static" / "fontawesomefree" / "metadata" / "icons.yml"
    icons = {}

    @classmethod
    def get_fontprop(cls, family="solid", size=11):
        fontname = cls.fontname_dict[family]
        fontpath = cls.root / "static" / "fontawesomefree" / "webfonts" / fontname

        fontprop = FontProperties(fname=fontpath, size=size)

        return fontprop

    @classmethod
    def load_icons_yaml(cls):
        import yaml

        with open(cls.ymlpath) as f:

            data = yaml.load(f, Loader=yaml.CLoader)
            icons = dict((k, chr(int(v["unicode"], 16))) for k, v in data.items())

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


# While it would be good to generate the fa_icons dictionary by parsing the
# yaml file included in the fontawesomefree package, reading the yaml file
# takes more than I expected. Using ryml improves the reading speed, but it's
# python interface seems to be still in development at this stage. We used to
# use fontawesome package, but its contents seems outdated. For now, we
# hardcode the unicode characters that are used in the package. We should think
# about better way for it.

if __name__ != "__main__":
    # we do not want to import fa_icons if this file is executed to create the
    # fa_icons.py file.
    from .fa_icons import fa_icons

    FontAwesome.icons.update(fa_icons)


def get_fa_textarea(
    icon_name: str,
    color="k",
    size: int = 10,
    family: str = "solid",
):

    assert family in ["regular", "solid"]
    fontprop = FontAwesome.get_fontprop(family=family, size=size)

    char = FontAwesome.icons.get(icon_name, icon_name)
    button = TextArea(
        char,
        textprops=dict(fontproperties=fontprop, color=color),
    )
    return button


def main():
    icons_all = FontAwesome.load_icons_yaml()
    kl = [
        "plus",
        "caret-down",
        "angles-right",
        "circle-dot",
        "circle",
        "square-check",
        "square",
        "clipboard-check",  # used by widget_span.py
    ]

    icons = dict((k, icons_all[k]) for k in kl)
    import pprint

    with open("fa_icons.py", "w") as fout:
        fout.write("# This is auto-generated by fa_helper.py\n")
        fout.write("fa_icons = \\\n")
        pprint.pprint(icons, indent=4, stream=fout)


if __name__ == "__main__":
    main()
