"""
Story Generation using LLM.

Transforms abstract mathematical expressions into engaging word problems
while preserving mathematical correctness.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
import random


class StoryTheme(str, Enum):
    """Themes for story generation."""
    SHOPPING = "shopping"
    SPORTS = "sports"
    COOKING = "cooking"
    TRAVEL = "travel"
    NATURE = "nature"
    ANIMALS = "animals"
    GAMES = "games"
    SCHOOL = "school"


@dataclass
class StoryContext:
    """Context for story generation."""
    theme: StoryTheme
    character_name: Optional[str] = None
    grade_level: int = 5
    language: str = "en"


@dataclass
class GeneratedStory:
    """Result of story generation."""
    story_text: str
    visual_prompt: Optional[str] = None
    theme_used: StoryTheme = StoryTheme.SHOPPING
    success: bool = True
    error_message: Optional[str] = None


# Character name pools
NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan",
    "Sophia", "Mason", "Isabella", "James", "Mia", "Lucas",
]


class StoryGenerator:
    """
    Transforms abstract math expressions into engaging word problems.

    Uses OpenAI GPT for story generation with fallback to templates.
    """

    STORY_PROMPT = """You are creating an engaging math word problem for a grade {grade_level} student.

Transform this mathematical expression into a fun story problem:

EXPRESSION: {expression}
CORRECT ANSWER: {answer}
THEME: {theme}
CHARACTER: {character}

Requirements:
1. The story must be age-appropriate and engaging
2. All numbers MUST match the original expression EXACTLY
3. The question must be clear and answerable
4. Use vocabulary appropriate for grade {grade_level}
5. Keep the story to 2-3 sentences maximum
6. Do NOT reveal the answer in the story
7. End with a clear question

