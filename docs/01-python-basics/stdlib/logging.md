# logging - 로깅

> 공식 문서: https://docs.python.org/3/library/logging.html

Java/Spring Boot 개발자라면 SLF4J + Logback 조합에 익숙할 것입니다. Python의 `logging` 모듈은 Java의 그것과 설계 철학이 매우 유사합니다. Logger 계층 구조, Handler(Appender), Formatter, 로그 레벨 개념이 거의 1:1로 대응됩니다.

---

## 1. 로그 레벨

Python `logging`의 레벨과 Java SLF4J/Logback 레벨은 아래와 같이 대응됩니다.

| Python          | 숫자값 | Java SLF4J/Logback |
|-----------------|-------|--------------------|
| `logging.DEBUG`    | 10    | `DEBUG`            |
| `logging.INFO`     | 20    | `INFO`             |
| `logging.WARNING`  | 30    | `WARN`             |
| `logging.ERROR`    | 40    | `ERROR`            |
| `logging.CRITICAL` | 50    | `ERROR` (치명적 오류, Java에는 `FATAL`이 있지만 SLF4J에서는 `ERROR`로 통합) |

> Python에는 Java의 `TRACE` 레벨이 없습니다. `DEBUG`가 가장 낮은 레벨입니다.

```python
import logging

# 각 레벨로 로그 출력
logging.debug("디버그 메시지")
logging.info("정보 메시지")
logging.warning("경고 메시지")     # 기본 출력 레벨 (basicConfig 없이도 출력됨)
logging.error("오류 메시지")
logging.critical("치명적 오류 메시지")
```

---

## 2. 기본 설정 (`basicConfig`)

### Python

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.info("애플리케이션 시작")
```

### Java `logback.xml` 비교

```xml
<!-- logback.xml -->
<configuration>
  <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
    <encoder>
      <pattern>%d{yyyy-MM-dd HH:mm:ss} [%level] %logger - %msg%n</pattern>
    </encoder>
  </appender>
  <root level="DEBUG">
    <appender-ref ref="STDOUT" />
  </root>
</configuration>
```

### format 패턴 대응표

| Python `%` 패턴      | Logback 패턴      | 의미                    |
|----------------------|-------------------|-------------------------|
| `%(asctime)s`        | `%d{...}`         | 타임스탬프              |
| `%(levelname)s`      | `%level`          | 로그 레벨명             |
| `%(name)s`           | `%logger`         | Logger 이름             |
| `%(message)s`        | `%msg`            | 로그 메시지             |
| `%(filename)s`       | `%file`           | 소스 파일명             |
| `%(lineno)d`         | `%line`           | 소스 라인 번호          |
| `%(funcName)s`       | 없음 (MDC 활용)   | 함수/메서드명           |
| `%(thread)d`         | `%thread`         | 스레드 ID               |
| `%(threadName)s`     | `%thread`         | 스레드 이름             |

> `basicConfig()`는 **root logger**에 Handler를 추가합니다. 프로그램 시작 시 한 번만 호출해야 합니다. 이미 Handler가 설정된 상태에서 다시 호출해도 적용되지 않으므로 주의하세요.

---

## 3. Logger 계층 구조

### Python

```python
import logging

# 모듈명을 Logger 이름으로 사용 (권장 패턴)
logger = logging.getLogger(__name__)

# 명시적으로 이름 지정
logger_a = logging.getLogger("myapp")
logger_b = logging.getLogger("myapp.service")   # myapp의 자식
logger_c = logging.getLogger("myapp.service.user")  # myapp.service의 자식
```

### Java 비교

```java
// Java SLF4J
private static final Logger logger = LoggerFactory.getLogger(UserService.class);
// 또는
private static final Logger logger = LoggerFactory.getLogger("com.example.service.UserService");
```

### 계층 구조와 propagate

Python Logger는 `.`으로 구분된 계층 구조를 갖습니다. Java의 Logger 계층 구조와 동일합니다.

```python
import logging

# root logger 설정
logging.basicConfig(level=logging.WARNING)

