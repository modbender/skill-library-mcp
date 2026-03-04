# Variables in CX Agent Studio

Variables store and retrieve runtime conversation data.

## Types
- Text: String values
- Number: Numeric values
- Yes/No: Boolean values
- Custom Object: Schema for the object
- List: List of variables (comma delimited)

## Referencing
- Use braces `{variable_name}` in instructions. CX Agent Studio replaces these with runtime values.

## Updating
- Agents cannot update variables directly.
- **Tools and callbacks** can update variables.
- Using Python tools:
  ```python
  context.state["variable_name"] = value
  ```