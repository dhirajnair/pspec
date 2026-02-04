"""Rule mapping layer: pycodestyle code → PEP 8 section, spec quote, suggestion.
Section URL fragment derived from section title. Reference: https://peps.python.org/pep-0008/
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

# PEP 8 section title → URL fragment (peps.python.org/pep-0008/#fragment)
_SECTION_FRAGMENTS: Dict[str, str] = {
    "Indentation": "indentation",
    "Whitespace in Expressions and Statements": "whitespace-in-expressions-and-statements",
    "Comments": "comments",
    "Blank Lines": "blank-lines",
    "Imports": "imports",
    "Maximum Line Length": "maximum-line-length",
    "Code Lay-out": "code-lay-out",
    "Programming Recommendations": "programming-recommendations",
    "Naming Conventions": "naming-conventions",
    "String Quotes": "string-quotes",
    "PEP 8": "",
}

# (pep8_quote, pep8_section, suggestion)
_RULE_MAP: Dict[str, Tuple[str, str, str]] = {
    # E1 Indentation
    "E101": (
        "Indentation contains mixed spaces and tabs.",
        "Indentation",
        "Use spaces only (4 spaces per indent level).",
    ),
    "E111": (
        "Indentation is not a multiple of four.",
        "Indentation",
        "Use 4 spaces per indentation level.",
    ),
    "E112": (
        "Expected an indented block.",
        "Indentation",
        "Add an indented block after the colon.",
    ),
    "E113": (
        "Unexpected indentation.",
        "Indentation",
        "Fix indentation to match the logical structure.",
    ),
    "E114": (
        "Indentation is not a multiple of four (comment).",
        "Indentation",
        "Indent comments to a multiple of 4 spaces.",
    ),
    "E115": (
        "Expected an indented block (comment).",
        "Indentation",
        "Indent the comment block properly.",
    ),
    "E116": (
        "Unexpected indentation (comment).",
        "Indentation",
        "Fix comment indentation.",
    ),
    "E117": (
        "Over-indented.",
        "Indentation",
        "Reduce indentation to match the block.",
    ),
    "E121": (
        "Continuation line under-indented for hanging indent.",
        "Indentation",
        "Align continuation line with opening delimiter or use hanging indent (4 spaces).",
    ),
    "E122": (
        "Continuation line missing indentation or outdented.",
        "Indentation",
        "Indent the continuation line.",
    ),
    "E123": (
        "Closing bracket does not match indentation of opening bracket's line.",
        "Indentation",
        "Align closing bracket with the first character of the line that starts the construct.",
    ),
    "E124": (
        "Closing bracket does not match visual indentation.",
        "Indentation",
        "Match closing bracket to visual indentation.",
    ),
    "E125": (
        "Continuation line with same indent as next logical line.",
        "Indentation",
        "Indent continuation line further or use hanging indent.",
    ),
    "E126": (
        "Continuation line over-indented for hanging indent.",
        "Indentation",
        "Use 4 spaces for hanging indent.",
    ),
    "E127": (
        "Continuation line over-indented for visual indent.",
        "Indentation",
        "Reduce continuation line indent to match opening.",
    ),
    "E128": (
        "Continuation line under-indented for visual indent.",
        "Indentation",
        "Indent continuation line to align with opening delimiter.",
    ),
    "E129": (
        "Visually indented line with same indent as next logical line.",
        "Indentation",
        "Indent to distinguish from the next logical line.",
    ),
    "E131": (
        "Continuation line unaligned for hanging indent.",
        "Indentation",
        "Align continuation lines for hanging indent.",
    ),
    "E133": (
        "Closing bracket is missing indentation.",
        "Indentation",
        "Indent the closing bracket.",
    ),
    # E2 Whitespace
    "E201": (
        "Whitespace after '('.",
        "Whitespace in Expressions and Statements",
        "Remove whitespace immediately inside parentheses.",
    ),
    "E202": (
        "Whitespace before ')'.",
        "Whitespace in Expressions and Statements",
        "Remove whitespace immediately inside parentheses.",
    ),
    "E203": (
        "Whitespace before ',', ';', or ':'.",
        "Whitespace in Expressions and Statements",
        "Remove whitespace before the punctuation.",
    ),
    "E204": (
        "Whitespace after decorator '@'.",
        "Whitespace in Expressions and Statements",
        "Remove whitespace between @ and decorator name.",
    ),
    "E211": (
        "Whitespace before '('.",
        "Whitespace in Expressions and Statements",
        "Do not put whitespace between a function name and the opening parenthesis.",
    ),
    "E221": (
        "Multiple spaces before operator.",
        "Whitespace in Expressions and Statements",
        "Use at most one space before and after operators.",
    ),
    "E222": (
        "Multiple spaces after operator.",
        "Whitespace in Expressions and Statements",
        "Use at most one space after operators.",
    ),
    "E223": (
        "Tab before operator.",
        "Whitespace in Expressions and Statements",
        "Use spaces, not tabs, around operators.",
    ),
    "E224": (
        "Tab after operator.",
        "Whitespace in Expressions and Statements",
        "Use spaces, not tabs, around operators.",
    ),
    "E225": (
        "Missing whitespace around operator.",
        "Whitespace in Expressions and Statements",
        "Surround operators with a single space on each side.",
    ),
    "E226": (
        "Missing whitespace around arithmetic operator.",
        "Whitespace in Expressions and Statements",
        "Surround arithmetic operators with spaces.",
    ),
    "E227": (
        "Missing whitespace around bitwise or shift operator.",
        "Whitespace in Expressions and Statements",
        "Surround bitwise/shift operators with spaces.",
    ),
    "E228": (
        "Missing whitespace around modulo operator.",
        "Whitespace in Expressions and Statements",
        "Surround the % operator with spaces.",
    ),
    "E231": (
        "Missing whitespace after ',', ';', or ':'.",
        "Whitespace in Expressions and Statements",
        "Add one space after commas, semicolons, and colons (when not starting a block).",
    ),
    "E241": (
        "Multiple spaces after ','.",
        "Whitespace in Expressions and Statements",
        "Use exactly one space after a comma.",
    ),
    "E242": (
        "Tab after ','.",
        "Whitespace in Expressions and Statements",
        "Use a space after a comma, not a tab.",
    ),
    "E251": (
        "Unexpected spaces around keyword / parameter equals.",
        "Whitespace in Expressions and Statements",
        "Do not use spaces around the = sign for keyword arguments.",
    ),
    "E261": (
        "At least two spaces before inline comment.",
        "Comments",
        "Separate inline comments by at least two spaces from the statement.",
    ),
    "E262": (
        "Inline comment should start with '# '.",
        "Comments",
        "Use exactly one space after the # for inline comments.",
    ),
    "E265": (
        "Block comment should start with '# '.",
        "Comments",
        "Use exactly one space after the # for block comments.",
    ),
    "E266": (
        "Too many leading '#' for block comment.",
        "Comments",
        "Use a single # for block comments.",
    ),
    "E271": (
        "Multiple spaces after keyword.",
        "Whitespace in Expressions and Statements",
        "Use one space after keywords.",
    ),
    "E272": (
        "Multiple spaces before keyword.",
        "Whitespace in Expressions and Statements",
        "Use one space before keywords.",
    ),
    "E273": (
        "Tab after keyword.",
        "Whitespace in Expressions and Statements",
        "Use spaces, not tabs, after keywords.",
    ),
    "E274": (
        "Tab before keyword.",
        "Whitespace in Expressions and Statements",
        "Use spaces, not tabs, before keywords.",
    ),
    "E275": (
        "Missing whitespace after keyword.",
        "Whitespace in Expressions and Statements",
        "Add a space after the keyword.",
    ),
    # E3 Blank lines
    "E301": (
        "Expected 1 blank line, found 0.",
        "Blank Lines",
        "Add one blank line before method definitions inside a class.",
    ),
    "E302": (
        "Expected 2 blank lines, found 0/1.",
        "Blank Lines",
        "Surround top-level function and class definitions with two blank lines.",
    ),
    "E303": (
        "Too many blank lines.",
        "Blank Lines",
        "Remove extra blank lines; use at most two between top-level definitions.",
    ),
    "E304": (
        "Blank lines found after function decorator.",
        "Blank Lines",
        "Do not put blank lines between the decorator and the function definition.",
    ),
    "E305": (
        "Expected 2 blank lines after end of function or class.",
        "Blank Lines",
        "Add two blank lines after the end of a function or class.",
    ),
    "E306": (
        "Expected 1 blank line before a nested definition.",
        "Blank Lines",
        "Add one blank line before nested function or class definitions.",
    ),
    # E4 Import
    "E401": (
        "Multiple imports on one line.",
        "Imports",
        "Put imports on separate lines.",
    ),
    "E402": (
        "Module level import not at top of file.",
        "Imports",
        "Place all imports at the top of the file, after module comments and docstrings.",
    ),
    # E5 Line length
    "E501": (
        "Line too long (PEP 8 recommends 79 characters for code, 72 for comments).",
        "Maximum Line Length",
        "Break the line or keep it under 79 characters.",
    ),
    "E502": (
        "The backslash is redundant between brackets.",
        "Maximum Line Length",
        "Remove the backslash; implied line continuation inside brackets.",
    ),
    # E7 Statement
    "E701": (
        "Multiple statements on one line (colon).",
        "Code Lay-out",
        "Put only one statement per line.",
    ),
    "E702": (
        "Multiple statements on one line (semicolon).",
        "Code Lay-out",
        "Put only one statement per line; avoid semicolons.",
    ),
    "E703": (
        "Statement ends with a semicolon.",
        "Code Lay-out",
        "Remove the trailing semicolon.",
    ),
    "E704": (
        "Multiple statements on one line (def).",
        "Code Lay-out",
        "Put the def on its own line.",
    ),
    "E711": (
        "Comparison to None should be 'if cond is None:'.",
        "Programming Recommendations",
        "Use 'is None' instead of == None.",
    ),
    "E712": (
        "Comparison to True should be 'if cond is True:' or 'if cond:'.",
        "Programming Recommendations",
        "Do not compare to True/False with ==; use 'if cond:' or 'if cond is True:'.",
    ),
    "E713": (
        "Test for membership should be 'not in'.",
        "Programming Recommendations",
        "Use 'x not in seq' instead of 'not x in seq'.",
    ),
    "E714": (
        "Test for object identity should be 'is not'.",
        "Programming Recommendations",
        "Use 'is not' instead of 'not ... is'.",
    ),
    "E721": (
        "Do not compare types, use 'isinstance()'.",
        "Programming Recommendations",
        "Use isinstance(x, type) instead of type(x) == type.",
    ),
    "E722": (
        "Do not use bare except, specify exception instead.",
        "Programming Recommendations",
        "Catch a specific exception (e.g. except ValueError:).",
    ),
    "E731": (
        "Do not assign a lambda expression, use a def.",
        "Programming Recommendations",
        "Use a normal function definition instead of assigning a lambda.",
    ),
    "E741": (
        "Do not use variables named 'l', 'O', or 'I' (ambiguous).",
        "Naming Conventions",
        "Use descriptive names; avoid single letters l, O, I.",
    ),
    "E742": (
        "Do not define classes named 'l', 'O', or 'I'.",
        "Naming Conventions",
        "Use a descriptive class name.",
    ),
    "E743": (
        "Do not define functions named 'l', 'O', or 'I'.",
        "Naming Conventions",
        "Use a descriptive function name.",
    ),
    # E9 Runtime
    "E901": (
        "SyntaxError or IndentationError.",
        "Code Lay-out / Syntax",
        "Fix the syntax or indentation error.",
    ),
    "E902": (
        "IOError.",
        "N/A",
        "Resolve the file or IO error.",
    ),
    # W1
    "W191": (
        "Indentation contains tabs.",
        "Indentation",
        "Use spaces instead of tabs (4 spaces per indent).",
    ),
    # W2
    "W291": (
        "Trailing whitespace.",
        "Whitespace in Expressions and Statements",
        "Remove trailing spaces at the end of the line.",
    ),
    "W292": (
        "No newline at end of file.",
        "Blank Lines",
        "Add a newline at the end of the file.",
    ),
    "W293": (
        "Blank line contains whitespace.",
        "Whitespace in Expressions and Statements",
        "Remove whitespace from blank lines.",
    ),
    # W3
    "W391": (
        "Blank line at end of file.",
        "Blank Lines",
        "Remove trailing blank lines at end of file.",
    ),
    # W5
    "W503": (
        "Line break before binary operator.",
        "Maximum Line Length",
        "PEP 8 allows break before or after binary operator; this check flags before.",
    ),
    "W504": (
        "Line break after binary operator.",
        "Maximum Line Length",
        "Line break after binary operator (alternative style).",
    ),
    "W505": (
        "Doc line too long.",
        "Maximum Line Length",
        "Wrap docstrings to 72 characters per line.",
    ),
    # W6
    "W605": (
        "Invalid escape sequence.",
        "String Quotes",
        "Use a raw string (r'...') or valid escape sequences.",
    ),
}

PEP8_URL = "https://peps.python.org/pep-0008/"


def get_pep8_info(code: str, message: str) -> Tuple[str, str, str, Optional[str]]:
    """Return (pep8_quote, pep8_section, suggestion, pep8_section_url_fragment) for a pycodestyle code."""
    entry = _RULE_MAP.get(code)
    if entry:
        quote, section, suggestion = entry
        frag = _SECTION_FRAGMENTS.get(section)
        return (quote, section, suggestion, frag or None)
    return (
        "This style issue is reported by pycodestyle; see PEP 8 for the full style guide.",
        "PEP 8",
        message or "Review PEP 8 and correct the reported issue.",
        None,
    )
