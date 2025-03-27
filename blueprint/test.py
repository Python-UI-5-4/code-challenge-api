from flask import Blueprint, request

test_bp = Blueprint('test_bp', __name__)

# 단위 테스트
# Celery JOB 실행 및 결과 수신
@test_bp.route('/test-case-result', methods=['POST'])
def test_case_result() :
    request_data = request.get_json()
    print(request_data)
    return "", 200

@test_bp.route('/judgment-passed', methods=['POST'])
def judgment_passed() :
    request_data = request.get_json()
    print(request_data)
    return "", 200

@test_bp.route('/judgment-unpassed', methods=['POST'])
def judgment_unpassed() :
    request_data = request.get_json()
    print(request_data)
    return "", 200

@test_bp.route('/error', methods=['POST'])
def error() :
    request_data = request.get_json()
    print(request_data)
    return "", 200