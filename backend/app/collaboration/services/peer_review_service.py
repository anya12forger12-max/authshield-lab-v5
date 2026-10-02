"""Peer review service – create reviews, advance stages, add comments, make decisions, revision tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..domain.entities.peer_review import (
        PeerReview,
        ReviewComment,
        ReviewDecision,
        ReviewHistory,
        ReviewRevision,
    )
    from ..domain.interfaces import PeerReviewRepository


class PeerReviewService:
    _STAGE_ORDER = [
        "draft", "internal_review", "a11y_review", "technical_review",
        "educational_review", "approval", "publication", "archive",
    ]

    def __init__(self, repo: PeerReviewRepository) -> None:
        self._repo = repo

    def create_review(
        self,
        title: str,
        content_id: str,
        content_type: str,
        submitter: str,
    ) -> "PeerReview":
        from ..domain.entities.peer_review import PeerReview
        review = PeerReview(
            title=title,
            content_id=content_id,
            content_type=content_type,
            submitter=submitter,
        )
        self._repo.add_review(review)
        history = self._make_history(review.id)
        self._append_event(history, "draft", "created", submitter, f"Review '{title}' created")
        self._repo.add_history(history)
        return review

    def get_review(self, review_id: str):
        return self._repo.get_review(review_id)

    def list_reviews(self) -> list:
        return self._repo.all_reviews()

    def advance_stage(self, review_id: str, actor: str) -> "PeerReview":
        review = self._repo.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")
        current_idx = self._STAGE_ORDER.index(review.current_stage.value)
        if current_idx >= len(self._STAGE_ORDER) - 1:
            raise ValueError("Review is already at the final stage")
        next_stage = self._STAGE_ORDER[current_idx + 1]
        review.current_stage = next_stage
        self._repo.update_review(review)
        history = self._repo.get_history_for_review(review_id)
        if history is None:
            history = self._make_history(review_id)
            self._repo.add_history(history)
        self._append_event(history, next_stage, "stage_advanced", actor, f"Advanced to {next_stage}")
        self._repo.update_history(history)
        return review

    def add_comment(
        self,
        review_id: str,
        author: str,
        comment: str,
        severity: str | None = None,
    ) -> "ReviewComment":
        from ..domain.entities.peer_review import ReviewComment
        review = self._repo.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")
        c = ReviewComment(
            review_id=review_id,
            author=author,
            stage=review.current_stage,
            comment=comment,
            severity=severity,
        )
        self._repo.add_comment(c)
        history = self._repo.get_history_for_review(review_id)
        if history is None:
            history = self._make_history(review_id)
            self._repo.add_history(history)
        self._append_event(history, review.current_stage.value, "comment_added", author, comment[:100])
        self._repo.update_history(history)
        return c

    def make_decision(
        self,
        review_id: str,
        reviewer: str,
        decision: str,
        comments: str = "",
    ) -> "ReviewDecision":
        from ..domain.entities.peer_review import ReviewDecision, ReviewDecisionType
        review = self._repo.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")
        d = ReviewDecision(
            review_id=review_id,
            stage=review.current_stage,
            reviewer=reviewer,
            decision=ReviewDecisionType(decision),
            comments=comments,
        )
        self._repo.add_decision(d)
        history = self._repo.get_history_for_review(review_id)
        if history is None:
            history = self._make_history(review_id)
            self._repo.add_history(history)
        self._append_event(history, review.current_stage.value, "decision_made", reviewer, f"{decision}: {comments[:80]}")
        self._repo.update_history(history)
        return d

    def add_revision(
        self,
        review_id: str,
        changes: list[str] | None = None,
        author: str = "",
    ) -> "ReviewRevision":
        from ..domain.entities.peer_review import ReviewRevision
        existing = self._repo.get_revisions_for_review(review_id)
        next_number = len(existing) + 1
        revision = ReviewRevision(
            review_id=review_id,
            revision_number=next_number,
            changes=changes,
            author=author,
        )
        self._repo.add_revision(revision)
        history = self._repo.get_history_for_review(review_id)
        if history is None:
            history = self._make_history(review_id)
            self._repo.add_history(history)
        self._append_event(history, "draft", "revision_added", author, f"Revision #{next_number}")
        self._repo.update_history(history)
        return revision

    def get_revisions(self, review_id: str) -> list:
        return self._repo.get_revisions_for_review(review_id)

    def get_comments(self, review_id: str) -> list:
        return self._repo.get_comments_for_review(review_id)

    def get_decisions(self, review_id: str) -> list:
        return self._repo.get_decisions_for_review(review_id)

    def get_history(self, review_id: str):
        return self._repo.get_history_for_review(review_id)

    def get_comments_at_stage(self, review_id: str, stage: str) -> list:
        comments = self._repo.get_comments_for_review(review_id)
        return [c for c in comments if c.stage.value == stage]

    def _make_history(self, review_id: str) -> "ReviewHistory":
        from ..domain.entities.peer_review import ReviewHistory
        return ReviewHistory(review_id=review_id)

    def _append_event(self, history, stage: str, action: str, actor: str, details: str) -> None:
        from ..domain.entities.peer_review import ReviewEvent, ReviewStage
        event = ReviewEvent(
            stage=ReviewStage(stage),
            action=action,
            actor=actor,
            details=details,
        )
        history.events.append(event)
