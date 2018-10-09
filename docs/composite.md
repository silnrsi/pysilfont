# Defining composite glyphs

A composite glyph is one that is defined in terms of one or more other glyphs.
The composite definition syntax described in this document is a subset of the [GlyphConstruction](https://github.com/typemytype/GlyphConstruction) syntax used by Robofont, but with extensions for additional functionality.
Composites defined in this syntax can be applied to a UFO using the [psfbuildcomp](scripts.md#psfbuildcomp) tool.

# Overview

Each composite definition is on a single line and has the format:
```
<result> = <one or more glyphs> <parameters> # comment
```
where
- `<result>` is the name of the composite glyph being constructed
- `<one or more glyphs>` represents one or more glyphs used in the construction of the composite glyph, with optional glyph-level parameters described below
- `<parameters>` represents adjustments made to the `<result>` glyph, using the following optional parameters:
    - at most one of the two following options:
        - `^x,y` (where `x` is the amount added to the left margin and `y` is the amount added to the right margin)
        - `^a` (where `a` is the advance width of the resulting glyph)
    - `|usv` where `usv` is the 4-, 5- or 6-digit hex Unicode scalar value assigned to the resulting glpyh
    - `!colordef` (currently ignored by SIL tools)
    - `[key1=value1;key2=value2;...]` to add one or more `key=value` pairs (representing SIL-specific properties documented below) to the resulting glyph
- `# comment` is an optional comment (everything from the `#` to the end of the line is ignored)

In addition, a line that begins with `#` is considered a comment and is ignored (as are blank lines).

If `[key=value]` properties for the resulting glyph are specified but no `|usv` is specified, then a `|` must be included before the `[`.
This insures that the properties are applied to the resulting composite glyph and not to the last glyph in the composite specification.

# Examples

In the following examples,
- `glyph` represents the resulting glyph being constructed
- `base`, `base1`, `base2` represent base glyphs being used in the construction
- `diac`, `diac1`, `diac2` represent diacritic glyphs being used in the construction
- `AP` represents an attachment point (also known as an anchor)

## glyph = base
```
Minus = Hyphen
```
This defines one glyph (`Minus`) in terms of another (`Hyphen`), without having to duplicate the contours used to create the shape.

## glyph = base1 & base2
```
ffi = f & f & i
```
This construct causes a glyph to be composed by aligning the origin of each successive base with the origin+advancewidth of the previous base.  Unless overridden by the `^` parameter, the left sidebearing of the composite is that of the first base, the right sidebearing is that of the last, and the advancewidth of the composite is the sum of the advance widths of all the component base glyphs. [Unsure how this changes for right-to-left scripts]

## glyph = base + diac@AP
```
Aacute = A + acute@U
```
The resulting composite has the APs of the base(s), minus any APs used to attach the diacritics, plus the APs of the diacritics (adjusted for any displacement, as would be the case for stacked diacritics). In this example, glyph `acute` attaches to glyph `A` at AP `U` on `A` (by default using the `_U` AP on `tilde`). The `U` AP from `A` is removed (as is the `_U` AP on the `tilde`) and the `U` AP from `acute` is added.

Unless overridden by the `^` parameter, the advance width of the resulting composite is that of the base.

## glyph = base + diac1@AP + diac2@APonpreviousdiac
```
Ocircumflexacute =  O + circumflex@U + acute@U
```
The acute is positioned according to the `U` AP on the immediately preceding glyph (`circumflex`), not the `U` AP on the base (`O`).

## glyph = base + diac@anyglyph:anyAP

The syntax allows you to express diacritic positioning using any arbitrary AP on any arbitrary glyph in the font, for example:
```
barredOacute = barredO + acute@O:U # not supported
```
Current SIL tools, however, only support an `anyglyph` that appears earlier in the composite definition, so the above example is **not** supported.

This syntax, however, makes it possible to override the default behavior of attaching to the immediately preceding glyph, so the following is supported (since the `@O:L` refers to the glyph `O` which appears earlier in the definition):
```
Ocircumflexdotaccent =  O + circumflex@U + dotaccent@O:L
```
The `@O:L` causes the `dotaccent` diacritic to attach to the base glyph `O` (rather the immediately preceding `circumflex` glyph) using the `L` AP on the glyph `O` and the `_L` AP on the glyph `dotaccent`.

## glyph = base + diac@AP | usv
```
Aacute = A + acute@U | 00C1
```
USV is always given as four- to six-digit hexadecimal number with no leading "U+" or "0x".

## glyph = base + diac@AP ^ leftmarginadd,rightmarginadd
```
itilde = i + tilde@U ^ 50,50
```
This adds the values (in design units) to the left and right sidebearings. Note that these values could be negative.

# SIL Extensions

SIL extensions are all expressed as property lists (`key=value`) separated by semicolons and enclosed in square brackets: `[key1=value1;key2=value2]`.
- Properties that apply to a glyph being used in the construction of the composite appear after the glyph.
- Properties that apply to the resulting composite glyph appear after `|` (either that of the `|usv` or a single `|` if no `|usv` is present).

## glyph = base + diac@atAP[with=AP]
```
Aacute = A + acute@Ucap[with=_U]
```
The `with` property can be used to override the default AP, \_AP convention. The `_U` attachment point on the `acute` glyph is paired with the `Ucap` attachment point on the

## glyph = base + diac@AP[shift=x,y]

Aacute = A + acute@U[shift=100,100]

By applying the `shift` property to the `acute` glyph, the position of the diacritic relative to the base glyph `A` is changed.
