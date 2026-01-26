"""
Topic and subtopic routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...models import Topic, Subtopic
from ...schemas import TopicListResponse

router = APIRouter()


@router.get("/topics")
async def get_topics(
    grade_level: int = None,
    db: Session = Depends(get_db)
):
    """Get all available topics."""
    query = db.query(Topic).filter(Topic.is_active == True)

    if grade_level:
        query = query.filter(
            Topic.grade_range_start <= grade_level,
            Topic.grade_range_end >= grade_level
        )

    topics = query.order_by(Topic.display_order).all()

    result = []
    for topic in topics:
        subtopic_count = db.query(Subtopic).filter(
            Subtopic.topic_id == topic.id,
            Subtopic.is_active == True
        ).count()

        result.append({
            "id": topic.id,
            "name": topic.name,
            "slug": topic.slug,
            "description": topic.description,
            "grade_range": f"{topic.grade_range_start}-{topic.grade_range_end}",
            "grade_range_start": topic.grade_range_start,
            "grade_range_end": topic.grade_range_end,
            "subtopic_count": subtopic_count,
            "mastery_score": None,
        })

    return result


@router.get("/topics/{topic_slug}")
async def get_topic(topic_slug: str, db: Session = Depends(get_db)):
    """Get a specific topic with its subtopics."""
    topic = db.query(Topic).filter(
        Topic.slug == topic_slug,
        Topic.is_active == True
    ).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    subtopics = db.query(Subtopic).filter(
        Subtopic.topic_id == topic.id,
        Subtopic.is_active == True
    ).order_by(Subtopic.display_order).all()

    return {
        "id": topic.id,
        "name": topic.name,
        "slug": topic.slug,
        "description": topic.description,
        "grade_range": f"{topic.grade_range_start}-{topic.grade_range_end}",
        "grade_range_start": topic.grade_range_start,
        "grade_range_end": topic.grade_range_end,
        "subtopics": [
            {
                "id": s.id,
                "name": s.name,
                "slug": s.slug,
                "description": s.description,
            }
            for s in subtopics
        ]
    }


@router.post("/topics/seed")
async def seed_topics(db: Session = Depends(get_db)):
    """Seed initial topics (for development)."""
    # Check if already seeded
    if db.query(Topic).first():
        return {"message": "Topics already seeded"}

    # Create topics
    topics_data = [
        {
            "name": "Arithmetic",
            "slug": "arithmetic",
            "description": "Basic arithmetic operations: addition, subtraction, multiplication, division",
            "grade_range_start": 1,
            "grade_range_end": 6,
            "display_order": 1,
            "subtopics": [
                {"name": "Addition", "slug": "addition", "display_order": 1},
                {"name": "Subtraction", "slug": "subtraction", "display_order": 2},
                {"name": "Multiplication", "slug": "multiplication", "display_order": 3},
                {"name": "Division", "slug": "division", "display_order": 4},
                {"name": "Mixed Operations", "slug": "mixed", "display_order": 5},
            ]
        },
        {
            "name": "Fractions",
            "slug": "fractions",
            "description": "Operations with fractions",
            "grade_range_start": 3,
            "grade_range_end": 8,
            "display_order": 2,
            "subtopics": [
                {"name": "Adding Fractions", "slug": "addition", "display_order": 1},
                {"name": "Subtracting Fractions", "slug": "subtraction", "display_order": 2},
                {"name": "Multiplying Fractions", "slug": "multiplication", "display_order": 3},
                {"name": "Dividing Fractions", "slug": "division", "display_order": 4},
            ]
        },
        {
            "name": "Percentages",
            "slug": "percentages",
            "description": "Working with percentages",
            "grade_range_start": 5,
            "grade_range_end": 9,
            "display_order": 3,
            "subtopics": [
                {"name": "Finding Percentage", "slug": "find_percentage", "display_order": 1},
                {"name": "Finding Whole", "slug": "find_whole", "display_order": 2},
                {"name": "Percentage Change", "slug": "change", "display_order": 3},
            ]
        },
        {
            "name": "Algebra",
            "slug": "algebra",
            "description": "Algebraic equations and expressions",
            "grade_range_start": 6,
            "grade_range_end": 12,
            "display_order": 4,
            "subtopics": [
                {"name": "Linear Equations", "slug": "linear", "display_order": 1},
                {"name": "Quadratic Equations", "slug": "quadratic", "display_order": 2},
            ]
        },
        {
            "name": "Geometry",
            "slug": "geometry",
            "description": "Geometric calculations",
            "grade_range_start": 3,
            "grade_range_end": 12,
            "display_order": 5,
            "subtopics": [
                {"name": "Area", "slug": "area", "display_order": 1},
                {"name": "Perimeter", "slug": "perimeter", "display_order": 2},
                {"name": "Volume", "slug": "volume", "display_order": 3},
            ]
        },
        {
            "name": "Ratios",
            "slug": "ratios",
            "description": "Ratios and proportions",
            "grade_range_start": 5,
            "grade_range_end": 9,
            "display_order": 6,
            "subtopics": [
                {"name": "Simplifying Ratios", "slug": "simplify", "display_order": 1},
                {"name": "Proportions", "slug": "proportions", "display_order": 2},
            ]
        },
    ]

    for topic_data in topics_data:
        subtopics_data = topic_data.pop("subtopics", [])

        topic = Topic(**topic_data)
        db.add(topic)
        db.flush()  # Get the ID

        for subtopic_data in subtopics_data:
            subtopic = Subtopic(topic_id=topic.id, **subtopic_data)
            db.add(subtopic)

    db.commit()
    return {"message": "Topics seeded successfully"}
