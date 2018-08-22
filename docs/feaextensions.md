# FEA Extensions Current

This document lists the extensions to fea that are currently supported by
psfmakefea.

## Statements

### baseclass

A baseclass is the base equivalent of a markclass. It specifies the position of a particular class of anchor points on a base, be that a true base or a mark base. The syntax is the same as for a markclass, but it is used differently in a pos rule:

```
markClass [acute] <anchor 350 0> @TOP_MARKS;
baseClass [a] <anchor 500 500> @BASE_TOPS;
baseClass b <anchor 500 750> @BASE_TOPS;

feature test {
    pos base @BASE_TOPS mark @TOP_MARKS;
} test;
```

Which is the functional equivalent of:

```
markClass [acute] <anchor 350 0> @TOP_MARKS;

feature test {
    pos base [a] <anchor 500 500> mark @TOP_MARKS;
    pos base b <anchor 500 750> mark @TOP_MARKS;
} test;
```

It should be borne in mind that both markClasses and baseClasses can also be used as normal glyph classes and as such use the same namespace.

The baseClass statement is a high priority need in order to facilitate auto generation of attachment point information without having to create what might be redundant lookups in the wrong order.

Given a set of base glyphs with attachment point A and marks with attachment point \_A, psfmakefea will generate the following:

* baseClass A - containing all bases with attachment point A
* markClass \_A - containing all marks with attachment point \_A
* baseClass A\_MarkBase - containing all marks with attachment point A

#### Cursive Attachment

Cursive attachment involves two base anchors, one for the entry and one for the exit. We can extend the use of baseClasses to support this, by passing two baseClasses to the pos cursive statement:

```
baseClass meem.medial <anchor 700 50> @ENTRIES;
baseClass meem.medial <anchor 0 10> @EXITS;

feature test {
    pos cursive @ENTRIES @EXITS;
} test;
```

Here we have two base classes for the two anchor points, and the pos cursive processing code works out which glyphs are in both classes, and which are in one or the other and generates the necessary pos cursive statement for each glyph. I.e. there will be statements for the union of the two classes but with null anchors for those only in one (according to which baseClass they are in). This has the added advantage that any code generating baseClasses does not need to know whether a particular attachment point is being used in a cursive attachment. That is entirely up to the user of the baseClass.

#### Mark Attachment

The current mark attachment syntax is related to the base mark attachment in that the base mark has to be specified explicitly and we cannot currently use a markclass as the base mark in a mark attachment lookup. We can extend the mark attachment in the same way as we extend the base attachment, by allowing the mark base to be a markclass. Thus:

```
pos mark @MARK_BASE_CLASS mark @MARK_MARK_CLASS;
```

Would expand out to a list of mark mark attachment rules.

### ifinfo

This statement initiates a block either of statements or within another block. The block is only processed if the ifinfo condition is met. ifinfo takes two parameters. The first is a name that is an entry in a fontinfo.plist. The second is a string containing a regular expression that is matched against the given value in the fontinfo.plist. If there is a match, the condition is considered to be met.

```
ifinfo(familyName, "Doulos") {

# statements

}
```

Notice the lack of a `;` after the block close.

ifinfo acts as a kind of macro, this means that the test is executed in the parser rather than collecting everything inside the block and processing it later like say the `do` statement. Notice that if you want to do something more complex than a regular expression test, then you may need to use a `do` statement and the `info()` function.

### ifclass

This statement initiates a block either of statements or within another block. The block is only processed if the given @class is defined and contains at least one glyph.

```
ifclass(@oddities) {

# statements

}
```

Notice the lack of a `;` after the block close.

### do

The `do` statement is a means of setting variables and repeating statement groups with variable expansion. A `do` statement is followed by various substatements that are in effect nested statements. The basic structure of the `do` statement is:

`do` _substatement_ _substatement_ _..._ [ `{` _statements_ `}` ]

Where _statements_ is a sequence of FEA statements. Within these statements, variables may be referenced by preceding them with a `$`.
Anything, including statement words, can be the result of variable expantion. The only constraints are:

- The item stands on its own as a single token, to the lexer. It cannot be joined to something preceding or following it to create a single name, token, whatever.
- The expansion may result in only one token not more than one. So it can be a single name, but not multiple glyphs, etc.

In effect a `{}` type block following a `for` or `let` substatement is the equivalent of inserting the substatement `if True;` before the block.

#### SubStatements

Each substatement is terminated by a `;`. The various substatements are:

##### for

The `for` substatement is structured as:

`for` _var_ `=` _glyphlist_ `;`

This creates a variable _var_ that will iterate over the _glyphlist_.

##### let

The `let` substatement executes a short python expression (via `eval`), storing the result in the given variable. The structure of the substatement is:

`let` _var_ `=` _expression_ `;`

There are various python functions that are especially supported, along with the builtins. These are:

| Function | Parameters | Description |
|-------------|----------------|----------------|
| ADVx       | _glyphname_             | Returns the advanced width of the given glyph |
| APx        | _glyphname_, "_apname_" | Returns the x co-ordinate of the given attachment point on the given glyph |
| APy        | _glyphname_, "_apname_" | Returns the y co-ordinate of the given attachment point on the given glyph |
| feaclass   | _classname_             | Returns a list of the glyph names in a class as a python list |
| info       | _finfoelement_          | Looks up the entry in the fontinfo plist and returns its value |
| MINx       | _glyphname_             | Returns the minimum x value of the bounding box of the glyph |
| MINy       | _glyphname_             | Returns the minimum y value of the bounding box of the glyph |
| MAXx       | _glyphname_             | Returns the maximum x value of the bounding box of the glyph |
| MAXy       | _glyphname_             | Returns the maximum y value of the bounding box of the glyph |

