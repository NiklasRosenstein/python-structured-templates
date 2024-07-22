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
