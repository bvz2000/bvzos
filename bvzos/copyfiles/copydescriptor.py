from dataclasses import dataclass


@dataclass
class Copydescriptor:
    source_p: str
    dest_relative_p: str
    name: str
    link_in_place: bool = False
