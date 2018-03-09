# FEA Extensions Future

## Introduction

This document is where people can dream of the extensions they would like to see
added to FEA. Notice that any extensions need to be convertible back to normal FEA
so shouldn't do things that can't be expressed in FEA.

As things get implemented from here, they will be moved to feaextensions.md. There
are no guaranteees that what is in here, will end up in psfmakefea.
The various features listed here are given priorities:

| Level | Priority
|------|-------------
| 1	| Intended to be implemented
| 2	| Probably will be implemented but after priority 1 stuff
| 3	| Almost certainly won't be implemented

There are a number of possible things that can be added to FEA, the question is whether they are worth adding in terms of meeting actual need (remove from this list if added to the rest of the document):

*   classsubtract() classand() functions
    *   classand(x, y) = classsubtract(x, (classsubtract(x, y))
*   classbuild(class, "$.ext") builds one class out of another. What if something is missing? Or do we just build those classes on the fly from make_fea and glyph name parsing?

## Statements

Statements are used to make rules, lookups, etc.

### setadvance

Priority: 3 (since the do statement has a higher priority and covers this)

This function does the calculations necessary to adjust the advance of a glyph based on information of attachment points, etc. The result is a single shift on each of the glyphs in the class. The syntax is:

```
setadvance(@glyphs, APName [, attachedGlyph[, APName, attachedGlyph [...]]])
```

In effect there are two modes for this function. The first only has two parameters
and shifts the advance from its default designed position to the x co-ordinate of
the given attachment point. The second mode adds extra glyphs. The advance is moved
to the advance of the attachedGlyph assuming the base has the other glyphs chained
attached at their given APs. An AP may be a number in which case that is the
x co-ordinate of the AP that will be used.

Typically there will be only one of these per lookup, unless the classes referenced
are non overlapping.

The statement only triggers if the resulting advance is greater than the current
advance. Thus some glyphs may not have a statement created for them. I.e. all
values in the lookup will be positive.

#### Examples

These examples also act as motivating use cases.

##### Nokyung

In Nokyung there is a need to kern characters that do not descend below the baseline closer to glyphs with a right underhang. This can be done through kerning pairs or we could add an attachment point to the glyphs with the right underhang and contextual adjust their advances to that position. The approach of using an AP to do kerning is certainly quirky and few designers would go that route. The contextual lookup would call a lookup that just does the single adjustment. Consider the AP to be called K (for kern). The fea might look like:

```
lookup overhangKernShift {
    setadvance(@overhangs, K);
} overhangKernShift;
```

And would expand, potentially, into

```
lookup overhangKernShift {
    @overhangs <-80>;
} overhangKernShift;
```
Not much, but that is because in Nokyung the overhanging glyphs all have the same overhang. If they didn't, then the list could well expand with different values for each glyph in the overhangs class. In fact, a simple implementation would do such an expansion anyway, while a more sophisticated implementation would group the results into ad hoc glyph lists.

##### Myanmar

An example from Myanmar is where a diacritic is attached such that the diacritic overhangs the right hand side of the base glyph and we want to extend the advance of the base glyph to encompass the diacritic. This is a primary motivating example for this statement. Such a lookup might read:

```
lookup advanceForLDotOnU {
    setadvance(@base, L, uvowel, LD, ldot);
} advanceForLDotOnU;
```

Which transforms to:

```
lookup advanceForLDotOnU {
    ka <120>;
    kha <80>;
# …
} advanceForLDotOnU;
```

##### Miao

Miao is slightly different in that the advance we want to use is a constant,
partly because calculating it involves a sequence of 3 vowel widths and you end up
with a very long list of possible values and lookups for each one:

```
lookup advancesShortShortShort {
    setadvance(@base, 1037);
} advancesShortShortShort;
```

#### Issues

*   Do we want to use a syntax more akin to that used for composites, since that is, in effect, what we are describing: make the base have the advance of the composite?
*   Do we want to change the output to reflect the sequence so that there can be more statements per lookup?
    *   The problem is that then you may want to skip intervening non-contributing glyphs (like upper diacritics in the above examples), which you would do anyway from the contextual driving lookup, but wouldn't want to have to do in each situation here.
*   It's a bit of a pain that in effect there is only one setadvance() per lookup. It would be nice to do more.
*   Does this work (and have useful meaning) in RTL?
*   Appears to leave the base glyph *position* unchanged. Is there a need to handle, for example in LTR scripts, LSB change for a base due to its diacritics? (Think i-tilde, etc.)

### move

Priority: 2

The move semantic results in a complex of lookups. See this [article](https://github.com/OpenType/opentype-layout/blob/master/docs/ligatures.md) on how to implement a move semantic successfully in OpenType. As such a move semantic can only be expressed as a statement at the highest level since it creates lookups. The move statement takes a number of parameters:

```
move lookup_basename, skipped, matched;
```

The *lookup_basename* is a name (unadorned string) prefix that is used in the naming of the lookups that the move statement creates. It also allows multiple move statements to share the same lookups where appropriate. Such lookups can be referenced by contextual chaining lookups. The lookups generated are:

|                              |                                                    |
| ---------------------------- | -------------------------------------------------- |
| lookup_basename_match        | Contextual chaining lookup to drive the sublookups |
| lookup_basename_pres_matched | Converts skipped(1) to matched + skipped(1) |
| lookup_basename_pref_matched | Converts skipped(1) to matched + skipped(1) + matched |
| lookup_basename_back         | Converts skipped(-1) + matched to skipped(-1). |

Multiple instances of a move statement that use the same *lookup_basename* will correctly merge the various rules in the the lookups created since often at least parts of the *skipped* or *matched* will be the same across different statements.

Since lookups may be added to, extra contextual rules can be added to the *lookup_basename*_match.

*skipped* contains a sequence of glyphs (of minimum length 1), where each glyph may be a class or whatever. The move statement considers both the first and last glyph of this sequence when it comes to the other lookups it creates. *skipped(1)* is the first glyph in the sequence and *skipped(-1)* is the last.

*matched* is a single glyph that is to be moved. There needs to be a two lookups for each matched glyph.

Notice that only *lookup_basename*_matched should be added to a feature. The rest are sublookups and can be in any order. The *lookup_basename*_matched lookup is created at the point of the first move statement that has a first parameter of *lookup_basename*.

#### Examples

While there are no known use cases for this in our fonts at the moment, this is an important statement in terms of showing how complex concepts of wider interest can be implemented as extensions to fea.

##### Myanmar

Moving prevowels to the front of a syllable from their specified position in the sequence, in a DFLT processor is one such use of a move semantic:

```
move(pv, @cons, my-e);
move(pv, @cons @medial, my-e);
move(pv, @cons @medial @medial, my-e);
move(pv, @cons @medial @medial @medial, my-e);
move(pv, @cons, my-shane);
move(pv, @cons, @medial, my-shane);
```

This becomes:

```
lookup pv_pres_my-e {
	sub @cons by my-e @cons;
} pv_pres_my-e;

lookup pv_pref_my-e {
	sub @cons by my-e @cons my-e;
} pv_pref_my-e;

lookup pv_back {
	sub @cons my-e by @cons;
	sub @medial my-e by @medial;
	sub @cons my-shane by @cons;
	sub @medial my-shane by @medial;
} pv_back;

lookup pv_match {
	sub @cons' lookup pv_pres-my-e my-e' lookup pv_back;
	sub @cons' lookup pv_pref-my-e @medial my-e' lookup pv_back;
	sub @cons' lookup pv_pref-my-e @medial @medial my-e' lookup pv_back;
	sub @cons' lookup pv_pref-my-e @medial @medial @medial my-e' lookup pv_back;
	sub @cons' lookup pv_pres-my-shane my-shane' lookup pv_back;
	sub @cons' lookup pv_pref-my-shane @medial my-shane' lookup pv_back;
} pv_match;

lookup pv_pres_my-shane {
	sub @cons by my-shane @cons;
} pv_pres_my-shane;

lookup pv_pref_my-shane {
	sub @cons by my-shane @cons my-shane;
} pv_pref_my-shane;
```

##### Khmer Split Vowels

Khmer has a system of split vowels, of which we will consider a very few:

```
lookup presplit {
	sub km-oe by km-e km-ii;
	sub km-ya by km-e km-yy km-ya.sub;
	sub km-oo by km-e km-aa;
} presplit;

move(split, @cons, km-e);
move(split, @cons @medial, km-e);
```

### ifinfo

Priority: 1

Like all if type statements, this is a macro statement that is executed during parsing rather than post parsing. ifinfo is designed to be extensible and has a syntax of:

```
ifinfo(info_type, "regexp") { … }
```

The *info_type* specifies what information is to be tested. Valid values are:

|          |                                                                            |
| -------- | -------------------------------------------------------------------------- |
| family   | Font family name as specified before fea processing                        |
| fullname | Full name including weight and italics modifiers. Regular is not included? |

The *regexp* is a regular expression that if matches means the block following the ifinfo will be parsed and added to the AST just as if the ifinfo and block elements did not exist.

#### Examples

```
ifinfo(family, "^Charis") {
	…
}
```

### ifclass

Like all if type statements, this is a macro statement that is executed during parsing rather than post parsing. ifclass tests for whether a class exists and is not empty and has a syntax of:

```
ifclass(class_name) { … }
```

#### Examples

```
ifclass(cno_sc) {
	feature smcp {
		sub @cno_sc by @c_sc;
	} smcp;
}
```

### do

Priority: 2

The `do` statement is a means of setting variables and repeating statement groups with variable expansion. A `do` statement is followed by various substatements that are in effect nested statements. The basic structure of the `do` statement is:

`do` _substatement_ `;` _substatement_ `;` _..._ `;`
`{` _statements_ `};`

Where _statements_ is a sequence of FEA statements. Within these statements, variables may be referenced by preceding them with a `$`.
There is only a limited set of fea objects that can be replaced by variables, including only: numbers, glyphnames.

One purpose of the `do` statement is to remove the need for the `setadvance` statement which is not generic enough. `do` statements do not nest in a way where variables from one can be used in the nested statement.

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
| APx        | _glyphname_, "_apname_" | Returns the x co-ordinate of the given attachment point on the given glyph |
| APy        | _glyphname_, "_apname_" | Returns the y co-ordinate of the given attachment point on the given glyph |
| ADVx     | _glyphname_                       | Returns the advanced width of the given glyph |

Security wise, it is not possible to stop people doing nasty things with it. But psfmakefea is not expected to be used in untrusted environments.

##### if

The `if` substatement evaluates the given expression and only executes following substatements if the evaluation results in True. The structure is:

`if` _expression_ `;`

#### Examples

The `do` statement is best understood through some examples.

##### Right Guard

It is often desirable to give a base character extra advance width to account for a diacritic hanging over the right hand side of the glyph. Calculating this can be very difficult by hand. This code achieves this:

```
do  for b = @bases;
    for d = @diacritics;
    let v = (ADVx(d) - APx(d, "_U")) - (ADVx(g) - APx(g, "U"));
    if v > 0; {
        pos $b' <$v> $d;
    };
```

##### Left Guard

A corresponding guarding of space for diacritics may be done on the left side of a glyph:

```
do  for b = @bases;
    for d = @diacritics;
    let v = APx(d, "_U") - APx(g, "U");
    if v > 0; {
        pos $b' <$v 0 $v 0> $d;
    };
```

##### Left Kern

Consider the case where someone has used an attachment point as a kerning point. In some context they want to adjust the advance of the left glyph based on the position of the attachment point in the right glyph:

```
do  for r = @rights;
    let v = APx(r, "K"); {
        pos @lefts' <$v> $r;
        pos @lefts' <$v> @diacritics $r;
    };
```

##### Myanmar Great Ya

One obscure situation is the Great Ya (U+103C) in the Myanmar script, that visual wraps around the following base glyph. The great ya is given a small advance to then position the following consonant glyph within it. The advance of this consonant needs to be enough to place the next character outside the great ya. So we create an A attachment point on the great ya to emulate this intended final advance. Note that there are many variants of the great ya glyph. Thus:

```
do  for y = @c103C_nar;
    for c = @cCons_nar;
    let v = APx(y, "A") - (ADVx(y) + ADVx(c));
    if v > 0; {
        pos $y' <$v> $c;
    };

do  for y = @c103C_wide;
    for c = @cCons_wide;
    let v = APx(y, "A") - (ADVx(y) + ADVx(c));
    if v > 0; {
        pos $y' <$v> $c;
    };
```

##### Advance for Ldot on U

This example mirrors that used in the `setadvance` statement. Here we want to add sufficient advance on the base to correspond to attaching an u vowel which in turn has a lower dot attached to it.

```
do for b = @cBases;
    for u in @cLVowels;
    let v = APx(b, "L") - APx(u, "_L") + APx(u, "LD") - APx("ldot", "_LD")  + ADVx("ldot") - ADVx(b);
    if v > 0; {
        pos $b' <$v> $u ldot;
    }
```


## Functions

Functions may be used in the place of a glyph or glyph class and return a list of glyphs.

### index

Priority: 2

Used in rules where the expansion of a rule results in a particular glyph from a class being used. Where two classes need to be synchronised, and which two classes are involved, this function specifies the rule element that drives the choice of glyph from this class. This function is motivated by the Keyman language. The parameters of index() are:

```
index(slot_index, glyphclass)
```

*slot_index* considers the rule as two sequences of slots, each slot referring to one glyph or glyphclass. The first sequence is on the left hand side of the rule and the second on the right, with the index running sequentially from one sequence to the other. Thus if a rule has 2 slots on the left hand side and 3 on the right, a *slot_index* of 5 refers to the last glyph on the right hand side. *Slot_index* values start from 1 for the first glyph on the left hand side.

What makes an index() function difficult to implement is that it requires knowledge of its context in the statement it occurs in. This is tricky to implement since it is a kind of layer violation. It doesn't matter how an index() type function is represented syntactically, the same problem applies.

### infont

Priority: 2

This function filters the glyph class that is passed to it, and returns only those glyphs, in glyphclass order, which are actually present in the font being compiled for. For example:

```
@cons = infont([ka kha gha nga]);
```

## Capabilities

### Permit classes on both sides of GSUB type 2 (multiple) and type 4 (ligature) lookups

Priority: 2

#### Slot correspondence

In Type 2 (multiple) substitutions, the LHS will be the singleton case and the RHS will be the sequence. In normal use-cases exactly one slot in the RHS will be a class -- all the others will be glyphs -- in which case that class and the singleton side class correspond.

If more than one RHS slot is to contain a class, then the only logical meaning is that all such classes must also correspond to the singleton class in the LHS, and will be expanded (along with the singleton side class) in parallel. Thus all the classes must have the same number of elements.

In Type 4 (ligature) substitutions, the RHS will be the singleton class. In the case that the LHS (sequence side) of the rule has class references in more than one slot, we need to identify which slot corresponds to the singleton side class.  Some alternatives:

*   Pick the slot that, when the classes are flattened, has the same number of glyphs as the class on the singleton side.  It is possible that there is more than one such slot, however.
*   Add a notation to the rule. Graphite uses the $n modifier on the RHS to identify the corresponding slot (in the context), which we could adapt to FEA as:

```
  sub @class1 @class2 @class3 by @class4$2 ;
```

Alternatively, since there can be only one such slot, we could use a simpler notation by putting something like the $ in the LHS:

```
  sub @class1 @class2$ @class3 by @class4 ;
```

[This won't look right to GDL programmers, but makes does sense for OT code]

*   Extra syntactic elements at the lexical level are hard to introduce. Instead a function such as:

```
sub @class1 @class2 @class3 by index(2, @class4);
```

Would give the necessary interpretation. See the discussion of the index() function for more details.

Note that the other classes in the LHS of ligature rules do not need further processing since FEA allows such classes.

#### Nested classes

We will want to expand nested classes in a way (i.e., depth or breadth first) that is compatible with Adobe.  **Concern:** Might this be different than Graphite? Is there any difference if one says always expand left to right? [a b [c [d e] f] g] flattens the same as [[[a b] c d] e f g] or whatever. The FontTools parser does not support nested glyph classes. To what extent are they required?
