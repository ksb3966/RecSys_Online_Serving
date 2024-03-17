# RecSys Serving Example by FastAPI
Book Recommendation 프로젝트를 FastAPI를 활용, Single Web Server로 구축했습니다.  
책 추천 서비스를 런칭할 때 사용할 수 있는 백엔드 차원에서의 BaseLine으로 활용할 수 있니다.  

서버를 띄운 뒤, Request를 보내면 학습 및 추론을 진행 및 전체 유저 및 아이템에 대한 결과값을 csv로 리턴합니다.(data/scr/submit 디렉토리 저장)   
모델을 선택해 post 요청을 보내게 되면, 모델의 savefile(.pt)이 있다면 곧바로 추론을, 없다면 학습을 진행 .pt 파일을 생성한 뒤에 추론을 수행하게 됩니다. 
현재 특정 유저에 대한 결과값만을 리턴하거나 도커로 구현하는 부분은 수정 단계에 있습니다.  

## Pre-requisites
- Python >= 3.9
- Poetry >= 1.1.4

## Project Structure
```bash
├── /data                   # Data 관련 파일 및 코드
│   └── /src                # input 파일 저장 경로
│       ├── /images         # image input 파일 저장 경로
│       ├── /model_versions # 모델 weight 저장
│       ├── /submit         # 제출 파일(submission.csv) 저장 경로
│       └── /text_vector    # 벡터 파일
├── /log                    # 로그 파일 저장 경로
├── /models                 # 모델 구현 코드
├── .dockerignore           # 도커 이미지 빌드 시 제외할 파일 목록
├── .gitignore              # git에서 제외할 파일 목록
├── Dockerfile              # 도커 이미지 빌드 설정 파일
├── README.md           # 프로젝트 설명 파일
├── __init__.py
├── api.py                  # API 엔드포인트 정의 파일
├── config.py               # Config 정의 파일
├── database.py             # 데이터베이스 연결 파일
├── db.sqlite3              # SQLite3 데이터베이스 파일
├── dependencies.py         # 앱 의존성 관련 로직 파일
├── main.py                 # 앱 실행 파일
├── model.py                # 모델 관련 로직 파일
├── poetry.lock             # Poetry 라이브러리 버전 관리 파일
└── pyproject.toml          # Poetry 프로젝트 설정 파일
```

## Installation

```bash
poetry install
```

## Run
환경 설정
```bash
# .env 
# Default Baseline for DeepCoNN
MODEL_PATH=./data/src/model_versions/deepconn_model.pt
```

실행
```bash
poetry run python main.py
```

## Usage
### Predict

```bash
curl -X POST "0.0.0.0:8000/scoring/context?model_type=wdn"
```
