import sqlfluff
import subprocess
import os
import sys
from sqlfluff.core.config import FluffConfig
from sqlfluff.core import Linter
import logging 

class DisableLogger():
    def __enter__(self):
       logging.disable(logging.CRITICAL)
    def __exit__(self, exit_type, exit_value, exit_traceback):
       logging.disable(logging.NOTSET)

def lint_result_to_string(lint_result: dict):
    result_string = '/*\nLine | Pos   | Rule | Description\n'

    for result in lint_result:
        result_string += '{}| {} | {} | {}\n'.format(str(result['line_no']).ljust(5), str(
            result['line_pos']).ljust(5), result['code'], result['description'])

    result_string += '*/\n'

    return result_string

def lint_result_object_to_string(lint_result: list):
    result_string = '/*\nLine | Pos   | Rule | Description\n'

    for result in lint_result:
        result_string += '{}| {} | {} | {}\n'.format(str(result.line_no).ljust(5), str(
            result.line_pos).ljust(5), result.rule.code, result.description)

    result_string += '*/\n'

    return result_string


sql_string = ''

for line in sys.stdin:
    if 'exit' == line.rstrip().lower():
        break

    sql_string += line

print(sql_string)

"""
with open('query.sql', 'r') as f:
    sql_string = f.read()

#  -------- LINTING ----------
# Lint the given string and get a list of violations found.
lint_result = sqlfluff.lint(sql_string)
print(lint_result_to_string(lint_result))

#  -------- FIXING ----------
# Fix the given string and get a string back which has been fixed.
result = sqlfluff.fix(sql_string)
print(result)

with open('query_fixed.sql', 'w') as f:
    f.write(lint_result_to_string(lint_result))
    f.write(result)
"""
with DisableLogger():
    parsed = sqlfluff.parse(sql_string)

    config = FluffConfig.from_path(path='.sqlfluff')
    fluff_linter = Linter(config=config)


    #linter_result = fluff_linter.lint(tree=parsed.tree, config=config)
    fixed_sql, linter_result = fluff_linter.fix(tree=parsed.tree, config=config)
    print(lint_result_object_to_string(linter_result))
    print(fixed_sql.raw)

with open('query_fixed_2.sql', 'w') as f:
    f.write(lint_result_object_to_string(linter_result))
    f.write(fixed_sql.raw)

