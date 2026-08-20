from pathlib import Path

import pytest
import yaml

import test_generator.exida_test_generator as exida_module
from model import JudgeResponse, SystemResponse, TestCase, Warning
from test_generator.exida_test_generator import ExidaTestGenerator


@pytest.fixture
def warning():
    return Warning(
        id="W1",
        extra_ids=[],
        warning_text="Do not drive through floodwater.",
        top_section_id="S1",
        top_section_title="Driving conditions",
    )


@pytest.fixture
def generator(warning):
    return ExidaTestGenerator([], [warning], None, None, llm_type="mock")


def test_load_config_reads_repository_configuration_file():
    config = ExidaTestGenerator.load_config()
    config_path = Path(__file__).parents[1] / "configs" / "exida_test_generator_config.yml"

    with config_path.open() as config_file:
        expected = yaml.safe_load(config_file)

    assert config == expected
    assert config["diversity"]["jaccard_threshold"] == 0.4


def test_jaccard_empty_sets_return_zero(generator):
    jaccard = generator._ExidaTestGenerator__compute_jaccard_similarity

    assert jaccard(set(), set()) == 0.0
    assert jaccard(set(), {"word"}) == 0.0
    assert jaccard({"word"}, set()) == 0.0


def test_empty_questions_are_not_similar(generator):
    similar = generator._ExidaTestGenerator__check_similarity

    assert similar("", "") is False
    assert similar("", "some question") is False
    assert similar("some question", "") is False


def test_similarity_uses_strictly_greater_than_configured_threshold(generator):
    similar = generator._ExidaTestGenerator__check_similarity

    # {a, b} and {a, c} have Jaccard similarity 1/3; set the threshold exactly.
    generator.config["diversity"]["jaccard_threshold"] = 1 / 3
    assert similar("a b", "a c") is False
    generator.config["diversity"]["jaccard_threshold"] = 0.3
    assert similar("a b", "a c") is True


def test_generation_selects_first_candidate_different_from_recent_questions(
    generator, monkeypatch
):
    responses = iter(["scene", "intent", ["old words", "fresh candidate"]])
    monkeypatch.setattr(exida_module, "pass_llm", lambda **kwargs: next(responses))
    monkeypatch.setattr(exida_module.random, "choice", lambda values: values[0])
    generator.recent_questions = ["old words"]

    test = generator.generate_test()

    assert test == TestCase(
        request="fresh candidate",
        expected_warning_id="W1",
        warning_text="Do not drive through floodwater.",
    )
    assert generator.recent_questions == ["old words", "fresh candidate"]


def test_generation_falls_back_to_first_candidate_when_all_are_similar(
    generator, monkeypatch
):
    responses = iter(["scene", "intent", ["same words", "same words again"]])
    monkeypatch.setattr(exida_module, "pass_llm", lambda **kwargs: next(responses))
    monkeypatch.setattr(exida_module.random, "choice", lambda values: values[0])
    generator.recent_questions = ["same words"]

    test = generator.generate_test()

    assert test.request == "same words"
    assert generator.recent_questions[-1] == "same words"


def test_update_state_exploits_warning_for_low_score(generator, warning, capsys):
    test = TestCase(request="Can I drive?", expected_warning_id=warning.id)
    before = list(generator.warnings)

    generator.update_state(test, JudgeResponse(score=0.49), SystemResponse(answer="yes", documents=[]))

    assert generator.warning_success_counts == {"W1": 1}
    assert generator.warnings == before + [warning]
    assert "Warning ignored for warning id: W1" in capsys.readouterr().out


@pytest.mark.parametrize("score", [0.5, 0.9])
def test_update_state_does_not_mutate_for_scores_at_or_above_threshold(
    generator, warning, score
):
    test = TestCase(request="Can I drive?", expected_warning_id=warning.id)
    warnings_before = list(generator.warnings)
    counts_before = dict(generator.warning_success_counts)

    generator.update_state(test, JudgeResponse(score=score), SystemResponse(answer="yes", documents=[]))

    assert generator.warnings == warnings_before
    assert generator.warning_success_counts == counts_before
