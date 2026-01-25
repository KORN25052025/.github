"""
Geometry Question Generator.

Generates geometry questions with deterministic correct answers.
Supports area, perimeter, volume, and Pythagorean theorem problems.
"""

import random
import math
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from ..base import (
    QuestionGenerator,
    QuestionType,
    OperationType,
    AnswerFormat,
    GeneratedQuestion,
    DifficultyTier,
)
from ..registry import register_generator


class Shape(str, Enum):
    """Geometric shapes supported."""
    SQUARE = "square"
    RECTANGLE = "rectangle"
    TRIANGLE = "triangle"
    CIRCLE = "circle"
    PARALLELOGRAM = "parallelogram"
    TRAPEZOID = "trapezoid"
    CUBE = "cube"
    RECTANGULAR_PRISM = "rectangular_prism"
    CYLINDER = "cylinder"
    SPHERE = "sphere"
    CONE = "cone"
    RIGHT_TRIANGLE = "right_triangle"


class GeometryOperation(str, Enum):
    """Types of geometry calculations."""
    AREA = "area"
    PERIMETER = "perimeter"
    VOLUME = "volume"
    SURFACE_AREA = "surface_area"
    PYTHAGOREAN = "pythagorean"
    CIRCUMFERENCE = "circumference"


@register_generator
class GeometryGenerator(QuestionGenerator):
    """
    Generator for geometry questions.

    Supports:
    - Area calculations (2D shapes)
    - Perimeter calculations
    - Circumference of circles
    - Volume calculations (3D shapes)
    - Surface area calculations
    - Pythagorean theorem problems

    Difficulty is controlled through:
    - Shape complexity
    - Dimension magnitude
    - Decimal vs integer answers
    - Composite figures
    - Multi-step problems
    """

    # Grade-based configuration
    GRADE_CONFIG = {
        3: {
            "shapes_2d": [Shape.SQUARE, Shape.RECTANGLE],
            "shapes_3d": [],
            "operations": [GeometryOperation.AREA, GeometryOperation.PERIMETER],
            "max_dimension": 20,
            "use_pi": False,
        },
        4: {
            "shapes_2d": [Shape.SQUARE, Shape.RECTANGLE, Shape.TRIANGLE],
            "shapes_3d": [Shape.CUBE],
            "operations": [GeometryOperation.AREA, GeometryOperation.PERIMETER, GeometryOperation.VOLUME],
            "max_dimension": 30,
            "use_pi": False,
        },
        5: {
            "shapes_2d": [Shape.SQUARE, Shape.RECTANGLE, Shape.TRIANGLE, Shape.PARALLELOGRAM],
            "shapes_3d": [Shape.CUBE, Shape.RECTANGULAR_PRISM],
            "operations": [GeometryOperation.AREA, GeometryOperation.PERIMETER, GeometryOperation.VOLUME],
            "max_dimension": 50,
            "use_pi": False,
        },
        6: {
            "shapes_2d": [Shape.SQUARE, Shape.RECTANGLE, Shape.TRIANGLE, Shape.PARALLELOGRAM, Shape.CIRCLE],
            "shapes_3d": [Shape.CUBE, Shape.RECTANGULAR_PRISM, Shape.CYLINDER],
            "operations": [GeometryOperation.AREA, GeometryOperation.PERIMETER, GeometryOperation.VOLUME, GeometryOperation.CIRCUMFERENCE],
            "max_dimension": 50,
            "use_pi": True,
        },
        7: {
            "shapes_2d": [Shape.SQUARE, Shape.RECTANGLE, Shape.TRIANGLE, Shape.PARALLELOGRAM, Shape.TRAPEZOID, Shape.CIRCLE],
            "shapes_3d": [Shape.CUBE, Shape.RECTANGULAR_PRISM, Shape.CYLINDER, Shape.CONE],
            "operations": [GeometryOperation.AREA, GeometryOperation.PERIMETER, GeometryOperation.VOLUME, GeometryOperation.CIRCUMFERENCE, GeometryOperation.PYTHAGOREAN],
            "max_dimension": 100,
            "use_pi": True,
        },
        8: {
            "shapes_2d": [Shape.SQUARE, Shape.RECTANGLE, Shape.TRIANGLE, Shape.PARALLELOGRAM, Shape.TRAPEZOID, Shape.CIRCLE, Shape.RIGHT_TRIANGLE],
            "shapes_3d": [Shape.CUBE, Shape.RECTANGULAR_PRISM, Shape.CYLINDER, Shape.CONE, Shape.SPHERE],
            "operations": [GeometryOperation.AREA, GeometryOperation.PERIMETER, GeometryOperation.VOLUME, GeometryOperation.SURFACE_AREA, GeometryOperation.CIRCUMFERENCE, GeometryOperation.PYTHAGOREAN],
            "max_dimension": 100,
            "use_pi": True,
        },
    }

    # Pythagorean triples for clean problems
    PYTHAGOREAN_TRIPLES = [
        (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25),
        (6, 8, 10), (9, 12, 15), (12, 16, 20), (15, 20, 25),
    ]

    @property
    def question_type(self) -> QuestionType:
        return QuestionType.GEOMETRY

    @property
    def supported_operations(self) -> List[OperationType]:
        return [OperationType.AREA, OperationType.PERIMETER, OperationType.VOLUME]

    def generate(
        self,
        difficulty: float = 0.5,
        operation: Optional[OperationType] = None,
        grade_level: Optional[int] = None,
        seed: Optional[int] = None,
        geometry_operation: Optional[str] = None,
        shape: Optional[str] = None,
        **kwargs
    ) -> GeneratedQuestion:
        """Generate a geometry question."""

        if seed is not None:
            random.seed(seed)

        # Determine grade level
        if grade_level is None:
            grade_level = self._difficulty_to_grade(difficulty)

        # Get configuration
        config = self._get_grade_config(grade_level)

        # Select operation
        if geometry_operation is None:
            geometry_operation = random.choice(config["operations"])
        else:
            geometry_operation = GeometryOperation(geometry_operation)

        # Generate based on operation
        if geometry_operation == GeometryOperation.AREA:
            return self._generate_area(difficulty, config, grade_level)
        elif geometry_operation == GeometryOperation.PERIMETER:
            return self._generate_perimeter(difficulty, config, grade_level)
        elif geometry_operation == GeometryOperation.CIRCUMFERENCE:
            return self._generate_circumference(difficulty, config, grade_level)
        elif geometry_operation == GeometryOperation.VOLUME:
            return self._generate_volume(difficulty, config, grade_level)
        elif geometry_operation == GeometryOperation.SURFACE_AREA:
            return self._generate_surface_area(difficulty, config, grade_level)
        elif geometry_operation == GeometryOperation.PYTHAGOREAN:
            return self._generate_pythagorean(difficulty, config, grade_level)
        else:
            return self._generate_area(difficulty, config, grade_level)

    def _generate_area(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate area calculation question."""
        shapes = config["shapes_2d"]
        shape = random.choice(shapes)
        max_dim = config["max_dimension"]
        scaled_max = max(3, int(max_dim * (0.3 + 0.7 * difficulty)))

        if shape == Shape.SQUARE:
            side = random.randint(2, scaled_max)
            area = side * side
            expression = f"Find the area of a square with side length {side} units."
            formula_latex = f"Area = s^2 = {side}^2"
            params = {"side": side}

        elif shape == Shape.RECTANGLE:
            length = random.randint(3, scaled_max)
            width = random.randint(2, length - 1) if length > 2 else 2
            area = length * width
            expression = f"Find the area of a rectangle with length {length} units and width {width} units."
            formula_latex = f"Area = l \\times w = {length} \\times {width}"
            params = {"length": length, "width": width}

        elif shape == Shape.TRIANGLE:
            base = random.randint(3, scaled_max)
            height = random.randint(2, scaled_max)
            # Ensure even product for integer area
            if (base * height) % 2 == 1:
                base += 1
            area = (base * height) // 2
            expression = f"Find the area of a triangle with base {base} units and height {height} units."
            formula_latex = f"Area = \\frac{{1}}{{2}} \\times b \\times h = \\frac{{1}}{{2}} \\times {base} \\times {height}"
            params = {"base": base, "height": height}

        elif shape == Shape.PARALLELOGRAM:
            base = random.randint(3, scaled_max)
            height = random.randint(2, scaled_max)
            area = base * height
            expression = f"Find the area of a parallelogram with base {base} units and height {height} units."
            formula_latex = f"Area = b \\times h = {base} \\times {height}"
            params = {"base": base, "height": height}

        elif shape == Shape.TRAPEZOID:
            a = random.randint(3, scaled_max)
            b = random.randint(2, scaled_max)
            h = random.randint(2, scaled_max // 2)
            # Ensure even for integer area
            if ((a + b) * h) % 2 == 1:
                h += 1
            area = ((a + b) * h) // 2
            expression = f"Find the area of a trapezoid with parallel sides {a} and {b} units, and height {h} units."
            formula_latex = f"Area = \\frac{{1}}{{2}}(a + b) \\times h = \\frac{{1}}{{2}}({a} + {b}) \\times {h}"
            params = {"a": a, "b": b, "height": h}

        elif shape == Shape.CIRCLE:
            radius = random.randint(2, min(20, scaled_max))
            area = round(math.pi * radius * radius, 2)
            expression = f"Find the area of a circle with radius {radius} units. (Use π = 3.14)"
            formula_latex = f"Area = \\pi r^2 = 3.14 \\times {radius}^2"
            # For cleaner answers, round to nearest integer for multiple choice
            area = round(3.14 * radius * radius, 2)
            params = {"radius": radius}

        else:
            # Default to square
            side = random.randint(2, scaled_max)
            area = side * side
            expression = f"Find the area of a square with side length {side} units."
            formula_latex = f"Area = s^2 = {side}^2"
            params = {"side": side}
            shape = Shape.SQUARE

        # Format answer
        answer_str = str(int(area)) if area == int(area) else f"{area:.2f}"

        # Generate distractors
        distractors = self._generate_geometry_distractors(area, shape, "area", params)

        calc_difficulty = self._calculate_geometry_difficulty(shape, "area", params)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id=f"geometry_area_{shape.value}",
            question_type=self.question_type,
            operation=OperationType.AREA,
            expression=expression,
            expression_latex=f"${formula_latex}$",
            correct_answer=answer_str,
            answer_format=AnswerFormat.INTEGER if area == int(area) else AnswerFormat.DECIMAL,
            distractors=distractors,
            all_options=self._shuffle_options(answer_str, distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "shape": shape.value,
                "operation": "area",
                "answer": area,
                **params,
                "grade_level": grade_level,
            },
        )

    def _generate_perimeter(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate perimeter calculation question."""
        shapes = [s for s in config["shapes_2d"] if s != Shape.CIRCLE]
        if not shapes:
            shapes = [Shape.SQUARE, Shape.RECTANGLE]

        shape = random.choice(shapes)
        max_dim = config["max_dimension"]
        scaled_max = max(3, int(max_dim * (0.3 + 0.7 * difficulty)))

        if shape == Shape.SQUARE:
            side = random.randint(2, scaled_max)
            perimeter = 4 * side
            expression = f"Find the perimeter of a square with side length {side} units."
            formula_latex = f"Perimeter = 4s = 4 \\times {side}"
            params = {"side": side}

        elif shape == Shape.RECTANGLE:
            length = random.randint(3, scaled_max)
            width = random.randint(2, length - 1) if length > 2 else 2
            perimeter = 2 * (length + width)
            expression = f"Find the perimeter of a rectangle with length {length} units and width {width} units."
            formula_latex = f"Perimeter = 2(l + w) = 2({length} + {width})"
            params = {"length": length, "width": width}

        elif shape == Shape.TRIANGLE:
            # Use integer sides
            a = random.randint(3, scaled_max)
            b = random.randint(3, scaled_max)
            c = random.randint(abs(a - b) + 1, a + b - 1)  # Triangle inequality
            perimeter = a + b + c
            expression = f"Find the perimeter of a triangle with sides {a}, {b}, and {c} units."
            formula_latex = f"Perimeter = a + b + c = {a} + {b} + {c}"
            params = {"a": a, "b": b, "c": c}

        else:
            # Default to rectangle
            length = random.randint(3, scaled_max)
            width = random.randint(2, length - 1) if length > 2 else 2
            perimeter = 2 * (length + width)
            expression = f"Find the perimeter of a rectangle with length {length} units and width {width} units."
            formula_latex = f"Perimeter = 2(l + w) = 2({length} + {width})"
            params = {"length": length, "width": width}
            shape = Shape.RECTANGLE

        answer_str = str(perimeter)
        distractors = self._generate_geometry_distractors(perimeter, shape, "perimeter", params)
        calc_difficulty = self._calculate_geometry_difficulty(shape, "perimeter", params)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id=f"geometry_perimeter_{shape.value}",
            question_type=self.question_type,
            operation=OperationType.PERIMETER,
            expression=expression,
            expression_latex=f"${formula_latex}$",
            correct_answer=answer_str,
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(answer_str, distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "shape": shape.value,
                "operation": "perimeter",
                "answer": perimeter,
                **params,
                "grade_level": grade_level,
            },
        )

    def _generate_circumference(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate circumference question."""
        max_dim = config["max_dimension"]
        scaled_max = max(3, int(max_dim * (0.3 + 0.7 * difficulty)))

        radius = random.randint(2, min(20, scaled_max))
        # Use diameter sometimes
        use_diameter = random.choice([True, False])

        if use_diameter:
            diameter = radius * 2
            circumference = round(3.14 * diameter, 2)
            expression = f"Find the circumference of a circle with diameter {diameter} units. (Use π = 3.14)"
            formula_latex = f"C = \\pi d = 3.14 \\times {diameter}"
            params = {"diameter": diameter}
        else:
            circumference = round(2 * 3.14 * radius, 2)
            expression = f"Find the circumference of a circle with radius {radius} units. (Use π = 3.14)"
            formula_latex = f"C = 2\\pi r = 2 \\times 3.14 \\times {radius}"
            params = {"radius": radius}

        answer_str = f"{circumference:.2f}".rstrip('0').rstrip('.')
        distractors = self._generate_geometry_distractors(circumference, Shape.CIRCLE, "circumference", params)
        calc_difficulty = 0.4 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="geometry_circumference",
            question_type=self.question_type,
            operation=OperationType.PERIMETER,
            expression=expression,
            expression_latex=f"${formula_latex}$",
            correct_answer=answer_str,
            answer_format=AnswerFormat.DECIMAL,
            distractors=distractors,
            all_options=self._shuffle_options(answer_str, distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "shape": "circle",
                "operation": "circumference",
                "answer": circumference,
                **params,
                "grade_level": grade_level,
            },
        )

    def _generate_volume(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate volume calculation question."""
        shapes = config["shapes_3d"]
        if not shapes:
            shapes = [Shape.CUBE]

        shape = random.choice(shapes)
        max_dim = config["max_dimension"]
        scaled_max = max(3, int(max_dim * (0.3 + 0.7 * difficulty)))

        if shape == Shape.CUBE:
            side = random.randint(2, min(15, scaled_max))
            volume = side ** 3
            expression = f"Find the volume of a cube with side length {side} units."
            formula_latex = f"V = s^3 = {side}^3"
            params = {"side": side}

        elif shape == Shape.RECTANGULAR_PRISM:
            length = random.randint(2, min(15, scaled_max))
            width = random.randint(2, min(10, scaled_max))
            height = random.randint(2, min(10, scaled_max))
            volume = length * width * height
            expression = f"Find the volume of a rectangular prism with length {length}, width {width}, and height {height} units."
            formula_latex = f"V = l \\times w \\times h = {length} \\times {width} \\times {height}"
            params = {"length": length, "width": width, "height": height}

        elif shape == Shape.CYLINDER:
            radius = random.randint(2, min(10, scaled_max))
            height = random.randint(3, min(15, scaled_max))
            volume = round(3.14 * radius * radius * height, 2)
            expression = f"Find the volume of a cylinder with radius {radius} and height {height} units. (Use π = 3.14)"
            formula_latex = f"V = \\pi r^2 h = 3.14 \\times {radius}^2 \\times {height}"
            params = {"radius": radius, "height": height}

        elif shape == Shape.CONE:
            radius = random.randint(2, min(10, scaled_max))
            height = random.randint(3, min(15, scaled_max))
            volume = round((1/3) * 3.14 * radius * radius * height, 2)
            expression = f"Find the volume of a cone with radius {radius} and height {height} units. (Use π = 3.14)"
            formula_latex = f"V = \\frac{{1}}{{3}}\\pi r^2 h = \\frac{{1}}{{3}} \\times 3.14 \\times {radius}^2 \\times {height}"
            params = {"radius": radius, "height": height}

        elif shape == Shape.SPHERE:
            radius = random.randint(2, min(8, scaled_max))
            volume = round((4/3) * 3.14 * radius ** 3, 2)
            expression = f"Find the volume of a sphere with radius {radius} units. (Use π = 3.14)"
            formula_latex = f"V = \\frac{{4}}{{3}}\\pi r^3 = \\frac{{4}}{{3}} \\times 3.14 \\times {radius}^3"
            params = {"radius": radius}

        else:
            # Default to cube
            side = random.randint(2, min(15, scaled_max))
            volume = side ** 3
            expression = f"Find the volume of a cube with side length {side} units."
            formula_latex = f"V = s^3 = {side}^3"
            params = {"side": side}
            shape = Shape.CUBE

        answer_str = str(int(volume)) if volume == int(volume) else f"{volume:.2f}"
        distractors = self._generate_geometry_distractors(volume, shape, "volume", params)
        calc_difficulty = self._calculate_geometry_difficulty(shape, "volume", params)

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id=f"geometry_volume_{shape.value}",
            question_type=self.question_type,
            operation=OperationType.VOLUME,
            expression=expression,
            expression_latex=f"${formula_latex}$",
            correct_answer=answer_str,
            answer_format=AnswerFormat.INTEGER if volume == int(volume) else AnswerFormat.DECIMAL,
            distractors=distractors,
            all_options=self._shuffle_options(answer_str, distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "shape": shape.value,
                "operation": "volume",
                "answer": volume,
                **params,
                "grade_level": grade_level,
            },
        )

    def _generate_pythagorean(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate Pythagorean theorem question."""
        # Use Pythagorean triples for clean answers
        triple = random.choice(self.PYTHAGOREAN_TRIPLES)

        # Scale the triple
        scale = 1 if difficulty < 0.5 else random.randint(1, 3)
        a, b, c = triple[0] * scale, triple[1] * scale, triple[2] * scale

        # Decide what to find
        find_type = random.choice(["hypotenuse", "leg"])

        if find_type == "hypotenuse":
            answer = c
            expression = f"A right triangle has legs of length {a} and {b}. Find the length of the hypotenuse."
            formula_latex = f"c = \\sqrt{{a^2 + b^2}} = \\sqrt{{{a}^2 + {b}^2}}"
            params = {"a": a, "b": b}
        else:
            # Find a leg
            answer = a
            expression = f"A right triangle has one leg of length {b} and hypotenuse of length {c}. Find the length of the other leg."
            formula_latex = f"a = \\sqrt{{c^2 - b^2}} = \\sqrt{{{c}^2 - {b}^2}}"
            params = {"b": b, "c": c}

        distractors = self._generate_pythagorean_distractors(answer, a, b, c)
        calc_difficulty = 0.5 + 0.2 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id="geometry_pythagorean",
            question_type=self.question_type,
            operation=OperationType.AREA,  # Using AREA as placeholder
            expression=expression,
            expression_latex=f"${formula_latex}$",
            correct_answer=str(answer),
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(str(answer), distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "operation": "pythagorean",
                "find_type": find_type,
                "triple": [a, b, c],
                "answer": answer,
                **params,
                "grade_level": grade_level,
            },
        )

    def _generate_surface_area(
        self,
        difficulty: float,
        config: Dict[str, Any],
        grade_level: int
    ) -> GeneratedQuestion:
        """Generate surface area calculation question."""
        shapes = [s for s in config["shapes_3d"] if s in [Shape.CUBE, Shape.RECTANGULAR_PRISM]]
        if not shapes:
            shapes = [Shape.CUBE]

        shape = random.choice(shapes)
        max_dim = config["max_dimension"]
        scaled_max = max(3, int(max_dim * (0.3 + 0.7 * difficulty)))

        if shape == Shape.CUBE:
            side = random.randint(2, min(12, scaled_max))
            sa = 6 * side * side
            expression = f"Find the surface area of a cube with side length {side} units."
            formula_latex = f"SA = 6s^2 = 6 \\times {side}^2"
            params = {"side": side}

        else:  # RECTANGULAR_PRISM
            l = random.randint(2, min(10, scaled_max))
            w = random.randint(2, min(8, scaled_max))
            h = random.randint(2, min(8, scaled_max))
            sa = 2 * (l*w + w*h + l*h)
            expression = f"Find the surface area of a rectangular prism with length {l}, width {w}, and height {h} units."
            formula_latex = f"SA = 2(lw + wh + lh) = 2({l}\\times{w} + {w}\\times{h} + {l}\\times{h})"
            params = {"length": l, "width": w, "height": h}

        answer_str = str(sa)
        distractors = self._generate_geometry_distractors(sa, shape, "surface_area", params)
        calc_difficulty = 0.5 + 0.25 * difficulty

        return GeneratedQuestion(
            question_id=self._generate_id(),
            template_id=f"geometry_surface_area_{shape.value}",
            question_type=self.question_type,
            operation=OperationType.AREA,
            expression=expression,
            expression_latex=f"${formula_latex}$",
            correct_answer=answer_str,
            answer_format=AnswerFormat.INTEGER,
            distractors=distractors,
            all_options=self._shuffle_options(answer_str, distractors),
            difficulty_score=calc_difficulty,
            difficulty_tier=self._get_difficulty_tier(calc_difficulty),
            parameters={
                "shape": shape.value,
                "operation": "surface_area",
                "answer": sa,
                **params,
                "grade_level": grade_level,
            },
        )

    def compute_answer(self, **parameters) -> Any:
        """Compute the correct answer deterministically."""
        return parameters.get("answer", 0)

    def generate_distractors(
        self,
        correct_answer: Any,
        parameters: Dict[str, Any],
        count: int = 3
    ) -> List[Any]:
        """Generate geometry distractors."""
        shape = Shape(parameters.get("shape", "square"))
        operation = parameters.get("operation", "area")
        return self._generate_geometry_distractors(correct_answer, shape, operation, parameters)

    def calculate_difficulty(self, parameters: Dict[str, Any]) -> float:
        """Calculate difficulty for geometry problem."""
        shape = Shape(parameters.get("shape", "square"))
        operation = parameters.get("operation", "area")
        return self._calculate_geometry_difficulty(shape, operation, parameters)

    # Helper methods

    def _difficulty_to_grade(self, difficulty: float) -> int:
        """Map difficulty to grade level."""
        if difficulty < 0.15:
            return 3
        elif difficulty < 0.3:
            return 4
        elif difficulty < 0.45:
            return 5
        elif difficulty < 0.6:
            return 6
        elif difficulty < 0.8:
            return 7
        else:
            return 8

    def _get_grade_config(self, grade_level: int) -> Dict[str, Any]:
        """Get configuration for grade level."""
        grade = max(3, min(8, grade_level))
        return self.GRADE_CONFIG[grade]

    def _calculate_geometry_difficulty(
        self,
        shape: Shape,
        operation: str,
        params: Dict[str, Any]
    ) -> float:
        """Calculate difficulty score for geometry problem."""
        difficulty = 0.2

        # Shape complexity
        shape_difficulty = {
            Shape.SQUARE: 0.0,
            Shape.RECTANGLE: 0.1,
            Shape.TRIANGLE: 0.2,
            Shape.PARALLELOGRAM: 0.25,
            Shape.CIRCLE: 0.3,
            Shape.TRAPEZOID: 0.35,
            Shape.CUBE: 0.3,
            Shape.RECTANGULAR_PRISM: 0.4,
            Shape.CYLINDER: 0.5,
            Shape.CONE: 0.55,
            Shape.SPHERE: 0.6,
        }
        difficulty += shape_difficulty.get(shape, 0.2)

        # Operation complexity
        op_difficulty = {
            "perimeter": 0.0,
            "area": 0.1,
            "circumference": 0.2,
            "volume": 0.25,
            "surface_area": 0.35,
            "pythagorean": 0.4,
        }
        difficulty += op_difficulty.get(operation, 0.1)

        return min(1.0, difficulty)

    def _generate_geometry_distractors(
        self,
        answer: float,
        shape: Shape,
        operation: str,
        params: Dict[str, Any]
    ) -> List[str]:
        """Generate plausible wrong answers for geometry."""
        distractors = set()
        ans = float(answer)

        # Common errors based on operation

        if operation == "area" and shape == Shape.RECTANGLE:
            # Perimeter instead of area
            l = params.get("length", 5)
            w = params.get("width", 3)
            wrong = 2 * (l + w)
            if wrong != ans:
                distractors.add(str(int(wrong)))

        if operation == "perimeter" and shape == Shape.RECTANGLE:
            # Area instead of perimeter
            l = params.get("length", 5)
            w = params.get("width", 3)
            wrong = l * w
            if wrong != ans:
                distractors.add(str(int(wrong)))

        if operation == "area" and shape == Shape.TRIANGLE:
            # Forgetting to divide by 2
            base = params.get("base", 4)
            height = params.get("height", 3)
            wrong = base * height
            if wrong != ans:
                distractors.add(str(int(wrong)))

        if operation == "volume" and shape == Shape.CUBE:
            # Using area formula instead
            side = params.get("side", 3)
            wrong = side * side
            if wrong != ans:
                distractors.add(str(int(wrong)))

        # General distractors
        # Off by common factors
        distractors.add(str(int(ans + 5)))
        if ans > 5:
            distractors.add(str(int(ans - 5)))
        distractors.add(str(int(ans * 2)))
        if ans > 10:
            distractors.add(str(int(ans / 2)))

        # Remove correct answer
        answer_str = str(int(ans)) if ans == int(ans) else f"{ans:.2f}"
        distractors.discard(answer_str)

        return list(distractors)[:3]

    def _generate_pythagorean_distractors(
        self,
        answer: int,
        a: int,
        b: int,
        c: int
    ) -> List[str]:
        """Generate distractors for Pythagorean problems."""
        distractors = set()

        # Common errors:
        # Adding instead of using formula
        distractors.add(str(a + b))

        # Using wrong formula
        distractors.add(str(abs(c - b)))
        distractors.add(str(abs(c - a)))

        # Close values
        distractors.add(str(answer + 1))
        distractors.add(str(answer - 1))

        distractors.discard(str(answer))
        return list(distractors)[:3]
