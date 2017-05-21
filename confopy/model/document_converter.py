# coding: utf-8
'''
File: document_converter.py
Author: Oliver Zscheyge
Description:
    Class for converting Document objects to other representations.
'''

from confopy.pdfextract.xml_util import escape
from lxml import etree

from confopy.model.document import Node, Float, Paragraph, Section, Chapter, Document, Meta, Footnote


XML_HEADER = "<?xml version=\"1.0\" encoding=\"utf-8\" ?>"
PRETTY_IDENT = "  "
EMPH_SEPARATOR = ","


class DocumentConverter(object):
    """Converts a Document to other representations (e.g. XML).
       Or the other way around.
    """
    def __init__(self):
        """Initializer.
        """
        super(DocumentConverter, self).__init__()

    def to_Documents(self, xml_paths):
        """Converts Confopy XML file(s) to a list of Documents.
        Args:
            xml_paths: Path of the XML file(s) to parse.
        Return:
            A list of Documents.
        """
        docs = list()
        if type(xml_paths) == list:
            for f in xml_paths:
                docs.expand(self.to_Documents(f))
        else:
            context = etree.iterparse(xml_paths, events=("end",), tag="document", encoding="utf-8")
            docs.extend(self._fast_iter(context, self._parse_xml_document))
            docs = [doc for doc in docs if doc != None]
        return docs

    def _parse_xml_document(self, node):
        if node.tag == "paragraph":
            pagenr = str(node.get("pagenr", ""))
            font = str(node.get("font", ""))
            fontsize = str(node.get("fontsize", ""))
            emph = str(node.get("emph", ""))
            emph = emph.split(EMPH_SEPARATOR)
            if len(emph) == 1 and emph[0] == "":
                emph = []
            text = str(node.text)
            return Paragraph(text=text, pagenr=pagenr, font=font, fontsize=fontsize, emph=emph)

        elif node.tag == "section":
            pagenr = str(node.get("pagenr", ""))
            title = str(node.get("title", ""))
            number = str(node.get("number", ""))
            children = [self._parse_xml_document(c) for c in node]
            return Section(pagenr=pagenr, title=title, number=number, children=children)

        elif node.tag == "float":
            pagenr = str(node.get("pagenr", ""))
            number = str(node.get("number", ""))
            text = str(node.text)
            return Float(pagenr=pagenr, number=number, text=text)

        elif node.tag == "footnote":
            pagenr = str(node.get("pagenr", ""))
            number = str(node.get("number", ""))
            text = str(node.text)
            return Footnote(pagenr=pagenr, number=number, text=text)

        elif node.tag == "chapter":
            pagenr = str(node.get("pagenr", ""))
            title = str(node.get("title", ""))
            number = str(node.get("number", ""))
            children = [self._parse_xml_document(c) for c in node]
            return Chapter(pagenr=pagenr, title=title, number=number, children=children)

        elif node.tag == "document":
            meta = None
            children = [self._parse_xml_document(c) for c in node]
            for c in children:
                if type(c) == Meta:
                    meta = c
            if meta:
                children.remove(meta)
            return Document(meta=meta, children=children)

        elif node.tag == "meta":
            title = ""
            authors = list()
            language = ""
            for c in node:
                if c.tag == "title":
                    title = str(c.text)
                elif c.tag == "author":
                    authors.append(str(c.text))
                elif c.tag == "language":
                    language = str(c.text)
            return Meta(title=title, authors=authors, language=language)

        return None

    def _fast_iter(self, context, func):
        buf = list()
        for event, elem in context:
            buf.append(func(elem))
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        del context
        return buf

    def to_XML(self, doc, pretty=False, linesep="", ident="", header=True):
        """Converts a Document to structure oriented XML.
        Args:
            doc:     The Document or part of a document or list of Documents
                     to convert.
            pretty:  If true: returns a human readable XML string.
                     Takes care of parameters linesep and ident automatically.
            linesep: Line seperator. Is overridden in case pretty is set.
            ident:   Ident for each line. Mainly used for recursion.
            header:  Place the XML header with version and encoding at the
                     beginning of the XML string.
        Return:
            Unicode string (XML markup).
        """
        if doc == None:
            return ""

        buf = list()
        if header:
            buf.append(XML_HEADER)
        if pretty:
            linesep = "\n"

        if type(doc) == list:
            buf.append("<documents>")
            for d in doc:
                buf.append(self.to_XML(d, linesep=linesep, ident=PRETTY_IDENT, header=False))
            buf.append("</documents>")

        elif type(doc) == Document:
            buf.append(ident + "<document>")
            if doc.meta:
                buf.append(self.to_XML(doc.meta, linesep=linesep, ident=ident + PRETTY_IDENT, header=False))
            for c in doc.children():
                buf.append(self.to_XML(c, linesep=linesep, ident=ident + PRETTY_IDENT, header=False))
            buf.append(ident + "</document>")

        elif type(doc) == Meta:
            buf.append(ident + "<meta>")
            if doc.title != "":
                title = "%s%s<title>%s</title>" % (ident, PRETTY_IDENT, escape(doc.title))
                buf.append(title)
            for author in doc.authors:
                author_xml = "%s%s<author>%s</author>" % (ident, PRETTY_IDENT, escape(author))
                buf.append(author_xml)
            if doc.language != "":
                lang = "%s%s<langauge>%s</language>" % (ident, PRETTY_IDENT, escape(doc.language))
                buf.append(lang)
            buf.append(ident + "</meta>")

        elif type(doc) == Section:
            buf.append("%s<section%s>" % (ident, self._section_attrs(doc)))
            for c in doc.children():
                buf.append(self.to_XML(c, linesep=linesep, ident=ident + PRETTY_IDENT, header=False))
            buf.append(ident + "</section>")

        elif type(doc) == Chapter:
            buf.append("%s<chapter%s>" % (ident, self._section_attrs(doc)))
            for c in doc.children():
                buf.append(self.to_XML(c, linesep=linesep, ident=ident + PRETTY_IDENT, header=False))
            buf.append(ident + "</chapter>")

        elif type(doc) == Paragraph:
            buf.append("%s<paragraph%s>" % (ident, self._paragraph_attrs(doc)))
            buf.append(escape(doc.text))
            buf.append(ident + "</paragraph>")

        elif type(doc) == Float:
            buf.append(ident + "%s<float%s>" % (ident, self._float_attrs(doc)))
            buf.append(escape(doc.text))
            buf.append(ident + "</float>")

        elif type(doc) == Footnote:
            buf.append(ident + "%s<footnote%s>" % (ident, self._float_attrs(doc)))
            buf.append(escape(doc.text))
            buf.append(ident + "</footnote>")

        return linesep.join(buf)

    def _section_attrs(self, sec):
        buf = list()
        if sec.number != "":
            buf.append(' number="%s"' % escape(sec.number))
        buf.append(' title="%s"' % escape(sec.title))
        if sec.pagenr != "":
            buf.append(' pagenr="%s"' % escape(sec.pagenr))
        return "".join(buf)

    def _paragraph_attrs(self, para):
        buf = list()
        if para.pagenr != "":
            buf.append(' pagenr="%s"' % escape(para.pagenr))
        if para.font != "":
            buf.append(' font="%s"' % escape(para.font))
        if para.fontsize != "":
            buf.append(' fontsize="%s"' % escape(para.fontsize))
        if len(para.emph) > 0:
            emph_str = EMPH_SEPARATOR.join(para.emph)
            if emph_str != "":
                buf.append(' emph="%s"' % escape(emph_str))
        return "".join(buf)

    def _float_attrs(self, flt):
        buf = list()
        if flt.number != "":
            buf.append(' number="%s"' % escape(flt.number))
        if flt.pagenr != "":
            buf.append(' pagenr="%s"' % escape(flt.pagenr))
        return "".join(buf)



