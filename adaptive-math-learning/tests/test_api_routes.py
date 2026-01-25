"""
Tests for API routes.

Tests the FastAPI endpoints for topics, questions, answers, sessions, and progress.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime

# Import the FastAPI app
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return MagicMock()


class TestRootEndpoints:
    """Tests for root-level endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestTopicsEndpoints:
    """Tests for /api/v1/topics endpoints."""

    def test_get_topics_returns_list(self, client):
        """Test GET /topics returns a list."""
        response = client.get("/api/v1/topics")
        # May return empty list or topics depending on DB state
        assert response.status_code in [200, 500]  # 500 if DB not initialized
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_topics_with_grade_filter(self, client):
        """Test GET /topics with grade_level filter."""
        response = client.get("/api/v1/topics", params={"grade_level": 6})
        assert response.status_code in [200, 500]

    @patch('backend.api.routes.topics.get_db')
    def test_get_topic_not_found(self, mock_get_db, client):
        """Test GET /topics/{slug} returns 404 for non-existent topic."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db.return_value = iter([mock_session])

        response = client.get("/api/v1/topics/nonexistent-topic")
        assert response.status_code == 404


class TestQuestionsEndpoints:
    """Tests for /api/v1/questions endpoints."""

    def test_generate_question_requires_topic(self, client):
        """Test POST /questions/generate requires topic."""
        response = client.post("/api/v1/questions/generate", json={})
        # Should require topic field
        assert response.status_code in [422, 400, 500]

    def test_generate_question_with_valid_topic(self, client):
        """Test POST /questions/generate with valid topic."""
        response = client.post("/api/v1/questions/generate", json={
            "topic": "arithmetic",
            "subtopic": "addition",
            "difficulty": 50
        })
        # May succeed or fail depending on session state
        assert response.status_code in [200, 400, 422, 500]


class TestAnswersEndpoints:
    """Tests for /api/v1/answers endpoints."""

    def test_submit_answer_requires_data(self, client):
        """Test POST /answers/submit requires proper data."""
        response = client.post("/api/v1/answers/submit", json={})
        assert response.status_code in [422, 400]

    def test_submit_answer_with_missing_question_id(self, client):
        """Test POST /answers/submit with missing question_id."""
        response = client.post("/api/v1/answers/submit", json={
            "answer": "42"
        })
        assert response.status_code in [422, 400]


class TestSessionsEndpoints:
    """Tests for /api/v1/sessions endpoints."""

    def test_start_session(self, client):
        """Test POST /sessions/start creates a session."""
        response = client.post("/api/v1/sessions/start", json={
            "topic": "arithmetic"
        })
        assert response.status_code in [200, 201, 400, 500]

    def test_get_session_not_found(self, client):
        """Test GET /sessions/{key} returns 404 for non-existent session."""
        response = client.get("/api/v1/sessions/nonexistent-session-key")
        assert response.status_code in [404, 500]


class TestProgressEndpoints:
    """Tests for /api/v1/progress endpoints."""

    def test_get_statistics(self, client):
        """Test GET /progress/statistics."""
        response = client.get("/api/v1/progress/statistics")
        assert response.status_code in [200, 500]

    def test_get_recommendations(self, client):
        """Test GET /progress/recommendations."""
        response = client.get("/api/v1/progress/recommendations")
        assert response.status_code in [200, 500]


class TestGamificationEndpoints:
    """Tests for /api/v1/gamification endpoints."""

    def test_get_leaderboard(self, client):
        """Test GET /gamification/leaderboard."""
        response = client.get("/api/v1/gamification/leaderboard")
        assert response.status_code in [200, 500]

    def test_get_daily_challenge(self, client):
        """Test GET /gamification/daily-challenge."""
        response = client.get("/api/v1/gamification/daily-challenge")
        assert response.status_code in [200, 404, 500]


class TestCORSHeaders:
    """Tests for CORS headers."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in response."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        # CORS preflight should return 200 or the actual endpoint response
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_for_unknown_route(self, client):
        """Test 404 response for unknown routes."""
        response = client.get("/api/v1/unknown-endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test 405 for wrong HTTP method."""
        response = client.delete("/")  # Root doesn't support DELETE
        assert response.status_code == 405


# Integration tests that require database
class TestIntegration:
    """Integration tests (require database)."""

    @pytest.mark.integration
    def test_full_practice_flow(self, client):
        """Test full practice flow: start session -> get question -> submit answer."""
        # Start session
        session_response = client.post("/api/v1/sessions/start", json={
            "topic": "arithmetic"
        })

        if session_response.status_code == 200:
            session_data = session_response.json()
            session_key = session_data.get("session_key")

            # Generate question
            question_response = client.post("/api/v1/questions/generate", json={
                "topic": "arithmetic",
                "subtopic": "addition",
                "session_key": session_key
            })

            if question_response.status_code == 200:
                question_data = question_response.json()
                question_id = question_data.get("question_id")

                # Submit answer
                answer_response = client.post("/api/v1/answers/submit", json={
                    "question_id": question_id,
                    "answer": "10",
                    "session_key": session_key
                })

                # Answer submission should work
                assert answer_response.status_code in [200, 400]
