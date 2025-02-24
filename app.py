from flask import Flask

from blueprints import job_bp

# 초기화 시에 필수 입력 매개변수는 import_name 으로, Flask 애플리케이션의 패키지나 모듈(소스 파일) 이름을 지정한다.
# Flask(__name__)는 현재 파일(app.py)을 기준으로 경로를 설정하도록 함
# 이 초기화 방식은 Flask는 현재 모듈이 어디에서 실행되는지 자동으로 파악할 수 있음
app = Flask(__name__)


if __name__ == '__main__':
    app.register_blueprint(job_bp, url_prefix='/job')
    app.run()
