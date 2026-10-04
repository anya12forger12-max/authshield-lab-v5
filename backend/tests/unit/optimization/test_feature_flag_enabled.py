"""Regression tests for ``FeatureFlagService.get_enabled_flags``.

The service used to fetch a single *default* page from the repository and keep
only that page's ``items``. The repository answers with a paginated envelope and
applies the ``enabled_only`` filter itself, so every enabled flag past the first
page was silently dropped -- a rollout past the twentieth flag would simply never
take effect, with no error anywhere.

These tests drive the **real** in-memory repository rather than a mock, because a
``MagicMock`` will happily return whatever the test asks for and so cannot
reproduce data loss through pagination at all. The assertions compare *counts*
against the repository's own filtered query rather than pinning a flag to a
particular page index, which keeps them independent of its sort order: the defect
is that flags are dropped, not that any one of them lands in a particular slot.
"""

from __future__ import annotations

from typing import Any

from app.optimization.repositories.optimization_repository_impl import (
    InMemoryConfigProfileRepository,
    InMemoryFeatureFlagRepository,
)
from app.optimization.services.feature_flag_service import FeatureFlagService

# The repository's own default page size. A caller that keeps a single default page
# can therefore never see more than this many enabled flags, however many exist.
REPO_DEFAULT_PER_PAGE = 20

# Comfortably past the repository default, so an unfiltered single page is
# guaranteed to be short regardless of ordering.
OVER_DEFAULT_PAGE = REPO_DEFAULT_PER_PAGE + 10

# Past the 100-per-page fetch the corrected service uses, so the paging loop has to
# advance at least once for every flag to come back.
OVER_ONE_FETCH = 150


def _service() -> FeatureFlagService:
    return FeatureFlagService(InMemoryFeatureFlagRepository(), InMemoryConfigProfileRepository())


def _seed_enabled(repo: InMemoryFeatureFlagRepository, *, count: int) -> None:
    for i in range(count):
        repo.create({"name": f"flag-{i:03d}", "enabled": True})


def test_enabled_flags_past_the_default_page_are_not_dropped() -> None:
    """The regression: enabled flags past page 1 must survive."""
    repo = InMemoryFeatureFlagRepository()
    _seed_enabled(repo, count=OVER_DEFAULT_PAGE)
    service = FeatureFlagService(repo, InMemoryConfigProfileRepository())

    found = service.get_enabled_flags()
    # Ask the repository with a page large enough to hold everything: its own
    # default page is REPO_DEFAULT_PER_PAGE, so a default-sized query would
    # truncate the control and make this test unable to detect anything.
    everything = repo.get_all(per_page=OVER_ONE_FETCH, enabled_only=True)["items"]
    assert len(everything) == OVER_DEFAULT_PAGE, (
        "control is invalid: the repository itself does not see every enabled flag, "
        "so this test cannot detect anything the service does"
    )
    assert len(found) == OVER_DEFAULT_PAGE


def test_every_enabled_flag_is_returned_across_all_pages() -> None:
    """More enabled flags than one fetch can hold must all come back."""
    repo = InMemoryFeatureFlagRepository()
    _seed_enabled(repo, count=OVER_ONE_FETCH)
    service = FeatureFlagService(repo, InMemoryConfigProfileRepository())

    found = service.get_enabled_flags()
    assert len(found) == OVER_ONE_FETCH
    assert {f["name"] for f in found} == {f"flag-{i:03d}" for i in range(OVER_ONE_FETCH)}


def test_disabled_flags_are_still_excluded() -> None:
    """Paging must not turn into an unfiltered dump of the repository."""
    repo = InMemoryFeatureFlagRepository()
    _seed_enabled(repo, count=OVER_DEFAULT_PAGE)
    for i in range(OVER_DEFAULT_PAGE):
        repo.create({"name": f"off-{i:03d}", "enabled": False})
    service = FeatureFlagService(repo, InMemoryConfigProfileRepository())

    found = service.get_enabled_flags()
    assert len(found) == OVER_DEFAULT_PAGE
    assert all(f["enabled"] for f in found)
    assert not any(f["name"].startswith("off-") for f in found)


def test_service_agrees_with_the_repositorys_own_filtered_query() -> None:
    repo = InMemoryFeatureFlagRepository()
    _seed_enabled(repo, count=OVER_DEFAULT_PAGE)
    repo.create({"name": "only-disabled", "enabled": False})
    service = FeatureFlagService(repo, InMemoryConfigProfileRepository())

    expected = repo.get_all(per_page=OVER_ONE_FETCH, enabled_only=True)["items"]
    assert [f["name"] for f in service.get_enabled_flags()] == [f["name"] for f in expected]


def test_no_enabled_flags_returns_empty_list() -> None:
    repo = InMemoryFeatureFlagRepository()
    repo.create({"name": "only-disabled", "enabled": False})
    service = FeatureFlagService(repo, InMemoryConfigProfileRepository())

    assert service.get_enabled_flags() == []


def test_empty_repository_returns_empty_list() -> None:
    assert _service().get_enabled_flags() == []


def test_sequence_envelope_is_returned_defensively() -> None:
    """A non-dict envelope from an alternative implementation still works.

    The real repository always returns the paginated dict, so this branch needs a
    minimal stand-in -- it is the one branch a real repository cannot reach.
    """

    class _SequenceRepo(InMemoryFeatureFlagRepository):
        def get_all(self, **_kwargs: Any) -> Any:  # type: ignore[override]
            return [{"name": "a", "enabled": True}, "not-a-dict"]

    service = FeatureFlagService(_SequenceRepo(), InMemoryConfigProfileRepository())

    assert [f["name"] for f in service.get_enabled_flags()] == ["a"]
