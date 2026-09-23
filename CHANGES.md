# Changes in pdfsizeopt3

pdfsizeopt3 is a fork of pdfsizeopt (https://github.com/pts/pdfsizeopt),
based on upstream commit 2bab160. The original needs Python 2.4--2.7 and
Ghostscript 9.05. pdfsizeopt3 runs on Python 3.6 or later and works with
current Ghostscript versions, including 10.x.

This file documents what was changed and why.

## Compatibility and testing

* Python: works with 3.6 or later, tested with 3.9, 3.12, 3.13 and 3.14. All
  four produce byte-identical output. Python 2 is no longer supported.
* Ghostscript: tested with 9.05 and 10.06.
* With Ghostscript 9.05 and the same image optimizers (sam2p, jbig2,
  pngout), pdfsizeopt3 produces output byte-identical to the original Python 2
  pdfsizeopt, for all tested PDFs and flag combinations. The
  `--stats` output is also identical.
* With Ghostscript 10.06, all tested PDFs are optimized successfully, output
  sizes are within a few bytes of the Ghostscript 9.05 results, and the pages
  render identically to the input (compared pixel by pixel). The only
  differences are the ones the original pdfsizeopt also produces.
* The 54 unit tests in `pdfsizeopt_test.py` pass.

## Python 3 port

### Binary data representation

pdfsizeopt parses and generates PDF data with str methods, regular
expressions and string literals throughout (about 10,000 lines of code). In
Python 2, str is a byte string. To keep all this code intact, pdfsizeopt3
represents binary data as latin-1-decoded str objects: each character has an
ordinal between 0 and 255, corresponding to exactly one byte.

The new module `lib/pdfsizeopt/binstr.py` converts to and from bytes at the
boundaries:

* `OpenLatin1`: opens files for binary I/O with latin-1 str, with newline
  translation disabled. Replaces `open(..., 'rb')` and `open(..., 'wb')`.
* `Latin1Popen`: replaces `os.popen(..., 'rb')` (not supported by Python 3)
  for reading Ghostscript output. `close()` returns the exit status like
  Python 2's `os.popen`.
* `zlib_latin1` and `struct_latin1`: wrappers around the zlib and struct
  modules which take and return latin-1 str. They are imported as `zlib` and
  `struct` in `main.py` and `cff.py`, so the call sites are unchanged.
* `HexEncode` and `HexDecode`: replace Python 2's `.encode('hex')` and
  `.decode('hex')`. `HexDecode` raises `TypeError` on bad input, like
  Python 2.
* `buffer`: replaces the Python 2 `buffer(...)` builtin (it returns a slice).

### Language changes

* Syntax: `except X, e` became `except X as e`; `print` statements (in
  `cff.py`) became function calls; `raise` with a traceback argument uses
  `with_traceback`; octal literals use `0o`.
* Removed builtins: `xrange`, `long`, `unicode`, `file`, `buffer`,
  `itertools.izip`, `dict.iteritems()`, `dict.itervalues()`, `.next()`.
* `map()` and `filter()` return iterators; wrapped in `list()` where the
  result is indexed, modified or compared.
* Integer division: `/` became `//` in the 9 places where it divides
  integers.
* Sorting: `list.sort(cmp_function)` and `int.__cmp__` don't exist anymore;
  replaced by `functools.cmp_to_key` and a `Cmp` helper.
* Sorting mixed keys: Python 3 can't compare int and str. Dicts which contain
  both object numbers and names (such as `'trailer'` and `'xref'`) are sorted
  with a key function (`ObjNumSortKey`) that puts the numbers first, as
  Python 2 did.
* `sort()` on tuples containing `PdfObj` objects now sorts on the size and
  name only, instead of falling back to comparing the objects.
* `__nonzero__` became `__bool__` (in `ImageData`).
* Class-scope names are not visible in comprehensions in Python 3. Two
  default arguments of `PdfObj` methods (the hex-escape caches) are now built
  by a module-level function.
* `except ... as e` unbinds `e` at the end of the block; `Rename` now keeps
  the exception in another variable.
* `zlib.crc32` returns an unsigned value in Python 3; the PNG chunk checksum
  is now packed as unsigned (`'>L'`), otherwise it fails for large values.
* `is not ()` (a syntax error in Python 3.8+) became a comparison with
  `None`.

### Regular expressions

* Global inline flags such as `(?s)` must be at the start of the pattern in
  Python 3.11+. Mid-pattern `(?s)` became a scoped `(?s:...)` group (or
  `re.S`), which matches the same way.
* In Python 3, `\w` and `\b` match non-ASCII letters in str patterns. Patterns
  using them on PDF data now use `re.ASCII`, as Python 2 matched ASCII only.
* `str.split()` without arguments splits on more whitespace characters in
  Python 3 (e.g. `\x85`, `\xa0`). Where it's applied to PDF data, it was
  replaced by an explicit split on ASCII whitespace; the same for `strip()`.
* About 20 string literals had invalid escape sequences (such as `'\d'`),
  which cause warnings in Python 3.12+. The backslashes were doubled; the
  strings have the same value.

### Pre-existing bugs fixed along the way

* `cff.py`: `return false` (should be `False`); undefined variables in three
  error messages (`header_size`, `font_name`, `value`); a `None` lookup that
  was done before the `None` check.
* `main.py`: a `LogFatal` message with a missing format argument, which would
  crash instead of reporting an image data error.

### Other files

* `pdfsizeopt_test.py`: ported to Python 3.
* `mksingle.py` (builds the single-file script): ported to Python 3,
  includes `binstr.py`, the shell prefix runs `python3`, ZIP entries are now
  deflate-compressed (so `advzip` is optional).
* The launcher `pdfsizeopt` became `pdfsizeopt3`, and runs `python3`.

## Ghostscript 10 compatibility

The original pdfsizeopt fails with Ghostscript 9.5x and 10.x when optimizing
fonts. These changes make it work with Ghostscript 10.x while keeping the
output with Ghostscript 9.05 unchanged.

### Missing operators (`psproc.py`)

* `.setpdfwrite` doesn't exist anymore. It's now called only if it's defined
  (Type1CConverter, Type1CGenerator).
* `.FontDirectory` and `.fontknownget` don't exist anymore. `TryFindFont` now
  looks in `FontDirectory` and `GlobalFontDirectory` with `.knownget` if they
  are missing.

### CFF font loading (Type1CParser, `psproc.py`)

The original code found the CFF loading procedure inside the internals of the
PostScript-based PDF interpreter (`GS_PDF_ProcSet` or `pdfdict /readType1C`).
Ghostscript 9.56 replaced this interpreter with a new one written in C, and
Ghostscript 10.x removed the old one, so these names don't exist anymore.

For Ghostscript 8.63 and later, `LoadCff` is now defined directly as

    /FontSetInit /ProcSet findresource begin //true //false ReadData

which is what `pdfdict /readType1C` did. `ReadData` is still provided by
`gs_cff.ps` in Ghostscript 10.x. The old lookup is kept for Ghostscript 8.62
and earlier.

### Glyph mix-up when merging fonts (Type1CParser, `psproc.py`)

In Ghostscript 9.5x and later, a loaded CFF font maps glyph names to glyph
indexes in `/CharStrings`, and stores the charstrings in a separate
`/CFFCharStrings` dict (mapping glyph indexes to charstrings). Earlier
versions map glyph names directly to charstrings.

pdfsizeopt merges subsets of the same font by merging their `/CharStrings`.
With the new representation, the glyph indexes of different subsets
collide. For example, merging a subset containing only `/one` with a subset
containing only `/two` made both names point to the charstring of `/one`, so
a page number 2 was rendered as 1.

Type1CParser now converts the font back to the old representation (glyph
name to charstring) before dumping it, and drops `/CFFCharStrings` and
`/Decoding`.

### File access in SAFER mode (`main.py`)

Since Ghostscript 9.50, `-dSAFER` is the default, and PostScript code can't
open files which are not named on the command line. pdfsizeopt passes some
temporary file names in variables (`-sDataFile=...` for Type1CParser,
`-sINFN=...` for stream decompression), so they were blocked.

pdfsizeopt3 detects the Ghostscript version (new `GS_VERSION`), and for 9.50
or later it adds `--permit-file-read=...` or `--permit-file-write=...` for
exactly these files (`GetGsPermitFlags`). SAFER mode stays enabled. The flags
are not added for earlier versions, which don't support them.

### Choosing Ghostscript (`main.py`)

pdfsizeopt3 prefers the system Ghostscript: `gs` on the PATH (or `gs-noX11`
on macOS). The Ghostscript bundled in `pdfsizeopt_libexec` (`pdfsizeopt_gs/gs`,
version 9.05) is used only if no working system Ghostscript is found. The
original pdfsizeopt preferred the bundled one. The environment variable
`PDFSIZEOPT_GS` still overrides both.

## Packaging and repository changes

* The program is named `pdfsizeopt3` (and the single-file script
  `pdfsizeopt3.single`), so it can be installed next to the original
  `pdfsizeopt`.
* New `Makefile` with the targets `all` (builds `pdfsizeopt3.single`),
  `test`, `check` (unit tests plus optimizing `test/small.pdf`), `install`,
  `uninstall` and `clean`. Install with e.g. `make install PREFIX=~`.
* Removed: the Windows port (`win32port/`), the Docker files (`docker/`,
  `docker_extraimgopt/`), the Debian packaging (`extra/debian/`), and the TeX
  helper files in `extra/` (font maps, `dvipdfmx_fontfix.py`,
  `pts-graphics-helper.sty`), which are not used by pdfsizeopt.
  `extra/small.pdf` moved to `test/small.pdf`.
* `README.md` describes the fork and its installation, and no longer contains
  the Windows, Docker and prebuilt-download instructions of the original.
* `lib/pdfsizeopt/pdfsizeopt_argparse.py` (a bundled copy of argparse 1.2.1)
  is unchanged; it's not used.
