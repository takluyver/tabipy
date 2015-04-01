import re
import pytest
from tabipy import Table

@pytest.fixture
def t():
    "Returns the table used in the col_span tests"
    t = Table((1,2,3),
              (4,5,6),
              (7,8,9))
    cell = t.cell(0,0)
    cell.row_span = 2
    return t

def test_row_span_html():
    "This test col_span works in html"
    t1_html = t()._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    lines = row_split.split(t1_html)
    assert len(lines)==4
    col_split = re.compile('>[\s\d\s]*<')
    row1_parts = col_split.split(lines[1])
    row2_parts = col_split.split(lines[2])
    cl_check = re.compile('rowspan\s*=\s*"\s*2\s*"')
    assert len(cl_check.findall(row1_parts[0]))>0
    assert len(row1_parts)==7
    assert len(row2_parts)==5
    #print("pass")

def test_row_span_latex():
    "This test col_span works in latex"
    t1_latex = t()._repr_latex_()
    row_split = re.compile(r'\\\\')
    lines = row_split.split(t1_latex)
    assert len(lines)==4
    col_split = re.compile('&')
    row1_parts = col_split.split(lines[0])
    row2_parts = col_split.split(lines[1])
    cl_check = re.compile('\w*\\multirow\s*\{\s*2\s*}')
    assert len(cl_check.findall(row1_parts[0]))>0
    assert row2_parts[0].strip().replace('\n','')==''
    #print("pass")
