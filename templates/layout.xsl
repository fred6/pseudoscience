<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" doctype-system="about:legacy-compat" encoding="UTF-8" indent="yes" omit-xml-declaration="yes"/>

    <xsl:template match="/">
        <html>
            <head>
                <meta>
                    <xsl:attribute name="charset">
                        <xsl:value-of select="'utf-8'"/>
                    </xsl:attribute>
                </meta>
                <title>
                    <xsl:value-of select="/root/title"/>
                </title>
                <link>
                    <xsl:attribute name="href">
                        <xsl:value-of select="'style.css'"/>
                    </xsl:attribute>
                    <xsl:attribute name="rel">
                        <xsl:value-of select="'stylesheet'"/>
                    </xsl:attribute>
                    <xsl:attribute name="type">
                        <xsl:value-of select="'text/css'"/>
                    </xsl:attribute>
                </link>
                <xsl:comment>
                    <![CDATA[[if lt IE 9]>
                    <script src="//html5shiv.googlecode.com/svn/trunk/html5.js"></script>
                    <![endif]]]>
                </xsl:comment>
            </head>
            <body>
                <h1>
                    <xsl:attribute name="id">
                        <xsl:value-of select="'page_title'"/>
                    </xsl:attribute>
                    <a>
                        <xsl:attribute name="href">
                            <xsl:value-of select="'index.html'"/>
                        </xsl:attribute>
                        <xsl:value-of select="/root/title"/>
                    </a>
                </h1>
                    <div>
                        <xsl:attribute name="id">
                            <xsl:value-of select="'container'"/>
                        </xsl:attribute>
                        <xsl:copy-of select="/root/content/*"/>
                    </div>
            </body>

        </html>
    </xsl:template>
</xsl:stylesheet>

