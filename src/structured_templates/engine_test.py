from structured_templates import TemplateEngine


def test_dict_if_condition() -> None:
    engine = TemplateEngine()

    template = {
        "if(True)": {
            "a": 42,
        },
        "if(False)": {
            "b": 24,
        },
    }

    result = engine.evaluate(template)
    assert result == {"a": 42}


def test_dict_for_block() -> None:
    engine = TemplateEngine()

    template = {
        "for(i in range(3))": {
            "key${{i}}": "value${{i}}",
        },
    }

    result = engine.evaluate(template)
    assert result == {
        "key0": "value0",
        "key1": "value1",
        "key2": "value2",
    }


def test_basic_expression() -> None:
    engine = TemplateEngine()
    assert engine.evaluate({"key": "${{ 1 + 1 }}"}) == {"key": 2}


def test_multiple_scopes() -> None:
    engine = TemplateEngine({"x": 2})

    template = {
        "for(i in range(2))": {
            "a${{i}}": "${{i * x}}",
        }
    }

    result = engine.evaluate(template)
    assert result == {"a0": 0, "a1": 2}


def test_nonrecursive() -> None:
    engine = TemplateEngine({"x": 2})

    template = {
        "if(True)": {
            "for(i in range(2))": {
                "a${{i}}": "${{i * x}}",
            }
        },
        "if(False)": {
            "a": 42,
        },
    }

    result = engine.evaluate(template, recursive=False)
    assert result == {
        "for(i in range(2))": {
            "a${{i}}": "${{i * x}}",
        }
    }

    result = engine.evaluate(result, recursive=False)
    assert result == {
        "with(i=0)": {
            "a${{i}}": "${{i * x}}",
        },
        "with(i=1)": {
            "a${{i}}": "${{i * x}}",
        },
    }

    result = engine.evaluate(result, recursive=False)
    assert result == {
        "a0": 0,
        "a1": 2,
    }


def test_list() -> None:
    engine = TemplateEngine()

    template = [
        "${{ 1 + 1 }}",
        "${{ 2 + 2 }}",
    ]

    result = engine.evaluate(template)
    assert result == [2, 4]
