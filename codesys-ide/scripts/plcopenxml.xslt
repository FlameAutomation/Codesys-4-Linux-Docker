<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:po="http://www.plcopen.org/xml/tc6_0200">

<!--
 | Parse POU start tags
-->
<xsl:template match="po:pou[@pouType='functionBlock']">

<xsl:text>
-------------------------------------------------------------------------------
</xsl:text>
<xsl:value-of select="@name" />
<xsl:text>
-------------------------------------------------------------------------------
</xsl:text>
<xsl:call-template name="trim">
<xsl:with-param name="input" select="po:interface/po:documentation"/>
</xsl:call-template>
<xsl:text>

</xsl:text>
      <xsl:text>FUNCTION_BLOCK </xsl:text><xsl:value-of select="@name" />
      <xsl:apply-templates select="po:interface"/>
      <xsl:apply-templates select="po:body"/>
      <xsl:apply-templates select="po:addData/po:data/po:Method"/>
</xsl:template>



<xsl:template match="po:pou[@pouType='program']">
<xsl:text>
-------------------------------------------------------------------------------
</xsl:text>
<xsl:value-of select="@name" />
<xsl:text>
-------------------------------------------------------------------------------
</xsl:text>
<xsl:call-template name="trim">
<xsl:with-param name="input" select="po:interface/po:documentation"/>
</xsl:call-template>
<xsl:text>

</xsl:text>
      <xsl:text>PROGRAM </xsl:text><xsl:value-of select="@name" />
      <xsl:apply-templates select="po:interface"/>
      <xsl:apply-templates select="po:body"/>
</xsl:template>



<xsl:template match="po:Method">
<xsl:text>
-------------------------------------------------------------------------------
</xsl:text>
<xsl:value-of select="@name" />
<xsl:text>
-------------------------------------------------------------------------------
</xsl:text>
<xsl:call-template name="trim">
<xsl:with-param name="input" select="po:interface/po:documentation"/>
</xsl:call-template>
<xsl:text>

</xsl:text>
<xsl:text>METHOD </xsl:text><xsl:value-of select="@name" />
      <xsl:text>: </xsl:text>
      <xsl:apply-templates select="*/po:returnType"/>
      <xsl:apply-templates select="po:interface"/>
      <xsl:apply-templates select="po:body"/>
</xsl:template>

<!--
 | Parse POU body
-->
<xsl:template match="po:body">
      <xsl:apply-templates select="*|@*"/>
</xsl:template>


<!--
 | Parse Interface (also finish the start tag, to be able to set "EXTENDS" or "IMPLEMENTS".
-->
<xsl:template match="po:interface">
      <xsl:if test="po:addData/po:data/po:Inheritance/po:Extends">
      	      <xsl:text> EXTENDS </xsl:text>
	      <xsl:value-of select="po:addData/po:data/po:Inheritance/po:Extends"/>
      </xsl:if>
      <xsl:text>
</xsl:text>
      <xsl:apply-templates select="po:localVars|po:tempVars|po:inputVars|po:outputVars|po:inOutVars|po:externalVars|po:globalVars"/>
</xsl:template>

<!--
 | Variables (Part of the interface)
-->
<xsl:template match="po:localVars">
  <xsl:text>
VAR
</xsl:text>
      <xsl:apply-templates select="po:variable"/>
      <xsl:text>END_VAR
</xsl:text>
</xsl:template>
<xsl:template match="po:tempVars">
  <xsl:text>
VAR_TEMP
</xsl:text>
      <xsl:apply-templates select="po:variable"/>
      <xsl:text>END_VAR
</xsl:text>
</xsl:template>
<xsl:template match="po:inputVars">
  <xsl:text>
VAR_INPUT
</xsl:text>
      <xsl:apply-templates select="po:variable"/>
      <xsl:text>END_VAR
</xsl:text>
</xsl:template>
<xsl:template match="po:outputVars">
  <xsl:text>
VAR_OUTPUT
</xsl:text>
      <xsl:apply-templates select="po:variable"/>
      <xsl:text>END_VAR
</xsl:text>
</xsl:template>
<xsl:template match="po:inOutVars">
  <xsl:text>
VAR_INOUT
</xsl:text>
      <xsl:apply-templates select="po:variable"/>
      <xsl:text>
END_VAR
</xsl:text>
</xsl:template>
<xsl:template match="po:externalVars">
  <xsl:text>
VAR_EXTERNAL
</xsl:text>
      <xsl:apply-templates select="po:variable"/>
      <xsl:text>END_VAR
</xsl:text>
</xsl:template>
<xsl:template match="po:globalVars">
  <xsl:text>
VAR_GLOBAL
</xsl:text>
      <xsl:apply-templates select="po:variable"/>
      <xsl:text>END_VAR
</xsl:text>
</xsl:template>

<xsl:template match="po:variable">
<xsl:text>    </xsl:text>
<xsl:if test="@name">
      <xsl:value-of select="@name"/>
      <xsl:text>: </xsl:text>
      <xsl:apply-templates select="po:type"/>
      <xsl:text>;
</xsl:text>
</xsl:if>
</xsl:template>

<xsl:template match="po:type|po:baseType|po:returnType">
      <xsl:if test="po:derived">
	      <xsl:value-of select="po:derived/@name"/>
      </xsl:if>
      <xsl:if test="po:array">
      	      <xsl:text>ARRAY [</xsl:text>
	      <xsl:value-of select="po:array/dimension/@lower"/>
      	      <xsl:text>..</xsl:text>
	      <xsl:value-of select="po:array/dimension/@upper"/>
      	      <xsl:text>] OF </xsl:text>
	      <xsl:apply-templates select="po:baseType"/>
      </xsl:if>
      <xsl:if test="not(po:derived) and not(po:array) and not(po:struct)">
	      <xsl:value-of select="name(*[1])"/>
      </xsl:if>
</xsl:template>


<!--
 | Implement the presentation of the different languages
-->
<xsl:template match="po:ST">
      <xsl:value-of select="*[1]"/>
</xsl:template>

<xsl:template name="trim">
        <xsl:param name="input"/>
        <xsl:choose>
                <xsl:when test="starts-with($input,' ')">
                        <xsl:call-template name="trim">
                                <xsl:with-param name="input" select="substring-after($input,' ')"/>
                        </xsl:call-template>
                </xsl:when>
                <xsl:when test="substring($input, string-length($input) ) = ' ' ">
                        <xsl:call-template name="trim">
                                <xsl:with-param name="input" select="substring($input, 1,
string-length($input)-1)"/>
                        </xsl:call-template>
                </xsl:when>
                <xsl:otherwise>
                        <xsl:value-of select="$input"/>
                </xsl:otherwise>
        </xsl:choose>
</xsl:template>
<!--
 | Fetch and ignore rest
-->
<xsl:template match="*|@*">
      <xsl:apply-templates select="*|@*"/>
</xsl:template>

</xsl:stylesheet>
	

	
