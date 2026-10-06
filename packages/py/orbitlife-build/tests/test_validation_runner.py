import sys
import textwrap
import types
from pathlib import Path

import pytest
from orbitlife_build.validation import (
    CaseResult,
    Outcome,
    Tolerance,
    ValidationCase,
    bib_keys,
    load_cases,
    run_case,
    within_tolerance,
)
from pydantic import ValidationError

BIB = textwrap.dedent(
    """
    % comment
    @book{vallado2013,
      title = {Fundamentals}
    }
    @misc{omni_hourly_dataset, title = {OMNI}}
    """
)


def _case(**overrides: object) -> dict[str, object]:
    case: dict[str, object] = {
        "id": "orbit-sso-600",
        "title": "SSO inclination at 600 km",
        "module": "orbit",
        "check": "implementation",
        "target": "fake_orbit.sso_inclination_deg",
        "inputs": {"altitude_km": 600.0},
        "quantity": "inclination",
        "unit": "deg",
        "reference": {
            "value": 97.8,
            "source": "vallado2013",
            "locator": "Table 1",
            "status": "CONFIRMED",
        },
        "tolerance": {"kind": "abs", "value": 0.01, "rationale": "textbook rounding"},
    }
    case.update(overrides)
    return case


@pytest.fixture
def fake_module() -> types.ModuleType:
    module = types.ModuleType("fake_orbit")

    def sso_inclination_deg(altitude_km: float) -> float:
        return 97.795 if altitude_km == 600.0 else 0.0

    module.sso_inclination_deg = sso_inclination_deg  # type: ignore[attr-defined]
    sys.modules["fake_orbit"] = module
    yield module
    del sys.modules["fake_orbit"]


def test_bib_keys_are_parsed() -> None:
    assert bib_keys(BIB) == {"vallado2013", "omni_hourly_dataset"}


@pytest.mark.parametrize(
    ("kind", "value", "ours", "ref", "ok"),
    [
        ("abs", 0.01, 97.795, 97.8, True),
        ("abs", 0.001, 97.795, 97.8, False),
        ("rel", 0.10, 105.0, 100.0, True),
        ("rel", 0.10, 111.0, 100.0, False),
        ("factor", 2.0, 49.0, 100.0, False),
        ("factor", 2.0, 51.0, 100.0, True),
        ("factor", 2.0, 199.0, 100.0, True),
        ("factor", 2.0, 201.0, 100.0, False),
    ],
)
def test_tolerance_kinds(kind: str, value: float, ours: float, ref: float, ok: bool) -> None:
    tol = Tolerance.model_validate({"kind": kind, "value": value, "rationale": "test"})
    assert within_tolerance(ours, ref, tol) is ok


def test_case_requires_a_tolerance_rationale() -> None:
    bad = _case(tolerance={"kind": "abs", "value": 0.01, "rationale": ""})
    with pytest.raises(ValidationError):
        ValidationCase.model_validate(bad)


def test_factor_tolerance_must_exceed_one() -> None:
    bad = _case(tolerance={"kind": "factor", "value": 1.0, "rationale": "x"})
    with pytest.raises(ValidationError):
        ValidationCase.model_validate(bad)


def test_unknown_source_key_is_rejected(tmp_path: Path) -> None:
    import yaml

    (tmp_path / "c.yaml").write_text(
        yaml.safe_dump(
            _case(
                reference={
                    "value": 1.0,
                    "source": "not_in_bib",
                    "locator": "p1",
                    "status": "CONFIRMED",
                }
            )
        )
    )
    with pytest.raises(ValueError, match="not_in_bib"):
        load_cases(tmp_path, BIB)


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    import yaml

    (tmp_path / "a.yaml").write_text(yaml.safe_dump(_case()))
    (tmp_path / "b.yaml").write_text(yaml.safe_dump(_case()))
    with pytest.raises(ValueError, match="duplicate"):
        load_cases(tmp_path, BIB)


def test_missing_target_is_not_implemented() -> None:
    case = ValidationCase.model_validate(_case(target="orbitlife.does_not_exist.fn"))
    result = run_case(case)
    assert result.outcome is Outcome.NOT_IMPLEMENTED


def test_matching_target_passes(fake_module: types.ModuleType) -> None:
    result = run_case(ValidationCase.model_validate(_case()))
    assert result.outcome is Outcome.PASS
    assert result.ours == pytest.approx(97.795)


def test_wrong_target_fails(fake_module: types.ModuleType) -> None:
    case = ValidationCase.model_validate(_case(inputs={"altitude_km": 700.0}))
    assert run_case(case).outcome is Outcome.FAIL


def test_unverified_reference_never_counts_as_a_plain_pass(
    fake_module: types.ModuleType,
) -> None:
    case = ValidationCase.model_validate(
        _case(
            reference={
                "value": 97.8,
                "source": "vallado2013",
                "locator": "Table 1",
                "status": "UNVERIFIED",
            }
        )
    )
    assert run_case(case).outcome is Outcome.PASS_UNVERIFIED_REF


def test_target_that_raises_is_an_error(fake_module: types.ModuleType) -> None:
    def broken(altitude_km: float) -> float:
        raise RuntimeError("boom")

    fake_module.sso_inclination_deg = broken  # type: ignore[attr-defined]
    result = run_case(ValidationCase.model_validate(_case()))
    assert result.outcome is Outcome.ERROR
    assert "boom" in result.detail