Respond with ONLY the story problem, nothing else."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize story generator."""
        self.api_key = api_key
        self._client = None

        if api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=api_key)
            except ImportError:
                pass

    async def generate(
        self,
        expression: str,
        answer: any,
        context: Optional[StoryContext] = None
    ) -> GeneratedStory:
        """
        Generate a story problem from a mathematical expression.

        Args:
            expression: The math expression (e.g., "15 + 8 = ?")
            answer: The correct answer
            context: Optional story context

        Returns:
            GeneratedStory with the word problem
        """
        context = context or StoryContext(
            theme=random.choice(list(StoryTheme)),
            character_name=random.choice(NAMES),
            grade_level=5,
        )

        # Try OpenAI if available
        if self._client:
            try:
                return await self._generate_with_openai(expression, answer, context)
            except Exception as e:
                # Fall back to templates
                return self._generate_from_template(expression, answer, context, str(e))

        # Use templates if no API key
        return self._generate_from_template(expression, answer, context)

    async def _generate_with_openai(
        self,
        expression: str,
        answer: any,
        context: StoryContext
    ) -> GeneratedStory:
        """Generate story using OpenAI API."""
        prompt = self.STORY_PROMPT.format(
            grade_level=context.grade_level,
            expression=expression,
            answer=answer,
            theme=context.theme.value,
            character=context.character_name or random.choice(NAMES),
        )

        response = self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful math education assistant that creates engaging word problems."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )

        story_text = response.choices[0].message.content.strip()

        # Generate visual prompt
        visual_prompt = f"A colorful illustration of {context.character_name} in a {context.theme.value} scene"

        return GeneratedStory(
            story_text=story_text,
            visual_prompt=visual_prompt,
            theme_used=context.theme,
            success=True,
        )

    def _generate_from_template(
        self,
        expression: str,
        answer: any,
        context: StoryContext,
        error: Optional[str] = None
    ) -> GeneratedStory:
        """Generate story using templates (fallback)."""
        name = context.character_name or random.choice(NAMES)
        theme = context.theme

        # Parse expression to get operation and operands
        story = self._template_story(expression, name, theme)

        return GeneratedStory(
            story_text=story,
            visual_prompt=None,
            theme_used=theme,
            success=error is None,
            error_message=error,
        )

    def _template_story(self, expression: str, name: str, theme: StoryTheme) -> str:
        """Generate story from template based on operation."""
        # Simple parsing
        expr = expression.replace("= ?", "").strip()

        if "+" in expr:
            parts = expr.split("+")
            a, b = parts[0].strip(), parts[1].strip()
            return self._addition_story(a, b, name, theme)

        elif "-" in expr:
            parts = expr.split("-")
            a, b = parts[0].strip(), parts[1].strip()
            return self._subtraction_story(a, b, name, theme)

        elif "×" in expr or "*" in expr:
            parts = expr.replace("×", "*").split("*")
            a, b = parts[0].strip(), parts[1].strip()
            return self._multiplication_story(a, b, name, theme)

        elif "÷" in expr or "/" in expr:
            parts = expr.replace("÷", "/").split("/")
            a, b = parts[0].strip(), parts[1].strip()
            return self._division_story(a, b, name, theme)

        # Fallback
        return f"Solve this problem: {expression}"

    def _addition_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate addition story."""
        templates = {
            StoryTheme.SHOPPING: f"{name} bought {a} apples and then bought {b} more. How many apples does {name} have now?",
            StoryTheme.SPORTS: f"{name} scored {a} points in the first half and {b} points in the second half. What is the total score?",
            StoryTheme.COOKING: f"{name} has {a} cookies and bakes {b} more. How many cookies does {name} have in total?",
            StoryTheme.ANIMALS: f"There are {a} birds on a tree. {b} more birds fly in. How many birds are on the tree now?",
            StoryTheme.GAMES: f"{name} collected {a} coins in level 1 and {b} coins in level 2. How many coins did {name} collect in total?",
            StoryTheme.SCHOOL: f"{name} read {a} pages yesterday and {b} pages today. How many pages did {name} read altogether?",
        }
        return templates.get(theme, templates[StoryTheme.SHOPPING])

    def _subtraction_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate subtraction story."""
        templates = {
            StoryTheme.SHOPPING: f"{name} had {a} dollars and spent {b} dollars on a toy. How much money does {name} have left?",
            StoryTheme.SPORTS: f"Team A scored {a} points and Team B scored {b} points. By how many points did Team A win?",
            StoryTheme.COOKING: f"{name} made {a} cupcakes and gave away {b} to friends. How many cupcakes does {name} have left?",
            StoryTheme.ANIMALS: f"There were {a} fish in the pond. {b} fish swam away. How many fish are left in the pond?",
            StoryTheme.GAMES: f"{name} had {a} lives in the game but lost {b}. How many lives does {name} have left?",
            StoryTheme.SCHOOL: f"{name} had {a} stickers and gave {b} to a friend. How many stickers does {name} have now?",
        }
        return templates.get(theme, templates[StoryTheme.SHOPPING])

    def _multiplication_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate multiplication story."""
        templates = {
            StoryTheme.SHOPPING: f"{name} bought {a} packs of pencils. Each pack has {b} pencils. How many pencils did {name} buy in total?",
            StoryTheme.SPORTS: f"There are {a} teams. Each team has {b} players. How many players are there in total?",
            StoryTheme.COOKING: f"{name} is making {a} batches of cookies. Each batch makes {b} cookies. How many cookies will there be?",
            StoryTheme.ANIMALS: f"There are {a} bird nests. Each nest has {b} eggs. How many eggs are there altogether?",
            StoryTheme.GAMES: f"{name} completed {a} levels. Each level gives {b} stars. How many stars did {name} earn?",
            StoryTheme.SCHOOL: f"There are {a} rows of desks. Each row has {b} desks. How many desks are there in the classroom?",
        }
        return templates.get(theme, templates[StoryTheme.SHOPPING])

    def _division_story(self, a: str, b: str, name: str, theme: StoryTheme) -> str:
        """Generate division story."""
        templates = {
            StoryTheme.SHOPPING: f"{name} has {a} candies to share equally among {b} friends. How many candies will each friend get?",
            StoryTheme.SPORTS: f"A coach has {a} jerseys to distribute equally among {b} teams. How many jerseys does each team get?",
            StoryTheme.COOKING: f"{name} has {a} slices of pizza to share equally with {b} people. How many slices does each person get?",
            StoryTheme.ANIMALS: f"A farmer has {a} carrots to feed {b} rabbits equally. How many carrots does each rabbit get?",
            StoryTheme.GAMES: f"{name} wants to split {a} coins equally into {b} treasure chests. How many coins go in each chest?",
            StoryTheme.SCHOOL: f"A teacher has {a} books to distribute equally to {b} students. How many books does each student get?",
        }
        return templates.get(theme, templates[StoryTheme.SHOPPING])


# Synchronous wrapper for non-async contexts
def generate_story_sync(
    expression: str,
    answer: any,
    api_key: Optional[str] = None,
    theme: Optional[StoryTheme] = None
) -> GeneratedStory:
    """Synchronous story generation."""
    import asyncio

    generator = StoryGenerator(api_key)
    context = StoryContext(
        theme=theme or random.choice(list(StoryTheme)),
        character_name=random.choice(NAMES),
    )

    # Run async function synchronously
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(generator.generate(expression, answer, context))
    finally:
        loop.close()
