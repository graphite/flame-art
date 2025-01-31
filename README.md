# FlameGraphs Art #
Take control over you Flame Graphs, define a simple outline and let the code do the rest!

## Initialiaze Submodules ##

```git checkout --recurse-submodules```

## Basic Use ##

**Preview**

Preview how your JSON outline converts into a picture:

```
python3 generate-flames.py -p samples/castle.json
```
[Output](https://github.com/graphite/flame-art/blob/master/samples/castle.ascii) - zoom out for a better preview

**Generate Rust Code**

```
python3 generate-flames.py samples/castle.json > build/castle.rs
```

Now you can build it with `rustc -g castle.rs` and profile as usual with [FlameGraphs](https://github.com/brendangregg/FlameGraph)

**End to End Run**

If you are on Linux and `perf` is available you can simply run:

```
./rust_flame.sh samples/castle.json
```

This will generate the code, compile, run the profiler for 5 seconds, clean up the profiler output to only keep `::main` and above, and produce a FlameGraph SVG.
![Castle](https://raw.githubusercontent.com/graphite/flame-art/refs/heads/master/samples/castle.svg)
