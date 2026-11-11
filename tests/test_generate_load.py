import json
from http.client import BadStatusLine, HTTPException
from pathlib import Path
from runpy import run_path
from types import SimpleNamespace
from urllib.error import HTTPError, URLError

import pytest

from careerpath.schema import Profile


@pytest.fixture(scope="module")
def generator():
    return run_path(Path(__file__).parents[1] / "scripts" / "generate_load.py")


def test_payloads_are_seeded_valid_and_shift_only_numeric_features(generator):
    build = generator["build_payloads"]
    baseline = build(100, seed=42, scenario="baseline")
    shifted = build(100, seed=42, scenario="shifted")
    assert len(baseline) == len(shifted) == 100
    assert baseline == build(100, seed=42, scenario="baseline")
    assert baseline != build(100, seed=43, scenario="baseline")
    assert len({p["age"] for p in baseline}) > 1
    assert len({p["hours_per_week"] for p in baseline}) > 1
    for original, changed in zip(baseline, shifted, strict=True):
        Profile.model_validate(original)
        Profile.model_validate(changed)
        assert changed == {
            **original,
            "age": original["age"] + 12,
            "hours_per_week": original["hours_per_week"] + 12,
        }


@pytest.mark.parametrize(("count", "scenario"), [(0, "baseline"), (-1, "baseline"), (1, "other")])
def test_invalid_build_parameters(generator, count, scenario):
    with pytest.raises(ValueError):
        generator["build_payloads"](count, seed=42, scenario=scenario)


@pytest.mark.parametrize(
    "args",
    [
        ["--count", "0"],
        ["--count", "2", "--invalid-every", "3"],
        ["--invalid-every", "-1"],
        ["--url", "file:///tmp"],
        ["--url", "http://127.0.0.1:3000?"],
        ["--url", "http://127.0.0.1:3000#"],
        ["--url", "http://127.0.0.1:3000/a b"],
    ],
)
def test_cli_rejects_invalid_parameters(generator, monkeypatch, args):
    main = generator["main"]
    monkeypatch.setitem(main.__globals__, "build_opener", lambda *args: pytest.fail("opened HTTP"))
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2


@pytest.mark.parametrize(
    ("statuses", "interval", "exit_code", "expected"),
    [
        ([200, 400, 200, 400], 2, 0, [2, 2, 0, 0, 0, 0]),
        ([200, 200], 0, 0, [2, 0, 0, 0, 0, 0]),
        ([400, 200, 500, 302, 403, None], 2, 1, [1, 2, 1, 1, 1, 6]),
        ([BadStatusLine("bad status"), 200], 0, 1, [1, 0, 0, 0, 1, 1]),
    ],
)
def test_cli_counts_responses_and_flags_unexpected_results(
    generator,
    monkeypatch,
    capsys,
    statuses,
    interval,
    exit_code,
    expected,
):
    replies = iter(statuses)
    payloads = []

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def send(request, *, timeout):
        assert timeout == 10
        assert request.full_url == "http://127.0.0.1:3000/predict"
        assert request.get_method() == "POST"
        payloads.append(json.loads(request.data))
        status = next(replies)
        if status is None:
            raise URLError("offline")
        if isinstance(status, HTTPException):
            raise status
        if status != 200:
            raise HTTPError(request.full_url, status, "test", {}, None)
        return Response()

    main = generator["main"]
    monkeypatch.setitem(main.__globals__, "build_opener", lambda *args: SimpleNamespace(open=send))
    assert main(["--count", str(len(statuses)), "--invalid-every", str(interval)]) == exit_code
    assert [i for i, payload in enumerate(payloads, 1) if payload["age"] == -1] == (
        list(range(interval, len(statuses) + 1, interval)) if interval else []
    )
    summary = json.loads(capsys.readouterr().out)
    assert summary["sent"] == len(statuses)
    assert [
        summary[key]
        for key in (
            "2xx",
            "4xx",
            "5xx",
            "other_status",
            "network_errors",
            "unexpected",
        )
    ] == expected
