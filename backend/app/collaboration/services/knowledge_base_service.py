"""Knowledge base service – articles CRUD, categories, versioning, search, citations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..domain.entities.knowledge_base import (
        ArticleCitation,
        KnowledgeArticle,
        KnowledgeCategory,
    )
    from ..domain.interfaces import KnowledgeBaseRepository


class KnowledgeBaseService:
    def __init__(self, repo: KnowledgeBaseRepository) -> None:
        self._repo = repo

    def create_article(
        self,
        title: str,
        content: str,
        category: str,
        author: str,
        tags: list[str] | None = None,
    ) -> "KnowledgeArticle":
        from ..domain.entities.knowledge_base import KnowledgeArticle
        article = KnowledgeArticle(
            title=title,
            content=content,
            category=category,
            author=author,
            tags=tags,
        )
        self._repo.add_article(article)
        self._record_version(article.id, 1, content, author)
        return article

    def get_article(self, article_id: str):
        return self._repo.get_article(article_id)

    def update_article(
        self,
        article_id: str,
        title: str | None = None,
        content: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ):
        article = self._repo.get_article(article_id)
        if not article:
            raise ValueError(f"Article {article_id} not found")
        if title is not None:
            article.title = title
        if content is not None:
            article.content = content
        if category is not None:
            article.category = category
        if tags is not None:
            article.tags = tags
        article.version += 1
        from datetime import datetime, timezone
        article.updated_at = datetime.now(timezone.utc)
        self._repo.update_article(article)
        if content is not None:
            self._record_version(article.id, article.version, content, article.author)
        return article

    def delete_article(self, article_id: str) -> None:
        self._repo.remove_article(article_id)

    def list_articles(self) -> list:
        return self._repo.all_articles()

    def list_articles_by_category(self, category: str) -> list:
        return [a for a in self._repo.all_articles() if a.category == category]

    def list_articles_by_status(self, status: str) -> list:
        return [a for a in self._repo.all_articles() if a.status.value == status]

    def publish_article(self, article_id: str) -> "KnowledgeArticle":
        article = self._repo.get_article(article_id)
        if not article:
            raise ValueError(f"Article {article_id} not found")
        article.status = "published"
        from datetime import datetime, timezone
        article.updated_at = datetime.now(timezone.utc)
        self._repo.update_article(article)
        return article

    def archive_article(self, article_id: str) -> "KnowledgeArticle":
        article = self._repo.get_article(article_id)
        if not article:
            raise ValueError(f"Article {article_id} not found")
        article.status = "archived"
        from datetime import datetime, timezone
        article.updated_at = datetime.now(timezone.utc)
        self._repo.update_article(article)
        return article

    def search_articles(self, query: str) -> list:
        results = []
        q = query.lower()
        for article in self._repo.all_articles():
            if q in article.title.lower() or q in article.content.lower() or q in article.category.lower():
                results.append(article)
            elif any(q in tag.lower() for tag in article.tags):
                results.append(article)
        return results

    def create_category(
        self,
        name: str,
        description: str,
        parent_id: str | None = None,
    ) -> "KnowledgeCategory":
        from ..domain.entities.knowledge_base import KnowledgeCategory
        cat = KnowledgeCategory(
            name=name,
            description=description,
            parent_id=parent_id,
        )
        self._repo.add_category(cat)
        return cat

    def get_category(self, category_id: str):
        return self._repo.get_category(category_id)

    def update_category(
        self,
        category_id: str,
        name: str | None = None,
        description: str | None = None,
    ):
        cat = self._repo.get_category(category_id)
        if not cat:
            raise ValueError(f"Category {category_id} not found")
        if name is not None:
            cat.name = name
        if description is not None:
            cat.description = description
        self._repo.update_category(cat)
        return cat

    def delete_category(self, category_id: str) -> None:
        self._repo.remove_category(category_id)

    def list_categories(self) -> list:
        return self._repo.all_categories()

    def get_versions(self, article_id: str) -> list:
        return self._repo.get_versions_for_article(article_id)

    def add_citation(
        self,
        source_id: str,
        target_id: str,
        citation_type: str,
    ) -> "ArticleCitation":
        from ..domain.entities.knowledge_base import ArticleCitation
        citation = ArticleCitation(
            source_id=source_id,
            target_id=target_id,
            citation_type=citation_type,
        )
        self._repo.add_citation(citation)
        return citation

    def get_citations(self, article_id: str) -> list:
        return self._repo.get_citations_for_article(article_id)

    def _record_version(self, article_id: str, version: int, content: str, author: str) -> None:
        from ..domain.entities.knowledge_base import ArticleVersion
        v = ArticleVersion(
            article_id=article_id,
            version=version,
            content=content,
            author=author,
        )
        self._repo.add_version(v)
