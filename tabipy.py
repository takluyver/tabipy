import sys
PY3 = sys.version_info[0] >= 3

try:
    from itertools import zip_longest  # Python 3
except ImportError:
    from itertools import izip_longest as zip_longest  # Python 2
from collections import Mapping

class TableCell(object):
    bg_colour = None
    
    def __init__(self, value, header=False, bg_colour=None, text_colour=None,
                 col_span=1):
        self.value = value
        self.header = header
        self.bg_colour = bg_colour
        self.text_colour = text_colour
        self.col_span = col_span
    
    def _make_css(self):
        rules = []
        if self.bg_colour:
            rules.append('background-color:%s' % self.bg_colour)
        if self.text_colour:
            rules.append('color:%s' % self.text_colour)
        return '; '.join(rules)
        
    def _check_span(self,val):
        "validate the span value"
        val = int(val)
        if val<1:
            er = "Row and columns spand must be greatter or equal to 1"
            raise(ValueError(er))
        return val
    
    @property
    def col_span(self):
        return self._col_span
    @col_span.setter
    def col_span(self,val):
        val = self._check_span(val)
        self._col_span = val
    
    def _repr_html_(self):
        tag = 'th' if self.header else 'td'
        spans = ''
        if self.col_span>1:
            spans += 'colspan="%s" '%self.col_span
        attrs = []
        style = self._make_css()
        if style:
            attrs.append('style="%s"'%style)
        return "<%s %s %s>%s</%s>"% (tag, spans,' '.join(attrs), self.value, 
                                     tag)

    def _repr_latex_(self):
        out = (str if PY3 else unicode)(self.value)
        # the bolf flag must only be next to the value of the cell not outside
        # of the multicolumn flag
        out = u"\\bf " + out if self.header else out
        text = "\multicolumn{%d}{l}{%s}"%(self.col_span, out)
        return text

class TableHeader(TableCell):
    def __init__(self, value, **kwargs):
       # header of a TableHeader is always True
       if 'header' in kwargs:
           del kwargs['header']
       super(TableHeader, self).__init__(value, header=True, **kwargs)

class TableRow(object):
    def  __init__(self, *cells):
        self.parent = None
        self.cells = []
        for c in cells:
            self.append_cell(c)
            
    @property
    def _current(self):
        ("This provides column information for the current row")
        count = 0
        current = []
        for index, c in enumerate(self.cells):
            if index == count:
                for col in range(c.col_span):
                    cs = c.col_span
                    current.append(cs)
                    count +=1
        return current

    def set_parent(self, parent):
        self.parent = parent
            
    def append_cell(self, c):
        if not isinstance(c, TableCell):
            c = TableCell(c)
        self.cells.append(c)

    def column_count(self):
        count = 0
        for index, c in enumerate(self.cells):
            if index == count:
                count += c.col_span
        return count
    
    def _repr_html_(self):
        # Note: Because of how a row is rendered, if a cell to the right of a
        # cell, with col_span greater than 1, contains content, that content 
        # will not be rendeded.  The content is not distroyed, just not rended.
        cur = self._current # Updates the current cells row span info
        html = '<tr>'
        index = 0      
        for count, c_col in enumerate(cur):
            if index == count:
                html += self.cells[index]._repr_html_()
                index += c_col
        html +='</tr>'
        return html


    def _repr_latex_(self):
        # Note: Because of how a row is rendered, if a cell to the right of a
        # cell, with col_span greater than 1, contains content, that content 
        # will not be rendeded.  The content is not distroyed, just not rended.
        cur = self._current # Updates the current cells row span info
        latex = ''
        index = 0
        for count, c_col in enumerate(cur):
            if index == count:
                _cell = self.cells[index]
                latex += _cell._repr_latex_() + ' & '
                index += c_col
        latex = latex.strip('& ')
        latex += '\\\\\n'
        return latex

class TableHeaderRow(TableRow):
    def append_cell(self, c):
        if not isinstance(c, TableCell):
            c = TableCell(c, header=True)
        self.cells.append(c)

    def set_parent(self, parent):
        super(TableHeaderRow, self).set_parent(parent)
        self.parent.has_header = True

    def _repr_latex_(self):
        return super(TableHeaderRow, self)._repr_latex_() + '\\hline\n'

class Table(object):
    def __init__(self, *rows):
        self.rows = []
        self.has_header = False

        # if argument is a single dict, convert it to a table with keys
        # as header
        if (len(rows) == 1) and isinstance(rows[0], Mapping):
            dict_arg = rows[0]
            new_rows = [TableHeaderRow(*dict_arg.keys())]
            new_rows.extend(zip_longest(*dict_arg.values(), fillvalue=''))
            rows = new_rows

        for r in rows:
            self.append_row(r)
    
    def append_row(self, r):
        if not isinstance(r, TableRow):
            r = TableRow(*r)
        r.set_parent(self)
        self.rows.append(r)
    
    def _repr_html_(self):
        return '<table>\n' + '\n'.join(r._repr_html_() for r in self.rows) + '\n</table>'

    def _repr_latex_(self):   
        out = '\n'.join(r._repr_latex_() for r in self.rows)
        if self.has_header:
            out = '\\hline\n' + out + '\\hline\n'
        return '\\begin{tabular}{*{%d}{l}}\n%s\\end{tabular}' % \
                        (self.rows[0].column_count(), out)

