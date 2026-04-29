# pathlib / os - 파일 시스템

> 공식 문서: https://docs.python.org/3/library/pathlib.html

Python 3.4+에서 도입된 `pathlib.Path`는 Java의 `java.nio.file.Path`에 해당합니다.
문자열 기반 경로 조작의 오래된 방식(`os.path`)을 대체하는 객체 지향 API입니다.

```python
from pathlib import Path
import os
```

---

## 1. `Path` 기본 사용법

### Java `java.nio.Path` / `Paths.get()`과 비교

```java
// Java
import java.nio.file.Path;
import java.nio.file.Paths;

Path path = Paths.get("/home/user/project/config.json");
Path relative = Paths.get("config", "settings.json");
```

```python
# Python
from pathlib import Path

# 절대 경로
path = Path("/home/user/project/config.json")

# 상대 경로
relative = Path("config") / "settings.json"

# 문자열로도 생성 가능
path2 = Path("/home/user") / "project" / "config.json"
```

### `Path(__file__)` - 현재 파일 기준 경로

`__file__`은 현재 실행 중인 Python 파일의 경로입니다.
Java의 `getClass().getResource()`와 유사한 역할입니다.

```java
// Java: 현재 클래스 기준 리소스 접근
URL resource = getClass().getResource("/config/settings.json");
Path configPath = Paths.get(resource.toURI());
```

```python
# Python: __file__로 현재 스크립트 위치 기준 경로 계산
from pathlib import Path

# 현재 파일의 Path 객체
current_file = Path(__file__)

# 현재 파일이 있는 디렉토리
current_dir = Path(__file__).parent

# 현재 파일 기준으로 상위 디렉토리의 config 파일
config_path = Path(__file__).parent.parent / "config" / "settings.json"

# resolve()로 심볼릭 링크를 제거하고 절대 경로로 정규화
absolute_path = Path(__file__).resolve()
```

### `/` 연산자로 경로 조합

Python의 `Path`는 `/` 연산자를 오버로딩하여 경로를 직관적으로 조합합니다.

```java
// Java
Path base = Paths.get("/home/user");
Path full = base.resolve("project").resolve("main.py");
// = /home/user/project/main.py
```

```python
# Python: / 연산자 사용
base = Path("/home/user")
full = base / "project" / "main.py"
# = /home/user/project/main.py

# 문자열과도 조합 가능
config = base / "config" / "app.json"

# joinpath()로도 동일하게 동작 (Java resolve()와 대응)
same = base.joinpath("project", "main.py")

print(full)        # /home/user/project/main.py
print(type(full))  # <class 'pathlib.PosixPath'>
```

---

## 2. 경로 정보 접근

### 속성 비교표

| Python `pathlib.Path` | Java `java.nio.file.Path` | 설명 |
|---|---|---|
| `path.name` | `path.getFileName().toString()` | 파일명 (확장자 포함) |
| `path.stem` | 없음 (직접 구현) | 확장자 없는 파일명 |
| `path.suffix` | 없음 (직접 구현) | 확장자 (`.json`) |
| `path.suffixes` | 없음 | 모든 확장자 리스트 |
| `path.parent` | `path.getParent()` | 부모 디렉토리 |
| `path.parts` | 없음 | 경로 구성 요소 튜플 |
| `path.root` | `path.getRoot()` | 루트 (`/`) |
| `str(path)` | `path.toString()` | 문자열 변환 |

```python
from pathlib import Path

path = Path("/home/user/project/archive.tar.gz")

print(path.name)      # archive.tar.gz
print(path.stem)      # archive.tar  (마지막 확장자만 제거)
print(path.suffix)    # .gz          (마지막 확장자만)
print(path.suffixes)  # ['.tar', '.gz']
print(path.parent)    # /home/user/project
print(path.parts)     # ('/', 'home', 'user', 'project', 'archive.tar.gz')
print(path.root)      # /
print(path.anchor)    # /  (root와 drive 조합, Windows에서 다름)

# 경로 변환
print(path.parent.parent)          # /home/user
print(str(path))                   # /home/user/project/archive.tar.gz

# 확장자 변경
new_path = path.with_suffix(".zip")
print(new_path)  # /home/user/project/archive.tar.zip

# 파일명 변경
renamed = path.with_name("backup.tar.gz")
print(renamed)  # /home/user/project/backup.tar.gz
```

