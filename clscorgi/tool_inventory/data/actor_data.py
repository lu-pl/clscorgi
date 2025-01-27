from dataclasses import dataclass, field

from lodkit import URIConstructorFactory
from rdflib import URIRef


@dataclass
class Actor:
    name: str
    note: str | None = None
    uri: URIRef = field(init=False)

    _mkuri = URIConstructorFactory("https://clscor.io/entity/")

    def __post_init__(self):
        self.uri = self._mkuri(self.name)


_actor_names: str | tuple[str, str] = [
    "Julie Birkholz",
    "Ingo Börner",
    "Silvie Cinková",
    "Tess Dejaeghere",
    "Serge Heiden",
    "Maarten Janssen",
    "Michal Křen",
    "Alvaro Perez Pozo",
    "Salvador Ros",
    "Matthieu Decorde",
    "Victor Diego Fresno Fernandez",
    (
        "Vera Maria Charvat",
        "responsible for transforming the written deliverables into a table, "
        "consolidating entries and modelling into rdf-ttl",
    ),
    (
        "Lukas Plank",
        "responsible for modelling into rdf-ttl, automatic data-transformation into rdf-ttl"
        "and uploading it into the CLSCor catalogue",
    ),
]

actors = [
    Actor(*entry) if isinstance(entry, tuple) else Actor(entry)
    for entry in _actor_names
]
