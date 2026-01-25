"""
SymPy Integration Utilities.

Provides symbolic mathematics capabilities for the question engine.
Falls back gracefully when SymPy is not available.
"""

from typing import Any, Optional, List, Tuple, Union
from fractions import Fraction
import math

# Try to import SymPy
try:
    import sympy as sp
    from sympy import (
        symbols, Symbol, Eq, solve, simplify, expand, factor,
        Rational, sqrt, pi, sin, cos, tan, log, exp,
        latex, pretty, sympify
    )
    from sympy.parsing.sympy_parser import parse_expr
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    # Create dummy classes/functions
    class Symbol:
        pass


class SymbolicMath:
    """
    Wrapper for symbolic mathematics operations.

    Provides a unified interface that works with or without SymPy.
    """

    def __init__(self):
        self.available = SYMPY_AVAILABLE
        if self.available:
            self.x = sp.Symbol('x')
            self.y = sp.Symbol('y')
            self.z = sp.Symbol('z')

    def solve_linear(self, a: float, b: float, c: float) -> Optional[float]:
        """
        Solve linear equation: ax + b = c

        Returns x = (c - b) / a
        """
        if a == 0:
            return None
        return (c - b) / a

    def solve_quadratic(
        self,
        a: float,
        b: float,
        c: float
    ) -> Optional[Tuple[float, float]]:
        """
        Solve quadratic equation: ax² + bx + c = 0

        Returns tuple of solutions or None if no real solutions.
        """
        if a == 0:
            # Linear equation
            if b != 0:
                return (-c / b, -c / b)
            return None

        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return None  # No real solutions

        sqrt_disc = math.sqrt(discriminant)
        x1 = (-b + sqrt_disc) / (2 * a)
        x2 = (-b - sqrt_disc) / (2 * a)

        return (x1, x2)

    def simplify_fraction(self, numerator: int, denominator: int) -> Tuple[int, int]:
        """Simplify a fraction to lowest terms."""
        if denominator == 0:
            return (numerator, 1)

        gcd = math.gcd(abs(numerator), abs(denominator))
        return (numerator // gcd, denominator // gcd)

    def gcd(self, a: int, b: int) -> int:
        """Greatest common divisor."""
        return math.gcd(abs(a), abs(b))

    def lcm(self, a: int, b: int) -> int:
        """Least common multiple."""
        return abs(a * b) // self.gcd(a, b) if a and b else 0

    def evaluate_expression(self, expression: str, **variables) -> Optional[float]:
        """
        Evaluate a mathematical expression.

        Args:
            expression: String expression like "2*x + 3"
            **variables: Variable values like x=5

        Returns:
            Evaluated result or None on error
        """
        if self.available:
            try:
                expr = parse_expr(expression)
                result = expr.subs(variables)
                return float(result.evalf())
            except:
                pass

        # Fallback: simple evaluation using safe AST parsing
        try:
            import ast
            import operator

            # Replace variable names with values
            eval_expr = expression
            for var, val in variables.items():
                eval_expr = eval_expr.replace(var, str(val))

            # Safe evaluation using ast.parse
            eval_expr = eval_expr.replace('^', '**')

            # Define allowed operations
            allowed_operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
                ast.UAdd: operator.pos,
            }

            allowed_functions = {
                'sqrt': math.sqrt,
                'pi': math.pi,
                'abs': abs,
            }

            def safe_eval(node):
                if isinstance(node, ast.Constant):
                    return node.value
                elif isinstance(node, ast.BinOp):
                    left = safe_eval(node.left)
                    right = safe_eval(node.right)
                    op = allowed_operators.get(type(node.op))
                    if op:
                        return op(left, right)
                    raise ValueError(f"Unsupported operator: {type(node.op)}")
                elif isinstance(node, ast.UnaryOp):
                    operand = safe_eval(node.operand)
                    op = allowed_operators.get(type(node.op))
                    if op:
                        return op(operand)
                    raise ValueError(f"Unsupported operator: {type(node.op)}")
                elif isinstance(node, ast.Call):
                    func_name = node.func.id if isinstance(node.func, ast.Name) else None
                    if func_name in allowed_functions:
                        func = allowed_functions[func_name]
                        if callable(func):
                            args = [safe_eval(arg) for arg in node.args]
                            return func(*args)
                        return func  # For constants like pi
                    raise ValueError(f"Unsupported function: {func_name}")
                elif isinstance(node, ast.Name):
                    if node.id in allowed_functions:
                        return allowed_functions[node.id]
                    raise ValueError(f"Unknown variable: {node.id}")
                elif isinstance(node, ast.Expression):
                    return safe_eval(node.body)
                else:
                    raise ValueError(f"Unsupported node type: {type(node)}")

            tree = ast.parse(eval_expr, mode='eval')
            return float(safe_eval(tree))
        except Exception:
            return None

    def to_latex(self, expression: str) -> str:
        """
        Convert expression to LaTeX format.

        Args:
            expression: Mathematical expression

        Returns:
            LaTeX formatted string
        """
        if self.available:
            try:
                expr = parse_expr(expression)
                return latex(expr)
            except:
                pass

        # Fallback: basic substitutions
        latex_str = expression
        latex_str = latex_str.replace('*', r'\times ')
        latex_str = latex_str.replace('/', r'\div ')
        latex_str = latex_str.replace('sqrt', r'\sqrt')
        latex_str = latex_str.replace('^', '^')
        return latex_str

    def expand_expression(self, expression: str) -> str:
        """Expand algebraic expression."""
        if self.available:
            try:
                expr = parse_expr(expression)
                return str(expand(expr))
            except:
                pass
        return expression

    def factor_expression(self, expression: str) -> str:
        """Factor algebraic expression."""
        if self.available:
            try:
                expr = parse_expr(expression)
                return str(factor(expr))
            except:
                pass
        return expression

    def simplify_expression(self, expression: str) -> str:
        """Simplify algebraic expression."""
        if self.available:
            try:
                expr = parse_expr(expression)
                return str(simplify(expr))
            except:
                pass
        return expression

    def solve_equation(
        self,
        equation_str: str,
        variable: str = 'x'
    ) -> Optional[List[Any]]:
        """
        Solve an equation for a variable.

        Args:
            equation_str: Equation like "2*x + 3 = 7" or "x^2 - 4 = 0"
            variable: Variable to solve for

        Returns:
            List of solutions or None
        """
        if self.available:
            try:
                var = sp.Symbol(variable)

                # Parse equation
                if '=' in equation_str:
                    left, right = equation_str.split('=')
                    equation = Eq(parse_expr(left), parse_expr(right))
                else:
                    equation = Eq(parse_expr(equation_str), 0)

                solutions = solve(equation, var)
                return [float(s.evalf()) if s.is_number else str(s) for s in solutions]
            except:
                pass

        return None

    def verify_solution(
        self,
        equation_str: str,
        variable: str,
        value: Any
    ) -> bool:
        """
        Verify if a value is a solution to an equation.

        Args:
            equation_str: The equation
            variable: Variable name
            value: Proposed solution

        Returns:
            True if value solves the equation
        """
        if self.available:
            try:
                if '=' in equation_str:
                    left, right = equation_str.split('=')
                    left_val = parse_expr(left).subs(variable, value)
                    right_val = parse_expr(right).subs(variable, value)
                    return abs(float(left_val.evalf()) - float(right_val.evalf())) < 0.0001
            except:
                pass

        return False

    def generate_step_by_step(
        self,
        equation_type: str,
        parameters: dict
    ) -> List[str]:
        """
        Generate step-by-step solution for common equation types.

        Args:
            equation_type: Type of equation (linear, quadratic, etc.)
            parameters: Parameters of the equation

        Returns:
            List of solution steps
        """
        steps = []

        if equation_type == "linear_two_step":
            # ax + b = c
            a = parameters.get('a', 1)
            b = parameters.get('b', 0)
            c = parameters.get('c', 0)
            x = parameters.get('solution', 0)

            steps.append(f"Given: {a}x + {b} = {c}")
            steps.append(f"Step 1: Subtract {b} from both sides")
            steps.append(f"        {a}x = {c} - {b}")
            steps.append(f"        {a}x = {c - b}")
            steps.append(f"Step 2: Divide both sides by {a}")
            steps.append(f"        x = {c - b} ÷ {a}")
            steps.append(f"        x = {x}")

        elif equation_type == "linear_one_step_add":
            a = parameters.get('a', 0)
            b = parameters.get('b', 0)
            x = parameters.get('solution', 0)

            steps.append(f"Given: x + {a} = {b}")
            steps.append(f"Step 1: Subtract {a} from both sides")
            steps.append(f"        x = {b} - {a}")
            steps.append(f"        x = {x}")

        elif equation_type == "linear_one_step_mult":
            a = parameters.get('a', 1)
            b = parameters.get('b', 0)
            x = parameters.get('solution', 0)

            steps.append(f"Given: {a}x = {b}")
            steps.append(f"Step 1: Divide both sides by {a}")
            steps.append(f"        x = {b} ÷ {a}")
            steps.append(f"        x = {x}")

        elif equation_type == "percentage_find":
            percent = parameters.get('percent', 10)
            value = parameters.get('value', 100)
            answer = parameters.get('answer', 10)

            steps.append(f"Find {percent}% of {value}")
            steps.append(f"Step 1: Convert percentage to decimal")
            steps.append(f"        {percent}% = {percent}/100 = {percent/100}")
            steps.append(f"Step 2: Multiply by the value")
            steps.append(f"        {percent/100} × {value} = {answer}")

        elif equation_type == "area_rectangle":
            l = parameters.get('length', 5)
            w = parameters.get('width', 3)
            area = parameters.get('answer', 15)

            steps.append(f"Find the area of a rectangle with length {l} and width {w}")
            steps.append(f"Step 1: Use the formula Area = length × width")
            steps.append(f"Step 2: Substitute values")
            steps.append(f"        Area = {l} × {w}")
            steps.append(f"        Area = {area} square units")

        return steps


# Global instance
symbolic_math = SymbolicMath()