def test_result_is_serializable(fake_module: types.ModuleType) -> None:
    result = run_case(ValidationCase.model_validate(_case()))
    assert isinstance(result, CaseResult)
    assert result.model_dump(mode="json")["outcome"] == "PASS"


# ---- Fixes from code review (PR #3) ----


def test_missing_dependency_inside_existing_module_is_an_error(tmp_path: Path) -> None:
    pkg = tmp_path / "fake_needs_dep.py"
    pkg.write_text("import a_dependency_that_is_not_installed\n\ndef fn():\n    return 1.0\n")
    sys.path.insert(0, str(tmp_path))
    try:
        result = run_case(ValidationCase.model_validate(_case(target="fake_needs_dep.fn")))
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("fake_needs_dep", None)
    assert result.outcome is Outcome.ERROR
    assert "a_dependency_that_is_not_installed" in result.detail


def test_import_time_crash_is_an_error_not_a_suite_crash(tmp_path: Path) -> None:
    (tmp_path / "fake_broken.py").write_text("raise RuntimeError('import boom')\n")
    sys.path.insert(0, str(tmp_path))
    try:
        result = run_case(ValidationCase.model_validate(_case(target="fake_broken.fn")))
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("fake_broken", None)
    assert result.outcome is Outcome.ERROR
    assert "import boom" in result.detail


@pytest.mark.parametrize("bad", [float("inf"), float("nan")])
def test_non_finite_tolerance_is_rejected(bad: float) -> None:
    with pytest.raises(ValidationError):
        ValidationCase.model_validate(
            _case(tolerance={"kind": "abs", "value": bad, "rationale": "x"})
        )


@pytest.mark.parametrize("bad", [float("inf"), float("nan")])
def test_non_finite_reference_is_rejected(bad: float) -> None:
    with pytest.raises(ValidationError):
        ValidationCase.model_validate(
            _case(
                reference={
                    "value": bad,
                    "source": "vallado2013",
                    "locator": "p",
                    "status": "CONFIRMED",
                }
            )
        )


def test_yml_extension_is_loaded(tmp_path: Path) -> None:
    import yaml

    (tmp_path / "c.yml").write_text(yaml.safe_dump(_case()))
    assert [c.id for c in load_cases(tmp_path, BIB)] == ["orbit-sso-600"]


def test_missing_cases_directory_is_an_error(tmp_path: Path) -> None:
    from orbitlife_build.validation import main

    bib = tmp_path / "refs.bib"
    bib.write_text(BIB)
    out = tmp_path / "out.json"
    with pytest.raises(SystemExit, match="does not exist"):
        main(["--cases", str(tmp_path / "nope"), "--bib", str(bib), "--out", str(out)])


def test_invalid_case_file_error_names_the_file(tmp_path: Path) -> None:
    import yaml

    (tmp_path / "broken.yaml").write_text(yaml.safe_dump(_case(id="Bad Id With Spaces")))
    with pytest.raises(ValueError, match=r"broken\.yaml"):
        load_cases(tmp_path, BIB)


def test_yaml_syntax_error_names_the_file(tmp_path: Path) -> None:
    (tmp_path / "typo.yaml").write_text('id: "unclosed\ntitle: x\n')
    with pytest.raises(ValueError, match=r"typo\.yaml"):
        load_cases(tmp_path, BIB)


# ---- E1: expected documented misses ----

_MISS = {"kind": "documented_miss", "reason": "empirical density models under-predict storms"}


def test_expected_miss_that_fails_is_known_miss(fake_module: types.ModuleType) -> None:
    case = ValidationCase.model_validate(_case(inputs={"altitude_km": 700.0}, expected=_MISS))
    result = run_case(case)
    assert result.outcome is Outcome.KNOWN_MISS
    assert result.residual is not None


def test_expected_miss_that_passes_is_flagged(fake_module: types.ModuleType) -> None:
    result = run_case(ValidationCase.model_validate(_case(expected=_MISS)))
    assert result.outcome is Outcome.PASS
    assert "expected a documented miss" in result.detail


def test_expected_miss_needs_a_reason() -> None:
    with pytest.raises(ValidationError):
        ValidationCase.model_validate(_case(expected={"kind": "documented_miss", "reason": ""}))


def test_known_miss_does_not_fail_ci_but_strict_still_fails_on_not_implemented(
    tmp_path: Path, fake_module: types.ModuleType
) -> None:
    import yaml
    from orbitlife_build.validation import main

    (tmp_path / "miss.yaml").write_text(
        yaml.safe_dump(_case(id="a-miss", inputs={"altitude_km": 700.0}, expected=_MISS))
    )
    bib = tmp_path / "refs.bib"
    bib.write_text(BIB)
    out = tmp_path / "out.json"
    args = ["--cases", str(tmp_path), "--bib", str(bib), "--out", str(out)]
    assert main(args) == 0
    assert main([*args, "--strict"]) == 0
    (tmp_path / "todo.yaml").write_text(
        yaml.safe_dump(_case(id="a-todo", target="orbitlife.nope.fn"))
    )
    assert main([*args, "--strict"]) == 1


def test_console_shows_detail_for_flagged_results(
    fake_module: types.ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    from orbitlife_build.validation import _print_table

    passed = run_case(ValidationCase.model_validate(_case(expected=_MISS)))
    missed = run_case(
        ValidationCase.model_validate(_case(id="b", inputs={"altitude_km": 700.0}, expected=_MISS))
    )
    _print_table([passed, missed])
    out = capsys.readouterr().out
    assert "expected a documented miss but passed" in out
    assert "empirical density models under-predict storms" in out
