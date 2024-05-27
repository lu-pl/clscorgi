"""Pydantic models for RDFGenerator bindings validation."""

import re
from collections.abc import Iterator
from typing import Annotated, Literal

import lodkit.importer
from pydantic import (AnyUrl, BaseModel, ConfigDict, Field, HttpUrl,
                      ValidationError, ValidationInfo, field_validator,
                      model_validator)
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
    languages: list[str]
    formats: dict[str, str]

    @field_validator("id_url")
    @classmethod
    def _get_id_url(cls, value: None, info: ValidationInfo) -> str:
        id_value: int = info.data["id"]
        return f"https://www.gutenberg.org/ebooks/{id_value}"



class _DLKAuthorsModel(BaseModel):
    forename: str
    surname: str
    full_name: str

    @model_validator(mode="after")
    def check_full_name(self):
        if not self.full_name == f"{self.forename} {self.surname}":
            raise Exception(f"Field fullname is not composed of forename and surname.")
        return self


class _DLKFeaturesModel(BaseModel):
    """Model for DLK features data."""

    stanzas: int
    verses: int
    verses_per_stanza: str
    syllables: int
    tokens: int
    characters: int


class DLKBindingsModel(BaseModel):
    """Bindings model for Gutenberg data."""

    model_config = ConfigDict(extra="ignore")

    resource_uri: HttpUrl
    urn: AnyUrl
    dlk_id: Annotated[str, Field(pattern=r"dta.poem.\d+")]
    authors: list[_DLKAuthorsModel]
    title: str | None
    first_line: str
    features: _DLKFeaturesModel

    @field_validator("title")
    @classmethod
    def title_validator(cls, value):
        """Validate the title field."""
        if isinstance(value, str) and re.match(r"N\.A\.", value):
            raise ValidationError("Field title must not be 'N.A.'.")
