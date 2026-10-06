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
from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    computed_with: str | None = None  # set when the value was derived, not read from the source
    note: str | None = None


class DesignChoice(_Strict):
    """A value we chose (not a published fact). The reason is required and shown in reports."""

    value: _FINITE
    design_choice: _NON_EMPTY


class Mission(_Strict):
    """A reference orbit.

    Definitions (physics-reviewer, PR #5):
    - altitude_km: mean semi-major axis minus Earth's equatorial radius 6378.137 km, for a circular
      orbit in mean (Brouwer/SGP4-mean) elements. Not geodetic height, which varies ~21 km
      around a near-polar orbit.
    - inclination_deg: mean inclination.
    - ltan_h: mean local time of the ascending node, in hours.
    """

    id: _ID
    name: _NON_EMPTY
    altitude_km: SourcedValue | DesignChoice
    inclination_deg: SourcedValue | DesignChoice
    ltan_h: DesignChoice | None = None
    note: str | None = None


class MissionSet(_Strict):
    schemaVersion: Literal[1]  # noqa: N815 (schema field name shared with TypeScript)
    missions: list[Mission]


Effect = Literal["TID", "SEU", "MBU", "SEFI", "SDC", "DUE", "UE", "STUCK_BIT", "SEL"]


class Measurement(_Strict):
    """One published result.

    bound: "equal" (value as stated), "lower" (true value is at least `value`), "upper" (at most
    `value`), or "range" (spread from `value` to `value_max` across modes or conditions).
    kind: "measurement" (test result), "rating" (datasheet guarantee) or "target" (design goal).
    """

    quantity: _NON_EMPTY
    effect: Effect
    kind: Literal["measurement", "rating", "target"] = "measurement"
    value: _FINITE
    value_max: _FINITE | None = None
    bound: Literal["equal", "lower", "upper", "range"] = "equal"
    unit: _NON_EMPTY
    conditions: _NON_EMPTY
    source: _NON_EMPTY
    locator: _NON_EMPTY
    status: RefStatus
    note: str | None = None

    @model_validator(mode="after")
    def _range_consistent(self) -> Measurement:
        if self.bound == "range":
            if self.value_max is None or self.value_max <= self.value:
                raise ValueError("a range needs value_max greater than value")
        elif self.value_max is not None:
            raise ValueError("value_max is only allowed with bound: range")
        return self


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
    see: EffectEvidence  # non-destructive SEE: SEU, MBU, SEFI, SDC, DUE, UE, stuck bits
    sel: EffectEvidence
    note: str | None = None

    @model_validator(mode="after")
    def _effects_in_right_bucket(self) -> Device:
        allowed: dict[str, set[str]] = {
            "tid": {"TID"},
            "sel": {"SEL"},
            "see": {"SEU", "MBU", "SEFI", "SDC", "DUE", "UE", "STUCK_BIT"},
        }
        for bucket, effects in allowed.items():
            evidence = getattr(self, bucket)
            if isinstance(evidence, list):
                for m in evidence:
                    if m.effect not in effects:
                        raise ValueError(f"{self.id}: effect {m.effect} not allowed in {bucket}")
        return self


class DeviceSet(_Strict):
    schemaVersion: Literal[1]  # noqa: N815
    devices: list[Device]


class License(_Strict):
    name: _NON_EMPTY
    source: _NON_EMPTY
    locator: _NON_EMPTY
    status: RefStatus
    note: str | None = None  # e.g. what research use and redistribution allow


class Benchmark(_Strict):
    name: _NON_EMPTY  # e.g. "ImageNet top-1", "MMLU 5-shot"
    result: SourcedValue
    unit: _NON_EMPTY


class WorkloadRole(_Strict):
    """Why this workload is in the set.

    calibration: checks our fault-injection tools against published studies; not a stand-in for
    orbital AI. representative: stands in for the AI work actually planned for orbit.
    """

    value: Literal["calibration", "representative"]
    reason: _NON_EMPTY


class Workload(_Strict):
    """A reference AI workload.

    Weight memory (parameters x precision) is one input to upset exposure; Phase 4 adds activations,
    caches, optimizer state and registers.
    """

    id: _ID
    name: _NON_EMPTY
    phase: Literal["inference", "training"]
    role: WorkloadRole
    model_name: _NON_EMPTY
    parameters: SourcedValue
    precision: SourcedValue | DesignChoice  # bits per weight
    flops_per_item: SourcedValue | None = (
        None  # multiply-adds per inference item, as the source defines
    )
    context_length: SourcedValue | None = None
    benchmark: Benchmark | None = None
    license: License
    note: str | None = None

    @model_validator(mode="after")
    def _positive(self) -> Workload:
        optional = [self.flops_per_item, self.context_length]
        if self.benchmark is not None:
            optional.append(self.benchmark.result)
        values = [self.parameters.value, self.precision.value]
        values += [v.value for v in optional if v is not None]
        if any(v <= 0 for v in values):
            raise ValueError(f"{self.id}: sizes, precision and benchmark values must be positive")
        return self


class WorkloadSet(_Strict):
    schemaVersion: Literal[1]  # noqa: N815
    workloads: list[Workload]


@dataclass(frozen=True)
class ReferenceSets:
    missions: MissionSet
    devices: DeviceSet
    workloads: WorkloadSet | None = None


def _sources(sets: ReferenceSets) -> Iterable[tuple[str, str]]:
    for m in sets.missions.missions:
        for value in (m.altitude_km, m.inclination_deg):
            if isinstance(value, SourcedValue):
                yield m.id, value.source
    for d in sets.devices.devices:
        for evidence in (d.tid, d.see, d.sel):
            if isinstance(evidence, list):
                for meas in evidence:
                    yield d.id, meas.source
    if sets.workloads is not None:
        for w in sets.workloads.workloads:
            sourced: list[SourcedValue | DesignChoice | None] = [
                w.parameters,
                w.precision,
                w.flops_per_item,
                w.context_length,
            ]
            if w.benchmark is not None:
                sourced.append(w.benchmark.result)
            for item in sourced:
                if isinstance(item, SourcedValue):
                    yield w.id, item.source
            yield w.id, w.license.source


def _check_unique(ids: list[str], kind: str) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise ValueError(f"duplicate {kind} id {item_id!r}")
        seen.add(item_id)


def load_reference_sets(directory: Path, bib_text: str) -> ReferenceSets:
    missions = MissionSet.model_validate(yaml.safe_load((directory / "missions.yaml").read_text()))
    devices = DeviceSet.model_validate(yaml.safe_load((directory / "devices.yaml").read_text()))
    workloads_path = directory / "workloads.yaml"
    workloads = (
        WorkloadSet.model_validate(yaml.safe_load(workloads_path.read_text()))
        if workloads_path.exists()
        else None
    )
    sets = ReferenceSets(missions=missions, devices=devices, workloads=workloads)
    _check_unique([m.id for m in missions.missions], "mission")
    _check_unique([d.id for d in devices.devices], "device")
    if workloads is not None:
        _check_unique([w.id for w in workloads.workloads], "workload")
    keys = bib_keys(bib_text)
    for owner, source in _sources(sets):
        if source not in keys:
            raise ValueError(f"{owner}: source {source!r} not in docs/refs.bib")
    return sets
