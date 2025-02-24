from common import get_env_var


class SecurityConfig:
    """
    Description:
        Security 설정 정보를 관리하는 클래스.
    """
    API_SECRET_KEY = get_env_var("API_SECRET_KEY")