---

## 3. 파일/디렉토리 조작

### 존재 여부 확인

```java
// Java
import java.nio.file.Files;

boolean exists = Files.exists(path);
boolean isFile = Files.isRegularFile(path);
boolean isDir = Files.isDirectory(path);
```

```python
# Python
from pathlib import Path

path = Path("/home/user/project")

path.exists()    # True/False - 존재 여부
path.is_file()   # True/False - 일반 파일 여부
path.is_dir()    # True/False - 디렉토리 여부
path.is_symlink()  # True/False - 심볼릭 링크 여부

# 실전 예: 파일 유효성 검사
def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    # ...
```

### 디렉토리 생성

```java
// Java
Files.createDirectories(path);  // 중간 경로도 자동 생성
```

```python
# Python
from pathlib import Path

# mkdir: 디렉토리 생성
path = Path("/home/user/new_project/src/main")

# parents=True: 중간 경로 없어도 자동 생성 (Java createDirectories)
# exist_ok=True: 이미 존재해도 에러 없음
path.mkdir(parents=True, exist_ok=True)

# parents, exist_ok 기본값은 False
# path.mkdir()  # 부모 없으면 FileNotFoundError, 이미 있으면 FileExistsError
```

### 파일/디렉토리 삭제

```java
// Java
Files.delete(path);           // 파일 삭제, 없으면 에러
Files.deleteIfExists(path);   // 없어도 에러 없음
// 디렉토리 재귀 삭제는 별도 구현 필요
```

```python
# Python
from pathlib import Path
import shutil

path = Path("/home/user/temp.txt")

# 파일 삭제
path.unlink()               # 없으면 FileNotFoundError
path.unlink(missing_ok=True)  # Python 3.8+: 없어도 에러 없음

# 빈 디렉토리 삭제
dir_path = Path("/home/user/empty_dir")
dir_path.rmdir()  # 비어있지 않으면 OSError

# 디렉토리 재귀 삭제 (shutil 사용)
import shutil
shutil.rmtree("/home/user/project")  # 주의: 복구 불가
```

### 파일 이동/이름변경

```java
// Java
Files.move(source, target);
Files.move(source, target, StandardCopyOption.REPLACE_EXISTING);
```

```python
# Python
from pathlib import Path

source = Path("/home/user/old_name.txt")
target = Path("/home/user/new_name.txt")

# rename: 대상이 존재하면 OS에 따라 동작이 다름 (비권장)
source.rename(target)

# replace: 대상이 존재하면 덮어씀 (권장)
source.replace(target)

# 다른 디렉토리로 이동
other_dir = Path("/home/user/archive/old_name.txt")
source.replace(other_dir)
```

### 파일 읽기/쓰기 - 간편 API

`pathlib`의 가장 편리한 기능 중 하나입니다.

```java
// Java
String content = Files.readString(path);
Files.writeString(path, content);
byte[] bytes = Files.readAllBytes(path);
Files.write(path, bytes);
```

```python
# Python
from pathlib import Path

path = Path("/home/user/config.json")

# 텍스트 읽기 (encoding 기본값: 플랫폼 설정)
content = path.read_text(encoding="utf-8")

# 텍스트 쓰기
path.write_text('{"key": "value"}', encoding="utf-8")

# 바이너리 읽기
data = path.read_bytes()

# 바이너리 쓰기
path.write_bytes(b"\x89PNG\r\n...")

# 주의: write_text/write_bytes는 파일 전체를 덮어씀
# 파일 추가(append)는 open()을 사용해야 함
with open(path, "a", encoding="utf-8") as f:
    f.write("appended content\n")
```

---

## 4. 파일 탐색

### `glob()` - 패턴 매칭으로 파일 탐색

```java
// Java (NIO)
try (Stream<Path> paths = Files.walk(base)) {
    paths.filter(p -> p.toString().endsWith(".py"))
         .forEach(System.out::println);
}
```

