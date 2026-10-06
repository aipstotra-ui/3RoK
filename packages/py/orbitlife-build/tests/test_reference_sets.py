from pathlib import Path

import pytest
import yaml
from orbitlife_build.reference import DeviceSet, MissionSet, load_reference_sets
from pydantic import ValidationError

REPO = Path(__file__).resolve().parents[4]
BIB = "@misc{src_a, title={A}}\n@misc{src_b, title={B}}\n"


def _sv(value: float, source: str = "src_a") -> dict[str, object]:
    return {"value": value, "source": source, "locator": "p1", "status": "CONFIRMED"}


def _mission(**overrides: object) -> dict[str, object]:
    m: dict[str, object] = {
        "id": "test-shell",
        "name": "Test shell",
        "altitude_km": _sv(550),
        "inclination_deg": _sv(53),
    }
    m.update(overrides)
    return m


def _meas(**overrides: object) -> dict[str, object]:
    m: dict[str, object] = {
        "quantity": "sel_let_threshold",
        "effect": "SEL",
        "value": 60.0,
        "bound": "lower",
        "unit": "MeV cm2/mg",
        "conditions": "95 C",
        "source": "src_b",
        "locator": "Tab. 1",
        "status": "CONFIRMED",
    }
    m.update(overrides)
    return m


def _device(**overrides: object) -> dict[str, object]:
    d: dict[str, object] = {
        "id": "test-dram",
        "name": "Test DRAM",
        "kind": "dram",
        "tid": {"no_data": "not tested"},
        "see": [
            _meas(quantity="seu_weibull_let_threshold", effect="SEU", value=0.5, bound="equal")
        ],
        "sel": [_meas()],
    }
    d.update(overrides)
    return d


def test_device_without_sel_entry_is_rejected() -> None:
    bad = _device()
    del bad["sel"]
    with pytest.raises(ValidationError):
        DeviceSet.model_validate({"schemaVersion": 1, "devices": [bad]})


def test_device_with_empty_sel_list_is_rejected() -> None:
    with pytest.raises(ValidationError):
        DeviceSet.model_validate({"schemaVersion": 1, "devices": [_device(sel=[])]})


def test_explicit_no_data_needs_a_reason() -> None:
    with pytest.raises(ValidationError):
        DeviceSet.model_validate({"schemaVersion": 1, "devices": [_device(sel={"no_data": ""})]})


def test_non_finite_values_are_rejected() -> None:
    with pytest.raises(ValidationError):
        MissionSet.model_validate(
            {"schemaVersion": 1, "missions": [_mission(altitude_km=_sv(float("inf")))]}
        )


def _write_sets(tmp: Path, missions: list[object], devices: list[object]) -> None:
    (tmp / "missions.yaml").write_text(yaml.safe_dump({"schemaVersion": 1, "missions": missions}))
    (tmp / "devices.yaml").write_text(yaml.safe_dump({"schemaVersion": 1, "devices": devices}))


def test_unknown_source_key_is_rejected(tmp_path: Path) -> None:
    _write_sets(tmp_path, [_mission(altitude_km=_sv(550, source="nope"))], [_device()])
    with pytest.raises(ValueError, match="nope"):
        load_reference_sets(tmp_path, BIB)


def test_unknown_source_inside_device_measurement_is_rejected(tmp_path: Path) -> None:
    _write_sets(tmp_path, [_mission()], [_device(sel=[_meas(source="missing")])])
    with pytest.raises(ValueError, match="missing"):
        load_reference_sets(tmp_path, BIB)


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    _write_sets(tmp_path, [_mission(), _mission()], [_device()])
    with pytest.raises(ValueError, match="duplicate"):
        load_reference_sets(tmp_path, BIB)


def test_repository_reference_sets_load_and_cite_known_sources() -> None:
    sets = load_reference_sets(
        REPO / "validation" / "reference", (REPO / "docs/refs.bib").read_text()
    )
    assert len(sets.missions.missions) >= 6
    assert len(sets.devices.devices) >= 6
    assert sets.workloads is not None
    assert len(sets.workloads.workloads) >= 3
    no_sel = [
        m
        for d in sets.devices.devices
        if isinstance(d.sel, list)
        for m in d.sel
        if m.conditions.lower().startswith("no sel")
    ]
    assert no_sel, "expected some 'no SEL up to LET X' entries"
    for m in no_sel:
        assert m.bound == "lower", f"'no SEL' must be a lower bound on the threshold: {m}"


def test_effect_must_match_its_bucket() -> None:
    with pytest.raises(ValidationError, match="sel"):
        DeviceSet.model_validate(
            {"schemaVersion": 1, "devices": [_device(sel=[_meas(effect="SEFI")])]}
        )
    with pytest.raises(ValidationError, match="see"):
        DeviceSet.model_validate(
            {"schemaVersion": 1, "devices": [_device(see=[_meas(effect="TID")])]}
        )


def test_range_needs_value_max_above_value() -> None:
    ok = _meas(effect="SEL", bound="range", value=1.0, value_max=2.0)
    DeviceSet.model_validate({"schemaVersion": 1, "devices": [_device(sel=[ok])]})
    for bad in (
        _meas(bound="range", value=2.0, value_max=1.0),
        _meas(bound="range", value=1.0),
        _meas(bound="equal", value=1.0, value_max=2.0),
    ):
        with pytest.raises(ValidationError):
            DeviceSet.model_validate({"schemaVersion": 1, "devices": [_device(sel=[bad])]})


def test_rating_kind_is_accepted_and_defaults_to_measurement() -> None:
    d = DeviceSet.model_validate(
        {"schemaVersion": 1, "devices": [_device(sel=[_meas(kind="rating")])]}
    ).devices[0]
    assert isinstance(d.sel, list)
    assert d.sel[0].kind == "rating"
    assert isinstance(d.see, list)
    assert d.see[0].kind == "measurement"


# ---- Workloads (Phase 1.3) ----


def _workload(**overrides: object) -> dict[str, object]:
    w: dict[str, object] = {
        "id": "test-model-inference",
        "name": "Test model inference",
        "phase": "inference",
        "model_name": "TestNet",
        "parameters": _sv(25.6e6),
        "precision": {"value": 16, "design_choice": "bf16 inference"},
        "license": {"name": "MIT", "source": "src_a", "locator": "LICENSE", "status": "CONFIRMED"},
    }
    w.update(overrides)
    return w


def test_workload_requires_a_sourced_license() -> None:
    from orbitlife_build.reference import WorkloadSet

    bad = _workload()
    del bad["license"]
    with pytest.raises(ValidationError):
        WorkloadSet.model_validate({"schemaVersion": 1, "workloads": [bad]})


def test_workload_parameters_must_be_positive() -> None:
    from orbitlife_build.reference import WorkloadSet

    with pytest.raises(ValidationError):
        WorkloadSet.model_validate(
            {"schemaVersion": 1, "workloads": [_workload(parameters=_sv(0.0))]}
        )


def test_workload_sources_are_checked(tmp_path: Path) -> None:
    _write_sets(tmp_path, [_mission()], [_device()])
    (tmp_path / "workloads.yaml").write_text(
        yaml.safe_dump(
            {"schemaVersion": 1, "workloads": [_workload(parameters=_sv(1e6, source="nope"))]}
        )
    )
    with pytest.raises(ValueError, match="nope"):
        load_reference_sets(tmp_path, BIB)