if __name__ == '__main__':
    print("Test for %s" % __file__)

    print("  Building test document...")
    doc = Document()
    sec1 = Section(title="1. Foo")
    sec11 = Section(title="1.1 Bar")
    sec12 = Section(title="1.2 Baz")
    sec2 = Section(title="2. Raboof")
    para0 = Paragraph(text="Intro text")
    para1 = Paragraph(text="""\
Lorem ipsum dolor sit amet, consectetur adipiscing elit. In lacinia nec massa id interdum. Ut dolor mauris, mollis quis sagittis at, viverra ac mauris. Phasellus pharetra dolor neque, sit amet ultricies nibh imperdiet lobortis. Fusce ac blandit ex, eu feugiat eros. Etiam nec erat enim. Fusce at metus ac dui sagittis laoreet. Nulla suscipit nisl ut lacus viverra, a vestibulum est lacinia. Aliquam finibus urna nunc, nec venenatis mi dictum eget. Etiam vitae ante quis neque aliquam vulputate id sit amet massa. Pellentesque elementum sapien non mauris laoreet cursus. Pellentesque at mauris id ipsum viverra egestas. Sed nec volutpat metus, vel sollicitudin ante. Pellentesque interdum justo vel ullamcorper dictum. Phasellus volutpat nibh eget arcu venenatis, a bibendum lorem mattis. Quisque in laoreet leo.""")
    para2 = Paragraph(text="Tabelle 1 zeigt Foobar.")
    floatA = Float(text="Tabelle 1: Foo bar.")
    floatB = Float(text="Tabelle 2: Foo bar baz bat.")

    sec11.add_child(para1)
    sec11.add_child(floatA)
    sec11.add_child(para2)
    sec12.add_child(floatB)
    sec1.add_child(sec11)
    sec1.add_child(sec12)
    doc.add_child(para0)
    doc.add_child(sec1)
    doc.add_child(sec2)

    print("  Testing Document2XML conversion...")
    doc_conv = DocumentConverter()
    xml = doc_conv.to_XML(doc, True)
    xml_expected = '<?xml version="1.0" encoding="utf-8" ?>\n<document>\n  <paragraph>\nIntro text\n  </paragraph>\n  <section title="1. Foo">\n    <section title="1.1 Bar">\n      <paragraph>\nLorem ipsum dolor sit amet, consectetur adipiscing elit. In lacinia nec massa id interdum. Ut dolor mauris, mollis quis sagittis at, viverra ac mauris. Phasellus pharetra dolor neque, sit amet ultricies nibh imperdiet lobortis. Fusce ac blandit ex, eu feugiat eros. Etiam nec erat enim. Fusce at metus ac dui sagittis laoreet. Nulla suscipit nisl ut lacus viverra, a vestibulum est lacinia. Aliquam finibus urna nunc, nec venenatis mi dictum eget. Etiam vitae ante quis neque aliquam vulputate id sit amet massa. Pellentesque elementum sapien non mauris laoreet cursus. Pellentesque at mauris id ipsum viverra egestas. Sed nec volutpat metus, vel sollicitudin ante. Pellentesque interdum justo vel ullamcorper dictum. Phasellus volutpat nibh eget arcu venenatis, a bibendum lorem mattis. Quisque in laoreet leo.\n      </paragraph>\n            <float>\nTabelle 1: Foo bar.\n      </float>\n      <paragraph>\nTabelle 1 zeigt Foobar.\n      </paragraph>\n    </section>\n    <section title="1.2 Baz">\n            <float>\nTabelle 2: Foo bar baz bat.\n      </float>\n    </section>\n  </section>\n  <section title="2. Raboof">\n  </section>\n</document>'
    assert xml == xml_expected

    xml = doc_conv.to_XML(doc, False)
    xml_expected = '<?xml version="1.0" encoding="utf-8" ?><document>  <paragraph>Intro text  </paragraph>  <section title="1. Foo">    <section title="1.1 Bar">      <paragraph>Lorem ipsum dolor sit amet, consectetur adipiscing elit. In lacinia nec massa id interdum. Ut dolor mauris, mollis quis sagittis at, viverra ac mauris. Phasellus pharetra dolor neque, sit amet ultricies nibh imperdiet lobortis. Fusce ac blandit ex, eu feugiat eros. Etiam nec erat enim. Fusce at metus ac dui sagittis laoreet. Nulla suscipit nisl ut lacus viverra, a vestibulum est lacinia. Aliquam finibus urna nunc, nec venenatis mi dictum eget. Etiam vitae ante quis neque aliquam vulputate id sit amet massa. Pellentesque elementum sapien non mauris laoreet cursus. Pellentesque at mauris id ipsum viverra egestas. Sed nec volutpat metus, vel sollicitudin ante. Pellentesque interdum justo vel ullamcorper dictum. Phasellus volutpat nibh eget arcu venenatis, a bibendum lorem mattis. Quisque in laoreet leo.      </paragraph>            <float>Tabelle 1: Foo bar.      </float>      <paragraph>Tabelle 1 zeigt Foobar.      </paragraph>    </section>    <section title="1.2 Baz">            <float>Tabelle 2: Foo bar baz bat.      </float>    </section>  </section>  <section title="2. Raboof">  </section></document>'
    assert xml == xml_expected

    print("Passed all tests!")
