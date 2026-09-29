from __future__ import annotations

import ast

from docagent.adapters.fake_llm import FakeDocGenerator
from docagent.domain.analyzer import analyze_source
from docagent.domain.models import DocProposal
from docagent.domain.rendering import render_documented_source
from docagent.ports.llm import DocGenerator

SOURCE = '''def multiply(a, b):
    return a * b


class Counter:
    def increment(self):
        self.n += 1
'''


def test_fake_conforms_to_protocol() -> None:
    gen = FakeDocGenerator()
    assert isinstance(gen, DocGenerator)


def test_fake_returns_docstring_per_target() -> None:
    gen = FakeDocGenerator()
    report = analyze_source(SOURCE, "src/m.py").value
    for target in report.targets:
        result = gen.generate_docstring(target)
        assert result.is_ok()
        assert isinstance(result.value, str)
        assert result.value.strip() != ""


def test_offline_pipeline_analyze_generate_render() -> None:
    gen = FakeDocGenerator()
    report = analyze_source(SOURCE, "src/m.py").value
    assert report.has_missing()

    proposals = []
    for target in report.targets:
        text = gen.generate_docstring(target).value
        proposals.append(DocProposal(target=target, docstring=text))

    rendered = render_documented_source(SOURCE, proposals)
    assert rendered.is_ok()

    # The rendered file parses and has no remaining missing docstrings.
    ast.parse(rendered.value)
    second = analyze_source(rendered.value, "src/m.py").value
    assert second.missing_count() == 0
