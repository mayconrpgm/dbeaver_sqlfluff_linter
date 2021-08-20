import sqlfluff
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
        result_string += '{}| {} | {} | {}\n'.format(str(result.line_no()).ljust(5), str(
            result.line_pos()).ljust(5), result.rule.code, result.description)

    result_string += '*/\n'

    return result_string


sql_string = ''
is_lint_request = False

for line in sys.stdin:
    if 'exit' == line.rstrip().lower():
        break

    sql_string += line

if sql_string.strip()[0] == '?':
    is_lint_request = True
    sql_string = sql_string.strip()[1:]

#print("-------- ORIGINAL QUERY --------")
#print(sql_string)

with DisableLogger():
    try:
        parsed = sqlfluff.parse(sql_string)

        config = FluffConfig.from_path(path=r"C:\sqlfluff\.sqlfluff")
        fluff_linter = Linter(config=config)


        #linter_result = fluff_linter.lint(tree=parsed.tree, config=config)
        fixed_sql, linter_result = fluff_linter.fix(tree=parsed.tree, config=config)

        if is_lint_request:
            print(sql_string)
            # print("-------- LINTER RESULT --------")
            print(lint_result_object_to_string(linter_result))
        else:
            # print("-------- FIXED QUERY --------")
            print(fixed_sql.raw)
        
    except Exception as e:
        print(sql_string)
        print('/*\n')
        print(e)
        print('\n*/')
