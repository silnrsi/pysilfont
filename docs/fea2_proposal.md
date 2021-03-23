# Proposed Extensions to FEA

This document describes various extensions to FEA that will enable it to grow
and support more powerful OpenType descriptions. The proposal is presented as
varoius syntax extensions to the core FEA syntax.

## Functions

Currently FEA makes no use of parentheses. This may be a conscious decision to
reserve these for later ues. Such parentheses lend themselves perfectly to the
addition of macro functions to the FEA syntax:

```
function = funcname '(' (parameter (',' parameter)*)? ')' ('{' tokens '}')?
function_statement = function ';'

funcname = /[A-Za-z_.][A-Za-z_0-9.]*/
parameter = glyph | glyphlist | classref | value_record | function
            | ('"' string '"')
tokens = ANY*
glyphlist = '[' glyph* ']'
classref = '@' classname
value_record = number | '<' chars '>'
```

A function call consists of a function name, a parenthesised parameter list,
which may be empty and an optional following token list enclosed in braces. The
token list is just that, an unparsed sequence of lexical tokens. The result of
the function is also an unparsed sequence of lexical tokens that are then parsed
and processed as if the function were replaced by a textual representation of
the tokens.

The parameters are parsed, so for example a classref would expand to its
resulting list of glyphs. Likewise a function call result would be parsed to its
single semantic item, it is not parsed as a token list. A value_record is the
widest interpretation of a value record, including an anchor. Basically it is
either a number or anything between < and >.

A function statement is the use of a function result as a statement in the FEA
syntax.

The FEA syntax defines nothing more that functions exist and how they may be
referenced. It is up to a particular FEA processor to supply the functions and
to execute them to resolve them to a token list. It is also up to the particular
FEA processor to report an error or otherwise handle an unknown function
reference. As such this is similar to other programming languages where the
language itself says nothing about what functions exist or what they do. That is
for libraries.

There is one exception. The `include` statement in the core FEA syntax follows
the same syntax, apart from the missing quotation marks around the filename. As
such `include` is not available for use as a function name.

### Sample Implementation

In this section we give a sample implementation based on the FEA library in
fonttools.

Functions are kept in module style namespaces, much like a simplified python module
system. A function name then typically consists of a `modulename.funcname` The
top level module is reserved for the fea processor itself. The following
functions are defined in the top level module (i.e. no modulename.)

#### load

The `load` function takes a path to a file containing python definitions.
Whether this python code is preprocessed for security purposes or not is an open
question. It also takes a modulename as its second parameter.

```
load("path/to/pythonfile.py", "mymodule")
```

The function returns an empty token string but has the effect of loading all the
functions defined in the python file as those functions prefixed by the
modulename, as described above.

#### set

This sets a variable to a token list. Variables are described in a later syntex
extension. The first parameter is the name of a variable. The token list is then
used for the variable expansion.

```
set("distance") { 30 };
```

Other non top level module may be supplied with the core FEA processing module.

#### core.refilter

This function is passed a glyphlist (or via a classref) and a regular
expression. The result is a glyphlist consisting of all the glyphs whose name
matches the regular expression. For example:

```
@csc = core.refilter("\.sc$", @allglyphs)
```

#### core.pairup

This function is passed two classnames, a regular expression and a glyph list.
The result is two class definitions for the two classnames. One class is
of all the glyphs which match the regular expression. The other class is a
corresponding list of glyphs whose name is the same as the matching regular
expression with the matching regular expression text removed. If no such glyph
exists in the font, then neither the name or the glyph matching the regular
expression is included. The resulting classes may therefore be used in a simple
substitution. For example:

```
core.pairup("cnosc", "csc", "\.sc$", [a.sc b.sc fred.sc]);
lookup smallcap {
   sub @cnosc by @csc;
} smallcap;
```

Assuming `fred.sc` exists but `fred` does not, this is equivalent to:

```
@cnosc = [a b];
@csc = [a.sc b.sc];
lookup smallcap {
    sub @cnosc by @csc;
} smallcap;
```

## Variables

A further extension to the FEA syntax is to add a simple variable expansion. A
variable expands to a token list. Since variables may occur anywhere they need a
syntactic identifier. The proposed identifier is an initial `$`.

```
variable = '$' funcname
```

Variables are expanded at the point of expansion. Since expansion is recursive,
the variable may contain a function call which expands when the variable
expands.

There is no syntax for defining a variable. This is unnatural and may be
revisited if a suitable syntax can be found. Definition is therefore a processor
specific activity.

It is undecided whether undefined variables expand to an empty token list or an
error.

