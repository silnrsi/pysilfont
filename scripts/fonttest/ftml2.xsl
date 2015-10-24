<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="utf-8"/>
<!-- Use with nested <testgroup> elements to create tables with multiple <test> elements per row -->

<!-- set variables from head element -->
<xsl:variable name="width-comment" select="/ftml/head/columns/@comment"/>
<xsl:variable name="width-label" select="/ftml/head/columns/@label"/>
<xsl:variable name="width-string" select="/ftml/head/columns/@string"/>
<xsl:variable name="font-scale" select="concat(/ftml/head/fontscale, substring('100', 1 div not(/ftml/head/fontscale)))"/>

<!-- 
	Process the root node to construct the html page
-->
<xsl:template match="/">
<html>
	<head>
		<title>
			<xsl:value-of select="ftml/head/title"/>
		</title>
		<meta charset="utf-8"/>
		<meta name="description">
			<xsl:attribute name="content">
				<xsl:value-of select="ftml/head/description"/>
			</xsl:attribute>
		</meta>
		<style>
	body, td { font-family: sans-serif; }
	@font-face {font-family: TestFont; src: <xsl:value-of select="ftml/head/fontsrc"/>; }
	th { text-align: left; }
	table { width: 100%; table-layout: fixed; }
	table,th,td { padding: 2px; border: 1px solid #111111; border-collapse: collapse; }
<xsl:if test="$width-label != ''">
	.label { width: <xsl:value-of select="$width-label"/> }
</xsl:if>
<xsl:if test="$width-string != ''">
	.string {width: <xsl:value-of select="$width-string"/>; font-family: TestFont; font-size: <xsl:value-of select="$font-scale"/>%;}
</xsl:if>
<xsl:if test="$width-comment != ''">
	.comment {width: <xsl:value-of select="$width-comment"/>}
</xsl:if>
	.dim {color: silver;}
	.bright {color: red;}
	<!-- NB: Uncomment the following to build separate css styles for each item in /ftml/head/styles -->
	<!-- <xsl:apply-templates select="/ftml/head/styles/*" /> -->
		</style>
	</head>
	<body>
		<h1><xsl:value-of select="/ftml/head/title"/></h1>
		<xsl:apply-templates select="/ftml/testgroup"/>
	</body>
</html>
</xsl:template>

<!-- 
	Build CSS style for FTML style element
-->
<xsl:template match="style">
	.<xsl:value-of select="@name"/> {
		font-family: TestFont; font-size: <xsl:value-of select="$font-scale"/>%;
<xsl:if test="@feats">
		-moz-font-feature-settings: <xsl:value-of select="@feats"/>;
		-ms-font-feature-settings: <xsl:value-of select="@feats"/>;
		-webkit-font-feature-settings: <xsl:value-of select="@feats"/>;
		font-feature-settings: <xsl:value-of select="@feats"/> ; 
</xsl:if>			
	}
</xsl:template>

<!-- 
	Process a top level testgroup, emitting a table (containing a row for each testgroup subelement)
-->
<xsl:template match="/ftml/testgroup">
	<h2><xsl:value-of select="@label"/></h2>
	<table>
		<tbody>
			<xsl:apply-templates/>
		</tbody>
	</table>
</xsl:template>

<!-- 
	Process a second level testgroup record, emitting a table row (containing a cell for each test subelement)
	Pick up comment, class and background from first test subelement
-->
<xsl:template match="/ftml/testgroup/testgroup">
<tr>
	<xsl:if test="test/@background">
		<xsl:attribute name="style">background-color: <xsl:value-of select="test/@background"/>;</xsl:attribute>
	</xsl:if>
	<xsl:if test="$width-label != ''">
		<!-- emit label column -->
		<td class="label">
			<xsl:value-of select="@label"/>
		</td>
	</xsl:if>

    	<xsl:apply-templates/>
	<xsl:if test="$width-comment != ''">
		<td class="comment">
			<!-- emit comment concatenated with class (if not default) -->
			<xsl:value-of select="test/comment"/>
			<xsl:if test="test/@class"> (<xsl:value-of select="test/@class"/>)</xsl:if>
		</td>
	</xsl:if>
</tr>
</xsl:template>

<!-- 
	Emit html lang and font-feature-settings for a test 
-->
<xsl:template match="style" mode="getLang">
	<xsl:if test="@lang">
		<xsl:attribute name="lang">
			<xsl:value-of select="@lang"/>
		</xsl:attribute>
	</xsl:if>
	<xsl:if test="@feats">
		<xsl:attribute name="style">
-moz-font-feature-settings: <xsl:value-of select="@feats"/>;
-ms-font-feature-settings: <xsl:value-of select="@feats"/>;
-webkit-font-feature-settings: <xsl:value-of select="@feats"/>;
font-feature-settings: <xsl:value-of select="@feats"/>;</xsl:attribute>
	</xsl:if>
</xsl:template>

<!-- 
	Process a single test record, emitting a table cell
-->
<xsl:template match="test">
	<xsl:if test="$width-string != ''">
		<!-- emit test data column -->
		<td class="string">   <!-- assume default string class -->
			<xsl:if test="@class">
				<!-- emit features and lang attributes -->
				<xsl:variable name="styleName" select="@class"/>
				<xsl:apply-templates select="/ftml/head/styles/style[@name=$styleName]" mode="getLang"/>
			</xsl:if>
			<!-- and finally the test data -->
			<xsl:choose>
				<!-- if the test has an <em> marker, the use a special template -->
				<xsl:when test="string[em]">
					<xsl:apply-templates select="string" mode="hasEM"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:apply-templates select="string"/>
				</xsl:otherwise>
			</xsl:choose>
		</td>
	</xsl:if>
</xsl:template>

<!--  
	suppress all text nodes except those we really want 
-->
<xsl:template match="text()"/>

<!-- 
	for test strings that have no <em> children, emit text nodes without any adornment 
-->
<xsl:template match="string/text()">
	<xsl:value-of select="."/>
</xsl:template>

<!-- 
	for test strings that have <em> children, emit text nodes dimmed 
-->
<xsl:template match="string/text()" mode="hasEM">
	<span class="dim"><xsl:value-of select="."/></span>
</xsl:template>

<!-- 
	for <em> children of test strings, emit the text nodes with no adornment 
-->
<xsl:template match="em/text()" mode="hasEM">
	<!-- <span class="bright"><xsl:value-of select="."/></span> -->
	<xsl:value-of select="."/>
</xsl:template>

</xsl:stylesheet>

