from flask import Blueprint, request

test_bp = Blueprint('test_bp', __name__)

# 단위 테스트
# Celery JOB 실행 및 결과 수신
@test_bp.route('/notify-verdict', methods=['POST'])
def notify_verdict() :
    request_data = request.get_json()
    print(request_data)
    return "", 200

@test_bp.route('/notify-result', methods=['POST'])
def notify_result() :
    request_data = request.get_json()
    print(request_data)
    return "", 200
