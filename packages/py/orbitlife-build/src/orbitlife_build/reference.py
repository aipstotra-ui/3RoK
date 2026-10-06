"""Reference sets: the standard missions, devices and workloads every validation case draws on.

Files live in validation/reference/*.yaml. Every number cites a docs/refs.bib key and a
status (CONFIRMED / CORRECTED / UNVERIFIED). Every device must state its TID, SEU and SEL
evidence, or say explicitly that none exists, so a missing measurement can never read as zero risk.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from orbitlife_build.validation import RefStatus, bib_keys

_NON_EMPTY = Annotated[str, Field(min_length=1)]
_ID = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]*$")]
_FINITE = Annotated[float, Field(allow_inf_nan=False)]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourcedValue(_Strict):
    value: _FINITE
    source: _NON_EMPTY
    locator: _NON_EMPTY
    status: RefStatus
    note: str | None = None


class DesignChoice(_Strict):
    """A value we chose (not a published fact). The reason is required and shown in reports."""

    value: _FINITE
    design_choice: _NON_EMPTY


class Mission(_Strict):
    id: _ID
    name: _NON_EMPTY
    altitude_km: SourcedValue | DesignChoice
    inclination_deg: SourcedValue | DesignChoice
    ltan_h: DesignChoice | None = None
    note: str | None = None


class MissionSet(_Strict):
    schemaVersion: Literal[1]  # noqa: N815 (schema field name shared with TypeScript)
    missions: list[Mission]


class Measurement(_Strict):
    """One published test result. `bound` says whether value is exact, a lower or an upper limit."""

    quantity: _NON_EMPTY
    value: _FINITE
    bound: Literal["equal", "lower", "upper"] = "equal"
    unit: _NON_EMPTY
    conditions: _NON_EMPTY
    source: _NON_EMPTY
    locator: _NON_EMPTY
    status: RefStatus
    note: str | None = None


class NoData(_Strict):
    """Explicit statement that no published test data exist (reason required)."""

    no_data: _NON_EMPTY


EffectEvidence = Annotated[list[Measurement], Field(min_length=1)] | NoData


class Device(_Strict):
    id: _ID
    name: _NON_EMPTY
    kind: Literal["dram", "hbm", "sram", "gpu", "accelerator", "soc"]
    part: str | None = None
    node_nm: _FINITE | None = None
    tid: EffectEvidence
    seu: EffectEvidence
    sel: EffectEvidence
    note: str | None = None


class DeviceSet(_Strict):
    schemaVersion: Literal[1]  # noqa: N815
    devices: list[Device]


@dataclass(frozen=True)
class ReferenceSets:
    missions: MissionSet
    devices: DeviceSet


def _sources(sets: ReferenceSets) -> Iterable[tuple[str, str]]:
    for m in sets.missions.missions:
        for value in (m.altitude_km, m.inclination_deg):
            if isinstance(value, SourcedValue):
                yield m.id, value.source
    for d in sets.devices.devices:
        for evidence in (d.tid, d.seu, d.sel):
            if isinstance(evidence, list):
                for meas in evidence:
                    yield d.id, meas.source


def _check_unique(ids: list[str], kind: str) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise ValueError(f"duplicate {kind} id {item_id!r}")
        seen.add(item_id)


def load_reference_sets(directory: Path, bib_text: str) -> ReferenceSets:
    missions = MissionSet.model_validate(yaml.safe_load((directory / "missions.yaml").read_text()))
    devices = DeviceSet.model_validate(yaml.safe_load((directory / "devices.yaml").read_text()))
    sets = ReferenceSets(missions=missions, devices=devices)
    _check_unique([m.id for m in missions.missions], "mission")
    _check_unique([d.id for d in devices.devices], "device")
    keys = bib_keys(bib_text)
    for owner, source in _sources(sets):
        if source not in keys:
            raise ValueError(f"{owner}: source {source!r} not in docs/refs.bib")
    return sets
