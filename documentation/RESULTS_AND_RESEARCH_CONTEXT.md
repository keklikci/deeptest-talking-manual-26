# Competition results and research context

This repository is the submitted Exida test generator for the DeepTest 2026
competition. The documents below are research references, not executable benchmark
artifacts.

## Sources

- [Exida Test Generator at the DeepTest 2026 Tool Competition](https://dl.acm.org/doi/full/10.1145/3786154.3796501)
- [DeepTest Tool Competition 2026: Benchmarking an LLM-Based Automotive Assistant](https://dl.acm.org/doi/10.1145/3786154.3796504)
- [Public competition results repository](https://github.com/keklikci/results-talking-manual-26)

## Reported results

The two papers report different evaluation contexts. They should not be treated as
interchangeable:

| Context | Reported Exida result | Interpretation |
| --- | --- | --- |
| Exida methodology paper | Failure rate `0.656`; normalized diversity `0.905` under a fixed budget of 100 generated tests | Controlled comparison against the paper's two baselines |
| Competition results paper | `57%` failure rate in the benchmark summary | Competition-wide benchmark result averaged across the reported evaluation setup |
| Competition ranking | Second place overall | Final ranking using the competition's combined assessment |

The competition results paper describes four submitted tools, two assistants, two
vehicle manuals, and evaluation with multiple model configurations and repeated
runs. It reports failure rate, warning coverage, failure coverage, and a combined
overall score. The paper's overall ranking places ATLAS first and Exida second; the
results repository contains the associated evaluation artifacts and extended data.

The methodology paper focuses on Exida's three-stage prompt decomposition: scene
generation, intent extraction, and question formulation. Its reported fixed-budget
figures measure failure-inducing generation and question diversity for that study,
not the final competition ranking.

## Reproducibility and limitations

Local execution is useful for checking integration with the mock SUT and simple
oracle, but it does not reproduce the industrial benchmark. The industrial SUT,
evaluation manuals, and competition-only execution conditions are not included in
this repository.

Results are also sensitive to LLM choice, temperature, token limits, prompt wording,
random sampling, and the available warning list. Consequently, a local run can
produce different requests and scores from the published experiments. The unit
tests intentionally mock LLM calls and verify generator state transitions; they are
behavioral regression tests, not a replacement for the competition evaluation.

Finally, the metrics answer different questions. Failure rate measures the fraction
of generated requests that induce an oracle-detected failure. Warning coverage
measures how many distinct warnings are reached. Failure coverage measures coverage
of clustered failing inputs. The overall score combines selected normalized metrics;
it is not equivalent to failure rate alone.
