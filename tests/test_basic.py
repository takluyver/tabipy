import re
from tabipy import Table, TableRow, TableCell, TableHeaderRow, TableHeader

def test_simple():
    # For now, this is little more than a smoke test to check that it's not
    # erroring out.
    t = Table(TableHeaderRow('a','b','c'),
          (1,  2,  3),
          (2,  4,  6),
         )
    
    html = t._repr_html_()
    assert '<th' in html
    assert '<td' in html
    
    latex = t._repr_latex_()
    assert r'\hline' in latex

def test_tableheader():
    t = Table((TableHeader('a'), 1, 2),
              (TableHeader('b'), 3, 4),
              (TableHeader('c'), 5, 6))

    html = t._repr_html_()
    assert html.count('<th') == 3

    latex = t._repr_latex_()
    assert latex.count(r'\bf') == 3

def test_escape():
    inp_expected = (('', ''),
                    ('&', r'\&'),
                    ('\\', r'{\textbackslash}'),
                    ('~', r'{\textasciitilde}'),
                    ('$', '\$'),
                    ('\n', r'{\linebreak}'),
                    ('\r', r'{\linebreak}'),
                    ('\r\n', r'{\linebreak}'),
                    ('_', r'\_'),
                    ('{', '\{'),
                    ('}', '\}'),
                    ('body & mind & r&d', r'body \& mind \& r\&d'),
                    (r'\_/~\_/', 
                     r'{\textbackslash}\_/{\textasciitilde}'
                     r'{\textbackslash}\_/'),
                    ('~_$\r\n{}', 
                     r'{\textasciitilde}\_\${\linebreak}\{\}'))
    for inp, expected in inp_expected:
        cell = TableCell(inp)
        assert cell._repr_latex_() == expected


