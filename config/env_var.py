# import os
#
#
# class EnvVar:
#     def __init__(self, key: str, cast_func=lambda x: x):
#         """
#         Description:
#             RedisConfig를 포함한 여타 클래스의 필드 접근을 제어하는 디스크립터 클래스.
#
#             EnvVar 인스턴스로 초기화된 외부 클래스(RedisConfig)의 필드 혹은 속성을 실제 사용할 때의 동작을 커스텀 하기 위해
#             디스크립터 메서드 중 하나인 __get__을 정의하고 있음.
#
#         Args:
#             key (str): .env 파일 또는 시스템 환경 변수에서 가져올 키 값.
#             cast_func (Callable, optional): 가져온 문자열 값을 원하는 타입으로 변환하기 위한 콜백 함수.
#                                             별도의 변환이 필요하지 않으면 기본값(lambda x: x)을 사용.
#         """
#         self.key = key
#         self.cast_func = cast_func
#
#     def __get__(self, instance, owner):
#         """
#         Description:
#             외부 클래스의 멤버나 속성(attribute)에 디스크립터 클래스가 적용되었을 때
#             해당 멤버나 속성에 대한 프로토콜(Protocol)을 정의하는 특수 메서드 중 하나.
#
#             쉽게 말해, A클래스의 필드 field_a의 값을 B클래스의 인스턴스로 정의하고,
#             field_a를 외부에서 접근할 때의 동작을 세밀하게 제어하기 위해 사용.
#
#             https://wikidocs.net/168363
#             https://docs.python.org/ko/3.13/howto/descriptor.html
#
#         Args:
#             instance: 디스크립터 클래스를 사용하는 클래스의 인스턴스. (클래스 자체(ex. RedisConfig)에서 접근할 경우 None)
#             owner: 디스크립터 클래스를 시용하는 클래스. (ex. EnvVar을 사용하고 있는 RedisConfig 클래스 자체)
#
#         Returns:
#             self.key에 해당하는 환경 변수를 반환.
#             타입 캐스팅 함수인 self.cast_func가 외부로 부터 초기화된 경우 해당 함수를 사용하여 환경 변수 값을 변환하여 반환.
#
#         Raises:
#             ValueError: 환경 변수가 설정되어 있지 않거나, 변환에 실패한 경우.
#         """
#         value = os.getenv(self.key)
#         if value is None:
#             raise ValueError(f"Environment variable '{self.key}' is not set.")
#         try:
#             return self.cast_func(value)
#         except Exception as e:
#             raise ValueError(f"Error converting environment variable '{self.key}': {e}") from e
#
# class RedisConfig:
#     """
#     Description:
#         Redis 설정 정보를 관리하는 클래스.
#         각 정적 멤버 필드는 환경 변수를 읽어 반환하는 디스크립터를 사용하여 초기화.
#     """
#
#     HOST: EnvVar = EnvVar("REDIS_HOST")
#     PORT: EnvVar = EnvVar("REDIS_PORT", int)
#     PASSWORD: EnvVar = EnvVar("REDIS_PASSWORD")
#     DB: EnvVar = EnvVar("REDIS_DB", int)
#     REDIS_URI: str = f'job://:{PASSWORD}@{HOST}:{PORT}/{DB}'