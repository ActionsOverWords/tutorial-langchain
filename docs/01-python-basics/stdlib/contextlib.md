# contextlib - 컨텍스트 매니저 도구

> 공식 문서: https://docs.python.org/3/library/contextlib.html

`contextlib` 모듈은 `with` 문에서 사용하는 컨텍스트 매니저를 쉽게 만들고 조합하는 도구를 제공합니다.
Java의 `try-with-resources`와 `AutoCloseable`에 대응하지만,
리소스 정리뿐만 아니라 트랜잭션, 락, 설정 임시 변경 등 다양한 패턴을 표현할 수 있습니다.

---

## 1. `@contextmanager`

클래스를 만들지 않고 제너레이터 함수로 컨텍스트 매니저를 작성합니다.
`yield` 이전이 `__enter__`, `yield` 이후가 `__exit__`에 해당합니다.

### 기본 구조

```python
from contextlib import contextmanager
from typing import Generator

@contextmanager
def managed_resource() -> Generator[str, None, None]:
    # __enter__ 역할 - 리소스 획득
    print("리소스 획득")
    resource = "some resource"
    try:
        yield resource          # with 블록에 값 전달
    finally:
        # __exit__ 역할 - 예외 여부와 무관하게 항상 실행
        print("리소스 해제")

with managed_resource() as res:
    print(f"사용 중: {res}")
    # raise Exception("오류 발생")  # finally는 예외 시에도 실행됨

# 출력:
# 리소스 획득
# 사용 중: some resource
# 리소스 해제
```

```java
// Java try-with-resources + AutoCloseable
public class ManagedResource implements AutoCloseable {
    public ManagedResource() {
        System.out.println("리소스 획득");
    }

    @Override
    public void close() {
        System.out.println("리소스 해제");
    }
}

try (var resource = new ManagedResource()) {
    System.out.println("사용 중: " + resource);
}
```

### DB 트랜잭션 패턴

```python
from contextlib import contextmanager
from typing import Generator
import sqlite3

@contextmanager
def transaction(db_path: str) -> Generator[sqlite3.Connection, None, None]:
    """자동 커밋/롤백 트랜잭션 컨텍스트 매니저"""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()    # 정상 종료 시 커밋
    except Exception:
        conn.rollback()  # 예외 발생 시 롤백
        raise
    finally:
        conn.close()     # 항상 연결 종료

with transaction("app.db") as conn:
    conn.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
    conn.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))
    # 예외 없이 종료되면 두 쿼리 모두 커밋

# with 블록에서 예외 발생 시 자동 롤백
try:
    with transaction("app.db") as conn:
        conn.execute("INSERT INTO users (name) VALUES (?)", ("Charlie",))
        raise ValueError("의도적 오류")  # 롤백 발생
except ValueError:
    print("트랜잭션이 롤백되었습니다")
```

```java
// Java Spring @Transactional
@Service
public class UserService {
    @Transactional
    public void createUsers() {
        userRepository.save(new User("Alice"));
        userRepository.save(new User("Bob"));
        // 예외 발생 시 자동 롤백
    }
}

// Java 수동 트랜잭션
try (Connection conn = dataSource.getConnection()) {
    conn.setAutoCommit(false);
    try {
        // SQL 실행
        conn.commit();
    } catch (SQLException e) {
        conn.rollback();
        throw e;
    }
}
```

### 파일 처리 패턴

```python
from contextlib import contextmanager
from typing import Generator, IO
import tempfile
import os

@contextmanager
def temp_file(suffix: str = ".tmp") -> Generator[str, None, None]:
    """임시 파일 생성 후 자동 삭제"""
    path = tempfile.mktemp(suffix=suffix)
    try:
        yield path
    finally:
        if os.path.exists(path):
            os.remove(path)

with temp_file(".json") as path:
    with open(path, "w") as f:
        f.write('{"key": "value"}')
    # 파일 처리...
# with 블록 종료 시 임시 파일 자동 삭제

# 타이머 컨텍스트 매니저
import time

@contextmanager
def timer(label: str = "") -> Generator[None, None, None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.3f}초")

with timer("데이터 처리"):
    time.sleep(0.1)
    # 처리 로직
# "데이터 처리: 0.100초"
```

### 예외 처리가 포함된 컨텍스트 매니저

