"""FastAPI API routes for the Content Studio module."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from ..repositories.content_repository_impl import (
    InMemoryCourseRepository,
    InMemoryLessonRepository,
    InMemoryQuizRepository,
    InMemoryMediaRepository,
    InMemoryKnowledgeNodeRepository,
)
from ..services.course_service import CourseService
from ..services.lesson_service import LessonService
from ..services.quiz_service import QuizService
from ..services.media_service import MediaService
from ..services.knowledge_service import KnowledgeService
from ..validators.content_validator import ContentValidator

router = APIRouter(prefix="/content", tags=["content-studio"])

# Shared in-memory instances (sufficient for an offline educational platform)
_course_repo = InMemoryCourseRepository()
_lesson_repo = InMemoryLessonRepository()
_quiz_repo = InMemoryQuizRepository()
_media_repo = InMemoryMediaRepository()
_knowledge_repo = InMemoryKnowledgeNodeRepository()
_validator = ContentValidator()

_course_service = CourseService(_course_repo, _validator)
_lesson_service = LessonService(_lesson_repo, _validator)
_quiz_service = QuizService(_quiz_repo, _validator)
_media_service = MediaService(_media_repo, _validator)
_knowledge_service = KnowledgeService(_knowledge_repo)


# ---------------------------------------------------------------------------
# Course endpoints
# ---------------------------------------------------------------------------


@router.post("/courses", status_code=201)
async def create_course(body: dict[str, Any]) -> dict[str, Any]:
    """Create a new course."""
    try:
        course = await _course_service.create_course(
            title=body.get("title", ""),
            description=body.get("description", ""),
            difficulty=body.get("difficulty", "beginner"),
            learning_objectives=body.get("learning_objectives", []),
            prerequisites=body.get("prerequisites", []),
            estimated_hours=body.get("estimated_hours", 0.0),
            target_audience=body.get("target_audience", ""),
            required_competencies=body.get("required_competencies", []),
            tags=body.get("tags", []),
            created_by=body.get("created_by", ""),
        )
        return {"status": "success", "data": course.__dict__}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courses")
async def list_courses(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    difficulty: str | None = Query(default=None),
    status: str | None = Query(default=None),
    tags: str | None = Query(default=None),
) -> dict[str, Any]:
    """List courses with optional filters."""
    try:
        filters: dict[str, Any] = {}
        if difficulty:
            filters["difficulty"] = difficulty
        if status:
            filters["status"] = status
        if tags:
            filters["tags"] = [t.strip() for t in tags.split(",")]
        result = await _course_service.list_courses(
            offset=offset, limit=limit, filters=filters if filters else None
        )
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courses/{course_id}")
async def get_course(course_id: str) -> dict[str, Any]:
    """Get a specific course by ID."""
    try:
        course = await _course_service.get_course(course_id)
        if course is None:
            raise HTTPException(status_code=404, detail=f"Course {course_id} not found.")
        return {"status": "success", "data": course.__dict__}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/courses/{course_id}")
async def update_course(course_id: str, body: dict[str, Any]) -> dict[str, Any]:
    """Update a course."""
    try:
        course = await _course_service.update_course(course_id, body)
        return {"status": "success", "data": course.__dict__}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/courses/{course_id}/publish")
async def publish_course(course_id: str) -> dict[str, Any]:
    """Publish a course."""
    try:
        course = await _course_service.publish_course(course_id)
        return {"status": "success", "message": f"Course '{course.title}' published.", "data": course.__dict__}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/courses/{course_id}/clone")
async def clone_course(course_id: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    """Clone a course."""
    try:
        new_title = body.get("title") if body else None
        cloned = await _course_service.clone_course(course_id, new_title=new_title)
        return {"status": "success", "data": cloned.__dict__}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Lesson endpoints
# ---------------------------------------------------------------------------


@router.get("/courses/{course_id}/lessons")
async def list_lessons(course_id: str) -> dict[str, Any]:
    """List all lessons for a course."""
    try:
        lessons = await _lesson_service.list_lessons_by_course(course_id)
        return {
            "status": "success",
            "items": [l.__dict__ for l in lessons],
            "total": len(lessons),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/courses/{course_id}/lessons", status_code=201)
async def create_lesson(course_id: str, body: dict[str, Any]) -> dict[str, Any]:
    """Create a new lesson in a course."""
    try:
        lesson = await _lesson_service.create_lesson(
            course_id=course_id,
            title=body.get("title", ""),
            content=body.get("content", ""),
            order=body.get("order", 0),
            lesson_type=body.get("lesson_type", "theory"),
            estimated_minutes=body.get("estimated_minutes", 30),
            learning_objectives=body.get("learning_objectives", []),
            media_refs=body.get("media_refs", []),
            accessible=body.get("accessible", True),
        )
        return {"status": "success", "data": lesson.__dict__}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Quiz endpoints
# ---------------------------------------------------------------------------


@router.post("/courses/{course_id}/quizzes", status_code=201)
async def create_quiz(course_id: str, body: dict[str, Any]) -> dict[str, Any]:
    """Create a new quiz in a course."""
    try:
        quiz = await _quiz_service.create_quiz(
            course_id=course_id,
            title=body.get("title", ""),
            passing_score=body.get("passing_score", 70.0),
            time_limit_minutes=body.get("time_limit_minutes", 30),
            shuffle_questions=body.get("shuffle_questions", False),
        )
        return {"status": "success", "data": quiz.__dict__}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quizzes/{quiz_id}/grade")
async def grade_quiz(quiz_id: str, body: dict[str, Any]) -> dict[str, Any]:
    """Grade a quiz submission."""
    try:
        answers = body.get("answers", {})
        result = await _quiz_service.grade_quiz(quiz_id, answers)
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Media endpoints
# ---------------------------------------------------------------------------


@router.get("/media")
async def list_media(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    media_type: str | None = Query(default=None),
) -> dict[str, Any]:
    """List media assets with optional type filter."""
    try:
        if media_type:
            assets = await _media_service.get_assets_by_type(media_type)
        else:
            assets = await _media_service.list_assets(offset=offset, limit=limit)
        return {
            "status": "success",
            "items": [a.__dict__ for a in assets],
            "total": len(assets),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/media", status_code=201)
async def create_media(body: dict[str, Any]) -> dict[str, Any]:
    """Register a new media asset."""
    try:
        asset = await _media_service.register_asset(
            title=body.get("title", ""),
            media_type=body.get("media_type", ""),
            uri=body.get("uri", ""),
            alt_text=body.get("alt_text", ""),
            caption=body.get("caption", ""),
            transcript=body.get("transcript", ""),
            accessible=body.get("accessible", True),
        )
        return {"status": "success", "data": asset.__dict__}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Knowledge graph endpoints
# ---------------------------------------------------------------------------


@router.get("/knowledge/nodes")
async def list_knowledge_nodes() -> dict[str, Any]:
    """Return the full knowledge graph."""
    try:
        graph = await _knowledge_service.get_node_graph()
        return {"status": "success", "data": graph}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/nodes", status_code=201)
async def create_knowledge_node(body: dict[str, Any]) -> dict[str, Any]:
    """Create a new knowledge node."""
    try:
        node = await _knowledge_service.create_node(
            title=body.get("title", ""),
            description=body.get("description", ""),
            node_type=body.get("node_type", "concept"),
            related_nodes=body.get("related_nodes", []),
            prerequisites=body.get("prerequisites", []),
            competencies=body.get("competencies", []),
        )
        return {"status": "success", "data": node.__dict__}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/link")
async def link_knowledge_nodes(body: dict[str, Any]) -> dict[str, Any]:
    """Create a bidirectional link between two knowledge nodes."""
    try:
        result = await _knowledge_service.link_nodes(
            source_id=body.get("source_id", ""),
            target_id=body.get("target_id", ""),
        )
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Search endpoint
# ---------------------------------------------------------------------------


@router.get("/search")
async def search_content(
    q: str = Query(default="", max_length=128),
    type: str | None = Query(default=None),
) -> dict[str, Any]:
    """Search across content types."""
    try:
        results: dict[str, Any] = {"courses": [], "knowledge_nodes": []}
        if not type or type == "course":
            courses = await _course_service.search_courses(q)
            results["courses"] = [c.__dict__ for c in courses]
        if not type or type == "knowledge_node":
            nodes = await _knowledge_service.search_by_tag(q)
            results["knowledge_nodes"] = [n.__dict__ for n in nodes]
        total = len(results["courses"]) + len(results["knowledge_nodes"])
        return {"status": "success", "total": total, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
