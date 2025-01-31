#!/bin/bash

set -e

NAME=${1%.*}
#python3 generate-flames.py $1 > build/$NAME.rs
rustc -g --out-dir build build/$NAME.rs
# sudo is required unless perf_event_paranoid is adjusted
# sudo with & messes up the terminal
build/$NAME &
PID=$!
sudo -b perf record -o build/perf.data -p $PID -F 1000 -a -g -q --call-graph dwarf
sleep 5
kill $PID
sleep 1
sudo perf script -i build/perf.data > build/out.perf
python3 clear-perf.py build/out.perf > build/clean.perf
FlameGraph/stackcollapse-perf.pl build/clean.perf > build/out.folded
FlameGraph/flamegraph.pl build/out.folded > build/$NAME.svg