```python
from contextlib import contextmanager
from typing import Generator

@contextmanager
def retry_on_failure(
    max_retries: int = 3,
    exceptions: tuple[type[Exception], ...] = (Exception,)
) -> Generator[None, None, None]:
    for attempt in range(max_retries):
        try:
            yield
            return  # 성공 시 종료
        except exceptions as e:
            if attempt == max_retries - 1:
                raise  # 마지막 시도에서도 실패하면 예외 전파
            print(f"시도 {attempt + 1} 실패, 재시도 중: {e}")

# 단, @contextmanager는 재진입(re-entry)이 불가하므로
# retry 패턴에는 직접 클래스 기반 컨텍스트 매니저가 더 적합
```

---

## 2. `@asynccontextmanager`

비동기 컨텍스트 매니저를 `async def` + `yield`로 작성합니다.
`async with` 문에서 사용합니다.

### 기본 사용법

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio

@asynccontextmanager
async def async_db_session() -> AsyncGenerator[dict, None]:
    print("비동기 DB 세션 시작")
    session = {"connected": True}  # 실제로는 aiopg, asyncpg 등
    try:
        yield session
        print("커밋")
    except Exception:
        print("롤백")
        raise
    finally:
        print("세션 종료")

async def main() -> None:
    async with async_db_session() as session:
        print(f"세션 사용 중: {session}")

asyncio.run(main())
```

### FastAPI `lifespan` 패턴 (실전 예시)

FastAPI 0.93.0+에서 `lifespan`을 사용해 애플리케이션 시작/종료 시 리소스를 관리합니다.

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
from fastapi import FastAPI
import asyncpg  # pip install asyncpg

# 애플리케이션 전역 상태 (간단한 예시)
db_pool: asyncpg.Pool | None = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI 앱의 수명 주기 관리"""
    global db_pool

    # 시작 시 (startup)
    print("애플리케이션 시작 - DB 커넥션 풀 생성")
    db_pool = await asyncpg.create_pool(
        dsn="postgresql://user:pass@localhost/dbname",
        min_size=5,
        max_size=20,
    )

    yield  # 앱이 실행되는 동안 대기

    # 종료 시 (shutdown)
    print("애플리케이션 종료 - DB 커넥션 풀 해제")
    if db_pool:
        await db_pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return dict(row) if row else {"error": "Not found"}
```

```java
// Java Spring Boot - @Bean + @PreDestroy 패턴
@Configuration
public class DatabaseConfig {
    private HikariDataSource dataSource;

    @Bean
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://localhost/dbname");
        config.setMinimumIdle(5);
        config.setMaximumPoolSize(20);
        dataSource = new HikariDataSource(config);
        return dataSource;
    }

    @PreDestroy
    public void close() {
        if (dataSource != null) dataSource.close();
    }
}
```

### 여러 리소스를 함께 관리하는 lifespan

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # 여러 리소스 초기화
    print("1. Redis 연결 초기화")
    redis_client = await create_redis_pool()

    print("2. DB 커넥션 풀 초기화")
    db_pool = await create_db_pool()

    print("3. 백그라운드 워커 시작")
    worker_task = asyncio.create_task(background_worker())

    # app.state에 저장하여 엔드포인트에서 접근
    app.state.redis = redis_client
    app.state.db = db_pool

    try:
        yield
    finally:
        # 역순으로 정리
        print("3. 백그라운드 워커 종료")
        worker_task.cancel()

        print("2. DB 커넥션 풀 해제")
        await db_pool.close()

        print("1. Redis 연결 해제")
        await redis_client.close()
```

---

## 3. `suppress(*exceptions)`

특정 예외를 무시하고 계속 진행합니다.
Java의 빈 `catch` 블록보다 의도를 명확하게 표현합니다.

```python
from contextlib import suppress
import os

# Java 스타일 - 의도가 불분명한 빈 catch
# try:
#     os.remove("temp.txt")
# except FileNotFoundError:
#     pass  # 왜 무시하는지 불분명

# Python 권장 스타일 - 의도가 명확
with suppress(FileNotFoundError):
    os.remove("temp.txt")  # 파일이 없어도 괜찮음

# 여러 예외 동시 억제
with suppress(FileNotFoundError, PermissionError):
    os.remove("/etc/sensitive_file")  # 없거나 권한 없어도 무시

# 실전 예시: 디렉토리 생성 (이미 존재해도 무시)
from contextlib import suppress

with suppress(FileExistsError):
    os.makedirs("output/logs")

# 더 나은 대안이 있을 때는 suppress 대신 사용
os.makedirs("output/logs", exist_ok=True)  # 이 경우엔 exist_ok=True가 더 명확

# 딕셔너리 키 삭제 (없어도 무시)
config = {"debug": True, "host": "localhost"}
with suppress(KeyError):
    del config["missing_key"]

# 더 나은 대안
config.pop("missing_key", None)
```

```java
// Java - 빈 catch 블록
try {
    Files.delete(Path.of("temp.txt"));
} catch (NoSuchFileException e) {
    // 무시 - 파일이 없어도 괜찮음
}

