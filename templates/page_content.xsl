<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output omit-xml-declaration="yes"/>
    <xsl:template match="/">
        <div>
            <xsl:attribute name="id">
                <xsl:value-of select="'page'"/>
            </xsl:attribute>
            <header>
                <xsl:value-of select="page/name"/>
            </header>
            <div>
                <xsl:value-of select="page/content"/>
            </div>
        </div>
    </xsl:template>
</xsl:stylesheet>

