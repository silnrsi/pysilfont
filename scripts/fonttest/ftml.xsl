<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="utf-8"/>

<xsl:template match="/">
<xsl:variable name="width-comment" select="/ftml/head/columns/@comment"/>
<xsl:variable name="width-label" select="/ftml/head/columns/@label"/>
<xsl:variable name="width-string" select="/ftml/head/columns/@string"/>
<!-- The following sets font-scale to /ftml/head/fontscale or else 100 if /ftml/head/fontscale doesn't exist. -->
<xsl:variable name="font-scale" select="concat(/ftml/head/fontscale, substring('100', 1 div not(/ftml/head/fontscale)))"/>
<html>
<head>
<title><xsl:value-of select="ftml/head/title"/></title>
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
 table { width: 100%; table-layout: fixed; padding: 2px; border: 1px solid; border-collapse: collapse; }
 <xsl:if test="$width-label != ''">
 col.label { width: <xsl:value-of select="$width-label"/>; padding: 2px; border: 1px solid; border-collapse: collapse; }
 </xsl:if>
 <xsl:if test="$width-string != ''">
 td.string, col.string {width: <xsl:value-of select="$width-string"/>; font: <xsl:value-of select="$font-scale"/>% TestFont; padding: 2px; border: 1px solid; border-collapse: collapse;}
 </xsl:if>
 <xsl:if test="$width-comment != ''">
 col.comment {width: <xsl:value-of select="$width-comment"/>; padding: 2px; border: 1px solid; border-collapse: collapse;}
 </xsl:if>
 <xsl:for-each select="/ftml/head/styles/style">
 .<xsl:value-of select="@name"/> {
 font: <xsl:value-of select="$font-scale"/>% TestFont; 
 lang="<xsl:value-of select="@lang"/>";
 -moz-font-feature-settings: <xsl:value-of select="@feats"/> ; 
 -ms-font-feature-settings: <xsl:value-of select="@feats"/> ; 
 -webkit-font-feature-settings: <xsl:value-of select="@feats"/> ; 
 font-feature-settings: <xsl:value-of select="@feats"/> ; 
 padding: 2px; border: 1px solid; border-collapse: collapse; }
 </xsl:for-each>
 .tableform { padding: 2px; border: 1px solid; border-collapse: collapse; }
</style>
</head>
<body>
<h1><xsl:value-of select="/ftml/head/title"/></h1>
<xsl:for-each select="/ftml/testgroup">
 <h2><xsl:value-of select="@label"/></h2>
 <table>
 <colgroup>
  <xsl:if test="$width-label != ''">
  <col class="label"/>
  </xsl:if>
  <xsl:if test="$width-string != ''">
  <col class="string"/>
  </xsl:if>
  <xsl:if test="$width-comment != ''">
  <col class="comment"/>
  </xsl:if>
 </colgroup>
 <thead>
 <tr>
 <xsl:if test="$width-label != ''">
 <th>label</th>
 </xsl:if>
 <xsl:if test="$width-string != ''">
 <th>string</th>
 </xsl:if>
 <xsl:if test="$width-comment != ''">
 <th>comment</th>
 </xsl:if>
 </tr>
 </thead>
 <tbody>
 <xsl:for-each select="test">
  <tr><xsl:if test="@background"><xsl:attribute name="style">background-color: <xsl:value-of select="@background"/>;</xsl:attribute></xsl:if>
  <xsl:if test="$width-label != ''">
  <td class="tableform"><xsl:value-of select="@label"/></td>
  </xsl:if>
  <xsl:if test="$width-string != ''">
  <td class="tableform"><xsl:attribute name="class"><xsl:value-of select="concat(@class, substring('string', 1 div not(@class)))"/></xsl:attribute>
  <xsl:value-of select="string"/></td>
  </xsl:if>
  <xsl:if test="$width-comment != ''">
  <td class="tableform"><xsl:value-of select="comment"/></td>
  </xsl:if>
  </tr>
 </xsl:for-each>
 </tbody>
 </table>
</xsl:for-each>
</body>
</html>
</xsl:template>
</xsl:stylesheet>

