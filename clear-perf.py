#!/usr/bin/python3

import argparse


class RustCleaner:
    def clear(data):
        result = []
        base_name = data[0].split(' ')[0] + '::'
        for l in data:
            if l.startswith('\t'):
                function = l.strip().split(' ', 1)[1]
                if not function.startswith(base_name):
                    continue
            if not l.strip():
                # Empty line, check that the trace starts from main
                function = result[-1].strip().split(' ', 1)[1]
                if not function.startswith(base_name + 'main'):
                    # Unknown/anon/broken trace
                    while result.pop().strip():
                        pass
            result.append(l)
        return ''.join(result)


CLEANERS = {'rust': RustCleaner}


def run():
    parser = argparse.ArgumentParser(
        prog='clear-perf.py',
        description='Clear the boilerplate from the perf output to have main'
                    ' as the baseline'
    )
    parser.add_argument(
        'input',
        type=argparse.FileType(),
        help='Output of perf script to be cleaned up'
    )
    parser.add_argument(
        '-l', '--language', default='rust',
        choices=['rust'], help='Target language'
    )

    args = parser.parse_args()

    cleaner = CLEANERS[args.language]
    data = args.input.readlines()
    output = cleaner.clear(data)
    print(output)


if __name__ == '__main__':
    run()
