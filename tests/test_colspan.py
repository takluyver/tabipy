import re
import pytest
from tabipy import Table

@pytest.fixture
def t():
    "Returns the table used in the col_span tests"
    t = Table((1,2,3),
              (4,5,6),
              (7,8,9))
    cell_1_1 = t.rows[0].cells[0]
    cell_1_1.col_span = 2
    return t

def test_col_span_html(t):
    "This test col_span works in html"
    t1_html = t._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    lines = row_split.split(t1_html)
    assert len(lines)==4
    col_split = re.compile('>[\s\d\s]*<')
    parts = col_split.split(lines[1])
    cl_check = re.compile('colspan\s*=\s*"\s*2\s*"')
    assert len(cl_check.findall(parts[0]))>0
    #print("pass")

def test_col_span_latex(t):
    "This test col_span works in latex"
    t1_latex = t._repr_latex_()
    row_split = re.compile(r'\\\\')
    lines = row_split.split(t1_latex)
    assert len(lines)==4
    col_split = re.compile('&')
    parts = col_split.split(lines[0])
    cl_check = re.compile('\w*\\multicolumn\s*\{\s*2\s*}')
    assert len(cl_check.findall(parts[0]))>0
    #print("pass")
