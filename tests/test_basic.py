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
    assert html.count('<th') == 6
