import os
from os.path import expanduser
import sys
import logging
import sqlfluff
from sqlfluff.core.config import FluffConfig
from sqlfluff.core import Linter
import sqlparse


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


def lint_result_object_to_line_dict(lint_result: list):
    result_dict = {}

    for result in lint_result:
        if result.line_no not in result_dict:
            result_dict[result.line_no] = ''

        result_dict[result.line_no] += '{}:{} - {} '.format(
            result.rule.code, str(result.line_pos), result.description)

    return result_dict


def insert_lint_comments_in_sql_string_array(sql_string_array, lint_result_line_dict):
    for key in lint_result_line_dict.keys():
        sql_string_array[key - 1] += ' -- ' + lint_result_line_dict[key]

    return '\n'.join(sql_string_array)


sql_string = ''
is_lint_request = False
i = 0
max_format_iterations = 3
stop_iterations = False
fluff_config_path = expanduser("~") + os.path.sep + '.sqlfluff'

for line in sys.stdin:
    if 'exit' == line.rstrip().lower():
        break

    sql_string += line

if sql_string.strip()[0] == '?':
    is_lint_request = True
    sql_string = sql_string.strip()[1:]

#print("-------- ORIGINAL QUERY --------")
# print(sql_string)

with DisableLogger():
    try:
        fluff_config = FluffConfig.from_path(path=fluff_config_path)

        sql_parsed = sqlfluff.parse(sql_string)
        fluff_linter = Linter(config=fluff_config)

        if is_lint_request:
            linter_result = fluff_linter.lint(
                tree=sql_parsed.tree, config=fluff_config)

            print(insert_lint_comments_in_sql_string_array(
                sql_string.splitlines(), lint_result_object_to_line_dict(linter_result)))
        else:
            """
            sql_string_preformatted = ''
            sql_statements = sqlparse.split(sql_string)

            for statement in sql_statements:
                sql_string_preformatted += sqlparse.format(statement, reindent=True, reindent_aligned=False, keyword_case='upper', identifier_case='lower', use_space_around_operators=True, indent_width=4, comma_first=True) + '\n'

            print(sql_string_preformatted) 
            """

            previous_fixed_sql_string = ''
            fixed_sql_string = ''

            while i < max_format_iterations:
                fixed_sql, linter_result = fluff_linter.fix(
                    tree=sql_parsed.tree, config=fluff_config)
                fixed_sql_string = fixed_sql.raw
                i += 1

                if fixed_sql_string == previous_fixed_sql_string:
                    break
                else:
                    previous_fixed_sql_string = fixed_sql_string
                    sql_parsed = sqlfluff.parse(fixed_sql_string)

            print(fixed_sql_string)

    except Exception as e:
        print(sql_string)
        print('/*')
        print(e)
        print('*/')
