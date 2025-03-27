import re
from common.enums import CodeLanguage
from common.constants import TEST_CASES, TEST_CASES_MEM_LIMITS, TEST_CASES_TIME_LIMITS, TEST_CASE_LIMITS_MEMORY_BONUS, TEST_CASE_LIMITS_TIME_BONUS, CODE_FILE_NAME


def snake_to_camel(snake_str: str) -> str:
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_test_cases(challenge_id: int) -> list:
    return TEST_CASES[str(challenge_id)]


def get_memory_limit(challenge_id: int, code_language: CodeLanguage) -> int:
    return TEST_CASES_MEM_LIMITS[str(challenge_id)] + TEST_CASE_LIMITS_MEMORY_BONUS[code_language.value]


def get_time_limit(challenge_id: int, code_language: CodeLanguage) -> float:
    return TEST_CASES_TIME_LIMITS[str(challenge_id)] + TEST_CASE_LIMITS_TIME_BONUS[code_language.value]


def get_source_code_file_name(code_language: CodeLanguage) -> str:
    return CODE_FILE_NAME[code_language]