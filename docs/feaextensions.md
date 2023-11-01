# FEA Extensions Current

This document describes the functionality of `psfmakefea` and lists the extensions to fea that are currently supported.
<!-- TOC -->

- [Generated Classes](#generated-classes)
    - [Variant glyph classes](#variant-glyph-classes)
    - [Ligatures](#ligatures)
- [Statements](#statements)
    - [baseclass](#baseclass)
        - [Cursive Attachment](#cursive-attachment)
        - [Mark Attachment](#mark-attachment)
        - [Ligature Attachment](#ligature-attachment)
    - [ifinfo](#ifinfo)
    - [ifclass](#ifclass)
    - [do](#do)
        - [SubStatements](#substatements)
            - [for](#for)
            - [let](#let)
            - [forlet](#forlet)
            - [if](#if)
        - [Examples](#examples)
            - [Simple calculation](#simple-calculation)
            - [More complex calculation](#more-complex-calculation)
            - [Right Guard](#right-guard)
            - [Left Guard](#left-guard)
            - [Left Kern](#left-kern)
            - [Myanmar Great Ya](#myanmar-great-ya)
            - [Advance for Ldot on U](#advance-for-ldot-on-u)
    - [def](#def)
        - [python support](#python-support)
    - [kernpairs](#kernpairs)
- [Capabilities](#capabilities)
    - [Permit classes on both sides of GSUB type 2 (multiple) and type 4 (ligature) lookups](#permit-classes-on-both-sides-of-gsub-type-2-multiple-and-type-4-ligature-lookups)
        - [Processing](#processing)
        - [Example](#example)
    - [Support classes in alternate lookups](#support-classes-in-alternate-lookups)
    - [groups.plist](#groupsplist)

<!-- /TOC -->
## Generated Classes

`psfmakefea` simplifies the hand creation of fea code by analysing the glyphs in the input font, particularly with regard to their names. Names are assumed to conform to the Adobe Glyph List conventions regarding `_` for ligatures and `.` for glyph variants.

### Variant glyph classes

If a font contains a glyph with a final variant (there may be more than one listed for a glyph, in sequence) and also a glyph without that final variant, then `psfmakefea` will create two classes based on the variant name: @c\__variant_ contains the glyph with the variant and @cno\__variant_ contains the glyph without the variant. The two lists are aligned such that a simple classes based replacement will change all the glyphs without the variant into ones with the variant.

For example, U+025B is an open e that occurs in some African languages. Consider a font that contains the glyphs `uni025B` and `uni025B.smcp` for a small caps version of the glyph. `psfmakefea` will create two classes:

```
@c_smcp = [uni025B.scmp];
@cno_smcp = [uni025B];
```

In addition, if this font contains two other glyphs `uni025B.alt`, an alternative shape to `uni025B` and `uni025B.alt.smcp`, the small caps version of the alternate. `psfmakefea` will create the following classes:

```
@c_smcp = [uni025B.scmp uni025B.alt.smcp];
@cno_smcp = [uni025B uni025B.alt];
@c_alt = [uni025B.alt];
@cno_alt = [uni025B];
```

Notice that the classes with multiple glyphs, while keeping the alignment, do not guarantee any particular order of the glyphs in one of the classes. Only that the other class will align its glyph order correctly. Notice also that `uni025B.alt.smcp` does not appear in the `@c_alt` class. This latter behaviour may change.

### Ligatures

Unless instructed on the command line via the `-L` or `--ligmode` option, `psfmakefea` does nothing special with ligatures and treats them simply as glyphs that may take variants. There are four ligature modes. The most commonly used is `-L last`. This says to create classes based on the last components in all ligatures. Thus if the font from the previous section also included `uni025B_acutecomb` and the corresponding small caps `uni025B_acutecomb.smcp`. We also need an `acutecomb`. If the command line included `-L last`, the generated classes would be:

```
@c_smcp = [uni025B.scmp uni025B.alt.smcp uni025B_acutecomb.smcp];
@cno_smcp = [uni025B uni025B.alt uni025B_acutecomb];
@c_alt = [uni025B.alt];
@cno_alt = [uni025B];
@clig_acutecomb = [uni025B_acutecomb];
@cligno_acutecomb = [uni025B];
```

And if the command line option were `-L first`, the last two lines of the above code fragment would become:

```
@clig_uni025B = [uni025B_acutecomb];
@cligno_uni025B = [acutecomb];
```

while the variant classes would remain the same.

There are two other ligaturemodes: `lastcomp` and `firstcomp`. These act like `last` and `first`, but in addition they say that any final variants must be handled differently. Instead of seeing the final variants (those on the last ligature component) as applying to the whole ligature, they are only to be treated as applying to the last component. To demonstrate this we need to add the nonsensical `acutecomb.smcp`. With either `-L last` or `-L first` we get the same ligature classes as above. (Although we would add `acutecomb.smcp` to the `@c_smcp` and `acutecomb` to `@cno_smcp`) With `-L firstcomp` we get:

```
@c_smcp = [uni025B.scmp uni025B.alt.smcp acutecomb.smcp];
@cno_smcp = [uni025B uni025B.alt acutecomb];
@c_alt = [uni025B.alt];
@cno_alt = [uni025B];
@clig_uni025B = [uni025B_acutecomb uni025B_acutecomb.smcp];
@cligno_uni025B = [acutecomb acutecomb.smcp];
```

Notice the removal of `uni025B_acutecomb.smcp` from `@c_smcp`, since `uni025B_acutecomb.smcp` is considered by `-L firstcomp` to be a ligature of `uni025B` and `acutecomb.smcp` there is no overall ligature `uni025B_acutecomb` with a variant `.smcp` that would fit into `@c_smcp`. If we use `-L lastcomp` we change the last two classes to:

```
@clig_acutecomb = [uni025B_acutecomb];
@cligno_acutecomb = [uni025B];
@clig_acutecomb_smcp = [uni025B_acutecomb.smcp];
@cligno_acutecomb_smcp = [un025B];
```

With any `.` in the variant being changed to `_` in the class name.

In our example, if the author wanted to use `-L lastcomp` or `-L firstcomp`, they might find it more helpful to rename `uni025B_acutecomb.smcp` to `uni025B.smcp_acutecomb` and remove the nonsensical `acutecomb.smcp`. This would give, for `-L lastcomp`:

```
@c_smcp = [uni025B.scmp uni025B.alt.smcp];
@cno_smcp = [uni025B uni025B.alt];
@c_alt = [uni025B.alt];
@cno_alt = [uni025B];
@clig_acutecomb = [uni025B_acutecomb uni025B.smcp_acutecomb];
@cligno_acutecomb = [uni025B uni025B.smcp];
```

and for `-L firstcomp`, the last two classes become:

```
@clig_uni025B = [uni025B_acutecomb];
@cligno_uni025B = [acutecomb];
@clig_uni025B_smcp = [uni025B.smcp_acutecomb];
@cligno_uni025B_smcp = [acutecomb];
```

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

- baseClass A - containing all bases with attachment point A
- markClass \_A - containing all marks with attachment point \_A
- baseClass A\_MarkBase - containing all marks with attachment point A

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

#### Ligature Attachment

Ligature attachment involves all the attachments to a ligature in a single rule. Given a list of possible ligature glyphs, the ligature positioning rule has been extended to allow the use of baseClasses instead of the base anchor on the ligature. For a noddy example:

```
baseClass a <anchor 200 200> @TOP_1;
baseClass fi <anchor 200 0> @BOTTOM_1;
baseClass fi <anchor 400 0> @BOTTOM_2;
markClass acute <anchor 0 200> @TOP;
markClass circumflex <anchor 200 0> @BOTTOM;

pos ligature [a fi] @BOTTOM_1 mark @BOTTOM @TOP_1 mark @TOP
        ligComponent @BOTTOM_2 mark @BOTTOM;
```

becomes

```
pos ligature a <anchor 200 200> mark @TOP
    ligComponent <anchor NULL>;
pos ligature fi <anchor 200 0> mark @BOTTOM
    ligComponent <anchor 400 0> mark @BOTTOM;
```

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

Where _statements_ is a sequence of FEA statements. Within these statements, variables may be referenced by preceding them with a `$`. Anything, including statement words, can be the result of variable expantion. The only constraints are:

- The item expands to one or more complete tokens. It cannot be joined to something preceding or following it to create a single name, token, whatever.

In effect a `{}` type block following a `for` or `let` substatement is the equivalent of inserting the substatement `if True;` before the block.

#### SubStatements

Each substatement is terminated by a `;`. The various substatements are:

##### for

The `for` substatement is structured as:

`for` _var_ `=` _glyphlist_ `;`

This creates a variable _var_ that will iterate over the _glyphlist_.

With the addition of `forlet` (see below), there is also `forgroup` that is a synonym for the `for` substatement defined here.

##### let

The `let` substatement executes a short python expression (via `eval`), storing the result in the given variable, or variable list. The structure of the substatement is:

`let` _var_ [`,` _var_]* `=` _expression_ `;`

There are various python functions that are especially supported, along with the builtins. These are:

| Function | Parameters | Description |
|-------------|-------------|------------------------|
| ADVx       | _glyphname_             | Returns the advanced width of the given glyph |
| allglyphs  |                         | Returns a list of all the glyph names in the font |
| APx        | _glyphname_, "_apname_" | Returns the x coordinate of the given attachment point on the given glyph |
| APy        | _glyphname_, "_apname_" | Returns the y coordinate of the given attachment point on the given glyph |
| feaclass   | _classname_             | Returns a list of the glyph names in a class as a python list |
| info       | _finfoelement_          | Looks up the entry in the fontinfo plist and returns its value |
| kerninfo |                           | Returns a list of tuples (left, right, kern_value) |
| opt     | _defined_                  | Looks up a given -D/--define variable. Returns empty string if missing |
| MINx       | _glyphname_             | Returns the minimum x value of the bounding box of the glyph |
| MINy       | _glyphname_             | Returns the minimum y value of the bounding box of the glyph |
| MAXx       | _glyphname_             | Returns the maximum x value of the bounding box of the glyph |
| MAXy       | _glyphname_             | Returns the maximum y value of the bounding box of the glyph |

See the section on python in the `def` command section following.

##### forlet

The `for` substatement only allows iteration over a group of glyphs. There are situations in which someone would want to iterate over a true python expression, for example, over the return value of a function. The `forlet` substatement is structured identically to a `let` substatement, but instead of setting the variable once, the following substatements are executed once for each value of the expression, with the variable set to each in turn. For example:

```
def optlist(*alist) {
    if len(alist) > 0:
        for r in optlist(*alist[1:]):
            yield [alist[0]] + r
            yield r
    else:
        yield alist
} optlist;

lookup example {
do
    forlet l = optlist("uni17CC", "@coeng_no_ro", "[uni17C9 uni17CA]", "@below_vowels", "@above_vowels");
    let s = " ".join(l)
    {
        sub uni17C1 @coeng_ro @base_cons $s uni17B8' lookup insert_dotted_circle;
        sub uni17C1 @base_cons $s uni17B8' lookup insert_dotted_circle;
    }
} example;
```

This examples uses a `def` statement as defined below. The example produces rules for each of the possible subsequences of the optlist parameters, where each element is treated as being optional. It is a way of writing:

```
sub uni17C1 @base_cons uni17CC? @coeng_no_ro [uni17C9 uni17CA]? @below_vowels? @above_vowels? uni17B8' lookup insert_dotted_circle;
```

The structure of a `forlet` substatement is:

`forlet` _var_ [`,` _var_]* `=` _expression_ `;`

A `forlet` substatement has the same access to functions that the `let` statement has, included those listed above under `let`.


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
    let v = (ADVx(d) - APx(d, "_U")) - (ADVx(b) - APx(b, "U"));
    if v > 0; {
        pos $b' $v $d;
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
        pos @lefts' $v $r;
        pos @lefts' $v @diacritics $r;
    }
```

##### Myanmar Great Ya

One obscure situation is the Great Ya (U+103C) in the Myanmar script, that visual wraps around the following base glyph. The great ya is given a small advance to then position the following consonant glyph within it. The advance of this consonant needs to be enough to place the next character outside the great ya. So we create an A attachment point on the great ya to emulate this intended final advance. Note that there are many variants of the great ya glyph. Thus:

```
do  for y = @c103C_nar;
    for c = @cCons_nar;
    let v = APx(y, "A") - (ADVx(y) + ADVx(c));
    if v > 0; {
        pos $y' $v $c;
    }

do  for y = @c103C_wide;
    for c = @cCons_wide;
    let v = APx(y, "A") - (ADVx(y) + ADVx(c));
    if v > 0; {
        pos $y' $v $c;
    }
```

##### Advance for Ldot on U

This example mirrors that used in the proposed [`setadvance`](feax_future.md#setadvance) statement. Here we want to add sufficient advance on the base to correspond to attaching an u vowel which in turn has a lower dot attached to it.

```
do  for b = @cBases;
    for u = @cLVowels;
    let v = APx(b, "L") - APx(u, "_L") + APx(u, "LD") - APx("ldot", "_LD")  + ADVx("ldot") - ADVx(b);
    if v > 0; {
        pos $b' $v $u ldot;
    }
```

### def

The `def` statement allows for the creation of python functions for use in `let` substatements of the `do` statement. The syntax of the `def` statement is:

```
def <fn>(<param_list>) {
    ... python code ...
} <fn>;
```

The `fn` must conform to a FEA name (not starting with a digit, etc.) and is repeated at the end of the block to mark the end of the function. The parameter is a standard python parameter list and the python code is standard python code, indented as if under a `def` statement. 

#### python support
Here and in `let` and `forlet` substatements, the python that is allowed to be executed is limited. Only a subset of functions from builtins is supported and the `__` may not occur in any attribute. This is to stop people escaping the sandbox in which python code is interpreted. The `math` and `re` modules are also included along with the functions available to a `let` and `forlet` substatement. The full list of builtins supported are:

```
True, False, None, int, float, str, abs, bool, dict, enumerate, filter, hex, isinstance, len, list,
map, max, min, ord, range, set, sorted, sum, tuple, type, zip
```

### kernpairs

The `kernpairs` statement expands all the kerning pairs in the font into `pos` statements. For example:

```
lookup kernpairs {
    lookupflag IgnoreMarks;
    kernpairs;
} kernpairs;
```

Might produce:

```
lookup kernpairs {
    lookupflag IgnoreMarks;
    pos @MMK_L_afii57929 -164 @MMK_R_uniA4F8;
    pos @MMK_L_uniA4D1 -164 @MMK_R_uniA4F8;
    pos @MMK_L_uniA4D5 -164 @MMK_R_afii57929;
    pos @MMK_L_uniA4FA -148 @MMK_R_space;
} kernpairs;
```

Currently, kerning information is only available from .ufo files.

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

This is implemented in FEAX as follows.

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

### Support classes in alternate lookups

The default behaviour in FEA is for a `sub x from [x.a x.b];` to only allow a single glyph before the `from` keyword. But it is often useful to do things like: `sub @a from [@a.lower @a.upper];`. Feax supports this by treating the right hand side list of glyphs as a single list and dividing it equally by the list on the left. Thus if `@a` is of length 3 then the first 3 glyphs in the right hand list will go one each as the first alternate for each glyph in `@a`, then the next 3 go as the second alternate, and so on until they are all consumed. If any are left over in that one of the glyphs ends up with a different number of alternates to another, then an error is given.

### groups.plist

If a .ufo file contains a `groups.plist` file, the groups declared there are propagated straight through to the output file and can be referenced within a source file.

