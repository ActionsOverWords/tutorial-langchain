# Python 표준 라이브러리 (Java 개발자용)

> Java JDK API 문서처럼 Python도 표준 라이브러리 공식 문서가 있습니다.
> **https://docs.python.org/3/library/**

---

## Java JDK ↔ Python 표준 라이브러리 대응표

| Java 패키지 | Python 모듈 | 문서 |
|---|---|---|
| `java.util.function.*` | `functools` | [functools.md](./functools.md) |
| `java.util.*` (컬렉션) | `collections` | [collections.md](./collections.md) |
| `java.util.stream.*` | `itertools` | [itertools.md](./itertools.md) |
| `java.nio.file.*`, `java.io.*` | `pathlib`, `os` | [pathlib.md](./pathlib.md) |
| `java.time.*` | `datetime` | [datetime.md](./datetime.md) |
| `java.util.logging.*` (SLF4J/Logback) | `logging` | [logging.md](./logging.md) |
| `java.util.concurrent.*` | `concurrent.futures`, `threading`, `asyncio` | [concurrent.md](./concurrent.md) |
| `java.util.regex.*` | `re` | [re.md](./re.md) |
| `java.lang.Enum` | `enum` | [enum.md](./enum.md) |
| 타입 시스템 (Generics) | `typing` | [typing.md](./typing.md) |
| Lombok `@Data` / `record` | `dataclasses` | [dataclasses.md](./dataclasses.md) |
| `abstract class` / `interface` | `abc` | [abc.md](./abc.md) |
| `try-with-resources` | `contextlib` | [contextlib.md](./contextlib.md) |

---

## 문서 목록

### 함수형 / 자료구조

| 모듈 | 핵심 기능 | 대표 사용처 |
|---|---|---|
| [functools](./functools.md) | `partial`, `lru_cache`, `wraps`, `reduce` | 캐싱, 데코레이터, FastAPI Depends |
| [collections](./collections.md) | `defaultdict`, `Counter`, `deque`, `ChainMap` | 그룹핑, 빈도 계산, 슬라이딩 윈도우 |
| [itertools](./itertools.md) | `chain`, `groupby`, `product`, `combinations` | 배치 처리, 조합 생성 |

### 파일 / 시간

| 모듈 | 핵심 기능 | 대표 사용처 |
|---|---|---|
| [pathlib / os](./pathlib.md) | `Path`, `glob`, `environ` | 파일 경로, 환경변수 |
| [datetime](./datetime.md) | `datetime`, `timedelta`, `timezone` | 날짜 계산, UTC 처리, API 타임스탬프 |

### 운영 / 동시성

| 모듈 | 핵심 기능 | 대표 사용처 |
|---|---|---|
| [logging](./logging.md) | `getLogger`, `Handler`, `Formatter` | 구조화 로그, uvicorn 통합 |
| [concurrent](./concurrent.md) | `ThreadPoolExecutor`, `asyncio.gather` | I/O 병렬, CPU 병렬, FastAPI async |
| [re](./re.md) | `search`, `findall`, `sub`, `compile` | 텍스트 파싱, 데이터 추출 |

### 타입 / OOP

| 모듈 | 핵심 기능 | 대표 사용처 |
|---|---|---|
| [typing](./typing.md) | `Optional`, `Protocol`, `TypeVar`, `TypedDict` | 타입 안전성, 제네릭, duck typing |
| [dataclasses](./dataclasses.md) | `@dataclass`, `field()`, `frozen=True` | DTO, Value Object |
| [abc](./abc.md) | `ABC`, `@abstractmethod`, `Protocol` | Repository 패턴, Strategy 패턴 |
| [contextlib](./contextlib.md) | `@contextmanager`, `@asynccontextmanager` | DB 트랜잭션, FastAPI lifespan |
| [enum](./enum.md) | `Enum`, `StrEnum`, `auto()`, `Flag` | 상태값, API 스키마 |

---

## 빠른 조회 방법

### 터미널에서 바로 확인

```bash
# 모듈 전체 문서
python3 -m pydoc functools

# 특정 함수/클래스
python3 -m pydoc functools.partial
python3 -m pydoc collections.defaultdict
```

### Python 인터프리터에서

```python
import functools
help(functools.lru_cache)   # 상세 문서
dir(functools)              # 모듈 내 전체 목록
```

### IDE
- 심볼에 커서 올리면 docstring 팝업
- `F12` → 소스 코드로 이동 (JDK 소스 보기와 동일)
