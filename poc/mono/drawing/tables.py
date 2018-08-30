from ..symbols import lines, Styles

empty = Styles.empty


class Node(object):
    def __init__(self, left=None, top=None, right=None, bottom=None):
        self.left, self.top, self.right, self.bottom = left, top, right, bottom

    @property
    def all(self):
        return [self.left, self.top, self.right, self.bottom]


class EmptyCell(object):
    def __init__(self):
        self.styles = Node(empty, empty, empty, empty)


class Cell(object):
    def __init__(self, left, top, right, bottom):
        self.styles = Node(left=left, top=top, right=right, bottom=bottom)
        self.neighbours = Node(EmptyCell(), EmptyCell(), EmptyCell(), EmptyCell())

    @staticmethod
    def all_sides(weight):
        return Cell(weight, weight, weight, weight)

    @staticmethod
    def make(format_string):
        if len(format_string) == 1:
            return {
                "L": Cell.all_sides(Styles.light),
                "H": Cell.all_sides(Styles.heavy),
                "D": Cell.all_sides(Styles.double)
            }[format_string]

        elif len(format_string) == 4:
            left, top, right, bottom = map(lambda l: Cell.long_format[l], format_string)
            return Cell(left=left, top=top, right=right, bottom=bottom)

    def __repr__(self):
        def long_format(meta_cell):
            return [Cell.reverse_long_format[s] for s in meta_cell.styles.all]

        styles = long_format(self)
        neighbours = "(%s, %s, %s, %s)" % (long_format(self.neighbours.left),
                                           long_format(self.neighbours.top),
                                           long_format(self.neighbours.right),
                                           long_format(self.neighbours.bottom))

        return "Cell(Styles: %s, Neighbours: %s)" % (styles, neighbours)


Cell.long_format = {
    "l": Styles.light,
    "h": Styles.heavy,
    "d": Styles.double,
    "e": Styles.empty
}
Cell.reverse_long_format = {v: k for k, v in Cell.long_format.items()}
Cell.reverse_long_format.update({empty: "."})


def make_cell_grid(formats):
    height = len(formats)
    width = len(formats[0])
    assert all(len(line) == width for line in formats)

    cells = [[Cell.make(format_string) for format_string in line] for line in formats]

    for y in range(height):
        for x in range(width):
            if y > 0:
                cells[y][x].neighbours.top = cells[y - 1][x]
            if y < height - 1:
                cells[y][x].neighbours.bottom = cells[y + 1][x]
            if x > 0:
                cells[y][x].neighbours.left = cells[y][x - 1]
            if x < width - 1:
                cells[y][x].neighbours.right = cells[y][x + 1]

    return cells


def draw_table(formats, contents):
    cells = make_cell_grid(formats)

    height = len(cells)
    width = len(cells[0])

    result = []

    contents = [[e.splitlines() for e in l] for l in contents]
    lengths = [[max(len(s) for s in e) for e in l] for l in contents]
    widths = [max(l) for l in zip(*lengths)]
    heights = [max(len(s) for s in l) for l in contents]

    for y, line in enumerate(cells):
        for content_y in range(heights[y]):
            top = ""
            middle = ""
            bottom = ""
            for x, cell in enumerate(line):
                s = cell.styles
                l = cell.neighbours.left.styles
                t = cell.neighbours.top.styles
                r = cell.neighbours.right.styles
                b = cell.neighbours.bottom.styles

                content_width = widths[x]
                # TODO: Different options
                if content_y < len(contents[y][x]):
                    content_string = contents[y][x][content_y].ljust(content_width)
                else:
                    content_string = " " * content_width

                # Strategy: draw left and top sides of current cell,
                # unless last column or last row

                if content_y == 0:
                    top    += lines[(l.top, t.left, s.top, s.left)]
                middle += lines[(empty, s.left, empty, s.left)]

                if content_y == 0:
                    top    += (2 + content_width) * lines[(s.top, empty, s.top, empty)]
                middle += " %s " % content_string

                if x == width - 1:
                    if content_y == 0:
                        top    += lines[(s.top, t.right, empty, s.right)]
                    middle += lines[(empty, s.right, empty, s.right)]

                if y == height - 1 and content_y == heights[y] - 1:
                    bottom += lines[(l.bottom, s.left, s.bottom, empty)]
                    bottom += (2 + content_width) * lines[(s.bottom, empty,  s.bottom, empty)]
                    if x == width - 1:
                        bottom += lines[(s.bottom, s.right, empty, empty)]

            if top:
                result.append(top)
            result.append(middle)
            if bottom:
                result.append(bottom)

    return result


def linear_formats(horizontal, vertical):
    formats = []
    for x in range(len(horizontal) - 1):
        line = []
        for y in range(len(vertical) - 1):
            line.append("%s%s%s%s" % (vertical[y], horizontal[x], vertical[y+1], horizontal[x+1]))
        formats.append(line)
    return formats

if __name__ == "__main__":
    from ..util.debug import debug_print_cell_grid

    formats = [
        ["elll", "lhlh", "llel"],
        ["llll", "lhlh", "lldl"],
        ["hlhl", "ehhh", "hedl"]
    ]

    alternate_format = [
        " l h l ",
        "e l l e",
        " l h l ",
        "l l l d",
        " l h e ",
        "h e h d",
        " l h l "
    ]

    format_3 = [
        "ellhlle",
        "lllhlld",
        "hlehhed",
        "lhl"
    ]

    contents = [
        ["Hello,\nworld!", "world", "!"],
        ["Foo", "bar", "These tables now\nsupport multiline\nstring goodness"],
        ["Bar", "This is nice,\nI love tables!", "b4z\nbiz"]
    ]

    #cells = make_cell_grid(formats)
    #debug_print_cell_grid(cells)

    table = draw_table(formats, contents)
    print("\n".join(table))

    table = draw_table(linear_formats("hllh", "eele"), contents)
    print("\n".join(table))