Security wise, it is not possible to stop people doing nasty things with it. But psfmakefea is not expected to be used in untrusted environments.

##### if

The `if` substatement consists of an expression and a block of statements. `if` substatements only make sense at the end of a sequence of substatements and are executed at the end of the `do` statement, in the order they occur but after all other `for` and `let` substatements. The expression is calculated and if the result is True then the _statements_ are expanded using variable expansion.

`if` _expression_ `;` `{` _statements_ `}`

There can be multiple `if` substatements, each with their own block, in a `do` statement.

#### Examples

The `do` statement is best understood through some examples.

##### Simple calculation

This calculates a simple offset shift and creates a lookup to apply it:

```
do  let a = -int(ADVx("u16F61") / 2);
    {
        lookup left_shift_vowel {
            pos @_H <$a 0 0 0>;
        } left_shift_vowel;
    }
```

Notice the lack of iteration here.

##### More complex calculation

This calculates the guard spaces on either side of a base glyph in response to applied diacritics.

```
lookup advance_base {
do  for g = @H;
    let a = APx(g, "H") - ADVx(g) + int(1.5 * ADVx("u16F61"));
    let b = int(1.5 * ADVx("u16F61")) - APx(g, "H");
    let c = a + b;
    {
        pos $g <$b 0 $c 0>;
    }
} advance_base;
```

##### Right Guard

It is often desirable to give a base character extra advance width to account for a diacritic hanging over the right hand side of the glyph. Calculating this can be very difficult by hand. This code achieves this:

```
do  for b = @bases;
    for d = @diacritics;
    let v = (ADVx(d) - APx(d, "_U")) - (ADVx(g) - APx(b, "U"));
    if v > 0; {
        pos $b' <$v> $d;
    }
```

##### Left Guard

A corresponding guarding of space for diacritics may be done on the left side of a glyph:

```
do  for b = @bases;
    for d = @diacritics;
    let v = APx(d, "_U") - APx(b, "U");
    if v > 0; {
        pos $b' <$v 0 $v 0> $d;
    }
```

##### Left Kern

Consider the case where someone has used an attachment point as a kerning point. In some context they want to adjust the advance of the left glyph based on the position of the attachment point in the right glyph:

```
do  for r = @rights;
    let v = APx(r, "K"); {
        pos @lefts' <$v> $r;
        pos @lefts' <$v> @diacritics $r;
    }
```

##### Myanmar Great Ya

One obscure situation is the Great Ya (U+103C) in the Myanmar script, that visual wraps around the following base glyph. The great ya is given a small advance to then position the following consonant glyph within it. The advance of this consonant needs to be enough to place the next character outside the great ya. So we create an A attachment point on the great ya to emulate this intended final advance. Note that there are many variants of the great ya glyph. Thus:

```
do  for y = @c103C_nar;
    for c = @cCons_nar;
    let v = APx(y, "A") - (ADVx(y) + ADVx(c));
    if v > 0; {
        pos $y' <$v> $c;
    }

do  for y = @c103C_wide;
    for c = @cCons_wide;
    let v = APx(y, "A") - (ADVx(y) + ADVx(c));
    if v > 0; {
        pos $y' <$v> $c;
    }
```

##### Advance for Ldot on U

This example mirrors that used in the `setadvance` statement. Here we want to add sufficient advance on the base to correspond to attaching an u vowel which in turn has a lower dot attached to it.

```
do  for b = @cBases;
    for u in @cLVowels;
    let v = APx(b, "L") - APx(u, "_L") + APx(u, "LD") - APx("ldot", "_LD")  + ADVx("ldot") - ADVx(b);
    if v > 0; {
        pos $b' <$v> $u ldot;
    }
```

## Capabilities

### Permit classes on both sides of GSUB type 2 (multiple) and type 4 (ligature) lookups

Adobe doesn't permit compact notation using groups in 1-to-many (decomposition) rules e.g:

```
    sub @AlefPlusMark by absAlef @AlefMark ;
```

or many-to-1 (ligature) rules, e.g.:

```
    sub @ShaddaKasraMarks absShadda by @ShaddaKasraLigatures ;
```

Afaict, there isn't a reason we couldn't allow this and then expand the rule to Adobe-compliant verboseness when needed.

#### Processing

Of the four simple (i.e., non-contextual) substitution lookups, Types 2 and 4
are the only ones using the  'by' keyword that have a *sequence* of glyphs or
classes on one side of the rule. The other side will, necessarily, contain a
single term -- which Adobe currently requires to be a glyph.  For convenience of
expression, we'll call the sides of the rule the *sequence side* and the *singleton side*.

*   Non-contextual substitution
*   Uses the 'by' keyword
*   Singleton side references a glyph class.

Such rules are expanded by enumerating the singleton side class and the corresponding
class(es) on the sequence side and writing a set of Adobe-compliant rules to give
the same result.  It is an error if the singleton and corresponding classes do
not have the same number of glyphs.

#### Example

Given:

```
    @class1 = [ g1  g2 ] ;
    @class2 = [ g1a g2a ] ;
```

then

```
    sub @class1 gOther by @class2 ;
```

would be rewritten as:

```
    sub g1 gOther by g1a ;
    sub g2 gOther by g2a ;
```

