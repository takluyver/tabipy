import re
import sys
import warnings
from collections import OrderedDict as Dict
PY3 = sys.version_info[0] >= 3

try:
    from itertools import zip_longest  # Python 3
except ImportError:
    from itertools import izip_longest as zip_longest  # Python 2
from collections import Mapping

class TableCell(object):
    bg_colour = None
    _latex_escape_table = {'&': r'\&',
                           '\\': r'{\textbackslash}',
                           '~': r'{\textasciitilde}',
                           '$': '\$',
                           '\r\n': r'{\linebreak}',
                           '\n': r'{\linebreak}',
                           '\r': r'{\linebreak}',
                           '_': r'\_',
                           '{': '\{',
                           '}': '\}'}
    _latex_escape_re = None
    
    def __init__(self, value, header=False, bg_colour=None, text_colour=None,
                 row_span=1, col_span=1):
        self.value = value
        self.header = header
        self.bg_colour = bg_colour
        self.text_colour = text_colour
        self.row_span = row_span
        self.col_span = col_span
        self._suppress = False
        # initialize regex for escaping to latex code
        if self._latex_escape_re is None:
            self._latex_escape_re = re.compile('|'.join(map(re.escape, 
                                        sorted(self._latex_escape_table.keys(),
                                               key=len, reverse=True))))
    def _defaults_(self):
        defaults = Dict([('value',('','self.value')),
                         ('header',(False,'self.header')),
                         ('bg_colour',(None,'self.bg_colour')),
                         ('text_colour',(None,'self.text_colour')),
                         ('row_span',(1,'self.row_span')),
                         ('col_span',(1,'self.col_span'))])
        return defaults
    
    def _latex_escape_func(self, match): 
        """Replace regex match with latex equivalent"""
        return self._latex_escape_table[match.group()]
        
    def __repr__(self):
        val = "'%s'"%self.value if type(self.value)==str else self.value
        text = "TableCell({}".format(val)
        for key, values in self._defaults_().items():
            if key == 'value':
                continue
            default, txt_actual = values
            current = eval(txt_actual)
            if default!=current:
                text += ', {}={}'.format(key,current)
        text += ')'
        return text
    
    def _make_css(self):
        rules = []
        if self.bg_colour:
            rules.append('background-color:%s' % self.bg_colour)
        if self.text_colour:
            rules.append('color:%s' % self.text_colour)
        return '; '.join(rules)
        
    def _check_span(self,val):
        "Validate the span value."
        val = int(val)
        if val<1:
            er = "Row and columns spand must be greater or equal to 1"
            raise(ValueError(er))
        return val
        
    @property
    def row_span(self):
        return self._row_span
    @row_span.setter
    def row_span(self,val):
        val = self._check_span(val)
        self._row_span = val
        
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
        if self.row_span>1:
            spans += 'rowspan="%s"'%self.row_span
        attrs = []
        style = self._make_css()
        if style:
            attrs.append('style="%s"'%style)
        return "<%s %s %s>%s</%s>"% (tag, spans,' '.join(attrs), self.value, 
                                     tag)

    def _repr_latex_(self):
        out = (str if PY3 else unicode)(self.value)
        out = self._latex_escape_re.sub(self._latex_escape_func, out)
        # the bolf flag must only be next to the value of the cell not outside
        # of the multicolumn flag
        if self._suppress: # For hiding cell content when using multicolumn
            out = ''
        elif self.header:
            out = u"\\bf " + out
        if self.row_span>1:
            warn_txt = ('Must use multirow package in the .tex file, \n e.g.'
            r' "\usepackage{multirow} % to support multiple rows"')
            warnings.warn(warn_txt)
            text_row = "\multirow{%d}{*}{%s}"%(self.row_span,out)  
        else:
            text_row = out
        if self.col_span>1:
            text = "\multicolumn{%d}{l}{%s}"%(self.col_span, text_row)
        else:
            text = text_row    
#         text = "\multicolumn{%d}{l}{%s}"%(self.col_span, text_row)
        return text

class TableHeader(TableCell):
    def __init__(self, value, **kwargs):
       # header of a TableHeader is always True
       if 'header' in kwargs:
           del kwargs['header']
       super(TableHeader, self).__init__(value, header=True, **kwargs)

