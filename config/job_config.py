class JobConfig:
    """
    Description:
        코드 채점 작업 설정 관련 설정(동시에 유지 가능한 코드 채점 job 갯수 제한 등)을 관리하는 클래스.
    """
    MAX_JOB_COUNT_PER_USER = 2
    VALID_LANGUAGE = {'java17', 'nodejs20', 'nodejs20esm'}
    LANGUAGE_TIME_BONUS_SECONDS = {
        'java17': 1.0,
        'nodejs20': 0.0,
        'nodejsesm': 0.0
    }
