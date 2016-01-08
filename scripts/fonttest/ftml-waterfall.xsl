<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="utf-8"/>

<!-- set variables from head element -->
<xsl:variable name="width-class" select="/ftml/head/columns/@class"/>
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
				<xsl:value-of select="ftml/head/comment"/>
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
<xsl:if test="$width-class != ''">
	.class {width: <xsl:value-of select="$width-class"/>}
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
	Process a testgroup, emitting a waterfall display for each test element
-->
<xsl:template match="testgroup">
	<h2><xsl:value-of select="@label"/></h2>
   	<xsl:apply-templates/>
</xsl:template>

<!-- 
	Process a single test record, emitting a series of waterfall lines (<p> elements with increasing point sizes)
-->
<xsl:template match="test">http://on.aol.com/video/-sliders--stealing-from-gas-station-customers-in-plain-sight-517891804
    <h3><xsl:value-of select="@label"/></h3>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">8</xsl:with-param></xsl:call-template>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">9</xsl:with-param></xsl:call-template>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">10</xsl:with-param></xsl:call-template>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">11</xsl:with-param></xsl:call-template>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">12</xsl:with-param></xsl:call-template>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">13</xsl:with-param></xsl:call-template>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">14</xsl:with-param></xsl:call-template>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">16</xsl:with-param></xsl:call-template>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">18</xsl:with-param></xsl:call-template>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">20</xsl:with-param></xsl:call-template>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">22</xsl:with-param></xsl:call-template>
    <xsl:call-template name="waterfallline"><xsl:with-param name="ptsize">24</xsl:with-param></xsl:call-template>
</xsl:template>


<!-- 
	Emit html for one line of waterfall data
-->
<xsl:template name="waterfallline">
    <xsl:param name="ptsize">8</xsl:param>
		<p class="string">   <!-- assume default string class -->
			<xsl:variable name="styleName" select="@class"/>
			<xsl:if test="$styleName != ''">
    			<!-- emit lang attribute -->
			    <xsl:apply-templates select="/ftml/head/styles/style[@name=$styleName]" mode="getLang"/>
			</xsl:if>
			<xsl:if test="@rtl='True' ">
                <xsl:attribute name="dir">RTL</xsl:attribute>
			</xsl:if>
			<!-- emit style attribute with features and font-size -->
        	<xsl:attribute name="style">
			<xsl:if test="$styleName != ''">
                <xsl:apply-templates select="/ftml/head/styles/style[@name=$styleName]" mode="getFeats"/>
			</xsl:if>
font-size: <xsl:value-of select="$ptsize * $font-scale div 100"/>pt; line-height: 0.9;
            </xsl:attribute>
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
		</p>
</xsl:template>

<!-- 
	Emit html lang attribute
-->
<xsl:template match="style" mode="getLang">
	<xsl:if test="@lang">
		<xsl:attribute name="lang">
			<xsl:value-of select="@lang"/>
		</xsl:attribute>
	</xsl:if>
</xsl:template>

<!-- 
	Emit html feature-settings (to add to style attribute)
-->
<xsl:template match="style" mode="getFeats">
	<xsl:if test="@feats">
-moz-font-feature-settings: <xsl:value-of select="@feats"/>;
-ms-font-feature-settings: <xsl:value-of select="@feats"/>;
-webkit-font-feature-settings: <xsl:value-of select="@feats"/>;
font-feature-settings: <xsl:value-of select="@feats"/>;
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