// Java - Files.deleteIfExists()가 더 명확
Files.deleteIfExists(Path.of("temp.txt"));
```

> **주의**: `suppress`는 예외를 삼켜버리므로 남용하면 버그를 숨길 수 있습니다.
> 정말로 무시해도 안전한 예외에만 사용하세요.
> 로깅이 필요하다면 `suppress` 대신 `try/except` 블록을 사용하세요.

---

## 4. `nullcontext()`

아무 동작도 하지 않는 더미 컨텍스트 매니저입니다.
조건부로 컨텍스트 매니저를 적용할 때 유용합니다.

```python
from contextlib import nullcontext
from typing import ContextManager

# 조건부 컨텍스트 매니저 패턴
def process_data(data: list, use_lock: bool = False) -> None:
    import threading

    lock = threading.Lock() if use_lock else nullcontext()

    with lock:  # use_lock=False면 nullcontext가 아무것도 안 함
        # 데이터 처리
        print(f"처리 중: {data}")

process_data([1, 2, 3], use_lock=True)   # Lock 사용
process_data([4, 5, 6], use_lock=False)  # Lock 없이

# 테스트에서 모킹을 선택적으로 적용
from unittest.mock import patch

def run_with_optional_mock(use_mock: bool) -> None:
    ctx = patch("some.module.external_call") if use_mock else nullcontext()
    with ctx:
        # 실제 코드 실행
        ...

# 반환값을 yield하는 패턴
with nullcontext("default_value") as value:
    print(value)  # "default_value"

# 실전: 트랜잭션이 필요할 수도 있고 없을 수도 있는 경우
def save_records(
    records: list[dict],
    conn=None  # 기존 연결이 있으면 사용, 없으면 새로 생성
) -> None:
    ctx = nullcontext(conn) if conn else get_db_connection()
    with ctx as db:
        for record in records:
            db.execute("INSERT INTO ...", record)
```

```java
// Java - 유사 패턴 (선택적 리소스 관리)
public void processData(List<Object> data, boolean useLock) throws Exception {
    Lock lock = useLock ? new ReentrantLock() : null;
    if (lock != null) lock.lock();
    try {
        // 데이터 처리
    } finally {
        if (lock != null) lock.unlock();
    }
}
```

---

## 5. `ExitStack`

여러 컨텍스트 매니저를 동적으로 관리합니다.
컨텍스트 매니저의 개수가 런타임에 결정될 때 유용합니다.

### 기본 사용법

```python
from contextlib import ExitStack

# 여러 파일을 동시에 열기 - 개수가 동적
file_paths = ["a.txt", "b.txt", "c.txt"]

with ExitStack() as stack:
    files = [
        stack.enter_context(open(path, "w"))
        for path in file_paths
    ]
    for i, f in enumerate(files):
        f.write(f"파일 {i + 1} 내용")
# ExitStack이 모든 파일을 역순으로 자동 닫음
```

```java
// Java try-with-resources - 개수가 컴파일 타임에 고정
// 동적 개수의 리소스는 try-with-resources로 처리 어려움
List<OutputStream> streams = new ArrayList<>();
try {
    for (String path : filePaths) {
        streams.add(new FileOutputStream(path));
    }
    // 처리
} finally {
    for (OutputStream s : streams) {
        try { s.close(); } catch (IOException e) { /* 무시 */ }
    }
}
```

### 조건부 컨텍스트 매니저

```python
from contextlib import ExitStack

def process(
    use_transaction: bool,
    use_lock: bool,
    use_timer: bool
) -> None:
    with ExitStack() as stack:
        if use_transaction:
            conn = stack.enter_context(get_db_connection())

        if use_lock:
            import threading
            stack.enter_context(threading.Lock())

        if use_timer:
            stack.enter_context(timer("처리 시간"))

        # 항상 실행되는 로직
        ...

# 런타임에 필요한 컨텍스트 매니저만 활성화
process(use_transaction=True, use_lock=True, use_timer=False)
```

### 콜백 등록 - `callback()`

```python
from contextlib import ExitStack
import tempfile
import os

with ExitStack() as stack:
    # 컨텍스트 매니저가 없는 정리 작업도 등록 가능
    temp_dir = tempfile.mkdtemp()
    stack.callback(lambda: print(f"임시 디렉토리 삭제: {temp_dir}"))
    stack.callback(lambda: os.rmdir(temp_dir) if os.path.exists(temp_dir) else None)

    # 여러 리소스 동적 관리
    files = []
    for i in range(3):
        path = os.path.join(temp_dir, f"file{i}.txt")
        f = open(path, "w")
        files.append(f)
        stack.callback(f.close)  # 각 파일에 close 콜백 등록

    for f in files:
        f.write("내용")
