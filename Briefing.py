

# needed?
from datetime import datetime, timedelta
from csv import *
import re
from cgi import escape
import pprint

# yes
from CustomEntry import *
from Article import *
from bs4 import BeautifulSoup
from urllib import urlopen

def detexify(str) :
    simpleEscaped = re.compile(r'\\([#$%&~_^{}|])')
    mathEscaped = re.compile(r'\$([<>])\$')
    str = mathEscaped.sub(r'\1', str)
    str = simpleEscaped.sub(r'\1', str)
    str = str.replace('\\textbacklash', '\\')
    return str
    
def hexColor(str) :
    return "#%02X%02X%02X" % tuple([int(num) for num in str.split()])

class Briefing :
    def __init__(self, cfg) : 
        self.date = datetime.now().strftime('%Y%m%d')
        self.cfg = cfg
        url = cfg.get("static", "briefingUrl")
        briefConn = urlopen(url)
        briefing = briefConn.read()

        soup = BeautifulSoup(briefing)
        self.entries = []
        entryFileName = cfg.get("static", "entriesFile")
        entryList = CustomEntry(entryFileName)
        todaysEntry = entryList.loadEntry()
        self.entries.append(todaysEntry)

        self.articles = []
        for item in  soup.findAll('item', limit=5) :
            self.articles.append(Article.from_item(item))

    def getFileName(self) :
        return "BriefingEmail" + self.date + ".html"

    def printBriefingHTML(self) :
        articles = self.articles
        cfg = self.cfg

        html = """
        <style>
        @media screen {
            .overflowEllipsis {
                display: none;
            }
        }
        @media print {
            table {
                font-size: 11px;
            }
            .articleBar {
                height: 20px;
            }
            .articleBar img {
                height: 19px;
                width: 24px;
            }
            .articleTitle {
                font-size: 12px !important;
            }
            .readMoreLink {
                display: none;
            }
            .articleBoxWrapper {
                padding-bottom: 10px;
            }
            .articleBoxWrapper.noTitle {
                padding-bottom: 18px;
            }
            .articleBox {
                max-height: 130px;
                overflow: hidden;
                position: relative;
            }
            .noTitle .articleBox {
                max-height:124px;
            }
            .overflowEllipsis {
                display: block;
                position: absolute;
                right: 15;
                bottom: 2;
                background-color: #f4f5f4;
                padding-left: 10px;
            }
            .noTitle .overflowEllipsis {
                bottom: 0;
            }
            .articleBoxTopSpacer {
                height: 5px;
            }
            .articleBoxBottomSpacer {
                display: none;
            }
        }
        </style>

        <table border="0" style="background-color:#FFFFFF; max-width: 960px; font-family: Calibri;" cellpadding="0" cellspacing="0">
            <tr><td>
                <!-- Header section table -->
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                        <td width="200" style="font-family: Calibri;">
                            """ + datetime.now().strftime('%B %d, %Y') + """<br/>
                            Daily Briefing: """ + cfg.get("static", "CVerb")  + " by " + cfg.get("static", "Compiler") +"""<br/>
                            <a href="https://briefing.nextjump.com/">Daily Briefing Site</a><br/>
                            <a href="https://wiki.nextjump.com/wiki/index.php/Daily_Briefing">Daily Briefing Wiki</a>
                        </td>
                        <td width="760" valign="middle" align="right">
                            <img src="https://imga.nxjimg.com/secured/image/briefing/dblogo.jpg" width="300" height="65">
                        </td>
                    </tr>
                    <tr height="10">
                    </tr>
                </table>
                <table border="0" cellpadding="0" cellspacing="0" width="100%">"""
                
        if len(self.entries) > 0 :
            if len(self.entries) == 1 :
                row = self.entries[0]
                html += """
                    <tr><!-- begin dp section -->
                        <td width="100%">
                            """ + row.getHTML(cfg) + """
                        </td>
                    </tr>"""
            else :
                row1 = self.entries[0]
                row2 = self.entries[1]
                html += """
                    <tr><!-- more than 1 daily practice -->
                        <td width="100%">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr valign="top">
                                    <td width="30%">""" + row1.getHTML(cfg) + """</td>
                                    <td width="2%"></td>
                                    <td width="68%">""" + row2.getHTML(cfg) + """ </td>
                                </tr>
                            </table>
                        </td>
                    </tr>"""


        for row in articles :
            html += """
                    <tr>
                        <td width="100%">
                        """ + row.getHTML(cfg) + """
                        </td>
                    </tr>"""
        html += """
                </table>
            <!-- Footer table-->
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr height="10">
                    </tr>
                    <tr>
                        <td align="center">
                            Want to get involved? Email comments, suggestions, and articles to Team Daily Briefing!
                        </td>
                    </tr>
                </table>
            </td></tr>
        </table>"""
        return html
