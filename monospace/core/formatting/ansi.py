from typing import List, Union
from .formatter import Formatter, FormatTag, Format as F


def csi(params, end):
    return "\033[%s%s" % (";".join(str(p) for p in params), end)


def rgb(hexa):
    if hexa[0] == "#":
        hexa = hexa[1:]
    return int(hexa[:2], 16), int(hexa[2:4], 16), int(hexa[4:6], 16)


def tag_color(tag):
    fg = csi([39], "m")
    bg = csi([49], "m")
    if "foreground" in tag.data:
        fg = csi([38, 2, *rgb(tag.data["foreground"])], "m")
    if "background" in tag.data:
        bg = csi([48, 2, *rgb(tag.data["background"])], "m")
    return fg + bg


codes = {
    F.Bold: (csi([1], "m"), csi([22], "m")),
    F.Italic: (csi([3], "m"), csi([23], "m")),
    F.Color: lambda tag: tag_color(tag) if tag.open else csi([39, 49], "m")
}


def get_code(tag):
    code = codes.get(tag.kind, ("", ""))
    if callable(code):
        return code(tag)
    return code[not tag.open]


class AnsiFormatter(Formatter):
    @staticmethod
    def format_tags(line: List[Union[FormatTag, str]]) -> str:
        result = ""
        for elem in line:
            if isinstance(elem, str):
                result += elem
            else:
                result += get_code(elem)

        return result