```python
# Python
from pathlib import Path

base = Path("/home/user/project")

# 현재 디렉토리의 .py 파일만
py_files = list(base.glob("*.py"))

# 재귀 탐색 (**): 모든 하위 디렉토리의 .py 파일
all_py = list(base.glob("**/*.py"))

# rglob: glob("**/{pattern}")의 단축형
all_py_2 = list(base.rglob("*.py"))  # 위와 동일

# 특정 패턴 예시
json_files = list(base.rglob("*.json"))
test_files = list(base.rglob("test_*.py"))

# 실전 예: 프로젝트의 모든 Python 파일에서 특정 패턴 검색
project = Path("/home/user/my_project")
for py_file in sorted(project.rglob("*.py")):
    print(py_file)
```

### `iterdir()` - 디렉토리 목록

```java
// Java
try (Stream<Path> entries = Files.list(dir)) {
    entries.forEach(System.out::println);
}
```

```python
# Python
from pathlib import Path

directory = Path("/home/user/project")

# 직접 자식 항목만 (재귀 없음)
for item in directory.iterdir():
    print(item.name, "- dir" if item.is_dir() else "- file")

# 정렬된 목록
sorted_items = sorted(directory.iterdir(), key=lambda p: p.name)

# 파일만, 디렉토리만 필터링
files = [p for p in directory.iterdir() if p.is_file()]
dirs  = [p for p in directory.iterdir() if p.is_dir()]
```

---

## 5. `os` 모듈 관련

### `os.environ` - 환경변수 접근

```java
// Java
String dbUrl = System.getenv("DATABASE_URL");
// null 가능성 있으므로 Optional 또는 null 체크 필요
```

```python
# Python
import os

# 환경변수 읽기
db_url = os.environ["DATABASE_URL"]      # KeyError if not set
db_url = os.environ.get("DATABASE_URL")  # None if not set
db_url = os.environ.get("DATABASE_URL", "sqlite:///default.db")  # 기본값

# 환경변수 설정 (현재 프로세스에만 적용)
os.environ["LOG_LEVEL"] = "DEBUG"

# 모든 환경변수 확인
for key, value in os.environ.items():
    print(f"{key}={value}")

# 실전 예: python-dotenv와 함께 사용
# pip install python-dotenv
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드
api_key = os.environ.get("OPENAI_API_KEY")
```

### `os.getcwd()` / `os.chdir()`

```java
// Java
Path cwd = Paths.get("").toAbsolutePath();  // 현재 작업 디렉토리
System.setProperty("user.dir", "/new/path");  // 변경은 JVM 전체에 영향
```

```python
# Python
import os
from pathlib import Path

# 현재 작업 디렉토리
cwd = os.getcwd()               # 문자열 반환
cwd_path = Path.cwd()           # Path 객체 반환 (권장)

print(cwd)       # /home/user/project
print(cwd_path)  # /home/user/project

# 작업 디렉토리 변경 (주의: 프로세스 전체에 영향)
os.chdir("/home/user")
# 일반적으로 권장하지 않음. 절대 경로 사용을 선호.
```

### `os.path` vs `pathlib.Path` 비교

구버전 코드에서 자주 보이는 `os.path` 함수와 현대적인 `pathlib.Path` 비교입니다.

| `os.path` (구버전) | `pathlib.Path` (신버전) | 설명 |
|---|---|---|
| `os.path.join(a, b)` | `Path(a) / b` | 경로 조합 |
| `os.path.exists(p)` | `Path(p).exists()` | 존재 여부 |
| `os.path.isfile(p)` | `Path(p).is_file()` | 파일 여부 |
| `os.path.isdir(p)` | `Path(p).is_dir()` | 디렉토리 여부 |
| `os.path.basename(p)` | `Path(p).name` | 파일명 |
| `os.path.dirname(p)` | `Path(p).parent` | 부모 경로 |
| `os.path.splitext(p)` | `Path(p).stem`, `.suffix` | 확장자 분리 |
| `os.path.abspath(p)` | `Path(p).resolve()` | 절대 경로 |
| `os.makedirs(p)` | `Path(p).mkdir(parents=True)` | 디렉토리 생성 |

