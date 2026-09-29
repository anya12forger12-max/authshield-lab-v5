"""Deterministic synthetic data generator for simulation datasets."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, TypeVar

from ..domain.entities.dataset import (
    DatasetArtifact,
    DatasetArtifactType,
    DatasetMetadata,
    SyntheticDataset,
)

_T = TypeVar("_T")


class DeterministicGenerator:
    """Generates realistic synthetic cybersecurity data deterministically.

    All randomness is sourced from a seeded ``random.Random`` instance,
    ensuring identical output for the same seed across runs.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self._rng = random.Random(seed)
        self._base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)

    def _random_ip(self) -> str:
        """Generate a fake 192.168.x.x IP address."""
        return f"192.168.{self._rng.randint(1, 254)}.{self._rng.randint(1, 254)}"

    def _random_username(self) -> str:
        """Generate a fake username like user_001."""
        idx = self._rng.randint(1, 500)
        return f"user_{idx:03d}"

    def _random_timestamp(self, offset_hours: int = 0) -> str:
        """Generate a random timestamp near the base time."""
        delta = timedelta(
            hours=self._rng.randint(0 + offset_hours, 720 + offset_hours),
            minutes=self._rng.randint(0, 59),
            seconds=self._rng.randint(0, 59),
        )
        return (self._base_time + delta).isoformat()

    def _random_event_id(self) -> str:
        """Generate a random hex event ID."""
        return uuid.UUID(
            bytes=self._rng.getrandbits(128).to_bytes(16, "big"),
            version=4,
        ).hex[:16]

    def _random_choice(self, items: list[_T]) -> _T:
        """Pick a random item from a list.

        Generic over the item type: most call sites pass a flat list of
        strings, but a few pass a list of lists (e.g. the assistive-technology
        and compliance-framework columns), and this helper is sometimes handed
        the result of another call to itself. Declaring the return as ``str``
        was a lie for those sites -- the value flows into a JSON-serialized
        artifact, so it is correct at runtime, but the annotation misdescribed
        it and mypy flagged every one of those list items.
        """
        return self._rng.choice(items)

    def _random_bool(self, probability: float = 0.5) -> bool:
        """Return a random boolean with given probability of True."""
        return self._rng.random() < probability

    def _random_status(self) -> str:
        """Generate a random auth status."""
        return self._random_choice(["success", "failure", "success", "success", "failure"])

    def _random_method(self) -> str:
        """Generate a random authentication method."""
        return self._random_choice(["password", "token", "biometric", "mfa", "sso"])

    def _random_role(self) -> str:
        """Generate a random role name."""
        return self._random_choice(
            [
                "admin",
                "editor",
                "viewer",
                "analyst",
                "auditor",
                "manager",
                "developer",
                "operator",
            ]
        )

    def _random_severity(self) -> str:
        """Generate a random severity level."""
        return self._random_choice(["low", "medium", "high", "critical"])

    def _random_action(self) -> str:
        """Generate a random audit action."""
        return self._random_choice(
            [
                "login",
                "logout",
                "create",
                "update",
                "delete",
                "read",
                "export",
                "import",
                "approve",
                "reject",
            ]
        )

    def _random_resource(self) -> str:
        """Generate a random resource type."""
        return self._random_choice(
            [
                "user",
                "document",
                "report",
                "config",
                "policy",
                "role",
                "permission",
                "session",
                "token",
                "backup",
            ]
        )

    def generate_auth_logs(self, count: int = 50) -> DatasetArtifact:
        """Generate deterministic authentication log records."""
        records: list[dict[str, Any]] = []
        for _ in range(count):
            records.append(
                {
                    "event_id": self._random_event_id(),
                    "timestamp": self._random_timestamp(),
                    "username": self._random_username(),
                    "source_ip": self._random_ip(),
                    "method": self._random_method(),
                    "status": self._random_status(),
                    "user_agent": self._random_choice(
                        [
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                            "Mozilla/5.0 (X11; Linux x86_64)",
                            "curl/7.68.0",
                            "Python-urllib/3.9",
                        ]
                    ),
                    "session_id": self._random_event_id(),
                    "failure_reason": (
                        self._random_choice(
                            [
                                "invalid_password",
                                "account_locked",
                                "mfa_timeout",
                                "token_expired",
                                "",
                            ]
                        )
                        if records and records[-1].get("status") == "failure"
                        else ""
                    ),
                }
            )
        return DatasetArtifact(
            id=str(uuid.uuid4()),
            artifact_type=DatasetArtifactType.AUTH_LOG,
            name="auth_log",
            content={"records": records},
            metadata={"record_count": count, "generated_with_seed": self.seed},
        )

    def generate_audit_logs(self, count: int = 100) -> DatasetArtifact:
        """Generate deterministic audit log records."""
        records: list[dict[str, Any]] = []
        for _ in range(count):
            records.append(
                {
                    "event_id": self._random_event_id(),
                    "timestamp": self._random_timestamp(),
                    "user_id": self._random_username(),
                    "action": self._random_action(),
                    "resource": self._random_resource(),
                    "resource_id": self._random_event_id(),
                    "source_ip": self._random_ip(),
                    "result": self._random_choice(["success", "failure", "denied"]),
                    "details": {
                        "method": self._random_choice(["GET", "POST", "PUT", "DELETE", "PATCH"]),
                        "path": f"/api/v1/{self._random_resource()}/{self._random_event_id()[:8]}",
                    },
                }
            )
        return DatasetArtifact(
            id=str(uuid.uuid4()),
            artifact_type=DatasetArtifactType.AUDIT_LOG,
            name="audit_log",
            content={"records": records},
            metadata={"record_count": count, "generated_with_seed": self.seed},
        )

    def generate_session_records(self, count: int = 30) -> DatasetArtifact:
        """Generate deterministic session records."""
        records: list[dict[str, Any]] = []
        for _ in range(count):
            created = self._random_timestamp()
            duration = self._rng.randint(300, 14400)
            records.append(
                {
                    "session_id": self._random_event_id(),
                    "user_id": self._random_username(),
                    "created_at": created,
                    "last_activity": self._random_timestamp(offset_hours=1),
                    "source_ip": self._random_ip(),
                    "user_agent": self._random_choice(
                        [
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                            "Mozilla/5.0 (X11; Linux x86_64)",
                        ]
                    ),
                    "is_active": self._random_bool(0.7),
                    "duration_seconds": duration,
                    "device_fingerprint": self._random_event_id(),
                    "mfa_used": self._random_bool(0.6),
                }
            )
        return DatasetArtifact(
            id=str(uuid.uuid4()),
            artifact_type=DatasetArtifactType.SESSION_RECORD,
            name="session_records",
            content={"records": records},
            metadata={"record_count": count, "generated_with_seed": self.seed},
        )

    def generate_user_profiles(self, count: int = 20) -> DatasetArtifact:
        """Generate deterministic user profile records."""
        departments = ["engineering", "marketing", "finance", "hr", "legal", "operations", "sales"]
        statuses = ["active", "active", "active", "inactive", "suspended"]
        records: list[dict[str, Any]] = []
        for i in range(1, count + 1):
            records.append(
                {
                    "user_id": f"user_{i:03d}",
                    "username": f"user_{i:03d}",
                    "email": f"user_{i:03d}@example.com",
                    "full_name": f"User {i:03d}",
                    "department": self._random_choice(departments),
                    "role": self._random_role(),
                    "status": self._random_choice(statuses),
                    "created_at": self._random_timestamp(),
                    "last_login": self._random_timestamp(offset_hours=1),
                    "mfa_enabled": self._random_bool(0.8),
                    "password_age_days": self._rng.randint(1, 365),
                    "failed_login_attempts": self._rng.randint(0, 10),
                    "is_locked": self._random_bool(0.1),
                }
            )
        return DatasetArtifact(
            id=str(uuid.uuid4()),
            artifact_type=DatasetArtifactType.USER_PROFILE,
            name="user_profiles",
            content={"records": records},
            metadata={"record_count": count, "generated_with_seed": self.seed},
        )

    def generate_role_assignments(self, count: int = 25) -> DatasetArtifact:
        """Generate deterministic role assignment records."""
        records: list[dict[str, Any]] = []
        for _ in range(count):
            records.append(
                {
                    "assignment_id": self._random_event_id(),
                    "user_id": self._random_username(),
                    "role": self._random_role(),
                    "scope": self._random_choice(["global", "department", "project", "team"]),
                    "assigned_by": self._random_username(),
                    "assigned_at": self._random_timestamp(),
                    "expires_at": self._random_timestamp(offset_hours=24),
                    "is_active": self._random_bool(0.9),
                    "justification": self._random_choice(
                        [
                            "Standard onboarding",
                            "Project assignment",
                            "Temporary elevation",
                            "Role change",
                            "Coverage for leave",
                        ]
                    ),
                }
            )
        return DatasetArtifact(
            id=str(uuid.uuid4()),
            artifact_type=DatasetArtifactType.ROLE_ASSIGNMENT,
            name="role_assignments",
            content={"records": records},
            metadata={"record_count": count, "generated_with_seed": self.seed},
        )

    def generate_config_snapshots(self, count: int = 10) -> DatasetArtifact:
        """Generate deterministic configuration snapshot records."""
        records: list[dict[str, Any]] = []
        for i in range(count):
            records.append(
                {
                    "snapshot_id": self._random_event_id(),
                    "captured_at": self._random_timestamp(),
                    "system_name": self._random_choice(
                        [
                            "auth-gateway",
                            "api-gateway",
                            "session-manager",
                            "audit-service",
                            "policy-engine",
                        ]
                    ),
                    "version": f"{self._rng.randint(1, 5)}.{self._rng.randint(0, 20)}.{self._rng.randint(0, 99)}",
                    "config": {
                        "max_sessions": self._rng.randint(100, 10000),
                        "session_timeout_minutes": self._rng.choice([15, 30, 60, 120]),
                        "max_login_attempts": self._rng.choice([3, 5, 10]),
                        "lockout_duration_minutes": self._rng.choice([15, 30, 60]),
                        "mfa_required": self._random_bool(0.8),
                        "password_min_length": self._rng.choice([8, 10, 12, 16]),
                        "audit_logging_enabled": self._random_bool(0.9),
                    },
                    "changed_by": self._random_username(),
                    "change_reason": self._random_choice(
                        [
                            "Security hardening",
                            "Compliance update",
                            "Performance tuning",
                            "Bug fix",
                            "Scheduled maintenance",
                        ]
                    ),
                }
            )
        return DatasetArtifact(
            id=str(uuid.uuid4()),
            artifact_type=DatasetArtifactType.CONFIG_SNAPSHOT,
            name="config_snapshots",
            content={"records": records},
            metadata={"record_count": count, "generated_with_seed": self.seed},
        )

    def generate_security_policies(self, count: int = 8) -> DatasetArtifact:
        """Generate deterministic security policy records."""
        policy_types = [
            "password_policy",
            "access_control",
            "data_classification",
            "incident_response",
            "acceptable_use",
            "encryption",
            "remote_access",
            "vendor_management",
        ]
        records: list[dict[str, Any]] = []
        for i in range(min(count, len(policy_types))):
            records.append(
                {
                    "policy_id": self._random_event_id(),
                    "policy_type": policy_types[i],
                    "title": f"{policy_types[i].replace('_', ' ').title()} Policy",
                    "version": f"{self._rng.randint(1, 5)}.{self._rng.randint(0, 9)}",
                    "status": self._random_choice(["active", "active", "under_review", "draft"]),
                    "effective_date": self._random_timestamp(),
                    "review_date": self._random_timestamp(offset_hours=24),
                    "owner": self._random_username(),
                    "compliance_frameworks": self._random_choice(
                        [
                            ["SOC2"],
                            ["ISO27001"],
                            ["NIST", "SOC2"],
                            ["GDPR"],
                            ["PCI-DSS", "SOC2"],
                            ["HIPAA"],
                        ]
                    ),
                    "rules_count": self._rng.randint(3, 20),
                    "last_audit_result": self._random_choice(["pass", "pass", "fail", "partial"]),
                }
            )
        return DatasetArtifact(
            id=str(uuid.uuid4()),
            artifact_type=DatasetArtifactType.SECURITY_POLICY,
            name="security_policies",
            content={"records": records},
            metadata={"record_count": len(records), "generated_with_seed": self.seed},
        )

    def generate_compliance_reports(self, count: int = 5) -> DatasetArtifact:
        """Generate deterministic compliance report records."""
        frameworks = ["SOC2", "ISO27001", "NIST CSF", "GDPR", "PCI-DSS"]
        records: list[dict[str, Any]] = []
        for i in range(min(count, len(frameworks))):
            total_controls = self._rng.randint(20, 80)
            passed = self._rng.randint(int(total_controls * 0.6), total_controls)
            records.append(
                {
                    "report_id": self._random_event_id(),
                    "framework": frameworks[i],
                    "report_date": self._random_timestamp(),
                    "assessor": f"assessor_{self._rng.randint(1, 10):03d}",
                    "overall_status": "compliant" if passed == total_controls else "non_compliant",
                    "total_controls": total_controls,
                    "controls_passed": passed,
                    "controls_failed": total_controls - passed,
                    "compliance_percentage": round(passed / total_controls * 100, 1),
                    "findings": [
                        {
                            "severity": self._random_severity(),
                            "description": f"Finding in {self._random_resource()} module",
                            "recommendation": f"Review and remediate {self._random_resource()} configuration",
                        }
                        for _ in range(self._rng.randint(0, 5))
                    ],
                }
            )
        return DatasetArtifact(
            id=str(uuid.uuid4()),
            artifact_type=DatasetArtifactType.COMPLIANCE_REPORT,
            name="compliance_reports",
            content={"records": records},
            metadata={"record_count": len(records), "generated_with_seed": self.seed},
        )

    def generate_incident_reports(self, count: int = 7) -> DatasetArtifact:
        """Generate deterministic incident report records."""
        incident_types = [
            "unauthorized_access",
            "data_breach",
            "malware_detection",
            "phishing",
            "account_compromise",
            "privilege_escalation",
            "denial_of_service",
        ]
        records: list[dict[str, Any]] = []
        for i in range(min(count, len(incident_types))):
            records.append(
                {
                    "incident_id": self._random_event_id(),
                    "incident_type": incident_types[i],
                    "severity": self._random_severity(),
                    "reported_at": self._random_timestamp(),
                    "reported_by": self._random_username(),
                    "affected_users": self._rng.randint(1, 50),
                    "affected_systems": [
                        self._random_choice(
                            [
                                "auth-gateway",
                                "api-gateway",
                                "session-manager",
                                "audit-service",
                                "user-service",
                            ]
                        )
                        for _ in range(self._rng.randint(1, 4))
                    ],
                    "status": self._random_choice(
                        [
                            "open",
                            "investigating",
                            "contained",
                            "resolved",
                            "closed",
                        ]
                    ),
                    "resolution_notes": self._random_choice(
                        [
                            "User account secured and password reset",
                            "System patched and access revoked",
                            "Network segment isolated",
                            "Monitoring enhanced",
                            "",
                        ]
                    ),
                    "time_to_detect_hours": self._rng.randint(1, 48),
                    "time_to_respond_hours": self._rng.randint(1, 24),
                }
            )
        return DatasetArtifact(
            id=str(uuid.uuid4()),
            artifact_type=DatasetArtifactType.INCIDENT_REPORT,
            name="incident_reports",
            content={"records": records},
            metadata={"record_count": len(records), "generated_with_seed": self.seed},
        )

    def generate_backup_reports(self, count: int = 6) -> DatasetArtifact:
        """Generate deterministic backup report records."""
        records: list[dict[str, Any]] = []
        for i in range(count):
            records.append(
                {
                    "backup_id": self._random_event_id(),
                    "backup_type": self._random_choice(["full", "incremental", "differential"]),
                    "started_at": self._random_timestamp(),
                    "completed_at": self._random_timestamp(offset_hours=1),
                    "status": self._random_choice(
                        ["success", "success", "success", "partial", "failed"]
                    ),
                    "size_mb": round(self._rng.uniform(100, 5000), 2),
                    "source_system": self._random_choice(
                        [
                            "auth-gateway",
                            "audit-service",
                            "user-service",
                            "session-manager",
                            "full-stack",
                        ]
                    ),
                    "destination": self._random_choice(
                        [
                            "local-s3://backups",
                            "encrypted-volume",
                            "offsite-storage",
                        ]
                    ),
                    "encryption_enabled": self._random_bool(0.95),
                    "retention_days": self._rng.choice([7, 14, 30, 90]),
                    "verified": self._random_bool(0.85),
                    "error_message": (
                        self._random_choice(
                            [
                                "Disk space insufficient",
                                "Connection timeout",
                                "Checksum mismatch",
                                "",
                            ]
                        )
                        if self._random_bool(0.2)
                        else ""
                    ),
                }
            )
        return DatasetArtifact(
            id=str(uuid.uuid4()),
            artifact_type=DatasetArtifactType.BACKUP_REPORT,
            name="backup_reports",
            content={"records": records},
            metadata={"record_count": count, "generated_with_seed": self.seed},
        )

    def generate_accessibility_reports(self, count: int = 5) -> DatasetArtifact:
        """Generate deterministic accessibility assessment records."""
        wcag_levels = ["A", "AA", "AAA"]
        records: list[dict[str, Any]] = []
        for i in range(count):
            total_issues = self._rng.randint(5, 30)
            resolved = self._rng.randint(0, total_issues)
            records.append(
                {
                    "report_id": self._random_event_id(),
                    "assessment_date": self._random_timestamp(),
                    "assessor": f"accessibility_reviewer_{self._rng.randint(1, 5):03d}",
                    "target_system": self._random_choice(
                        [
                            "web_app",
                            "api_docs",
                            "admin_console",
                            "learner_portal",
                            "instructor_dashboard",
                        ]
                    ),
                    "wcag_target_level": self._random_choice(wcag_levels),
                    "total_issues": total_issues,
                    "issues_resolved": resolved,
                    "issues_remaining": total_issues - resolved,
                    "compliance_percentage": round(resolved / total_issues * 100, 1)
                    if total_issues > 0
                    else 100.0,
                    "categories": {
                        "color_contrast": self._rng.randint(0, 5),
                        "keyboard_navigation": self._rng.randint(0, 5),
                        "screen_reader": self._rng.randint(0, 5),
                        "aria_labels": self._rng.randint(0, 5),
                        "form_labels": self._rng.randint(0, 5),
                        "focus_management": self._rng.randint(0, 5),
                    },
                    "assistive_technologies_tested": self._random_choice(
                        [
                            ["NVDA"],
                            ["JAWS", "NVDA"],
                            ["VoiceOver"],
                            ["NVDA", "JAWS", "VoiceOver"],
                        ]
                    ),
                }
            )
        return DatasetArtifact(
            id=str(uuid.uuid4()),
            artifact_type=DatasetArtifactType.ACCESSIBILITY_REPORT,
            name="accessibility_reports",
            content={"records": records},
            metadata={"record_count": count, "generated_with_seed": self.seed},
        )

    def generate_full_dataset(
        self,
        name: str = "Full Synthetic Dataset",
        description: str = "Complete deterministic dataset for simulation exercises",
    ) -> SyntheticDataset:
        """Generate a complete dataset with all artifact types."""
        artifacts: list[DatasetArtifact] = [
            self.generate_auth_logs(50),
            self.generate_audit_logs(100),
            self.generate_session_records(30),
            self.generate_user_profiles(20),
            self.generate_role_assignments(25),
            self.generate_config_snapshots(10),
            self.generate_security_policies(8),
            self.generate_compliance_reports(5),
            self.generate_incident_reports(7),
            self.generate_backup_reports(6),
            self.generate_accessibility_reports(5),
        ]

        total_records = 0
        for artifact in artifacts:
            records = artifact.content.get("records", [])
            total_records += len(records)

        metadata = DatasetMetadata(
            creator="deterministic_generator",
            generation_date=datetime.now(timezone.utc).isoformat(),
            total_records=total_records,
        )
        all_contents = [a.content for a in artifacts]
        metadata.compute_checksum(all_contents)

        return SyntheticDataset(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            seed=self.seed,
            artifacts=artifacts,
            metadata=metadata,
            created_at=datetime.now(timezone.utc),
            version=1,
        )
