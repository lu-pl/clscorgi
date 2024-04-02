"""Pydantic models for RDFGenerator bindings validation."""

from collections.abc import Iterator
from typing import Annotated, Literal

import lodkit.importer
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator
from rdflib.namespace import RDFS

from clscorgi.vocabs import identifier

# better list cast here, else the iterator will likely be exhausted somewhere
vocab_id_types: tuple[str, ...] = tuple(
    map(str, identifier.objects(None, RDFS.label))
)

source_types: tuple[str, ...] = (
    "firstEdition",
    "printSource",
    "digitalSource",
    "unspecified"
)


class IDMapping(BaseModel):
    """Simple model schema for IDMappings."""
    id_type: Literal[vocab_id_types] | None  # type: ignore
    id_value: str | None = None


class SourceData(IDMapping):
    """Model schema for source data (tei:sourceDesc)."""
    source_type: Literal[source_types]  # type: ignore


class ELTeCBindingsModel(BaseModel):
    """Bindings model schema for basic CLSCor conversion."""

    model_config = ConfigDict(extra="allow")

    resource_uri: str
    work_title: str
    author_name: str

    author_ids: list[IDMapping] | None = None
    work_ids: list[SourceData] | None = None


class PublicationData(BaseModel):
    idno: str | None
    date: str | None


class ReMSourceData(BaseModel):
    msname: str | None
    repo: str
    idno: str
    tpq: str | None
    taq: str | None
    census_link: str | None


class ReMBindingsModel(BaseModel):
    id: str
    title: str
    genre: str | None
    token_count: str
    publication: PublicationData
    source: ReMSourceData


class GutenbergAuthorsModel(BaseModel):
    """Model for Gutenberg Authors data."""
    name: str
    birth_year: int | None
    death_year: int | None


class GutenbergBindingsModel(BaseModel):
    """Bindings model for Gutenberg data."""
    model_config = ConfigDict(extra="ignore")

    id: int
    id_url: Annotated[str | None, Field(validate_default=True)] = None
    title: str
    authors: list[GutenbergAuthorsModel]
    formats: dict[str, str]

    @field_validator("id_url")
    @classmethod
    def _get_id_url(cls, value: None, info: ValidationInfo) -> str:
        id_value: int = info.data["id"]
        return f"https://www.gutenberg.org/ebooks/{id_value}"