```python
# 구버전 스타일 (os.path)
import os

config_dir = os.path.join(os.path.dirname(__file__), "config")
config_file = os.path.join(config_dir, "settings.json")
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        content = f.read()

# 현대적 스타일 (pathlib) - 권장
from pathlib import Path

config_dir = Path(__file__).parent / "config"
config_file = config_dir / "settings.json"
if config_file.exists():
    content = config_file.read_text(encoding="utf-8")
```

---

## 6. 실전 패턴

### 프로젝트 루트 경로 찾기

Python 프로젝트에서 모듈 간에 일관된 기준 경로가 필요할 때 사용합니다.

```python
# 방법 1: 특정 파일/디렉토리 존재 여부로 루트 탐색
from pathlib import Path

def find_project_root(marker: str = "pyproject.toml") -> Path:
    """
    pyproject.toml 또는 setup.py 등이 있는 디렉토리를 프로젝트 루트로 간주.
    현재 파일에서 상위로 올라가며 탐색.
    """
    current = Path(__file__).resolve()
    for parent in [current, *current.parents]:
        if (parent / marker).exists():
            return parent
    raise FileNotFoundError(f"Project root with '{marker}' not found")

project_root = find_project_root()
data_dir = project_root / "data"
output_dir = project_root / "output"

# 방법 2: __file__ 기준으로 고정된 레벨 상위
# 예: src/mypackage/utils.py -> 루트는 두 단계 상위
ROOT = Path(__file__).resolve().parent.parent.parent

# 방법 3: 환경변수로 명시적 설정 (Spring의 application.properties와 유사)
import os
ROOT = Path(os.environ.get("PROJECT_ROOT", Path(__file__).parent.parent))
```

### `.env` 파일 경로 처리

LangChain, FastAPI 등의 프로젝트에서 자주 사용하는 패턴입니다.

```python
# .env 파일 로드 패턴
from pathlib import Path
from dotenv import load_dotenv
import os

def load_env():
    """
    여러 위치에서 .env 파일을 탐색하여 로드.
    1. 현재 작업 디렉토리
    2. 프로젝트 루트 (현재 파일 기준 상위)
    """
    # 현재 작업 디렉토리의 .env
    env_in_cwd = Path.cwd() / ".env"

    # 현재 파일 기준 프로젝트 루트의 .env
    env_in_root = Path(__file__).resolve().parent.parent / ".env"

    if env_in_cwd.exists():
        load_dotenv(env_in_cwd)
        print(f"Loaded .env from: {env_in_cwd}")
    elif env_in_root.exists():
        load_dotenv(env_in_root)
        print(f"Loaded .env from: {env_in_root}")
    else:
        print("Warning: .env file not found")

load_env()

# 실전 예: LangChain 프로젝트 구조
# my_project/
#   .env                    <- OPENAI_API_KEY=sk-...
#   pyproject.toml
#   src/
#     my_app/
#       config.py           <- 이 파일
#       main.py

# config.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in .env")

# 경로 상수 정의 (Spring의 @Value와 유사한 역할)
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = PROJECT_ROOT / "logs"

# 디렉토리 없으면 생성
for d in [DATA_DIR, OUTPUT_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)
```

---

## 핵심 요약

- **새 코드는 항상 `pathlib.Path`를 사용하세요.** `os.path`는 레거시 코드 읽기용입니다.
- **`Path(__file__).parent`** 로 현재 파일 기준 경로를 만드세요. `os.getcwd()` 의존은 실행 위치에 따라 달라져 버그를 유발합니다.
- **`/` 연산자**는 `str`과도 조합 가능하고, 플랫폼에 상관없이 올바른 구분자를 사용합니다.
- **`read_text()` / `write_text()`** 에는 항상 `encoding="utf-8"`을 명시하세요.
- **`mkdir(parents=True, exist_ok=True)`** 조합이 Java의 `Files.createDirectories()`와 동일합니다.
