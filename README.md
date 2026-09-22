# README for pdfsizeopt3

pdfsizeopt3 is a fork of pdfsizeopt (https://github.com/pts/pdfsizeopt) by
Peter Szabo, ported to Python 3 and to current Ghostscript versions
(including Ghostscript 10.x). The original pdfsizeopt needs Python 2.4--2.7
and Ghostscript 9.05. pdfsizeopt3 is installed as the command `pdfsizeopt3`,
so it can be used next to the original (Python 2) `pdfsizeopt`. With the
same Ghostscript and image optimizers, it produces the same output as the
original.

pdfsizeopt is a program for converting large PDF files to small ones,
without decreasing visual quality or removing interactive features (such as
hyperlinks). More specifically, pdfsizeopt is a free, command-line
application and a collection of best practices to optimize the size of PDF
files, with focus on PDFs created from TeX and LaTeX documents. pdfsizeopt
is written in Python, so it is a bit slow, but it offloads some of the heavy
work to its faster (C and C++) dependencies.

Problems specific to pdfsizeopt3 (Python 3 or Ghostscript 10 issues) should
be reported at https://github.com/mocenigo/pdfsizeopt3/issues . Everything
else about pdfsizeopt is documented upstream at
https://github.com/pts/pdfsizeopt .

## Installation and usage

pdfsizeopt3 works on Unix systems (such as Linux and macOS). Windows is not
supported by this fork. There is no installer and no GUI.

Requirements:

* Python (command: python3): Version 3.6 or later (tested with 3.9, 3.12,
  3.13 and 3.14). Python 2.x doesn't work.
* Ghostscript (command: gs): Version 9.05 or later, including 10.x (tested
  with 9.05 and 10.06). pdfsizeopt3 uses the Ghostscript found on the PATH
  (gs, or gs-noX11 on macOS). To use a specific Ghostscript, set the
  environment variable PDFSIZEOPT_GS to its command, e.g.
  `PDFSIZEOPT_GS=/usr/local/bin/gs`.
* imgdataopt or sam2p (command: sam2p): Install imgdataopt from source:
  https://github.com/pts/imgdataopt , and copy the `imgdataopt` program file
  as `sam2p` (e.g. /usr/local/bin/sam2p) to your PATH. Alternatively, sam2p
  >=0.49.3 + png22pnm also works. If you are unable to install it, use
  pdfsizeopt3 --do-optimize-images=no .
* jbig2 (command: jbig2): Install from source:
  https://github.com/pts/pdfsizeopt-jbig2
  If you are unable to install, use pdfsizeopt3 --use-jbig2=no .
* pngout (command: pngout): Download binaries from here:
  http://www.jonof.id.au/kenutils Source code is not available.
  If you are unable to install, use pdfsizeopt3 --use-pngout=no .
* The Multivalent PDF compressor (written in Java) is an optional dependency,
  turned off by default. Don't bother installing it.

Instead of installing sam2p, jbig2 and pngout separately, you can use the
prebuilt binaries in the pdfsizeopt_libexec directory of the original
pdfsizeopt (see its installation instructions for Linux and macOS): put the
pdfsizeopt_libexec directory next to the pdfsizeopt3 program file. The
Ghostscript and Python bundled there are not used by pdfsizeopt3 (except that
the bundled Ghostscript 9.05 is used if no working Ghostscript is found on
the PATH).

To build, test and install pdfsizeopt3 from a source checkout, run these
commands (without the leading `$`):

```
  $ make check                   # Build pdfsizeopt3.single and test it.
  $ make install PREFIX=$HOME    # Installs $HOME/bin/pdfsizeopt3.
```

`make install` installs to /usr/local/bin by default. You can also run
pdfsizeopt3 directly from the source checkout, as `./pdfsizeopt3` or
`python3 pdfsizeopt3`.

Try it with:

```
  $ pdfsizeopt3 --version
```

To optimize a PDF, run the following command:

```
  $ pdfsizeopt3 input.pdf output.pdf
```

If the input PDF has many images or large images, pdfsizeopt can be very
slow. You can speed it up by disabling pngout, the slowest image optimization
method, like this:

```
  $ pdfsizeopt3 --use-pngout=no input.pdf output.pdf
```

pdfsizeopt creates lots of temporary files (psotmp.*) in the temporary
directory ($TMPDIR, or the output directory), but it also cleans up after
itself.

Run `pdfsizeopt3 --help` to see all command-line flags.

## Image optimizers

pdfsizeopt can use the following external tools to make images in embedded
PDF files smaller:

* sam2p (used by default, cannot be disabled)
* jbig2 (used by default, disable with --use-jbgi2=no)
* pngout (used by default, disable with --use-pngout=no)
* zopflipng (not enabled by default)
* optipng (not enabled by default)
* advpng (not enabled by default)
* ECT (not enabled by default)

To enable or disable any image optimizer, specify all image optimizers you
want to be enabled like this: --use-image-optimizer=optipng,jbig2 . This
will also disable the default pngout.

You can also specify custom image optimizer command patterns by specifying
separate, additional --use-image-optimier= flags, like this:

```
  --use-image-optimizer="optipng %(sourcefnq)s -o6 -fix -force %(optipng_gray_flags)s-out %(targetfnq)s"
```

You always have to specify %(targetfnq) in the command pattern.

Specify --do-debug-image-optimizers=yes to see which image optimizers are
enabled (and their full command-line) for the current run.

At startup, pdfsizeopt checks that the requested image optimizers are
available (as program files), and fails if some of them are missing. To
ignore those which are missing, specify --do-require-image-optimizers=no .

It's your (the user's) responsibility to install the image optimizers and
add them to the PATH (or put them to pdfsizeopt_libexec, see above).

