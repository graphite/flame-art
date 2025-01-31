#!/usr/bin/python3

# Takes a JSON file that contains the points on the outline and generates
# a program that results in a Flame Graph matching this outline.
# The canvas is 304x25 and the points in the input have to be ordered left to
# right.
# https://github.com/brendangregg/FlameGraph

import argparse
import json


class RustHelper:
    def validate_fname(fname):
        '''Validates the name of the filler function'''
        # TODO: https://doc.rust-lang.org/reference/identifiers.html
        # TODO: replace the below with proper validation
        if '<' in fname:
            raise ValueError('Rust function name cannot contain "<"')


HELPERS = {'rust': RustHelper}
LENGTH = 304
HEIGHT = 25


class Picture:
    def __init__(self):
        self.data = [['\x00'] * (LENGTH // 8) for _ in range(HEIGHT)]

    def __str__(self):
        return '\n'.join(
            [''.join([format(ord(c), '08b') for c in line])
                for line in self.data[::-1]]
        )

    def __getitem__(self, coords):
        x, y = coords
        a, b = x // 8, (7 - x % 8)
        return 1 if ord(self.data[y][a]) & (1 << b) else 0

    def __setitem__(self, coords, val):
        x, y = coords
        a, b = x // 8, (7 - x % 8)
        if val == 0:
            self.data[y][a] = chr(ord(self.data[y][a]) & (127 - 2**b))
        elif val == 1:
            self.data[y][a] = chr(ord(self.data[y][a]) | (1 << b))
        else:
            raise ValueError('Only 0 and 1 allowed for the bitmap')

    def fill(self, nulls=set()):
        to_fill = [(i, 0) for i in range(LENGTH) if i not in nulls]
        filled = set(to_fill)
        while to_fill:
            n = to_fill.pop(0)
            self[n] = 1
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                x, y = n[0] + dx, n[1] + dy
                if x < 0 or x >= LENGTH or y < 0 or y >= HEIGHT:
                    continue
                if self[(x, y)] == 1 or (x, y) in filled:
                    continue
                to_fill.append((x, y))
                filled.add((x, y))


def parse_outline(outline):
    # Flame always starts at 0,0 and ends at LENGTH,0
    if outline[0] != [0, 0]:
        outline = [[0, 0]] + outline
    if outline[-1] != [LENGTH - 1, 0]:
        outline.append([LENGTH - 1, 0])

    nulls = set()

    picture = Picture()

    p1 = outline[0]
    picture[p1] = 1
    for p2 in outline[1:]:
        if p1[1] == 0:
            nulls.add(p1[0])
        if p2[1] == 0:
            nulls.add(p2[0])
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        if dx < 0:
            raise ValueError('Point {} is to the left of {}'.format(p2, p1))
        if abs(dx) > abs(dy):
            # Below 45 degrees
            for i in range(x1, x2 + 1):
                y = round(y1 + (i - x1) / dx * dy)
                picture[(i, y)] = 1
        else:
            # 45 to 90 degrees
            for i in range(y1, y2 + dy // abs(dy), dy // abs(dy)):
                x = round(x1 + (i - y1) / dy * dx)
                picture[(x, i)] = 1
        p1 = p2

    picture.fill(nulls)
    return picture


class Function:
    def __init__(self, depth, start, end, calls=None):
        self.depth = depth
        self.start = start
        self.end = end
        # Positive number is a call to an indexed function.
        # Negative number indicates how long to spend in this function.
        self.calls = calls if calls else []

    def __str__(self):
        return str(self.calls)

    def __repr__(self):
        return str(self)


def to_functions(picture):
    functions = [Function(0, 0, LENGTH - 1)]
    cur = 0
    while cur < len(functions):
        f = functions[cur]
        if f.calls:
            cur += 1
            continue
        if f.depth == HEIGHT - 1:
            # Deepest call, just fill in
            f.calls.append(f.start - f.end - 1)
        else:
            start = f.start
            v = picture[(f.start, f.depth + 1)]
            for i in range(f.start, f.end + 1):
                if v == picture[(i, f.depth + 1)]:
                    continue
                if v == 0:
                    f.calls.append(
                        Function(
                            f.depth + 1, start, i - 1, calls=[-1 * (i - start)]
                        )
                    )
                else:
                    functions.append(Function(f.depth + 1, start, i - 1))
                    f.calls.append(len(functions) - 1)
                start = i
                v = 1 - v

            if v == 0:
                f.calls.append(
                    Function(
                        f.depth + 1, start, i, calls=[-1 * (i - start + 1)]
                    )
                )
            else:
                functions.append(Function(f.depth + 1, start, i))
                f.calls.append(len(functions) - 1)

        cur += 1

    return functions


def run():
    parser = argparse.ArgumentParser(
        prog='generate-flames.py',
        description='Generate a program that produces a Flame Graph'
                    ' for a provided outline'
    )
    parser.add_argument(
        'outline',
        type=argparse.FileType(),
        help='JSON file with the target outline defined by points on {}x{} '
             'canvas sorted left to right'.format(LENGTH, HEIGHT)
    )
    parser.add_argument(
        '-l', '--language', default='rust',
        choices=['rust'], help='Target language'
    )
    parser.add_argument(
        '-n', '--name', default='f',
        help='The base name of the filler function'
    )
    args = parser.parse_args()
    helper = HELPERS[args.language]
    helper.validate_fname(args.name)

    outline = json.load(args.outline)
    picture = parse_outline(outline)
    functions = to_functions(picture)


if __name__ == '__main__':
    run()
