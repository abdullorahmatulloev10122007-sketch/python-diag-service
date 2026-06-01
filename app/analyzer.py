import ast
import re
from typing import List, Dict, Any
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    line: int
    type: str
    message: str
    fix: str
    resource: str
    severity: str = "warning"


class PythonCodeAnalyzer:
    """Анализатор Python-кода для выявления типичных ошибок новичков"""

    def __init__(self):
        self.errors: List[ErrorDetail] = []
        self.builtins = {
            'list', 'str', 'int', 'dict', 'set', 'tuple', 
            'len', 'sum', 'max', 'min', 'range', 'enumerate'
        }

    def analyze(self, code: str) -> List[ErrorDetail]:
        """Основной метод анализа кода"""
        self.errors = []
        
        # Проверка синтаксиса
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [ErrorDetail(
                line=e.lineno or 1,
                type="syntax_error",
                message=f"Синтаксическая ошибка: {e.msg}",
                fix="Проверьте отступы, двоеточия, скобки и операторы",
                resource="https://docs.python.org/3/tutorial/errors.html#syntax-errors",
                severity="error"
            )]

        # Запуск всех проверок
        self._check_builtin_shadowing(tree)
        self._check_bool_comparison(tree)
        self._check_modify_during_iteration(tree)
        self._check_mutable_defaults(tree)
        self._check_unused_variables(tree)
        self._check_exception_handling(tree)
        self._check_imports(tree)
        self._check_naming_conventions(tree)
        self._check_common_mistakes(code)

        return self.errors

    def _check_builtin_shadowing(self, tree: ast.AST):
        """Проверка переопределения встроенных имен"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in self.builtins:
                        self.errors.append(ErrorDetail(
                            line=node.lineno,
                            type="builtin_shadowing",
                            message=f'Не переопределяйте встроенное имя "{target.id}"',
                            fix=f'Используйте другое имя: my_{target.id}, {target.id}_data и т.д.',
                            resource="https://docs.python.org/3/library/functions.html",
                            severity="error"
                        ))

    def _check_bool_comparison(self, tree: ast.AST):
        """Проверка сравнения с True/False"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant):
                        if comparator.value is True:
                            self.errors.append(ErrorDetail(
                                line=node.lineno,
                                type="bool_comparison",
                                message="Не сравнивайте с True через ==",
                                fix='Вместо "if x == True:" пишите "if x:"',
                                resource="https://realpython.com/python-boolean/",
                                severity="warning"
                            ))
                        elif comparator.value is False:
                            self.errors.append(ErrorDetail(
                                line=node.lineno,
                                type="bool_comparison",
                                message="Не сравнивайте с False через ==",
                                fix='Вместо "if x == False:" пишите "if not x:"',
                                resource="https://realpython.com/python-boolean/",
                                severity="warning"
                            ))

    def _check_modify_during_iteration(self, tree: ast.AST):
        """Проверка модификации списка во время итерации"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                if isinstance(node, ast.For) and isinstance(node.iter, ast.Name):
                    list_name = node.iter.id
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Attribute):
                                if (child.func.attr in ['append', 'remove', 'pop', 'insert'] and 
                                    isinstance(child.func.value, ast.Name) and 
                                    child.func.value.id == list_name):
                                    self.errors.append(ErrorDetail(
                                        line=node.lineno,
                                        type="modify_during_iteration",
                                        message="Не изменяйте список во время итерации",
                                        fix="Создайте копию: for item in my_list[:]",
                                        resource="https://docs.python-guide.org/writing/gotchas/",
                                        severity="error"
                                    ))

    def _check_mutable_defaults(self, tree: ast.AST):
        """Проверка изменяемых значений по умолчанию в функциях"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        self.errors.append(ErrorDetail(
                            line=node.lineno,
                            type="mutable_default",
                            message="Не используйте изменяемые объекты как аргументы по умолчанию",
                            fix="Используйте None и создавайте объект внутри функции",
                            resource="https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments",
                            severity="error"
                        ))

    def _check_unused_variables(self, tree: ast.AST):
        """Проверка неиспользуемых переменных"""
        assigned_vars = set()
        used_vars = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned_vars.add(target.id)
            elif isinstance(node, ast.Name):
                used_vars.add(node.id)

        unused = assigned_vars - used_vars - {'_', '__'}
        for var in unused:
            self.errors.append(ErrorDetail(
                line=1,
                type="unused_variable",
                message=f'Переменная "{var}" объявлена, но не используется',
                fix="Удалите неиспользуемую переменную или используйте её",
                resource="https://realpython.com/python-variables/",
                severity="info"
            ))

    def _check_exception_handling(self, tree: ast.AST):
        """Проверка обработки исключений"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.errors.append(ErrorDetail(
                        line=node.lineno,
                        type="bare_except",
                        message="Не используйте bare except - он перехватывает все исключения",
                        fix="Укажите конкретное исключение: except ValueError:",
                        resource="https://docs.python.org/3/tutorial/errors.html#handling-exceptions",
                        severity="warning"
                    ))
                elif isinstance(node.type, ast.Name) and node.type.id == 'Exception':
                    self.errors.append(ErrorDetail(
                        line=node.lineno,
                        type="broad_exception",
                        message="Не перехватывайте общее исключение Exception",
                        fix="Перехватывайте конкретные исключения",
                        resource="https://docs.python.org/3/library/exceptions.html",
                        severity="warning"
                    ))

    def _check_imports(self, tree: ast.AST):
        """Проверка импортов"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == '*' and node.level == 0:
                    self.errors.append(ErrorDetail(
                        line=node.lineno,
                        type="wildcard_import",
                        message="Не используйте import * - это загрязняет пространство имен",
                        fix="Импортируйте конкретные имена: from module import name1, name2",
                        resource="https://peps.python.org/pep-0008/#imports",
                        severity="warning"
                    ))

    def _check_naming_conventions(self, tree: ast.AST):
        """Проверка соглашений об именах"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    self.errors.append(ErrorDetail(
                        line=node.lineno,
                        type="naming_convention",
                        message=f'Функция "{node.name}" должна быть в snake_case',
                        fix="Используйте lowercase_with_underscores для имен функций",
                        resource="https://peps.python.org/pep-0008/#function-and-variable-names",
                        severity="info"
                    ))
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.errors.append(ErrorDetail(
                        line=node.lineno,
                        type="naming_convention",
                        message=f'Класс "{node.name}" должен быть в PascalCase',
                        fix="Используйте CapitalizedWords для имен классов",
                        resource="https://peps.python.org/pep-0008/#class-names",
                        severity="info"
                    ))

    def _similarity(self, s1: str, s2: str) -> float:
        """Простое сравнение схожести строк для детекции опечаток"""
        if len(s1) < len(s2):
            return self._similarity(s2, s1)
        if len(s2) == 0:
            return 0.0
        matches = sum(c1 == c2 for c1, c2 in zip(s1.lower(), s2.lower()))
        return matches / max(len(s1), len(s2))

    def _check_common_mistakes(self, code: str):
        """Проверка распространенных ошибок через regex"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Проверка отступов (смесь tab и spaces)
            if '\t' in line and ' ' in line.replace('\t', ''):
                self.errors.append(ErrorDetail(
                    line=i,
                    type="mixed_indentation",
                    message="Смешаны табы и пробелы в отступах",
                    fix="Используйте только 4 пробела для отступов",
                    resource="https://peps.python.org/pep-0008/#indentation",
                    severity="error"
                ))
            
            # Проверка лишнего пробела перед :
            if re.search(r'\s+:', stripped):
                self.errors.append(ErrorDetail(
                    line=i,
                    type="spacing",
                    message="Лишний пробел перед двоеточием",
                    fix="Удалите пробел перед двоеточием",
                    resource="https://peps.python.org/pep-0008/#other-recommendations",
                    severity="info"
                ))
            
            # Проверка на опечатки в ключевых словах
            keywords = ['while', 'for', 'if', 'else', 'elif', 'def', 'class', 'import', 'from', 'return', 'try', 'except', 'finally']
            words = stripped.split()
            for word in words:
                for keyword in keywords:
                    if len(word) >= 3 and word != keyword and self._similarity(word, keyword) > 0.7:
                        self.errors.append(ErrorDetail(
                            line=i,
                            type="typo_in_keyword",
                            message=f"Возможно, опечатка в ключевом слове: \"{word}\" → \"{keyword}\"",
                            fix=f"Исправьте \"{word}\" на \"{keyword}\"",
                            resource="https://docs.python.org/3/reference/lexical_analysis.html#keywords",
                            severity="error"
                        ))
            
            # Проверка на неопределённые переменные (простая эвристика)
            if '(' in stripped and ')' in stripped and not stripped.startswith('#'):
                identifiers = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', stripped)
                for ident in identifiers:
                    if ident not in self.builtins and ident not in ['print', 'input', 'len', 'range', 'str', 'int', 'float', 'list', 'dict']:
                        defined = False
                        for prev_line in lines[:i-1]:
                            if f'{ident} =' in prev_line or f'{ident}=' in prev_line:
                                defined = True
                                break
                        if not defined and len(ident) > 1:
                            self.errors.append(ErrorDetail(
                                line=i,
                                type="undefined_variable",
                                message=f"Возможно, использование неопределённой переменной \"{ident}\"",
                                fix=f"Определите переменную {ident} перед использованием",
                                resource="https://docs.python.org/3/tutorial/introduction.html#using-python-as-a-calculator",
                                severity="warning"
                            ))


