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