## Troubleshooting

### 1. pdfsizeopt fails for some fonts.

Specify --do-unify-fonts=no and --do-regenerate-all-fonts=no .

If it still fails, specify --do-optimize-fonts=no .

In either case, please report it on https://github.com/mocenigo/pdfsizeopt3/issues

### 2. pdfsizeopt fails for some images.

Specify --do-optimize-images=no .

Please report it on https://github.com/mocenigo/pdfsizeopt3/issues

### 3. pdfsizeopt is too slow processing images.

Specify --use-pngout=no . This disables pngout, which is the slowest
optimization step for images.

### 4. pdfsizeopt fails without creating the output PDF.

Please report it on https://github.com/mocenigo/pdfsizeopt3/issues , attaching the
input PDF file and the console output of pdfsizeopt. Your report is very
much appreciated.

If pdfsizeopt exits with an uncaught exception, it may leave some temporary
files (psotmp.*) behind in the current directory. You can remove these files.

Please note that pdfsizeopt is not resilient in processing corrupt PDF
files (i.e. those which are not compliant to the PDF standard). So if
pdfsizeopt fails, then the reason may be a bug in pdfsizeopt or a corrupt
PDF input file. Nevertheless, please report an issue (see above).

### 5. The output PDF of pdfsizeopt doesn't look like the same as the input PDF.

Please report it on https://github.com/mocenigo/pdfsizeopt3/issues , attaching the
input PDF file and the output PDF file (.pso.pdf) and the console output of
pdfsizeopt. Your report is very much appreciated.

### 6. Ghostscript errors with Type1CParser and Type1CConverter

These errors happen with the original (Python 2) pdfsizeopt and Ghostscript
9.5x or later. pdfsizeopt3 works with these Ghostscript versions. If you
still get such an error with pdfsizeopt3, please report it (see above), and
as a workaround, specify --do-optimize-fonts=no , or use Ghostscript 9.05
(with PDFSIZEOPT_GS).

## More documentation

* https://github.com/pts/pdfsizeopt/releases/download/docs-v1/pts_pdfsizeopt2009.psom.pdf
  White paper on EuroTex 2009.
* https://github.com/pts/pdfsizeopt/releases/download/docs-v1/pts_pdfsizeopt2009_talk.psom.pdf
  Conference talk slides on EuroTex 2009.

<!-- __END__ -->