# 역순으로 모든 콜백 실행: file2.close, file1.close, file0.close, 디렉토리 정리
```

### `ExitStack`을 통한 지연 초기화

```python
from contextlib import ExitStack

class Application:
    def __init__(self) -> None:
        self._exit_stack = ExitStack()

    def start(self) -> None:
        """애플리케이션 시작 - 여러 리소스 초기화"""
        self._exit_stack.__enter__()

        db = self._exit_stack.enter_context(get_db_connection())
        cache = self._exit_stack.enter_context(get_cache_client())

        self.db = db
        self.cache = cache
        print("애플리케이션 시작 완료")

    def stop(self) -> None:
        """애플리케이션 종료 - 모든 리소스 정리"""
        self._exit_stack.__exit__(None, None, None)
        print("애플리케이션 종료 완료")

app = Application()
app.start()
# ... 사용 ...
app.stop()
```

---

## 6. `closing()`

`.close()` 메서드가 있는 객체를 `with` 문으로 사용할 수 있게 합니다.
`AutoCloseable`을 구현하지 않은 Java 객체를 `try-with-resources`로 감싸는 것과 유사합니다.

```python
from contextlib import closing
import urllib.request

# urllib.request.urlopen은 컨텍스트 매니저를 지원하지만
# .close()만 있는 레거시 객체에는 closing()이 유용
with closing(urllib.request.urlopen("https://httpbin.org/get")) as response:
    data = response.read()
    print(data[:100])
# response.close() 자동 호출

# 소켓 관리
import socket

with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
    sock.connect(("localhost", 8080))
    sock.sendall(b"GET / HTTP/1.0\r\n\r\n")
    response = sock.recv(4096)
# sock.close() 자동 호출

# 제너레이터 닫기
def infinite_counter():
    n = 0
    while True:
        yield n
        n += 1

with closing(infinite_counter()) as counter:
    for _ in range(5):
        print(next(counter))
# counter.close() 자동 호출 - GeneratorExit 전송
```

```java
// Java - AutoCloseable 미구현 객체의 try-with-resources
// AutoCloseable을 구현한 래퍼 사용
public class ClosingWrapper<T> implements AutoCloseable {
    private final T resource;
    private final Consumer<T> closeAction;

    public ClosingWrapper(T resource, Consumer<T> closeAction) {
        this.resource = resource;
        this.closeAction = closeAction;
    }

    public T get() { return resource; }

    @Override
    public void close() { closeAction.accept(resource); }
}

try (var wrapper = new ClosingWrapper<>(socket, Socket::close)) {
    // socket 사용
}
```

---

## 컨텍스트 매니저 클래스 직접 구현

`@contextmanager` 없이 클래스로 직접 구현하는 방법입니다.
`__enter__`와 `__exit__` 메서드를 직접 정의합니다.

```python
from types import TracebackType

class DatabaseTransaction:
    def __init__(self, connection_string: str) -> None:
        self._conn_str = connection_string
        self._conn = None

    def __enter__(self) -> "DatabaseTransaction":
        import sqlite3
        self._conn = sqlite3.connect(self._conn_str)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()
        self._conn.close()
        return False  # True 반환 시 예외 억제, False는 예외 전파

    def execute(self, sql: str, params: tuple = ()) -> None:
        self._conn.execute(sql, params)

with DatabaseTransaction("app.db") as tx:
    tx.execute("INSERT INTO log (msg) VALUES (?)", ("시작",))
    tx.execute("INSERT INTO log (msg) VALUES (?)", ("완료",))
```

---

## 정리: Java와 Python 컨텍스트 관리 비교

| Java | Python | 비고 |
|------|--------|------|
| `try-with-resources` | `with` 문 | 기본 패턴 |
| `AutoCloseable.close()` | `__exit__()` | 리소스 정리 메서드 |
| `@Bean` + `@PreDestroy` | `lifespan` | 앱 수명 주기 관리 |
| 빈 `catch` 블록 | `suppress()` | 의도적 예외 무시 |
| 동적 리소스 관리 (직접 구현) | `ExitStack` | 여러 리소스 동적 조합 |
| 래퍼 클래스 | `closing()` | close() 메서드 보유 객체 래핑 |
| `null` 가드 패턴 | `nullcontext()` | 선택적 컨텍스트 적용 |
| `@Transactional` | `@contextmanager` + `try/finally` | 트랜잭션 관리 |
