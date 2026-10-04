"""Template studio service — template CRUD, inheritance, and versioning."""

from __future__ import annotations

import logging
from typing import Any, Optional

from ..domain.entities.template_studio import (
    ContentTemplate,
    TemplateInstance,
    TemplateType,
    TemplateVersion,
)
from ..domain.events.content_studio_events import TemplateCreated
from ..domain.interfaces.content_studio_interfaces import IContentTemplateRepository

logger = logging.getLogger(__name__)


class TemplateStudioService:
    """Service for managing content templates with inheritance and versioning."""

    def __init__(self, template_repo: IContentTemplateRepository) -> None:
        self._template_repo = template_repo
        self._version_history: dict[str, list[dict[str, Any]]] = {}
        self._instances: dict[str, list[dict[str, Any]]] = {}

    def create_template(self, data: dict[str, Any], author: str = "") -> dict[str, Any]:
        template = ContentTemplate(
            name=data.get("name", ""),
            template_type=TemplateType(data.get("template_type", "lesson")),
            description=data.get("description", ""),
            structure=data.get("structure", {}),
            author=author or data.get("author", ""),
            inherit_from=data.get("inherit_from"),
        )

        if template.inherit_from:
            parent = self._template_repo.get_by_id(template.inherit_from)
            if not parent:
                raise ValueError(f"Parent template '{template.inherit_from}' not found.")
            merged_structure = dict(parent.get("structure", {}))
            merged_structure.update(template.structure)
            template.structure = merged_structure

        result = self._template_repo.create({
            "id": template.id,
            "name": template.name,
            "template_type": template.template_type.value,
            "description": template.description,
            "structure": template.structure,
            "version": template.version,
            "author": template.author,
            "inherit_from": template.inherit_from,
        })

        self._version_history.setdefault(template.id, []).append({
            "version": template.version,
            "changes": ["Initial creation"],
        })

        event = TemplateCreated(
            template_id=template.id,
            template_name=template.name,
            template_type=template.template_type.value,
            created_by=template.author,
        )
        logger.info("template_created", extra={"template_id": result["id"], "event_id": event.event_id})
        return result

    def get_template(self, template_id: str) -> Optional[dict[str, Any]]:
        return self._template_repo.get_by_id(template_id)

    def list_templates(
        self, page: int = 1, per_page: int = 20, template_type: Optional[str] = None
    ) -> dict[str, Any]:
        return self._template_repo.get_all(page=page, per_page=per_page, template_type=template_type)

    def update_template(
        self, template_id: str, data: dict[str, Any], changes: list[str] | None = None
    ) -> Optional[dict[str, Any]]:
        existing = self._template_repo.get_by_id(template_id)
        if not existing:
            raise ValueError(f"Template '{template_id}' not found.")

        new_version = existing.get("version", 1) + 1
        data["version"] = new_version
        result = self._template_repo.update(template_id, data)

        change_descriptions = changes or [f"Updated at version {new_version}"]
        self._version_history.setdefault(template_id, []).append({
            "version": new_version,
            "changes": change_descriptions,
        })
        return result

    def delete_template(self, template_id: str) -> bool:
        if not self._template_repo.get_by_id(template_id):
            raise ValueError(f"Template '{template_id}' not found.")
        self._version_history.pop(template_id, None)
        self._instances.pop(template_id, None)
        return self._template_repo.delete(template_id)

    def get_version_history(self, template_id: str) -> list[dict[str, Any]]:
        if not self._template_repo.get_by_id(template_id):
            raise ValueError(f"Template '{template_id}' not found.")
        return self._version_history.get(template_id, [])

    def create_instance(
        self, template_id: str, customizations: dict[str, Any], created_by: str = ""
    ) -> dict[str, Any]:
        template = self._template_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' not found.")

        instance = TemplateInstance(
            template_id=template_id,
            customizations=customizations,
            created_by=created_by,
        )
        instance_dict = instance.to_dict()
        self._instances.setdefault(template_id, []).append(instance_dict)
        logger.info("template_instance_created", extra={
            "template_id": template_id,
            "instance_id": instance.id,
        })
        return instance_dict

    def get_instances(self, template_id: str) -> list[dict[str, Any]]:
        if not self._template_repo.get_by_id(template_id):
            raise ValueError(f"Template '{template_id}' not found.")
        return self._instances.get(template_id, [])

    def update_instance(
        self, template_id: str, instance_id: str, customizations: dict[str, Any]
    ) -> dict[str, Any]:
        if not self._template_repo.get_by_id(template_id):
            raise ValueError(f"Template '{template_id}' not found.")

        instances = self._instances.get(template_id, [])
        for inst in instances:
            if inst["id"] == instance_id:
                inst["customizations"].update(customizations)
                return inst
        raise ValueError(f"Instance '{instance_id}' not found for template '{template_id}'.")

    def get_template_with_inheritance(self, template_id: str) -> dict[str, Any]:
        template = self._template_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' not found.")

        if template.get("inherit_from"):
            parent = self._template_repo.get_by_id(template["inherit_from"])
            if parent:
                merged = dict(parent.get("structure", {}))
                merged.update(template.get("structure", {}))
                template["merged_structure"] = merged
                template["parent_name"] = parent.get("name", "")
        return template

    def get_templates_by_type(self, template_type: str) -> list[dict[str, Any]]:
        """Return every template of ``template_type``.

        The repository applies this filter itself and answers with a *paginated*
        envelope, so filtering a single default page silently drops every match
        past ``per_page`` (the repository default is 20) -- a caller asking for
        a type that only appears on a later page got an empty list instead of
        an error.  Page through the envelope until it is exhausted rather than
        re-implementing the filter here.
        """
        results: list[dict[str, Any]] = []
        page = 1
        while True:
            envelope = self._template_repo.get_all(
                page=page, per_page=100, template_type=template_type
            )
            if not isinstance(envelope, dict):
                # Defensive: a plain sequence from an alternative implementation.
                return [
                    t
                    for t in envelope
                    if isinstance(t, dict) and t.get("template_type") == template_type
                ]
            batch = list(envelope.get("items") or [])
            results.extend(t for t in batch if isinstance(t, dict))
            if not batch or page >= int(envelope.get("pages") or 1):
                return results
            page += 1
