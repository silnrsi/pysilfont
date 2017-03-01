# FTML (Font Test Markup Language) tools

## .xsl to generate HTML from FTML (.xml) input

| .xsl file | Description
| :-------- | :-----------
| FTMLcreateList.xsl  | one test string per line
| FTMLcreateChart.xsl | multiple test strings per line (using nested testgroup elements)
| FTMLcreateWaterfall.xsl | each test string repeated on successive lines at increasing point sizes
| FTMLcreateWaterfall4col.xsl | each test string repeated in four horizontal cells at increasing point sizes

The .xsl file can be specified in the .xml file using (for example):

```<?xml-stylesheet type="text/xsl" href="FTMLcreateList.xsl"?>```

For nested testgroup elements, those at the outer level are successive rows,
whereas those at the inner level are successive cells in the row.

Including the attribute rtl="True" in the test element
will set the paragraph direction as RTL for the paragraph or table cell.

Part or all of the text in the string element can be enclosed in ```<em>...</em>``` tags.
This will make the enclosed text normal and text before and after lighter colored.

Including the attribute background="#CCCCCC" in the test element will change the background
color. #CCCCCC represents the six hex digits that define the color.
Lower case hex digits (abcdef rather than ABCDEF) are used in the canonical representation.
