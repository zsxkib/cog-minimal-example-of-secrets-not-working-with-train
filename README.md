# Cog Secret Input Bug - Minimal Example

This repo shows a super simple example of a bug I found when using `Secret` inputs with `cog train`. The problem happens when you use `None` as the default value.

## What's Going On?

So here's the deal - if you try to use `cog train` with parameters that have `Secret` type and `default=None`, everything just breaks with validation errors. It's pretty annoying because:

1. It works fine in prediction mode (`cog predict`)
2. It only happens during training 
3. Using empty strings (`""`) as defaults works fine, but `None` is totally fucked

I'm 100% sure this is caused by Pydantic 2.x (specifically 2.10.6). It's just handling the validation differently than older versions and breaking everything.

## The Error Message

When you run `cog train` with parameters that have `default=None`, you get this error:

```
The return value of predict() was not valid:

2 validation errors for TrainingResponse
input.hf_repo_id
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.10/v/string_type
input.hf_token
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.10/v/string_type
```

## What I've Tried

I've messed around with this a bit and here's what I found:

### Stuff That Doesn't Work:
- Using `default=None` for both regular strings and `Secret` types - breaks every time
- Running with just some parameters - still breaks
- Trying to use `Optional[Secret]` - Cog doesn't even like this syntax

### Stuff That Works:
- Using `default=""` (empty string) instead of `None` - this is the main workaround
- Explicitly providing values for all parameters: 
  ```
  cog train -i some_input="hello" -i hf_repo_id="test" -i hf_token="dummy_token"
  ```

## The Simplest Example

I've made this super minimal example that shows the issue:

```python
def train(
    # Basic input
    some_input: str = Input(
        description="A basic string input to satisfy minimum requirements.",
        default="default value",
    ),
    # String input with None default (problematic)
    hf_repo_id: str = Input(
        description="String with None default - this causes issues.",
        default=None,
    ),
    # Secret with None default (problematic) 
    hf_token: Secret = Input(
        description="Secret with None default - this also causes issues.",
        default=None,
    ),
    # These work fine with empty string defaults
    working_repo_id: str = Input(
        description="String with empty string default - this works.",
        default="",
    ),
    working_token: Secret = Input(
        description="Secret with empty string default - this works.",
        default="",
    ),
) -> TrainingOutput:
    # Function body...
```

## How This Example Works

The code in this repo demonstrates the bug in a minimal way:

1. `train.py` accepts various inputs including problematic Secret inputs with `None` defaults
2. When run successfully, it creates a tar file containing a dummy output text file
3. `predict.py` contains a `replicate_weights` parameter that can accept this tar file
4. The predictor will extract the tar file and read the contents of the dummy output

This structure mimics the standard Cog training-to-prediction workflow.

## Technical Details

- **Cog Version**: 0.13.7
- **Pydantic Version**: 2.10.6 (the problematic one)
- **Python Version**: 3.12.6

## Workaround

Just use empty strings (`""`) as default values instead of `None`. It's not ideal but it works.

## Why This Matters

This is a real pain if you're building training pipelines with optional Secret inputs (like API keys). Having to use empty strings means you need to add extra checks in your code to see if a string is empty versus actually not provided.

## How To Fix It

The Cog team needs to fix their validation for training inputs. They're not handling the case where `None` is the default value for a `Secret` input properly. 

Pretty sure they need to:
1. Update how they handle optional inputs
2. Fix the `None` value handling for `Secret` types 
3. Make sure it works with Pydantic 2.x

## Running This Example

See the bug in action:

```bash
# This will fail
cog train -i some_input="hello"

# This works because you provide values for all the params
cog train -i some_input="hello" -i hf_repo_id="test" -i hf_token="dummy_token"

# This will still fail because one parameter is missing
cog train -i some_input="hello" -i hf_repo_id="test"
```

To test the prediction with the trained weights:

```bash
# After successful training
cog predict -i prompt="Hello world" -i replicate_weights=weights.tar
``` 