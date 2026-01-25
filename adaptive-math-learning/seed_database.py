"""
Database seeding script.

Populates the database with initial topics and subtopics from the seed data.
"""

import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, init_db
from backend.models.topic import Topic, Subtopic


def load_seed_data():
    """Load seed data from JSON file."""
    seed_path = os.path.join(
        os.path.dirname(__file__),
        "data", "seed", "topics.json"
    )
    
    with open(seed_path, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_topics(db, topics_data):
    """Seed topics and subtopics into database."""
    for topic_data in topics_data:
        # Check if topic already exists
        existing = db.query(Topic).filter(
            Topic.slug == topic_data["slug"]
        ).first()
        
        if existing:
            print(f"Topic '{topic_data['name']}' already exists, skipping...")
            continue
        
        # Create topic
        topic = Topic(
            name=topic_data["name"],
            slug=topic_data["slug"],
            description=topic_data.get("description", ""),
            grade_range_start=topic_data.get("grade_range_start", 1),
            grade_range_end=topic_data.get("grade_range_end", 12),
            display_order=topic_data.get("display_order", 0),
            is_active=True,
        )
        db.add(topic)
        db.flush()  # Get the topic ID
        
        print(f"Created topic: {topic.name}")
        
        # Create subtopics
        for subtopic_data in topic_data.get("subtopics", []):
            subtopic = Subtopic(
                topic_id=topic.id,
                name=subtopic_data["name"],
                slug=subtopic_data["slug"],
                difficulty_base=subtopic_data.get("difficulty_base", 50),
                display_order=subtopic_data.get("display_order", 0),
                is_active=True,
            )
            db.add(subtopic)
            print(f"  Created subtopic: {subtopic.name}")
    
    db.commit()
    print("\nDatabase seeding completed!")


def main():
    """Main seeding function."""
    print("Initializing database...")
    init_db()
    
    print("Loading seed data...")
    seed_data = load_seed_data()
    
    print("Seeding topics...")
    db = SessionLocal()
    try:
        seed_topics(db, seed_data["topics"])
    finally:
        db.close()


if __name__ == "__main__":
    main()
