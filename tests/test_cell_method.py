import re
import pytest
from tabipy import Table

@pytest.fixture
def t():
    "Returns the table used in the cell_method tests"
    t = Table((1,2,3),
              (4,5,6),
              (7,8,9))
    cell = t.cell(0,0)
    cell.col_span = 2
    return t
    
def test_cell_method_col_span_html():
    "This tests that col_span works in html"
    #t = t()
    t1_html = t()._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    lines = row_split.split(t1_html)
    assert len(lines)==4
    col_split = re.compile('>[\s\d\s]*<')
    parts = col_split.split(lines[1])
    cl_check = re.compile('colspan\s*=\s*"\s*2\s*"')
    assert len(cl_check.findall(parts[0]))>0
    
def test_cell_method_col_span_html():
    "This tests that col_span works in latex"
    #t = t()
    t1_latex = t()._repr_latex_()
    row_split = re.compile(r'\\\\')
    lines = row_split.split(t1_latex)
    assert len(lines)==4
    col_split = re.compile('&')
    parts = col_split.split(lines[0])
    cl_check = re.compile('\w*\\multicolumn\s*\{\s*2\s*}')
    assert len(cl_check.findall(parts[0]))>0