# 특정 패키지 Logger만 DEBUG로 설정
logging.getLogger("myapp").setLevel(logging.DEBUG)

logger = logging.getLogger("myapp.service.user")
logger.debug("이 메시지는 출력됨")  # myapp 레벨이 DEBUG이므로

# propagate: 부모 Logger로 로그 전파 (기본값 True)
logger.propagate = False  # 상위 Logger로 전파 차단
```

**계층 탐색 순서:**

```
myapp.service.user
    → myapp.service (없으면 위로)
        → myapp (레벨 = DEBUG, Handler 있으면 처리)
            → root logger
```

> Java Logback의 `additivity` 속성이 Python의 `propagate`에 해당합니다.

---

## 4. Handler / Formatter

Java Logback의 `Appender` = Python의 `Handler`입니다.

### StreamHandler (콘솔 출력)

```python
import logging
import sys

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

# Java ConsoleAppender에 해당
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("콘솔에 출력됩니다")
```

### FileHandler (파일 출력)

```python
import logging

logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)

# Java FileAppender에 해당
file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logger.addHandler(file_handler)
```

### RotatingFileHandler (로그 로테이션)

```python
from logging.handlers import RotatingFileHandler
import logging

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

# Java Logback RollingFileAppender (size-based) 에 해당
rotating_handler = RotatingFileHandler(
    filename="app.log",
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5,               # app.log.1 ~ app.log.5 유지
    encoding="utf-8",
)
rotating_handler.setLevel(logging.DEBUG)
logger.addHandler(rotating_handler)
```

**Java Logback 비교:**

```xml
<!-- Logback RollingFileAppender (size-based) -->
<appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
  <file>app.log</file>
  <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
    <fileNamePattern>app.%d{yyyy-MM-dd}.%i.log</fileNamePattern>
    <maxFileSize>10MB</maxFileSize>
    <maxHistory>5</maxHistory>
  </rollingPolicy>
</appender>
```

날짜 기반 로테이션이 필요하면 `TimedRotatingFileHandler`를 사용합니다:

```python
from logging.handlers import TimedRotatingFileHandler

# 매일 자정에 로테이션, 30일치 보관
timed_handler = TimedRotatingFileHandler(
    filename="app.log",
    when="midnight",      # 'S', 'M', 'H', 'D', 'midnight', 'W0'~'W6'
    interval=1,
    backupCount=30,
    encoding="utf-8",
)
```

### 여러 Handler 동시 사용

```python
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

    # 콘솔: INFO 이상
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    # 파일: DEBUG 이상
    file_ = RotatingFileHandler("app.log", maxBytes=5_000_000, backupCount=3)
    file_.setLevel(logging.DEBUG)
    file_.setFormatter(fmt)

    logger.addHandler(console)
    logger.addHandler(file_)
    return logger

logger = setup_logger("myapp")
logger.debug("파일에만 기록")
logger.info("콘솔과 파일 모두 기록")
```

---

## 5. FastAPI / uvicorn 로깅 설정

### uvicorn 로그와 통합

FastAPI 애플리케이션에서는 uvicorn이 자체 Logger를 가지고 있습니다. 이를 앱 Logger와 통합하려면 `logging.config.dictConfig()`를 사용합니다.

```python
# main.py
import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        },
    },
    "loggers": {
        # 앱 Logger
        "myapp": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
        # uvicorn 기본 Logger 제어
        "uvicorn": {"level": "INFO", "handlers": ["console"], "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"level": "WARNING"},  # 액세스 로그 억제
    },
    "root": {"level": "WARNING", "handlers": ["console"]},
}

logging.config.dictConfig(LOGGING_CONFIG)

from fastapi import FastAPI

app = FastAPI()

logger = logging.getLogger("myapp")

@app.get("/")
def root():
    logger.info("루트 엔드포인트 호출")
    return {"status": "ok"}
