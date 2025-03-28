import logging
import binascii
from celery import Celery

from blueprint.helper import *
from common import *
from schema.job import CodeChallengeJudgmentJob as Job
from redisutil.repository import job_repository
from config import RedisConfig, JobConfig, TestCaseConfig


job_bp = flask.Blueprint('job_bp', __name__)

# celery 태스크큐에 작업을 등록하는 API를 사용하기 위한 클라이언트 객체 생성
celery_client = Celery(
    "task-sender",
    broker=RedisConfig.REDIS_URI,
    backend=RedisConfig.REDIS_URI
)

# -------------------------------------------------
# bp Error Handler
# -------------------------------------------------

@job_bp.errorhandler(Exception)
def handle_exception(e):
    logging.error("[Unexpected exception occurred]", exc_info=True)
    return error_response("Internal server error", 500)


# -------------------------------------------------
# Before Request Hook
# -------------------------------------------------

@job_bp.before_request
def validate_request():
    # -------------------------------------------------
    # EndPoint 전역 검증
    # -------------------------------------------------
    # 1) 키 검증
    api_key = flask.request.headers.get("X-Api-Key")
    client_id = flask.request.headers.get("X-Client-Id")
    if not (api_key and client_id) or not validate_hmac_key(api_key, client_id):
        return error_response("Access denied", 403)

    # 2) JSON 본문 구조 검증
    if flask.request.method not in ("GET", "HEAD") and flask.request.get_data() and not flask.request.is_json:
        return error_response("Request must be in JSON format", 400)


    # -------------------------------------------------
    # 개별 EndPoint 검증
    # -------------------------------------------------
    # 1) /job/create
    if flask.request.path == '/job/create' and flask.request.method == 'POST':
        request_body = flask.request.get_json()
        if not validate_request_body(request_body, '/job/create'):
            return error_response(
                "Request body must contain valid 'userId'(integer), 'challengeId'(integer), 'code' and 'codeLanguage'",
                400
            )
        test_cases = TestCaseConfig.get_test_cases(request_body["challengeId"])
        if not test_cases:
            return error_response(f"No test cases found for the provided 'challengeId'={request_body["challengeId"]}", 404)

        # 제출된 코드 유효성(크기 및 형식) 검사
        # 코드 검증(base64 디코딩, utf-8 디코딩, 파일 크기 검사 등) 자체는 보안 이슈를 발생시키지 않음
        code_base64 = request_body.get("code")
        try:
            # base64 디코딩 (validate=True를 사용하면 유효하지 않은 문자가 포함된 경우 예외 발생)
            decoded_bytes = base64.b64decode(code_base64, validate=True)
        except binascii.Error as e:
            return error_response("'code' field is not in a valid format", 400)
        except Exception as e:
            logging.error("Unexpected exception occurred", exc_info=True)
            return error_response("Internal server error", 500)

        # 코드 크기 1MB 초과 여부 검증
        if len(decoded_bytes) > 1 * 1024 * 1024:  # 1MB = 1,048,576 바이트
            return error_response("Source code size exceeds 1MB", 400)

        # UTF-8 디코딩 처리
        try:
            code_str = decoded_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            return error_response("'code' field is not in a valid format", 400)

        # 공백 검사
        if not code_str.strip():
            return error_response("Empty source file", 400)

    # 2) /job/execute
    elif flask.request.path == '/job/execute' and flask.request.method == 'POST':
        request_body = flask.request.get_json()
        if not validate_request_body(request_body, '/job/execute'):
            return error_response(
                "Request body must contain 'userId'(integer) and 'jobId'",
                400
            )

    # 3) /job/cancel
    elif flask.request.path == '/job/cancel' and flask.request.method == 'POST':
        request_body = flask.request.get_json()
        if not validate_request_body(request_body, '/job/cancel'):
            return error_response(
                "Request body must contain 'userId'(integer) and 'jobId'",
                400
            )

    # 4) /job
    elif flask.request.path == '/job' and flask.request.method == 'POST':
        request_body = flask.request.get_json()
        if not validate_request_body(request_body, '/job'):
            return error_response(
                "Request body must contain 'userId'(integer) and 'jobId'",
                400
            )
    return None


# -------------------------------------------------
# Route 처리
# -------------------------------------------------

# 1) /job/create
@job_bp.route('/create', methods=['POST'])
def create_job() :
    # request body 파싱
    request_data = flask.request.get_json()
    user_id = int(request_data['userId'])
    code_language = CodeLanguage[request_data['codeLanguage'].upper()]
    code = request_data['code']
    challenge_id = int(request_data['challengeId'])
    total_test_cases = len(TestCaseConfig.get_test_cases(request_data["challengeId"]))

    user_active_jobs: list[Job] = job_repository.find_by_user_id(user_id)
    if len(user_active_jobs) >= JobConfig.MAX_JOB_COUNT_PER_USER:
        return error_response(f"Max job count={JobConfig.MAX_JOB_COUNT_PER_USER} exceeded for userId:{user_id}", 422)

    job = Job.create(
        code_language=code_language,
        code=code,
        challenge_id=challenge_id,
        total_test_cases=total_test_cases
    )

    # 테스트 케이스 별 시간 제한
    test_case_time_limit = TestCaseConfig.get_time_limit(challenge_id, job.code_language)

    job_ttl = round(test_case_time_limit * total_test_cases * 2) # job ttl은 정수형 값만 허용하므로 반올림

    if job_repository.save(user_id, job, job_ttl) == 0:
        logging.error("[Handling \"/job/create\" request failed. No exception but job doesn't saved]")
        return error_response("Internal server error", 500)

    return success_response({"jobId": f"{job.job_id}"}, 201)


# 2) /job/execute
@job_bp.route('/execute', methods=['POST'])
def execute_job():
    request_data = flask.request.get_json()
    user_id = int(request_data['userId'])
    job_id = request_data['jobId']

    job: Job = job_repository.find_by_user_id_and_job_id(user_id, job_id)
    if not job:
        return error_response(f"Job not found for user_id={user_id} with job_id={job_id}", 404)

    # Celery task queue에 task를 등록
    # 매개변수 전달 시 python 기본 타입으로 전달
    celery_client.send_task('worker.tasks.execute_code', args=[user_id, job.as_dict()])
    return success_response({"totalTestCases": job.total_test_cases}, 202) # Accepted, 실제 요청에 대한 작업은 비동기 처리


# 3) /job/cancel
@job_bp.route('/cancel', methods=['POST'])
def cancel_job():
    request_data = flask.request.get_json()
    user_id = int(request_data['userId'])
    job_id = request_data['jobId']

    update_res = job_repository.update(job_id=job_id, user_id=user_id, stop_flag=True)

    if update_res == -1:
        return error_response(f"Job not found for user_id={user_id} with job_id={job_id}", 404)

    elif update_res == 0:
        logging.error("[Handling \"/job/cancel\" request failed. No exception but job doesn't updated]")
        return error_response("Internal server error", 500)

    return success_response(http_status=202)


#4) /job
@job_bp.route('', methods=['POST'])
def check_job_exists():
    request_data = flask.request.get_json()
    user_id = int(request_data['userId'])
    job_id = request_data['jobId']

    job: Job = job_repository.find_by_user_id_and_job_id(user_id, job_id)
    if not job:
        return error_response(f"Job not found for user_id={user_id} with job_id={job_id}", 404)
    else:
        return success_response(http_status=200)
