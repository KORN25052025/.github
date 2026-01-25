# Adaptive Mathematics Learning System

An intelligent educational platform that provides personalized mathematics practice through adaptive question generation and AI-powered storytelling.

## Features

- **Deterministic Question Generation**: 100% mathematically correct questions
- **Adaptive Difficulty**: EMA-based mastery tracking adjusts difficulty automatically
- **AI Story Generation**: Transforms abstract equations into engaging word problems (OpenAI GPT)
- **Multiple Topics**: Arithmetic, Fractions, Percentages, Algebra, Geometry, Ratios
- **Progress Tracking**: Track mastery, streaks, and overall progress

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: SQLite
- **Math Engine**: Custom deterministic generators
- **AI**: OpenAI GPT-3.5 (optional)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Copy `.env.example` to `.env` and add your OpenAI API key for story generation:

```bash
cp .env.example .env
# Edit .env and add OPENAI_API_KEY=your_key
```

### 3. Start the Backend

```bash
python run_backend.py
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### 4. Seed Initial Data

Open a new terminal and run:

```bash
curl -X POST http://localhost:8000/api/v1/topics/seed
```

### 5. Start the Frontend

```bash
python run_frontend.py
```

Open `http://localhost:8501` in your browser.

## Project Structure

```
adaptive-math-learning/
├── backend/                    # FastAPI backend
│   ├── api/routes/            # API endpoints
│   │   ├── answers.py         # Answer validation
│   │   ├── questions.py       # Question generation
│   │   ├── progress.py        # Progress tracking
│   │   ├── sessions.py        # Learning sessions
│   │   └── topics.py          # Topic management
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   │   ├── answer_service.py  # Answer validation with explanations
│   │   └── question_service.py # Question orchestration
│   └── main.py                # Application entry
│
├── question_engine/            # Deterministic question generation
│   ├── generators/            # Topic-specific generators
│   │   ├── arithmetic.py      # +, -, *, / operations
│   │   ├── fractions.py       # Fraction operations
│   │   ├── percentages.py     # Percentage calculations
│   │   ├── algebra.py         # Linear & quadratic equations
│   │   ├── geometry.py        # Area, perimeter, volume
│   │   └── ratios.py          # Ratios and proportions
│   ├── base.py                # Base classes & types
│   ├── registry.py            # Generator registry
│   ├── difficulty.py          # Difficulty calculation
│   ├── distractor.py          # Distractor generation
│   └── sympy_utils.py         # SymPy integration
│
├── ai_integration/             # AI/LLM integration
│   ├── llm/                   # Story generation
│   │   ├── story_generator.py # LLM story generation
│   │   └── providers/         # LLM provider implementations
│   └── fallback.py            # Fallback mechanisms
│
├── adaptation/                 # Adaptive learning
│   ├── mastery_tracker.py     # EMA mastery tracking
│   └── difficulty_mapper.py   # Difficulty adjustment
│
├── frontend/                   # Streamlit frontend
│   ├── app.py                 # Main landing page
│   ├── pages/                 # Multi-page app pages
│   │   ├── home.py            # Home dashboard
│   │   ├── practice.py        # Question practice
│   │   ├── topics.py          # Topic browser
│   │   └── progress.py        # Progress dashboard
│   └── components/            # Reusable UI components
│       ├── question_display.py
│       ├── answer_input.py
│       └── feedback.py
│
├── data/                       # Data files
│   ├── seed/                  # Seed data
│   │   └── topics.json        # Topic definitions
│   └── math_learning.db       # SQLite database
│
├── seed_database.py           # Database seeding script
├── run_backend.py             # Backend runner
└── run_frontend.py            # Frontend runner
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/topics` | GET | List available topics |
| `/api/v1/questions/generate` | POST | Generate a new question |
| `/api/v1/answers/validate` | POST | Validate an answer |
| `/api/v1/sessions/start` | POST | Start a learning session |
| `/api/v1/progress/mastery` | GET | Get mastery scores |

## How It Works

### Question Generation

Questions are generated deterministically to guarantee mathematical correctness:

1. Select topic and operation
2. Generate parameters within difficulty-appropriate ranges
3. Compute correct answer using verified formulas
4. Generate pedagogically meaningful distractors

### Adaptive Difficulty

Uses Exponential Moving Average (EMA) for mastery tracking:

```
mastery_new = α × performance + (1 - α) × mastery_old
α = 0.3
```

- Correct answers increase mastery
- Mastery score determines next question's difficulty
- Provides smooth difficulty progression

### AI Story Generation (Optional)

When OpenAI API key is configured:

1. Abstract equation is sent to GPT
2. GPT generates an engaging word problem
3. Story preserves exact numerical values
4. Falls back to abstract equations if API fails

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Question Types

1. Create a new generator in `question_engine/generators/`
2. Extend `QuestionGenerator` base class
3. Register with `@register_generator` decorator
4. Add topic to database seed

## Team

- Emre Ekşi - Team Lead / Backend
- Ahmet Babagil - AI Integration
- Seda Naz Dolu - Frontend / UX
- Cemil Gündüz - Question Engine

## Question Types

### Arithmetic (Grades 1-6)
- Addition, Subtraction, Multiplication, Division
- Mixed operations
- Grade-appropriate number ranges
- Distractor types: sign errors, off-by-one, wrong operation

### Fractions (Grades 3-8)
- Adding/subtracting with like and unlike denominators
- Multiplying and dividing fractions
- Automatic simplification
- Mixed numbers support

### Percentages (Grades 5-9)
- Finding percentage of a number
- Finding the whole from percentage
- Percentage change (increase/decrease)
- Discounts and tax calculations

### Algebra (Grades 6-12)
- One-step equations (x + a = b, ax = b)
- Two-step equations (ax + b = c)
- Multi-step equations
- Variables on both sides
- Quadratic equations with integer solutions

### Geometry (Grades 3-12)
- Perimeter (square, rectangle, triangle)
- Area (rectangle, triangle, circle, parallelogram, trapezoid)
- Circumference
- Volume (cube, rectangular prism, cylinder, cone, sphere)
- Surface area
- Pythagorean theorem

### Ratios (Grades 5-9)
- Simplifying ratios
- Equivalent ratios
- Solving proportions
- Word problems
- Part-to-whole calculations
- Scale problems

## Distractor Generation

Each question type generates pedagogically meaningful distractors based on common student errors:

| Strategy | Description | Example |
|----------|-------------|---------|
| Sign Error | Wrong sign | Correct: 5, Distractor: -5 |
| Off-by-One | Close but wrong | Correct: 12, Distractor: 11, 13 |
| Wrong Operation | Common mix-up | Using + instead of * |
| Partial Solution | Incomplete work | Intermediate calculation result |
| Magnitude Error | Decimal place error | Correct: 0.5, Distractor: 5 |
| Not Simplified | Unsimplified answer | 4/8 instead of 1/2 |

## Running the Seeder

To populate the database with initial topics:

```bash
python seed_database.py
```

## License

MIT License - TOBB ETU BIL495/YAP495 Spring 2025
