# Exporting your figure
You want to export your figure.

Matplotlib has the [`savefig()`](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html) method for saving a figure to file, including PDF, PNG, and SVG formats.
You will almost certainly have to modify the configuration of this saving to have something that works for you.
This guide details some considerations you may have to make when exporting your figure.
Different programs, like Word or LaTeX, can handle different formats of images.

Scilayout provides `scilayout.exportfig()` which may work for you, but if it doesn't then you may want to read on or consult Matplotlib's [`savefig()` documentation](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html) to work out what you need.

## Reasonable defaults
`scilayout.base.savefigure()` is reasonable default that works for my application, and may be a good starting point for making your own modifications.
### `#!python bbox = "tight"`
The bounding box of the exported image can be specified in all kinds of ways.
The "tight" option will make matplotlib calculate a bounding box that is tightly wrapped around all elements of the figure.

You may want to modify `bbox` in situations where you want to export subcomponents of the figure.

## Exporting as a vector or raster image
It is worth understanding the difference between a raster and a vector image.
A raster image stores image information in pixels.
Examples of raster formats are TIF and PNG files, where a .tif file stores the values of each pixel, while .jpg or .png use compression to reduce file size.
On the other hand, a vector image uses maths to determine how the image will be displayed, and so have essentially infinite "quality".

Another way to understand it is that a circle in a raster image has a finite number of pixels, while a circle in a vector image may have maths that describe how it should appear.
A raster can be a more portable (smaller size and guaranteed appearance) while a vector is more powerful (editable in other programs, practically unlimited "quality").

> [!note]
> A vector can contain a raster within it. For example `imshow()` produces a raster.

- .pdf files are easily inserted into LaTeX documents but .svg are not
- .svg files are easily inserted in Typst documents
- .svg documents are text documents so Git can track the changes

| File format | Type   | Word embed | Latex embed | Typst embed |
| ----------- | ------ | ---------- | ----------- | ----------- |
| .pdf        | Vector | No         | Yes         | No          |
| .svg        | Vector | Yes        | No*         | Yes*        |
| .png        | Raster | Yes        | Yes         | No          |

An SVG (Scalable Vector Graphics) file is actually just an XML (Extensible Markup Language) file.
SVG files can be included in LaTeX files with CTAN's `svg` package, but note that this uses Inkscape under the hood to convert the SVG upon embedding it.
Depending on what your output is, you may want to double check that this process works as expected.

## Text in figures
The TL;DR of this section is that when saving figures in vector format you should probably set `pdf.fonttype` to `42` to ensure broader compatibility for editing across different programs.

> [!info]
> Matplotlib exports text as PostScript Type 1, which Adobe Illustrator cannot read. Use `pdf.fonttype: 42` to use TrueType.

In a .png file text is simply pixels, but in a vector format text could either be a shape or text.
% todo: find out how text selection goes with different things

??? tip "Installing Microsoft fonts on Linux"

    Journals may expect fonts to use one of the default Windows fonts, which a Linux installation will not have access to.
    The `apt install ttf-mscorefonts-installer` hasn't worked for years, so you have to manually install the files yourself.
    If you're on Ubuntu, you can find a .deb file ehre: http://ftp.de.debian.org/debian/pool/contrib/m/msttcorefonts/

    Following the installation you may need to delete Matplotlib's font cache for it to recognise that the new fonts exist.
    https://stackoverflow.com/a/37921026

### Saving vector graphics with text as text and not a path
In a vector image, text can be encoded as text (e.g. you can edit it in vector programs) or a shape (i.e. it is a series of lil nodes in the vector program).
On export, Matplotlib converted the text into the lines it's displayed as, ensuring that the exported file will look precisely as you want.
But this means you cannot edit the text in an image editor (which you might want to do).

But vector file formats also support storing text as a text object specifically, allowing it to be selected/modified in different editors.
`svg.fonttype: none` # TODO: how does this effect pdf output?
The benefits 

It is worth noting that in my experience, converting a LaTeX document, with .pdf figures inside that have text encoded as text, into a Word document by opening it with Word will result in the text within figure becoming garbled.

### Make Matplotlib use TrueType as the font specification
To display text on a screen or print it out, the shape of the letters must be defined.
The specification of these shapes exists in different formats.
It's an interesting world of font history, but all you need to know is that Matplotlib will use the Type 1 PostScript specification by default and Adobe Illustrator cannot read this.
The standard in the world of technology and fonts has moved to a different specification called TrueType, which you can specify with `pdf.fonttype: 42`.
This should not change the physical appearance of the text

By default, Matplotlib exports text using the Type 1 PostScript specification.
The short history you'll find on the net is that in the 1980s Adobe created the PostScript specification with 3 Types for it, which is essentially the file format/encoding method for how a font is drawn.
Apple created TrueType in response and Microsoft eventually adopted it as the Windows specification.
The world of typography is moving away from PostScript and into TrueType or even further into OpenType (a TrueType successor developed by Microsoft and Adobe).

The important part of this is that Adobe Illustrator does not support Type 1 PostScript, so if you export a figure with text and import into Adobe Illustrator it's going to make it all weird.
Adobe Illustrator does not support this font encoding, and so will perform some kind of conversion to the fonts
The fix is [here](https://jonathansoma.com/lede/data-studio/matplotlib/exporting-from-matplotlib-to-open-in-adobe-illustrator/), which is to 
`pdf.fonttype: 42`
Inkscape, on the other hand, can handle TrueType 1.

## Metadata
You may want to consult [this Stack Overflow thread](https://stackoverflow.com/questions/10532614/can-matplotlib-add-metadata-to-saved-figures) about saving metadata into figures, as different formats can have different types of metadata added.

For example, you might use the title key to store the figure's identity and version information.

The short of it is that the PDF specification has a limited set of metadata keys (like title and author) while SVG can have metadata added as comment strings (as SVG is a text file).

## Saving your figure
If you find that `scilayout.exportfigure()` doesn't work in the way you want, you may have to write your own function to export the figure.

You could use a stylesheet with the required settings

Or you could use a context (so you can have different save parameters for different usages).
```python
styledict = {'pdf.fonttype': 42, 'font.family': 'Arial'}
with plt.rc_context(styledict):
    fig.savefig('figure-in-arial.pdf')

styledict = {'font.family': 'Comic Sans'}
with plt.rc_context(styledict):
    fig.savefig('figure-in-garamond.pdf')
```