```

### JSON 로그 포매터

프로덕션 환경에서는 Elasticsearch, Datadog 등과 연동하기 위해 JSON 형식 로그를 사용합니다. 표준 라이브러리만으로도 구현할 수 있지만, `loguru` 또는 `python-json-logger` 라이브러리 사용을 권장합니다.

**표준 라이브러리로 JSON Formatter 구현:**

```python
import json
import logging
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.getLogger("myapp").addHandler(handler)
```

**loguru 라이브러리 (외부 패키지, 권장):**

```python
# pip install loguru
from loguru import logger

# JSON 직렬화 내장
logger.add("app.log", serialize=True, rotation="10 MB", retention=5)

logger.info("loguru는 설정이 훨씬 간단합니다")
```

> loguru는 `structlog`과 함께 Python 생태계에서 가장 널리 쓰이는 서드파티 로깅 라이브러리입니다. Spring Boot의 Logback처럼 표준 `logging` 모듈을 대체합니다.

---

## 6. 실전 패턴

### 모듈별 Logger 사용 (`__name__`)

가장 중요한 권장 패턴입니다. 모든 모듈 최상단에 아래와 같이 선언합니다.

```python
# src/myapp/service/user_service.py
import logging

logger = logging.getLogger(__name__)
# __name__ = "myapp.service.user_service"
# → Logger 계층: root → myapp → myapp.service → myapp.service.user_service

class UserService:
    def get_user(self, user_id: int):
        logger.debug("사용자 조회 시작: user_id=%d", user_id)
        try:
            # ...
            logger.info("사용자 조회 성공: user_id=%d", user_id)
        except Exception as e:
            logger.error("사용자 조회 실패: user_id=%d", user_id, exc_info=True)
            raise
```

**Java 비교:**

```java
// Java - 클래스명을 Logger 이름으로 사용
@Slf4j  // Lombok
public class UserService {
    public User getUser(long userId) {
        log.debug("사용자 조회 시작: userId={}", userId);
        // ...
    }
}
```

### `print()` 대신 logging을 써야 하는 이유

| 비교 항목         | `print()`         | `logging`                       |
|------------------|-------------------|---------------------------------|
| 레벨 제어         | 불가              | 레벨별 필터링 가능              |
| 출력 대상 변경    | 코드 수정 필요    | Handler 교체로 가능             |
| 타임스탬프        | 직접 추가 필요    | Formatter로 자동 포함           |
| 성능              | 항상 실행         | 레벨 미달 시 메시지 생성 생략   |
| 프로덕션 억제     | 불가              | 레벨 설정으로 즉시 억제 가능    |
| 구조화 로그       | 불가              | JSON Formatter 등 활용 가능     |
| 파일 출력 / 로테이션 | 직접 구현 필요 | Handler로 즉시 지원             |

```python
# 나쁜 예
print(f"[DEBUG] user_id={user_id} 조회 중")  # 프로덕션에서 제거하려면 코드 수정 필요

# 좋은 예
logger.debug("user_id=%d 조회 중", user_id)  # 레벨 설정만으로 프로덕션에서 억제 가능
```

### 예외 로깅

```python
try:
    result = 1 / 0
except ZeroDivisionError:
    # exc_info=True: Java의 log.error("메시지", e)에 해당 (stack trace 포함)
    logger.error("계산 중 오류 발생", exc_info=True)

    # 또는 logger.exception() 사용 (exc_info=True와 동일, ERROR 레벨 고정)
    logger.exception("계산 중 오류 발생")
```

**Java 비교:**

```java
try {
    int result = 1 / 0;
} catch (ArithmeticException e) {
    log.error("계산 중 오류 발생", e);  // stack trace 자동 포함
}
```

### 성능을 고려한 로깅

```python
# 나쁜 예: 레벨이 DEBUG 미만이어도 문자열 포매팅이 먼저 실행됨
logger.debug(f"복잡한 객체: {expensive_to_serialize()}")

# 좋은 예: % 스타일 - 레벨 미달 시 문자열 포매팅 자체를 건너뜀
logger.debug("복잡한 객체: %s", expensive_to_serialize())

# 또는 명시적으로 레벨 체크
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("복잡한 객체: %s", expensive_to_serialize())
```
