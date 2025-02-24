import json
from typing import Optional
import flask
import hmac
import hashlib
import base64

from config import SecurityConfig


def validate_request_body(request_body: dict, endpoint: str) -> bool:
    """
    요청 JSON 데이터에 필수 필드가 모두 존재하는지 검증합니다.
    :param
        json_data: 요청 JSON 데이터
        url: 요청 URL
    :return: 필수 필드가 모두 존재하고 값이 유효하면 True, 아니면 False
    """
    if not request_body:
        return False

    required_fields = {
        "/job/create": ["code", "codeLanguage", "challengeId", "userId"],
        "/job/execute": ["jobId"],
        "/job/delete": ["jobId"],
        "/job/cancel": ["jobId"],
    }

    missing_fields = [field for field in required_fields[endpoint] if request_body.get(field) is None]
    if missing_fields:
        return False

    if "/job/create" == endpoint:
        try:
            int(request_body["challengeId"])
            int(request_body["userId"])
        except (ValueError, TypeError):
            return False

    return True


def error_response(message: str, http_status: int) -> flask.Response:
    response_data = {
        "success": False,
        "error": message
    }
    return _convert_data_to_json_content_type_response(response_data, http_status)


def success_response(data: Optional[dict] = None, http_status: int = 200) -> flask.Response:
    response_data = {"success": True}
    if data:
        response_data.update(data)
    return _convert_data_to_json_content_type_response(response_data, http_status)


def _convert_data_to_json_content_type_response(data: dict, code: int) -> flask.Response:
    response_json = json.dumps(data, ensure_ascii=False)
    response = flask.Response(response_json, status=code, content_type="application/json")
    return response


def generate_hmac_key(_client_id: str) -> Optional[str]:
    """
    HMAC-SHA256 기반으로 API 키를 생성합니다.

    Args:
        _client_id (str): 사전에 합의된 클라이언트 식별자

    Returns:
        Optional[str]: 생성된 API 키, 실패 시 None
    """

    try:
        message = _client_id.encode('utf-8')
        secret_key = SecurityConfig.API_SECRET_KEY.encode('utf-8')
        hashed = hmac.new(secret_key, message, hashlib.sha256)
        api_key = base64.urlsafe_b64encode(hashed.digest()).decode('utf-8')
    except Exception as e:
        print(e)
        return None

    return api_key


def validate_hmac_key(received_key: str, received_client_id: str) -> bool:
    """
    요청에 포함된 HMAC 키의 유효성을 검증합니다.

    Args:
        received_key (str): 요청 헤더에서 받은 API 키
        received_client_id (str): 요청 헤더에서 받은 클라이언트 식별자

    Returns:
        bool: 키가 유효하면 True, 아니면 False
    """
    expected_key = generate_hmac_key(received_client_id)
    return hmac.compare_digest(expected_key, received_key)
