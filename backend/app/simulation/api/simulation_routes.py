"""Simulation API routes."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from ..repositories.simulation_repository_impl import (
    InMemoryScenarioRepository,
    InMemoryDatasetRepository,
    InMemoryTimelineRepository,
    InMemoryExerciseRepository,
    InMemoryInstructorSessionRepository,
    InMemoryLearnerSessionRepository,
    InMemoryResultsRepository,
)
from ..services.scenario_service import ScenarioService
from ..services.dataset_generator import DeterministicGenerator
from ..services.timeline_service import TimelineService
from ..services.exercise_service import ExerciseService
from ..services.instructor_console import InstructorConsoleService
from ..services.learner_console import LearnerConsoleService
from ..services.replay_service import ReplayService
from ..services.results_service import ResultsService
from ..services.export_service import ExportService

router = APIRouter(prefix="/simulation", tags=["simulation"])

# ------------------------------------------------------------------
# Singleton repository instances
# ------------------------------------------------------------------
_scenario_repo = InMemoryScenarioRepository()
_dataset_repo = InMemoryDatasetRepository()
_timeline_repo = InMemoryTimelineRepository()
_exercise_repo = InMemoryExerciseRepository()
_instructor_session_repo = InMemoryInstructorSessionRepository()
_learner_session_repo = InMemoryLearnerSessionRepository()
_results_repo = InMemoryResultsRepository()

# ------------------------------------------------------------------
# Service instances
# ------------------------------------------------------------------
_scenario_service = ScenarioService(_scenario_repo)
_timeline_service = TimelineService(_timeline_repo)
_exercise_service = ExerciseService(_exercise_repo)
_instructor_console = InstructorConsoleService(
    _instructor_session_repo, _results_repo
)
_learner_console = LearnerConsoleService(_learner_session_repo)
_replay_service = ReplayService(_timeline_repo)
_results_service = ResultsService(_results_repo)
_export_service = ExportService()


# ====================================================================
# Scenario Routes
# ====================================================================


@router.post("/scenarios")
async def create_scenario(body: dict[str, Any]) -> dict[str, Any]:
    """Create a new simulation scenario."""
    try:
        scenario = await _scenario_service.create_scenario(
            title=body.get("title", ""),
            description=body.get("description", ""),
            difficulty=body.get("difficulty", "beginner"),
            learning_objectives=body.get("learning_objectives"),
            prerequisites=body.get("prerequisites"),
            estimated_duration_minutes=body.get("estimated_duration_minutes", 30),
            target_audience=body.get("target_audience", ""),
            required_competencies=body.get("required_competencies"),
            tags=body.get("tags"),
            scenario_type=body.get("scenario_type", "AuthenticationReview"),
            created_by=body.get("created_by", ""),
            metadata=body.get("metadata"),
        )
        return {"status": "success", "data": scenario.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/scenarios")
async def list_scenarios(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """List all scenarios with pagination."""
    result = await _scenario_service.list_scenarios(page=page, per_page=per_page)
    return {
        "status": "success",
        "items": [s.to_dict() for s in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"],
    }


@router.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str) -> dict[str, Any]:
    """Get a scenario by ID."""
    scenario = await _scenario_service.get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"status": "success", "data": scenario.to_dict()}


@router.put("/scenarios/{scenario_id}")
async def update_scenario(
    scenario_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Update an existing scenario."""
    result = await _scenario_service.update_scenario(scenario_id, body)
    if result is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"status": "success", "data": result.to_dict()}


@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str) -> dict[str, Any]:
    """Delete a scenario."""
    deleted = await _scenario_service.delete_scenario(scenario_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"status": "success", "message": "Scenario deleted"}


