"""Regression tests for ``TemplateStudioService.get_templates_by_type``.

The service used to fetch a single *default* page from the repository and filter
it client-side. The repository answers with a paginated envelope and applies the
``template_type`` filter itself, so any match living past the first page was
silently dropped -- a caller received a short (or empty) list rather than an
error, and nothing raised anywhere. These tests drive the **real** in-memory
repository rather than a mock, because a ``MagicMock`` will happily return
whatever the test asks for and so cannot reproduce data loss through pagination
at all.

The assertions compare *counts* against the repository's own filtered query
rather than pinning a particular template to a particular page index. That keeps
them independent of the repository's sort order: the defect is that matches are
dropped, not that any one of them lands in a particular slot.
"""

from __future__ import annotations

from typing import Any

from app.content_studio.repositories.content_studio_repository_impl import (
    InMemoryContentTemplateRepository,
)
from app.content_studio.services.template_studio_service import TemplateStudioService

# The repository's own default page size. A caller that filters a single default
# page can therefore never see more than this many matches, however many exist.
REPO_DEFAULT_PER_PAGE = 20

# Comfortably past the repository default, so an unfiltered single page is
# guaranteed to be short regardless of ordering.
OVER_DEFAULT_PAGE = REPO_DEFAULT_PER_PAGE + 10

# Past the 100-per-page fetch the corrected service uses, so the paging loop has
# to advance at least once for every match to come back.
OVER_ONE_FETCH = 150


def _seed_types(
    repo: InMemoryContentTemplateRepository,
    *,
    wanted_type: str,
    count: int,
) -> None:
    for i in range(count):
        repo.create({"name": f"{wanted_type}-{i}", "template_type": wanted_type})


def test_matches_past_the_default_page_are_not_dropped() -> None:
    """The regression: matches past page 1 must survive the filter."""
    repo = InMemoryContentTemplateRepository()
    service = TemplateStudioService(repo)
    _seed_types(repo, wanted_type="rubric", count=OVER_DEFAULT_PAGE)

    found = service.get_templates_by_type("rubric")
    # Ask the repository with a page large enough to hold everything: its own
    # default page is REPO_DEFAULT_PER_PAGE, so a default-sized query would
    # truncate the control and make this test unable to detect anything.
    everything = repo.get_all(per_page=OVER_ONE_FETCH, template_type="rubric")["items"]
    assert len(everything) == OVER_DEFAULT_PAGE, (
        "control is invalid: the repository itself does not see every match, so "
        "this test cannot detect anything the service does"
    )
    assert len(found) == OVER_DEFAULT_PAGE


def test_every_match_is_returned_across_all_pages() -> None:
    """More matches than one fetch can hold must all come back."""
    repo = InMemoryContentTemplateRepository()
    service = TemplateStudioService(repo)
    _seed_types(repo, wanted_type="rubric", count=OVER_ONE_FETCH)

    found = service.get_templates_by_type("rubric")
    assert len(found) == OVER_ONE_FETCH
    assert {t["name"] for t in found} == {f"rubric-{i}" for i in range(OVER_ONE_FETCH)}


def test_filter_is_delegated_to_the_repository() -> None:
    """The service must agree with the repository's own filtered query."""
    repo = InMemoryContentTemplateRepository()
    service = TemplateStudioService(repo)
    _seed_types(repo, wanted_type="summary", count=OVER_DEFAULT_PAGE)
    repo.create({"name": "only-rubric", "template_type": "rubric"})

    expected = repo.get_all(per_page=OVER_ONE_FETCH, template_type="rubric")["items"]
    assert [t["name"] for t in service.get_templates_by_type("rubric")] == [
        t["name"] for t in expected
    ]
    assert len(service.get_templates_by_type("summary")) == OVER_DEFAULT_PAGE


def test_unknown_template_type_returns_empty_list() -> None:
    repo = InMemoryContentTemplateRepository()
    service = TemplateStudioService(repo)
    repo.create({"name": "a", "template_type": "summary"})

    assert service.get_templates_by_type("does-not-exist") == []


def test_empty_repository_returns_empty_list() -> None:
    service = TemplateStudioService(InMemoryContentTemplateRepository())

    assert service.get_templates_by_type("rubric") == []


def test_sequence_envelope_is_filtered_defensively() -> None:
    """A non-dict envelope from an alternative implementation still filters.

    The real repository always returns the paginated dict, so this branch needs a
    minimal stand-in -- it is the one branch a real repository cannot reach.
    """

    class _SequenceRepo(InMemoryContentTemplateRepository):
        def get_all(self, **_kwargs: Any) -> Any:  # type: ignore[override]
            return [
                {"name": "a", "template_type": "rubric"},
                {"name": "b", "template_type": "summary"},
            ]

    service = TemplateStudioService(_SequenceRepo())

    assert [t["name"] for t in service.get_templates_by_type("rubric")] == ["a"]
