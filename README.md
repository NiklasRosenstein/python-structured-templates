# structured-templates

This package implements a simple templating engine for structured data, such as YAML or JSON. It is designed to be
used in conjunction with any structured data format, such as JSON, YAML or TOML. It provides control elements and
variable substition, all based on evaluating keys and strings.

## Example

```yaml
apiVersion: v1
kind: Secret
data:
  password: ${{ b64encode(secrets.password) }}
  if(secrets.username):
    username: ${{ b64encode(secrets.username) }}
  for(key, value in secrets.additional.items()):
    ${{ key }}: ${{ b64encode(value) }}
```

This example demonstrates how to use the templating engine to generate a Kubernetes Secret object. The `if(...)` and
`for(...)` control elements are used to conditionally include keys and loop over a dictionary, respectively. The
`${{ ... }}` syntax is used to evaluate expressions and substitute the result into the template.

## Usage

Install the package from PyPI:

```bash
pip install structured-templates
```

The `TemplateEngine` is the main class that is used to evaluate templates.

```py
from structured_templates import TemplateEngine

engine = TemplateEngine()
assert engine.evaluate({"key": "${{ 1 + 1 }}"}) == {"key": 2}
```

## Specification

### Value substitution

Value substitution is done by evaluating an expression and substituting the result into the template. The expression
can be any valid Python expression, and the result type is inserted as-is into the template. If the result is a string,
the value substition can be prefixed and/or suffixed with text.

```yaml
key: prefix${{ expression }}suffix
10integers: ${{ list(range(10)) }}
```

Attempting to substitute a non-string value into a string will raise an error.

### Control elements

#### `if(<expr>)`

Conditionally include keys in the parent object or items in a list. The value of this control block can only be
a scalar value if the parent object is a list.

> ```yaml
> items:
>  - item1
>  - if(condition): item2
>  - if(condition):
>    - item3
>    - item4
> ```

May result in

```yaml
items:
  - item1
  - item2
  - item3
  - item4
```

#### `for(<names> in <expr>)`

Iterate over the elements of an iterable. The value for this field is evaluated in the new scope. If the value is
an object, the results of every loop are merged into a single object. If the value is a list, the results are
concatenated. The value of this control block cannot be a scalar value.

> ```yaml
> items:
>   for(idx in range(2)):
>     ${{ str(idx) }}: Number ${idx}
> ```

Results in

```yaml
items:
  '0': Number 0
  '1': Number 1    
```

#### `macro(<expr>)`

Define a macro that can be used in the template.

> ```yaml
> macro(inc(x)): ${{ x + 1 }}
> key: ${{ inc(1) }}
> ```

Results in

```yaml
key: 2
```
