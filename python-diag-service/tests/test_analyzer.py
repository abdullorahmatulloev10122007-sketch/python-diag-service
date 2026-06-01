import pytest
from app.analyzer import PythonCodeAnalyzer, calculate_score


@pytest.fixture
def analyzer():
    return PythonCodeAnalyzer()


def test_builtin_shadowing(analyzer):
    code = "list = [1, 2, 3]"
    errors = analyzer.analyze(code)
    assert any(e.type == "builtin_shadowing" for e in errors)


def test_bool_comparison_true(analyzer):
    code = "if x == True:\n    pass"
    errors = analyzer.analyze(code)
    assert any(e.type == "bool_comparison" for e in errors)


def test_bool_comparison_false(analyzer):
    code = "if x == False:\n    pass"
    errors = analyzer.analyze(code)
    assert any(e.type == "bool_comparison" for e in errors)


def test_syntax_error(analyzer):
    code = "if True\n    pass"
    errors = analyzer.analyze(code)
    assert any(e.type == "syntax_error" for e in errors)
    assert len(errors) == 1


def test_mutable_default(analyzer):
    code = "def func(x=[]):\n    return x"
    errors = analyzer.analyze(code)
    assert any(e.type == "mutable_default" for e in errors)


def test_bare_except(analyzer):
    code = "try:\n    pass\nexcept:\n    pass"
    errors = analyzer.analyze(code)
    assert any(e.type == "bare_except" for e in errors)


def test_wildcard_import(analyzer):
    code = "from math import *"
    errors = analyzer.analyze(code)
    assert any(e.type == "wildcard_import" for e in errors)


def test_clean_code(analyzer):
    code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

result = calculate_sum([1, 2, 3])
"""
    errors = analyzer.analyze(code)
    assert len(errors) == 0


def test_score_calculation():
    from app.analyzer import ErrorDetail
    
    errors = [
        ErrorDetail(line=1, type="error1", message="msg", fix="fix", resource="url", severity="error"),
        ErrorDetail(line=2, type="error2", message="msg", fix="fix", resource="url", severity="warning"),
    ]
    
    score = calculate_score(errors)
    assert score == 85.0  # 100 - 10 - 5


def test_score_perfect():
    score = calculate_score([])
    assert score == 100.0