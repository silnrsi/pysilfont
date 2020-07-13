# required_chars - recommended characters for Non-Roman fonts

For optimal compatibility with a variety of operating systems, all Non-Roman fonts should include 
a set of glyphs for basic Roman characters and punctuation. Ideally this should include all the 
following characters, although some depend on other considerations (see the notes). The basis 
for this list is a union of the Windows Codepage 1252 and MacRoman character sets plus additional 
useful characters. 

The csv includes the following headers:

* USV - Unicode Scalar Value
* ps_name - postscript name of glyph that will end up in production
* glyph_name - glyphsApp name that will be used in UFO
* sil_set - set to include in a font
   * basic - should be included in any Non-Roman font
   * rtl - should be included in any right-to-left script font
   * sil - should be included in any SIL font 
* rationale - worded to complete the phrase: "This character is needed ..."
   * A - in Codepage 1252
   * B - in MacRoman
   * C - for publishing
   * D - for Non-Roman fonts and publishing
   * E - by Google Fonts
   * F - by TeX for visible space
   * G - for encoding conversion utilities
   * H - in case Variation Sequences are defined in future
   * I - to detect byte order
   * J - to render combining marks in isolation
   * K - to view sidebearings for every glyph using these characters
* additional_notes - how the character might be used

The list was previously maintained here: https://scriptsource.org/entry/gg5wm9hhd3