class TableRow(object):
    def  __init__(self, *cells, **kwargs):
        self.parent = None
        self.max_len = kwargs.get('max_len',None)
        self.cells = []
        for c in cells:
            self.append_cell(c)
        if self.max_len is not None:
            cur_len = self.column_count()
            if cur_len < self.max_len:
                for c in range(self.max_len - cur_len):
                    self.append_cell('')
            
    @property
    def _current(self):
        """This provides column and rowspan information for the following row

        If the row above spans into the current row it decrements the row 
        span value from the row above.  This also updates the current row's 
        cell's row_span information to reflect any correction based on the 
        previous row."""
        decp_a = []
        if len(self._above)>0:
            for r, c in self._above:
                decp_a += [(r,c)]
        else:
            decp_a = [(1,1) for c in range(self.column_count())]
        count = 0
        current = []
        for index, c in enumerate(self.cells):
            if index == count:
                for col in range(c.col_span):
                    row_above, col_above = decp_a[count]
                    rs = c.row_span if row_above==1 else row_above-1
                    cs = c.col_span if row_above==1 else col_above
                    current.append([rs, cs])
                    count +=1
        return current

    def set_parent(self, parent):
        self.parent = parent
            
    def append_cell(self, c):
        if not isinstance(c, TableCell):
            c = TableCell(c)
        if c.col_span>1:
            self.cells.append(c)
            index = self.column_count()
            blanks = c.col_span -1
            if self.max_len is not None:
                m_l = self.max_len
                new_len = index + blanks
                count = m_l - index if new_len > self.max_len else blanks
            else:
                count = blanks
            for blank in range(count):
                self.cells.append(TableCell(''))
        else:
            self.cells.append(c)

    def column_count(self, debug=False):
        count = 0
        for index, c in enumerate(self.cells):
            if debug:
                print('index = {}, value = "{}", col_span = {}'.format(index,
                                                                     c.value,
                                                                     c.col_span))
            if index == count:
                count += c.col_span
        return count
    
    def _repr_html_(self):
        # Note: Because of how a row is rendered, if a cell to the right of a
        # cell, with col_span greater than 1, contains content, that content 
        # will not be rendeded.  The content is not distroyed, just not rended.
        cur = self._current # Updates the current cells row span info
        abv = [[1,1] for c in cur] if len(self._above)==0 else self._above
        html = '<tr>'
        index = 0      
        for count, values in enumerate(zip(abv,cur)):
            (a_row, a_col), (c_row, c_col) = values
            if index == count:
                if a_row==1:
                    html += self.cells[index]._repr_html_()
                    index += c_col
                else:
                    index += a_col
        html +='</tr>'
        return html

    def _repr_latex_(self):
        # Note: Because of how a row is rendered, if a cell to the right of a
        # cell, with col_span greater than 1, contains content, that content 
        # will not be rendeded.  The content is not distroyed, just not rended.
        cur = self._current # Updates the current cells row span info
        abv = [[1,1] for c in cur] if len(self._above)==0 else self._above
        latex = ''
        index = 0
        for count, values in enumerate(zip(abv,cur)):
            (a_row, a_col), (c_row, c_col) = values
            if index == count:
                if index != 0:
                    latex += ' & '
                _cell = self.cells[index]
                if a_row==1:
                    latex += _cell._repr_latex_()
                    index += c_col
                else:
                    # For cells not being rendered, their status need to be  
                    # temporarily changed to suppress output and reflec the 
                    # previous row's column span.
                    _cell._suppress = True
                    tmp, _cell._col_span = _cell._col_span, a_col
                    latex += _cell._repr_latex_()
                    _cell._col_span = tmp
                    _cell._suppress = False
                    index += a_col
        latex += '\\\\'#\n'
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
        return super(TableHeaderRow, self)._repr_latex_() + '\\\nhline'

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
        max_len = None
        for index, r in enumerate(rows):
        
            self.append_row(r, max_len)
            if index==0:
                max_len = self.rows[0].column_count()
            
    def cell(self, row, col):
        """Allows for direct addressing of individual cells (row, column)

        Any value not entered will remain unchanged.
        Address is (row, column) with an origin index of 0."""
        Row = self.rows[row]
        cell = Row.cells[col]
        return cell
    
    def append_row(self, r, max_len=None):
        if not isinstance(r, TableRow):
            r = TableRow(*r, max_len=max_len)
        r.set_parent(self)
        self.rows.append(r)
    
    def _repr_html_(self):
        html = '<table>\n' 
        above = []
        for row in self.rows:
            row._above = above
            html += row._repr_html_() + '\n'
            above = row._current # Should this be passed back by the repr?
        html += '</table>'
        return html

    def _repr_latex_(self):   
        latex = '\\begin{tabular}{*{%d}{l}}\n'%self.rows[0].column_count()
        # Top horizontal line of table
        latex += r'\hline' + '\n' if self.has_header else ''
        above = []
        # Fill table contents
        for row in self.rows:
            row._above = above
            latex += row._repr_latex_() + '\n'
            above = row._current
        #Bottom horizontal line of table
        latex += r'\hline' + '\n' if self.has_header else ''
        # Finish table
        latex += r'\end{tabular}'
        return latex

