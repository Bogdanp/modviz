# modviz

Modviz lets you visualize your module dependencies.

[![Build Status](https://travis-ci.org/Bogdanp/modviz.svg?branch=master)](https://travis-ci.org/Bogdanp/modviz)

## Installation

`pip install modviz`

## Usage

`$ modviz /path/to/a/python/package -o output.html`

```
~$ modviz --help
usage: modviz [-h] [-o TARGET] [-f [FOLD_PATHS [FOLD_PATHS ...]]] [-e [EXCLUDE_PATHS [EXCLUDE_PATHS ...]]] PATH

Modviz lets you visualize your module dependencies.

positional arguments:
  PATH                  the path to the package you want to visualize

optional arguments:
  -h, --help            show this help message and exit
  -o TARGET             the output file (default: stdout)
  -f [FOLD_PATHS [FOLD_PATHS ...]]
                        paths that need to be folded up ('vendor' dirs, for example)
  -e [EXCLUDE_PATHS [EXCLUDE_PATHS ...]]
                        paths that should be excluded from the output
```

## Screenshot

![Screenshot](/example/screenshot.png)
