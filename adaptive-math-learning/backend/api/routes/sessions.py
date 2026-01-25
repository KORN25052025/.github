"""
Session management routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from ...database import get_db
from ...models import LearningSession, Topic, Subtopic
from ...schemas import SessionStartRequest, SessionResponse, SessionSummaryResponse

router = APIRouter()


@router.post("/sessions/start", response_model=SessionResponse)
async def start_session(
    request: SessionStartRequest,
    db: Session = Depends(get_db)
):
    """Start a new learning session."""
    # Find topic
    topic = None
    topic_name = None

    if request.topic_id:
        topic = db.query(Topic).filter(Topic.id == request.topic_id).first()
    elif request.topic_slug:
        topic = db.query(Topic).filter(Topic.slug == request.topic_slug).first()

    if topic:
        topic_name = topic.name

    # Find subtopic
    subtopic = None
    subtopic_name = None

    if request.subtopic_id:
        subtopic = db.query(Subtopic).filter(Subtopic.id == request.subtopic_id).first()
        if subtopic:
            subtopic_name = subtopic.name

    # Create session
    session = LearningSession(
        session_key=str(uuid.uuid4())[:8],
        topic_id=topic.id if topic else None,
        subtopic_id=subtopic.id if subtopic else None,
        session_type=request.session_type,
        started_at=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionResponse(
        session_id=session.id,
        session_key=session.session_key,
        topic_id=session.topic_id,
        topic_name=topic_name,
        subtopic_id=session.subtopic_id,
        subtopic_name=subtopic_name,
        session_type=session.session_type,
        started_at=session.started_at,
        is_active=session.is_active,
    )


@router.post("/sessions/{session_key}/end", response_model=SessionSummaryResponse)
async def end_session(
    session_key: str,
    db: Session = Depends(get_db)
):
    """End a learning session."""
    session = db.query(LearningSession).filter(
        LearningSession.session_key == session_key
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.ended_at:
        raise HTTPException(status_code=400, detail="Session already ended")

    # End session
    session.ended_at = datetime.utcnow()
    db.commit()

    # Calculate duration
    duration = None
    if session.started_at and session.ended_at:
        duration = int((session.ended_at - session.started_at).total_seconds())

    return SessionSummaryResponse(
        session_id=session.id,
        session_key=session.session_key,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_seconds=duration,
        questions_attempted=session.questions_attempted,
        questions_correct=session.questions_correct,
        accuracy=session.accuracy,
    )


@router.get("/sessions/{session_key}", response_model=SessionResponse)
async def get_session(
    session_key: str,
    db: Session = Depends(get_db)
):
    """Get session details."""
    session = db.query(LearningSession).filter(
        LearningSession.session_key == session_key
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get topic and subtopic names
    topic_name = None
    subtopic_name = None

    if session.topic_id:
        topic = db.query(Topic).filter(Topic.id == session.topic_id).first()
        if topic:
            topic_name = topic.name

    if session.subtopic_id:
        subtopic = db.query(Subtopic).filter(Subtopic.id == session.subtopic_id).first()
        if subtopic:
            subtopic_name = subtopic.name

    return SessionResponse(
        session_id=session.id,
        session_key=session.session_key,
        topic_id=session.topic_id,
        topic_name=topic_name,
        subtopic_id=session.subtopic_id,
        subtopic_name=subtopic_name,
        session_type=session.session_type,
        started_at=session.started_at,
        is_active=session.is_active,
    )


@router.get("/sessions/active/current")
async def get_active_session(db: Session = Depends(get_db)):
    """Get the most recent active session."""
    session = db.query(LearningSession).filter(
        LearningSession.ended_at == None
    ).order_by(LearningSession.started_at.desc()).first()

    if not session:
        return {"message": "No active session", "session": None}

    return {
        "session_id": session.id,
        "session_key": session.session_key,
        "started_at": session.started_at.isoformat(),
    }
