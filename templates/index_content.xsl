<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output omit-xml-declaration="yes"/>
    <xsl:template match="/">
        <div>
            <xsl:attribute name="id">
                <xsl:value-of select="'index'"/>
            </xsl:attribute>
            <ul>
                <xsl:for-each select="/pages/page">
                    <li>
                        <a>
                            <xsl:attribute name="href">
                                <xsl:value-of select="concat(name, '.html')"/>
                            </xsl:attribute>
                            <xsl:value-of select="name"/>
                        </a>
                    </li>
                </xsl:for-each>
            </ul>
        </div>
    </xsl:template>
</xsl:stylesheet>