@router.post("/scenarios/{scenario_id}/publish")
async def publish_scenario(scenario_id: str) -> dict[str, Any]:
    """Publish a scenario."""
    try:
        scenario = await _scenario_service.publish_scenario(scenario_id)
        return {"status": "success", "data": scenario.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/scenarios/{scenario_id}/archive")
async def archive_scenario(scenario_id: str) -> dict[str, Any]:
    """Archive a scenario."""
    try:
        scenario = await _scenario_service.archive_scenario(scenario_id)
        return {"status": "success", "data": scenario.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/scenarios/{scenario_id}/clone")
async def clone_scenario(scenario_id: str) -> dict[str, Any]:
    """Clone a scenario."""
    try:
        scenario = await _scenario_service.clone_scenario(scenario_id)
        return {"status": "success", "data": scenario.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/scenarios/search")
async def search_scenarios(
    q: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """Search scenarios by query."""
    result = await _scenario_service.search_scenarios(q, page=page, per_page=per_page)
    return {
        "status": "success",
        "items": [s.to_dict() for s in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"],
    }


# ====================================================================
# Dataset Routes
# ====================================================================


@router.post("/datasets/generate")
async def generate_dataset(body: dict[str, Any]) -> dict[str, Any]:
    """Generate a deterministic synthetic dataset."""
    seed = body.get("seed", 42)
    name = body.get("name", "Generated Dataset")
    description = body.get("description", "Synthetic dataset")

    generator = DeterministicGenerator(seed=seed)
    dataset = generator.generate_full_dataset(name=name, description=description)
    created = await _dataset_repo.create(dataset)

    return {"status": "success", "data": created.to_dict()}


@router.get("/datasets")
async def list_datasets(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """List all datasets."""
    result = await _dataset_repo.get_all(page=page, per_page=per_page)
    return {
        "status": "success",
        "items": [d.to_dict() for d in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"],
    }


@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str) -> dict[str, Any]:
    """Get a dataset by ID."""
    dataset = await _dataset_repo.get_by_id(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"status": "success", "data": dataset.to_dict()}


@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str) -> dict[str, Any]:
    """Delete a dataset."""
    deleted = await _dataset_repo.delete(dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"status": "success", "message": "Dataset deleted"}


@router.get("/datasets/{dataset_id}/export/csv", response_class=PlainTextResponse)
async def export_dataset_csv(dataset_id: str) -> str:
    """Export a dataset as CSV."""
    dataset = await _dataset_repo.get_by_id(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return _export_service.export_dataset_csv(dataset)


# ====================================================================
# Timeline Routes
# ====================================================================


@router.post("/timelines")
async def create_timeline(body: dict[str, Any]) -> dict[str, Any]:
    """Create a new timeline."""
    try:
        timeline = await _timeline_service.create_timeline(
            name=body.get("name", ""),
            scenario_id=body.get("scenario_id", ""),
        )
        return {"status": "success", "data": timeline.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/timelines")
async def list_timelines(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """List all timelines."""
    result = await _timeline_service.list_timelines(page=page, per_page=per_page)
    return {
        "status": "success",
        "items": [t.to_dict() for t in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"],
    }


@router.get("/timelines/{timeline_id}")
async def get_timeline(timeline_id: str) -> dict[str, Any]:
    """Get a timeline by ID."""
    timeline = await _timeline_service.get_timeline(timeline_id)
    if timeline is None:
        raise HTTPException(status_code=404, detail="Timeline not found")
    return {"status": "success", "data": timeline.to_dict()}


@router.delete("/timelines/{timeline_id}")
async def delete_timeline(timeline_id: str) -> dict[str, Any]:
    """Delete a timeline."""
    deleted = await _timeline_service.delete_timeline(timeline_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Timeline not found")
    return {"status": "success", "message": "Timeline deleted"}


@router.post("/timelines/{timeline_id}/events")
async def add_timeline_event(
    timeline_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Add an event to a timeline."""
    try:
        event = await _timeline_service.add_event(
            timeline_id=timeline_id,
            event_type=body.get("event_type", ""),
            timestamp_offset_ms=body.get("timestamp_offset_ms", 0),
            data=body.get("data"),
            milestone=body.get("milestone", False),
            instructor_annotation=body.get("instructor_annotation", ""),
            learner_checkpoint=body.get("learner_checkpoint", False),
            replay_marker=body.get("replay_marker", False),
        )
        return {"status": "success", "data": event.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/timelines/{timeline_id}/events/{event_id}")
async def remove_timeline_event(
    timeline_id: str, event_id: str
) -> dict[str, Any]:
    """Remove an event from a timeline."""
    try:
        removed = await _timeline_service.remove_event(timeline_id, event_id)
        if not removed:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"status": "success", "message": "Event removed"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/timelines/{timeline_id}/branches")
async def add_timeline_branch(
    timeline_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Add a branch to a timeline."""
    try:
        branch = await _timeline_service.add_branch(
            timeline_id=timeline_id,
            source_event_id=body.get("source_event_id", ""),
            target_event_id=body.get("target_event_id", ""),
            condition=body.get("condition", ""),
        )
        return {"status": "success", "data": branch.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/timelines/{timeline_id}/milestones")
async def get_timeline_milestones(timeline_id: str) -> dict[str, Any]:
    """Get milestones for a timeline."""
    try:
        milestones = await _timeline_service.get_milestones(timeline_id)
        return {
            "status": "success",
            "items": [m.to_dict() for m in milestones],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ====================================================================
# Exercise Routes
# ====================================================================


@router.post("/exercises")
async def create_exercise(body: dict[str, Any]) -> dict[str, Any]:
    """Create a new exercise."""
    try:
        exercise = await _exercise_service.create_exercise(
            title=body.get("title", ""),
            description=body.get("description", ""),
            scenario_id=body.get("scenario_id", ""),
            category=body.get("category", ""),
            tags=body.get("tags"),
            difficulty=body.get("difficulty", 1),
            learning_outcomes=body.get("learning_outcomes"),
            estimated_completion_minutes=body.get(
                "estimated_completion_minutes", 30
            ),
        )
        return {"status": "success", "data": exercise.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/exercises")
async def list_exercises(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """List all exercises."""
    result = await _exercise_service.list_exercises(page=page, per_page=per_page)
    return {
        "status": "success",
        "items": [e.to_dict() for e in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"],
    }


@router.get("/exercises/{exercise_id}")
async def get_exercise(exercise_id: str) -> dict[str, Any]:
    """Get an exercise by ID."""
    exercise = await _exercise_service.get_exercise(exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return {"status": "success", "data": exercise.to_dict()}


@router.put("/exercises/{exercise_id}")
async def update_exercise(
    exercise_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Update an existing exercise."""
    result = await _exercise_service.update_exercise(exercise_id, body)
    if result is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return {"status": "success", "data": result.to_dict()}


@router.delete("/exercises/{exercise_id}")
async def delete_exercise(exercise_id: str) -> dict[str, Any]:
    """Delete an exercise."""
    deleted = await _exercise_service.delete_exercise(exercise_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return {"status": "success", "message": "Exercise deleted"}


@router.post("/exercises/{exercise_id}/favorite")
async def toggle_exercise_favorite(exercise_id: str) -> dict[str, Any]:
    """Toggle favorite on an exercise."""
    try:
        exercise = await _exercise_service.toggle_favorite(exercise_id)
        return {"status": "success", "data": exercise.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/exercises/{exercise_id}/clone")
async def clone_exercise(exercise_id: str) -> dict[str, Any]:
    """Clone an exercise."""
    try:
        exercise = await _exercise_service.clone_exercise(exercise_id)
        return {"status": "success", "data": exercise.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/exercises/{exercise_id}/publish")
async def publish_exercise(exercise_id: str) -> dict[str, Any]:
    """Publish an exercise."""
    try:
        exercise = await _exercise_service.publish_exercise(exercise_id)
        return {"status": "success", "data": exercise.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/exercises/search")
async def search_exercises(
    q: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """Search exercises."""
    result = await _exercise_service.search_exercises(q, page=page, per_page=per_page)
    return {
        "status": "success",
        "items": [e.to_dict() for e in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"],
    }


# ====================================================================
# Instructor Console Routes
# ====================================================================


@router.post("/instructor/sessions")
async def launch_instructor_session(body: dict[str, Any]) -> dict[str, Any]:
    """Launch an instructor session."""
    try:
        session = await _instructor_console.launch_session(
            instructor_id=body.get("instructor_id", ""),
            exercise_id=body.get("exercise_id", ""),
        )
        return {"status": "success", "data": session.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/instructor/sessions")
async def list_instructor_sessions(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """List all instructor sessions."""
    result = await _instructor_console.list_sessions(page=page, per_page=per_page)
    return {
        "status": "success",
        "items": [s.to_dict() for s in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"],
    }


@router.get("/instructor/sessions/{session_id}")
async def get_instructor_session(session_id: str) -> dict[str, Any]:
    """Get an instructor session."""
    session = await _instructor_console.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "data": session.to_dict()}


@router.post("/instructor/sessions/{session_id}/pause")
async def pause_instructor_session(session_id: str) -> dict[str, Any]:
    """Pause an instructor session."""
    try:
        session = await _instructor_console.pause_session(session_id)
        return {"status": "success", "data": session.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/instructor/sessions/{session_id}/resume")
async def resume_instructor_session(session_id: str) -> dict[str, Any]:
    """Resume an instructor session."""
    try:
        session = await _instructor_console.resume_session(session_id)
        return {"status": "success", "data": session.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/instructor/sessions/{session_id}/complete")
async def complete_instructor_session(session_id: str) -> dict[str, Any]:
    """Complete an instructor session."""
    try:
        session = await _instructor_console.complete_session(session_id)
        return {"status": "success", "data": session.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/instructor/sessions/{session_id}/review")
async def review_session(
    session_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Review and grade a learner session."""
    try:
        result = await _instructor_console.review_and_grade(
            session_id=session_id,
            result_id=body.get("result_id", ""),
            scores=body.get("scores", {}),
            feedback=body.get("feedback", ""),
            competency_updates=body.get("competency_updates"),
            recommendations=body.get("recommendations"),
        )
        return {"status": "success", "data": result.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ====================================================================
# Learner Console Routes
# ====================================================================


@router.post("/learner/sessions")
async def assign_learner_exercise(body: dict[str, Any]) -> dict[str, Any]:
    """Assign an exercise to a learner."""
    try:
        session = await _learner_console.assign_exercise(
            learner_id=body.get("learner_id", ""),
            exercise_id=body.get("exercise_id", ""),
            accessibility_settings=body.get("accessibility_settings"),
        )
        return {"status": "success", "data": session.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/learner/sessions")
async def list_learner_sessions(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """List all learner sessions."""
    result = await _learner_console.list_sessions(page=page, per_page=per_page)
    return {
        "status": "success",
        "items": [s.to_dict() for s in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"],
    }


@router.get("/learner/sessions/{session_id}")
async def get_learner_session(session_id: str) -> dict[str, Any]:
    """Get a learner session."""
    session = await _learner_console.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "data": session.to_dict()}


@router.post("/learner/sessions/{session_id}/start")
async def start_learner_session(session_id: str) -> dict[str, Any]:
    """Start a learner session."""
    try:
        session = await _learner_console.start_session(session_id)
        return {"status": "success", "data": session.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/learner/sessions/{session_id}/evidence")
async def add_learner_evidence(
    session_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Add evidence to a learner session."""
    try:
        session = await _learner_console.add_evidence(
            session_id, body.get("evidence", "")
        )
        return {"status": "success", "data": session.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/learner/sessions/{session_id}/reflection")
async def add_learner_reflection(
    session_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Add a reflection to a learner session."""
    try:
        session = await _learner_console.add_reflection(
            session_id, body.get("reflection", "")
        )
        return {"status": "success", "data": session.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/learner/sessions/{session_id}/submit")
async def submit_learner_work(
    session_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Submit work for a learner session."""
    try:
        submission = await _learner_console.submit(
            session_id, body.get("content", "")
        )
        return {"status": "success", "data": submission.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/learner/sessions/{session_id}/complete")
async def complete_learner_session(session_id: str) -> dict[str, Any]:
    """Complete a learner session."""
    try:
        session = await _learner_console.complete_session(session_id)
        return {"status": "success", "data": session.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ====================================================================
# Replay Routes
# ====================================================================


@router.post("/replay/{timeline_id}/start")
async def start_replay(
    timeline_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Start a timeline replay."""
    try:
        result = await _replay_service.start_replay(
            timeline_id=timeline_id,
            initiated_by=body.get("initiated_by", ""),
            speed_multiplier=body.get("speed_multiplier", 1.0),
            highlighted_event_ids=body.get("highlighted_event_ids"),
        )
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/replay/{timeline_id}/state")
async def get_replay_state(
    timeline_id: str,
    offset_ms: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    """Get replay state at a specific offset."""
    try:
        state = await _replay_service.get_playback_state(
            timeline_id, offset_ms
        )
        return {"status": "success", "data": state}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/replay/compare")
async def compare_timelines(body: dict[str, Any]) -> dict[str, Any]:
    """Compare two timelines."""
    try:
        result = await _replay_service.compare_timelines(
            body.get("timeline_a", ""),
            body.get("timeline_b", ""),
        )
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ====================================================================
# Results Routes
# ====================================================================


@router.post("/results")
async def create_result(body: dict[str, Any]) -> dict[str, Any]:
    """Create a new exercise result."""
    try:
        result = await _results_service.create_result(
            session_id=body.get("session_id", ""),
            exercise_id=body.get("exercise_id", ""),
        )
        return {"status": "success", "data": result.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/results")
async def list_results(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """List all results."""
    result = await _results_service.list_results(page=page, per_page=per_page)
    return {
        "status": "success",
        "items": [r.to_dict() for r in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"],
    }


@router.get("/results/{result_id}")
async def get_result(result_id: str) -> dict[str, Any]:
    """Get a result by ID."""
    result = await _results_service.get_result(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"status": "success", "data": result.to_dict()}


@router.post("/results/{result_id}/finalize")
async def finalize_result(result_id: str) -> dict[str, Any]:
    """Calculate and finalize a result."""
    try:
        result = await _results_service.calculate_and_finalize(result_id)
        return {"status": "success", "data": result.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/results/exercise/{exercise_id}/stats")
async def get_exercise_stats(exercise_id: str) -> dict[str, Any]:
    """Get score statistics for an exercise."""
    stats = await _results_service.get_score_statistics(exercise_id)
    return {"status": "success", "data": stats}


# ====================================================================
# Export Routes
# ====================================================================


@router.get("/export/scenario/{scenario_id}/json")
async def export_scenario_json(scenario_id: str) -> dict[str, Any]:
    """Export a scenario to JSON."""
    scenario = await _scenario_service.get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    json_str = _export_service.export_scenario_json(scenario)
    return {"status": "success", "data": json.loads(json_str)}


@router.get(
    "/export/scenario/{scenario_id}/markdown",
    response_class=PlainTextResponse,
)
async def export_scenario_markdown(scenario_id: str) -> str:
    """Export a scenario to Markdown."""
    scenario = await _scenario_service.get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return _export_service.export_scenario_markdown(scenario)


@router.get(
    "/export/exercise/{exercise_id}/markdown",
    response_class=PlainTextResponse,
)
async def export_exercise_markdown(exercise_id: str) -> str:
    """Export an exercise to Markdown."""
    exercise = await _exercise_service.get_exercise(exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return _export_service.export_exercise_markdown(exercise)


@router.get(
    "/export/timeline/{timeline_id}/markdown",
    response_class=PlainTextResponse,
)
async def export_timeline_markdown(timeline_id: str) -> str:
    """Export a timeline to Markdown."""
    timeline = await _timeline_service.get_timeline(timeline_id)
    if timeline is None:
        raise HTTPException(status_code=404, detail="Timeline not found")
    return _export_service.export_timeline_markdown(timeline)


@router.get("/export/results/{result_id}/json")
async def export_results_json(result_id: str) -> dict[str, Any]:
    """Export results to JSON."""
    result = await _results_service.get_result(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    json_str = _export_service.export_results_json(result)
    return {"status": "success", "data": json.loads(json_str)}


@router.get(
    "/export/results/{result_id}/markdown",
    response_class=PlainTextResponse,
)
async def export_results_markdown(result_id: str) -> str:
    """Export results to Markdown."""
    result = await _results_service.get_result(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return _export_service.export_results_markdown(result)
