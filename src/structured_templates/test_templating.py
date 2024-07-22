from structured_templates import TemplateEngine


def test_dict_if_condition() -> None:
    template_engine = TemplateEngine()

    template = {
        "if(True)": {
            "a": 42,
        },
        "if(False)": {
            "b": 24,
        },
    }

    result = template_engine.evaluate(template)
    assert result == {"a": 42}


def test_dict_for_block() -> None:
    template_engine = TemplateEngine()

    template = {
        "for(i in range(3))": {
            "key${{i}}": "value${{i}}",
        },
    }

    result = template_engine.evaluate(template)
    assert result == {
        "key0": "value0",
        "key1": "value1",
        "key2": "value2",
    }
