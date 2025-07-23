from dataclasses import dataclass


@dataclass
class Discovery:
    finder: str
    target: str
    evidence_found: str
    is_discovery_explicit: bool

    @classmethod
    def from_json(cls, json_data: dict):
        finder = json_data["finder"]
        target = json_data["target"]
        evidence_found = json_data["evidence_found"]
        is_discovery_explicit = json_data["is_discovery_explicit"]
        return cls(finder, target, evidence_found, is_discovery_explicit)
