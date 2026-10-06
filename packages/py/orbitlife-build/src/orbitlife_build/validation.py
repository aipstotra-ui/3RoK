"""Validation suite: check orbitlife against reference cases in validation/cases/**/*.yaml.

Each case names a trusted reference value (with a docs/refs.bib source) and the orbitlife
function that should reproduce it. Cases are written before the code they check (Phase 1),
so a missing function is reported as NOT_IMPLEMENTED rather than as an error.

Usage:
    python -m orbitlife_build.validation [--cases DIR] [--bib FILE] [--out FILE] [--strict]

Exit code: 1 if any case is FAIL or ERROR. With --strict, also 1 if any case is
NOT_IMPLEMENTED or matched only an UNVERIFIED reference.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import re
import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

_NON_EMPTY = Annotated[str, Field(min_length=1)]


class Module(StrEnum):
    ORBIT = "orbit"
    DRAG = "drag"
    THERMAL = "thermal"
    RADIATION = "radiation"
    SEE = "see"
    SEL = "sel"
    FORECAST = "forecast"
    WORKLOAD = "workload"
    FLEET = "fleet"


class Check(StrEnum):
    IMPLEMENTATION = "implementation"  # same model as a reference code (SPENVIS, CREME96, Orekit)
    PHYSICS = "physics"  # against measured flight or ground data


class RefStatus(StrEnum):
    CONFIRMED = "CONFIRMED"
    CORRECTED = "CORRECTED"
    UNVERIFIED = "UNVERIFIED"


class Reference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: Annotated[float, Field(allow_inf_nan=False)]
    uncertainty: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    source: _NON_EMPTY
    locator: _NON_EMPTY
    status: RefStatus
    computed_with: str | None = None
    note: str | None = None


class Tolerance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["abs", "rel", "factor"]
    value: float = Field(gt=0, allow_inf_nan=False)
    rationale: _NON_EMPTY

    @model_validator(mode="after")
    def _factor_above_one(self) -> Tolerance:
        if self.kind == "factor" and self.value <= 1:
            raise ValueError("a factor tolerance must be greater than 1")
        return self


class ValidationCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]*$")]
    title: _NON_EMPTY
    module: Module
    check: Check
    target: Annotated[str, Field(pattern=r"^[A-Za-z_][\w.]*\.[A-Za-z_]\w*$")]
    inputs: dict[str, Any]
    quantity: _NON_EMPTY
    unit: _NON_EMPTY
    reference: Reference
    tolerance: Tolerance
    notes: str | None = None


class Outcome(StrEnum):
    PASS = "PASS"
    PASS_UNVERIFIED_REF = "PASS_UNVERIFIED_REF"
    FAIL = "FAIL"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    ERROR = "ERROR"


class CaseResult(BaseModel):
    id: str
    module: Module
    check: Check
    quantity: str
    unit: str
    reference: float
    ours: float | None
    residual: float | None
    outcome: Outcome
    detail: str = ""


_BIB_KEY = re.compile(r"^\s*@\w+\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)


def bib_keys(bib_text: str) -> set[str]:
    return set(_BIB_KEY.findall(bib_text))


def within_tolerance(ours: float, ref: float, tol: Tolerance) -> bool:
    if not math.isfinite(ours):
        return False
    if tol.kind == "abs":
        return abs(ours - ref) <= tol.value
    if tol.kind == "rel":
        return abs(ours - ref) <= tol.value * abs(ref)
    if ours <= 0 or ref <= 0:
        return False
    return 1 / tol.value <= ours / ref <= tol.value


def load_cases(cases_dir: Path, bib_text: str) -> list[ValidationCase]:
    keys = bib_keys(bib_text)
    cases: list[ValidationCase] = []
    seen: dict[str, Path] = {}
    paths = [*cases_dir.rglob("*.yaml"), *cases_dir.rglob("*.yml")]
    for path in sorted(paths):
        case = ValidationCase.model_validate(yaml.safe_load(path.read_text()))
        if case.reference.source not in keys:
            raise ValueError(f"{path}: source {case.reference.source!r} not in docs/refs.bib")
        if case.id in seen:
            raise ValueError(f"{path}: duplicate id {case.id!r} (also in {seen[case.id]})")
        seen[case.id] = path
        cases.append(case)
    return cases


def _resolve(target: str) -> Any | None:
    """Return the target callable, or None if the target module or attribute doesn't exist yet.

    A ModuleNotFoundError for some *other* module (a missing dependency inside an existing
    target module) is re-raised, so a broken module is never reported as NOT_IMPLEMENTED.
    """
    module_name, _, attr = target.rpartition(".")
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        missing = exc.name or ""
        if missing and (module_name == missing or module_name.startswith(missing + ".")):
            return None
        raise
    return getattr(module, attr, None)


def _as_float(value: Any) -> float:
    """Accept plain numbers or orbitlife Quantity-like objects with a `.value`."""
    raw = getattr(value, "value", value)
    return float(raw)


def _result(
    case: ValidationCase, outcome: Outcome, ours: float | None = None, detail: str = ""
) -> CaseResult:
    ref = case.reference.value
    return CaseResult(
        id=case.id,
        module=case.module,
        check=case.check,
        quantity=case.quantity,
        unit=case.unit,
        reference=ref,
        ours=ours,
        residual=None if ours is None else ours - ref,
        outcome=outcome,
        detail=detail,
    )


def run_case(case: ValidationCase) -> CaseResult:
    try:
        fn = _resolve(case.target)
    except Exception as exc:  # broken target module: report it, never crash the suite
        return _result(case, Outcome.ERROR, detail=f"import failed: {type(exc).__name__}: {exc}")
    if fn is None:
        return _result(case, Outcome.NOT_IMPLEMENTED, detail=f"{case.target} does not exist yet")
    try:
        ours = _as_float(fn(**case.inputs))
    except Exception as exc:  # report every failure mode of the target, never crash the suite
        return _result(case, Outcome.ERROR, detail=f"{type(exc).__name__}: {exc}")
    if not within_tolerance(ours, case.reference.value, case.tolerance):
        return _result(case, Outcome.FAIL, ours)
    if case.reference.status is RefStatus.UNVERIFIED:
        return _result(case, Outcome.PASS_UNVERIFIED_REF, ours)
    return _result(case, Outcome.PASS, ours)


def _print_table(results: list[CaseResult]) -> None:
    width = max((len(r.id) for r in results), default=10)
    for r in results:
        ours = "—" if r.ours is None else f"{r.ours:.6g}"
        print(
            f"{r.outcome.value:<20} {r.id:<{width}}  ours={ours:<12} ref={r.reference:.6g} {r.unit}"
        )
    counts: dict[str, int] = {}
    for r in results:
        counts[r.outcome.value] = counts.get(r.outcome.value, 0) + 1
    summary = ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
    print(f"\n{len(results)} cases: {summary or 'none'}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m orbitlife_build.validation")
    parser.add_argument("--cases", type=Path, default=Path("validation/cases"))
    parser.add_argument("--bib", type=Path, default=Path("docs/refs.bib"))
    parser.add_argument("--out", type=Path, default=Path("validation/last-run.json"))
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    if not args.cases.is_dir():
        raise SystemExit(f"cases directory {args.cases} does not exist")
    cases = load_cases(args.cases, args.bib.read_text())
    results = [run_case(c) for c in cases]
    _print_table(results)
    args.out.write_text(json.dumps([r.model_dump(mode="json") for r in results], indent=2) + "\n")

    bad = {Outcome.FAIL, Outcome.ERROR}
    if args.strict:
        bad |= {Outcome.NOT_IMPLEMENTED, Outcome.PASS_UNVERIFIED_REF}
    return 1 if any(r.outcome in bad for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
