#!/usr/bin/env python
# coding: utf-8

"""
    A clean reStructuredText html writer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    It will produce a minimal set of html output.
    (No extry divs, classes oder ids.)
    
    Some code stolen from:
    http://www.arnebrodowski.de/blog/write-your-own-restructuredtext-writer.html
    https://github.com/alex-morega/docutils-plainhtml/blob/master/plain_html_writer.py
    
    :copyleft: 2011 by python-creole team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import warnings


try:
    from docutils.core import publish_parts
except ImportError:
    REST_INSTALLED = False
    warnings.warn(
        "Markup error: 'Python Documentation Utilities' isn't installed. Can't use reStructuredText."
        " Download: http://pypi.python.org/pypi/docutils"
    )
else:
    REST_INSTALLED = True


from docutils.writers import html4css1


DEBUG = False
#DEBUG = True

IGNORE_ATTR = (
    "class", "frame", "rules",
)
IGNORE_TAGS = (
    "div",
)


class CleanHTMLWriter(html4css1.Writer):
    """
    This docutils writer will use the CleanHTMLTranslator class below.
    """
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = CleanHTMLTranslator


class CleanHTMLTranslator(html4css1.HTMLTranslator, object):
    """
    Clean html translator for docutils system.
    """
    def _do_nothing(self, node, *args, **kwargs):
        pass

    def starttag(self, node, tagname, suffix='\n', empty=0, **attributes):
        """
        create start tag with the filter IGNORE_TAGS and IGNORE_ATTR.
        """
#        return super(CleanHTMLTranslator, self).starttag(node, tagname, suffix, empty, **attributes)
#        return "XXX%r" % tagname

        if tagname in IGNORE_TAGS:
            if DEBUG:
                print "ignore tag %r" % tagname
            return ""

        parts = [tagname]
        for name, value in sorted(attributes.items()):
            # value=None was used for boolean attributes without
            # value, but this isn't supported by XHTML.
            assert value is not None

            name = name.lower()

            if name in IGNORE_ATTR:
                continue

            if isinstance(value, list):
                values = [unicode(v) for v in value]
                parts.append('%s="%s"' % (name.lower(),
                                          self.attval(' '.join(values))))
            else:
                parts.append('%s="%s"' % (name.lower(),
                                          self.attval(unicode(value))))

        if DEBUG:
            print "Tag %r - ids: %r - attributes: %r - parts: %r" % (
                tagname, getattr(node, "ids", "-"), attributes, parts
            )

        if empty:
            infix = ' /'
        else:
            infix = ''
        html = '<%s%s>%s' % (' '.join(parts), infix, suffix)
        if DEBUG:
            print "startag html: %r" % html
        return html

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1

    set_class_on_child = _do_nothing
    set_first_last = _do_nothing

    # remove <blockquote> (e.g. in nested lists)
    visit_block_quote = _do_nothing
    depart_block_quote = _do_nothing

    # set only html_body, we used in rest2html() and don't surround it with <div>
    def depart_document(self, node):
        self.html_body.extend(self.body_prefix[1:] + self.body_pre_docinfo
                              + self.docinfo + self.body
                              + self.body_suffix[:-1])
        assert not self.context, 'len(context) = %s' % len(self.context)


    #__________________________________________________________________________
    # Clean table:

    visit_thead = _do_nothing
    depart_thead = _do_nothing
    visit_tbody = _do_nothing
    depart_tbody = _do_nothing

    def visit_table(self, node):
        self.body.append(self.starttag(node, 'table'))

    def visit_tgroup(self, node):
        node.stubs = []

    def visit_field_list(self, node):
        super(CleanHTMLTranslator, self).visit_field_list(node)
        if "<col" in self.body[-1]:
            del(self.body[-1])

    def depart_field_list(self, node):
        self.body.append('</table>\n')
        self.compact_field_list, self.compact_p = self.context.pop()

    def visit_docinfo(self, node):
        self.body.append(self.starttag(node, 'table'))

    def depart_docinfo(self, node):
        self.body.append('</table>\n')


def rest2html(content):
    """
    Convert reStructuredText markup to clean html code: No extra div, class or ids.
    
    >>> rest2html(u"- bullet list")
    u'<ul>\\n<li>bullet list</li>\\n</ul>\\n'
    """
    parts = publish_parts(
        source=content,
        writer=CleanHTMLWriter(),
        settings_overrides={
            "input_encoding": "unicode",
            "doctitle_xform": False,
        },
    )
#    import pprint
#    pprint.pprint(parts)
    return parts["html_body"] # Don't detache the first heading


if __name__ == '__main__':
    import doctest
    print doctest.testmod()

#    print rest2html(u"""
#+------------+------------+
#| Headline 1 | Headline 2 |
#+============+============+
#| cell one   | cell two   |
#+------------+------------+
#    """)

#    print rest2html(u"""
#:homepage:
#  http://code.google.com/p/python-creole/
#
#:sourcecode:
#  http://github.com/jedie/python-creole
#    """)

    print rest2html(u"""
===============
Section Title 1
===============

---------------
Section Title 2
---------------

Section Title 3
===============

Section Title 4
---------------

Section Title 5
```````````````

Section Title 6
'''''''''''''''
    """)