"""Regression tests for two further validator defects.

1. ``validate_profile_update`` passed ``min_length``/``max_length`` to
   ``Validator.validate_length``, whose parameters are actually named
   ``min_len``/``max_len``. Any payload containing ``display_name`` raised
   ``TypeError: Validator.validate_length() got an unexpected keyword
   argument 'min_length'`` -- the profile validator crashed on the most
   basic valid input.

2. That call site also accumulated failures with ``result.errors.extend(...)``
   instead of ``result.merge(...)``. ``ValidationResult.is_valid`` is a plain
   bool that only flips inside ``add_error()``/``merge()``, so extending the
   list directly left ``is_valid == True`` *with* a non-empty ``errors`` list.
   Any caller gating on ``.is_valid`` therefore accepted an invalid profile.
"""

from __future__ import annotations

from app.shared.validation.validator import Validator
from app.users.validators.user_validator import validate_profile_update


class TestProfileUpdateKwargNames:
    """validate_length must be called with the real parameter names."""

    def test_validate_length_accepts_min_len_max_len(self):
        result = Validator().validate_length("abc", "f", min_len=1, max_len=64)
        assert result.is_valid

    def test_profile_with_valid_display_name_does_not_raise(self):
        # Regression: TypeError on unexpected kwarg 'min_length'.
        result = validate_profile_update({"display_name": "Ada"})
        assert result.is_valid
        assert not result.errors

    def test_profile_without_display_name_does_not_raise(self):
        result = validate_profile_update({"bio": "hello"})
        assert result.is_valid


class TestProfileUpdateIsValidConsistency:
    """is_valid must never disagree with the errors list."""

    def test_empty_display_name_is_rejected_and_flagged(self):
        result = validate_profile_update({"display_name": ""})
        # Regression: is_valid stayed True because the errors were appended
        # directly rather than merged.
        assert result.errors, "empty display_name should be rejected"
        assert result.is_valid is False, "is_valid must be False when errors exist"

    def test_oversized_bio_is_rejected_and_flagged(self):
        result = validate_profile_update({"bio": "z" * 2000})
        assert result.errors
        assert result.is_valid is False

    def test_invalid_email_is_rejected_and_flagged(self):
        result = validate_profile_update({"email": "not-an-email"})
        assert result.errors
        assert result.is_valid is False

    def test_is_valid_always_agrees_with_errors(self):
        for payload in (
            {"display_name": "Ada"},
            {"display_name": ""},
            {"display_name": "z" * 500},
            {"bio": "hello"},
            {"bio": "z" * 2000},
            {"email": "a@b.co"},
            {"email": "bad"},
            {},
        ):
            result = validate_profile_update(payload)
            assert result.is_valid == (not result.errors), f"disagreement on {payload!r}"
