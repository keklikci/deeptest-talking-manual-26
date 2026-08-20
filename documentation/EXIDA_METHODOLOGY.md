# Exida methodology and reproducibility

## Purpose

Exida is a test generator for conversational assistants that retrieve information
from vehicle owner manuals. Its target is a request for which the assistant should
mention a safety warning but may omit it. The generator receives the extracted
warning list and produces a `TestCase` containing a user request and the warning
expected to be checked by the oracle.

## Generation pipeline

For each test, `ExidaTestGenerator` performs these stages:

1. It selects a warning and its component from the supplied warning list.
2. It generates a concrete scene using ordinary context such as weather, a
   destination, and time pressure. The prompt asks the model to avoid warning
   terminology while retaining the circumstance addressed by the warning.
3. It extracts the driver intent from that scene in a short, casual phrase.
4. It requests a batch of candidate questions about the action and circumstance.
5. It filters candidates against a bounded recent-question window using word-set
   Jaccard similarity, then returns the first sufficiently different candidate.

The scene and extracted intent are transient scaffolding. They influence the final
question but are not returned as the user request. This separation is intentional:
the final request can sound like a normal driver question while retaining enough
context to make a warning relevant.

## Configuration

The defaults are stored in
[`configs/exida_test_generator_config.yml`](../configs/exida_test_generator_config.yml):

| Setting | Default | Meaning |
| --- | ---: | --- |
| Scene temperature | `0.9` | Variation for scene generation |
| Intent temperature | `0.4` | More focused intent extraction |
| Question temperature | `0.8` | Variation in final questions |
| Stage token limits | `100`, `30`, `50` | Maximum output per stage |
| Candidate batch size | `3` | Questions considered per generation |
| Recent-question window | `8` | Requests retained for diversity checks |
| Jaccard threshold | `0.4` | Candidate is rejected only when similarity is greater than this |
| Exploitation copies | `1` | Extra warning entry after a judged failure |

## Why context degradation can expose failures

Manual warnings often depend on environmental conditions, component state, or an
action that sounds routine. Exida constructs the condition first, compresses it to
the driver intent, and then asks for a concise request. This progressively removes
technical phrasing and direct warning cues while preserving a plausible situation.
The resulting requests are intended to probe whether the assistant propagates the
warning when it is relevant, rather than merely matching an explicit warning phrase.

## Competition constraints and local execution

The competition pipeline validates requests before execution. Requests are expected
to use English vocabulary and contain fewer than 25 words; invalid requests are not
executed as failures. The repository's mock SUT and simple oracle are useful for
local development, but they are not the industrial evaluation environment.

Install the locked environment and run a bounded local example with:

```bash
uv sync
uv run python main.py --time_limit_seconds 60 --n_tests 100 \
  --test_generator custom --sut_type mock --oracle_type simple
```

Cloud and local LLM modes require their own provider setup. Do not commit API keys,
`.env` files, model caches, or private manuals. The unit tests use monkeypatching to
replace `pass_llm`, making test execution deterministic and offline:

```bash
uv run pytest
```

The repository validation compiles only project source directories; it intentionally
does not recurse into the generated `.venv` directory.
