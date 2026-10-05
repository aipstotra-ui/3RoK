import orbitlife
import orbitlife_build


def test_build_package_sees_core_package() -> None:
    assert orbitlife_build.__doc__
    assert orbitlife.__version__