def calculate_score(errors: List[ErrorDetail]) -> float:
    """Расчет оценки качества кода (0-100)"""
    if not errors:
        return 100.0
    
    severity_weights = {
        'syntax_error': 30,
        'error': 15,
        'warning': 8,
        'info': 2
    }
    
    total_penalty = 0
    error_count = len(errors)
    
    for error in errors:
        severity = getattr(error, 'severity', 'error')
        weight = severity_weights.get(severity, 10)
        total_penalty += weight
    
    if error_count >= 2:
        extra_penalty = (error_count - 1) * 5
        if error_count >= 4:
            extra_penalty += (error_count - 3) * 5
        total_penalty += extra_penalty
    
    has_syntax_error = any(getattr(e, 'type', '') == 'syntax_error' for e in errors)
    if has_syntax_error:
        total_penalty = max(total_penalty, 50)
    
    score = max(0, 100 - total_penalty)
    return round(score, 1)


def get_recommendations(errors: List[ErrorDetail]) -> List[str]:
    """Генерация рекомендаций на основе найденных ошибок"""
    recommendations = []
    error_types = {getattr(e, 'type', '') for e in errors}
    
    if 'builtin_shadowing' in error_types:
        recommendations.append("Изучите встроенные функции Python: https://docs.python.org/3/library/functions.html")
    if 'bool_comparison' in error_types:
        recommendations.append("Почитайте про работу с булевыми значениями: https://realpython.com/python-boolean/")
    if 'mutable_default' in error_types:
        recommendations.append("Разберитесь с изменяемыми аргументами по умолчанию: https://docs.python-guide.org/writing/gotchas/")
    if 'modify_during_iteration' in error_types:
        recommendations.append("Изучите правильные способы модификации списков: https://docs.python-guide.org/writing/gotchas/")
    
    if not recommendations:
        recommendations.append("Отличная работа! Продолжайте изучать Python.")
    
    return recommendations