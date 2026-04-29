# concurrent - 동시성 처리

> 공식 문서: https://docs.python.org/3/library/concurrent.futures.html

Java/Spring Boot 개발자라면 `ExecutorService`, `CompletableFuture`, `ForkJoinPool` 등을 통해 동시성 처리를 해왔을 것입니다. Python은 GIL(Global Interpreter Lock)이라는 독특한 제약이 있어 Java와는 다른 접근법이 필요합니다. 이 문서에서는 Python의 주요 동시성 도구들을 Java와 비교하며 설명합니다.

---

## GIL (Global Interpreter Lock) 먼저 이해하기

Python에는 GIL이 있어 **CPython 인터프리터에서 한 번에 하나의 스레드만 Python 바이트코드를 실행**할 수 있습니다. 이로 인해:

- **I/O 작업**: GIL이 해제되므로 멀티스레드가 효과 있음
- **CPU 집약적 작업**: GIL 경합으로 멀티스레드가 오히려 느려질 수 있음 → `ProcessPoolExecutor` 또는 `asyncio` 필요

Java에는 GIL이 없습니다. Java의 `Thread`는 진정한 병렬 실행이 가능합니다.

---

## 1. `concurrent.futures` 개요

`concurrent.futures`는 Java의 `ExecutorService` + `Future<T>` 조합과 가장 유사한 고수준 API입니다.

| Java                          | Python                          |
|-------------------------------|---------------------------------|
| `ExecutorService`             | `ThreadPoolExecutor` / `ProcessPoolExecutor` |
| `Future<T>`                   | `Future`                        |
| `Callable<T>`                 | `callable` (함수 객체)          |
| `executor.submit(task)`       | `executor.submit(fn, *args)`    |
| `executor.invokeAll(tasks)`   | `executor.map(fn, iterable)`    |
| `CompletableFuture.allOf()`   | `asyncio.gather()`              |

---

## 2. `ThreadPoolExecutor`

### 기본 사용법

```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch_data(url: str) -> str:
    time.sleep(1)  # I/O 시뮬레이션
    return f"data from {url}"

# context manager 사용 (Java try-with-resources에 해당)
with ThreadPoolExecutor(max_workers=4) as executor:
    future = executor.submit(fetch_data, "https://api.example.com")
    result = future.result()  # 블로킹 대기
    print(result)
# with 블록 종료 시 executor.shutdown(wait=True) 자동 호출
```

**Java 비교:**

```java
ExecutorService executor = Executors.newFixedThreadPool(4);
try {
    Future<String> future = executor.submit(() -> fetchData("https://api.example.com"));
    String result = future.get();  // 블로킹 대기
} finally {
    executor.shutdown();
}
```

### `submit()` - 단일 태스크 제출

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

urls = [
    "https://api.example.com/users",
    "https://api.example.com/orders",
    "https://api.example.com/products",
]

with ThreadPoolExecutor(max_workers=3) as executor:
    # Future 객체 리스트 생성
    futures = {executor.submit(fetch_data, url): url for url in urls}

    for future in as_completed(futures):  # 완료 순서대로 처리
        url = futures[future]
        try:
            result = future.result()
            print(f"{url}: {result}")
        except Exception as e:
            print(f"{url} 오류: {e}")
```

### `map()` - 병렬 map

```python
from concurrent.futures import ThreadPoolExecutor

def process(item: int) -> int:
    return item * item

with ThreadPoolExecutor(max_workers=4) as executor:
    # Java Stream.parallel().map()과 유사
    results = list(executor.map(process, range(10)))
    # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    # 순서는 입력 순서대로 보장됨 (as_completed와 다름)
```

**Java 비교:**

```java
List<Integer> results = IntStream.range(0, 10)
    .parallel()
    .map(i -> i * i)
    .boxed()
    .collect(Collectors.toList());
```

### `as_completed()` - 완료 순서대로 처리

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time

def slow_task(n: int) -> int:
    time.sleep(random.uniform(0.1, 1.0))
    return n * n

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(slow_task, i) for i in range(5)]

    for future in as_completed(futures):
        # 입력 순서가 아닌 완료 순서대로 출력
        print(f"완료: {future.result()}")
```

> `map()`은 입력 순서대로 결과를 반환하고, `as_completed()`는 완료 순서대로 반환합니다. Java의 `CompletableFuture.anyOf()` 체이닝과 유사한 패턴입니다.

---

## 3. `ProcessPoolExecutor`

### GIL 우회 - CPU 집약적 작업

```python
from concurrent.futures import ProcessPoolExecutor
import math

def cpu_intensive(n: int) -> float:
    """소수 판별 - CPU 집약적 작업"""
    return sum(math.sqrt(i) for i in range(n))

if __name__ == "__main__":
    # 반드시 if __name__ == "__main__": 안에서 실행 (Windows/macOS 요구사항)
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(cpu_intensive, [10**6] * 4))
    print(results)
```

**Java `ForkJoinPool` 비교:**

```java
// Java ForkJoinPool - CPU 코어 수에 맞춰 자동 설정
ForkJoinPool pool = new ForkJoinPool(4);
List<Double> results = pool.submit(() ->
    IntStream.range(0, 4)
        .parallel()
        .mapToDouble(i -> cpuIntensive(1_000_000))
        .boxed()
        .collect(Collectors.toList())
).get();
```

### ProcessPoolExecutor 주의사항

```python
# 프로세스 간 데이터는 직렬화(pickle)되어 전달됨
# Java의 Serializable처럼 모든 인자/반환값이 pickle 가능해야 함

# 불가능한 예: lambda, 클래스 메서드 직접 전달
with ProcessPoolExecutor() as executor:
    # 오류 발생: lambda는 pickle 불가
    # futures = executor.map(lambda x: x*x, range(10))

    # 가능: 모듈 레벨 함수
    futures = executor.map(cpu_intensive, range(10))
```

### Thread vs Process 선택 기준

| 상황                          | 권장 선택              | 이유                                        |
|-------------------------------|------------------------|---------------------------------------------|
| HTTP API 호출, DB 쿼리        | `ThreadPoolExecutor`   | I/O 대기 중 GIL 해제, 오버헤드 낮음        |
| 파일 읽기/쓰기                | `ThreadPoolExecutor`   | I/O 바운드                                  |
| 수학 계산, 이미지 처리         | `ProcessPoolExecutor`  | CPU 바운드, GIL 우회 필요                   |
| NumPy, pandas 연산            | `ThreadPoolExecutor`   | C 확장에서 GIL 해제됨                       |
| FastAPI 엔드포인트 내 I/O     | `asyncio` (`async def`)| 코루틴이 가장 효율적                        |

---

## 4. `Future` 객체

```python
from concurrent.futures import ThreadPoolExecutor
import time

def long_task() -> str:
    time.sleep(2)
    return "완료"

with ThreadPoolExecutor() as executor:
    future = executor.submit(long_task)

    print(future.done())       # False (아직 실행 중)
    print(future.running())    # True
    print(future.cancelled())  # False

    # 타임아웃 지정
    try:
        result = future.result(timeout=3.0)  # 3초 초과 시 TimeoutError
        print(result)
    except TimeoutError:
        future.cancel()  # 취소 시도 (이미 실행 중이면 취소 불가)

    # 예외 확인
    # future.exception() - 태스크에서 발생한 예외 반환 (없으면 None)
```

**Java `Future<T>` / `CompletableFuture` 비교:**

```java
ExecutorService executor = Executors.newCachedThreadPool();
Future<String> future = executor.submit(() -> {
    Thread.sleep(2000);
    return "완료";
});

boolean done = future.isDone();
boolean cancelled = future.isCancelled();

try {
    String result = future.get(3, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    future.cancel(true);
}

// CompletableFuture - Python asyncio와 더 유사
CompletableFuture<String> cf = CompletableFuture.supplyAsync(() -> "결과")
    .thenApply(s -> s + " 처리됨")
    .exceptionally(e -> "오류: " + e.getMessage());
```

---

## 5. `asyncio` 기초 (동시성 관점)

`asyncio`는 단일 스레드에서 이벤트 루프를 이용한 비동기 I/O입니다. Java의 Reactor/WebFlux(Project Reactor) 또는 Vert.x와 개념적으로 유사합니다.

### `asyncio.gather()` - 여러 코루틴 병렬 실행

```python
import asyncio
import httpx

async def fetch(client: httpx.AsyncClient, url: str) -> str:
    response = await client.get(url)
    return response.text

async def main():
    async with httpx.AsyncClient() as client:
        # Java CompletableFuture.allOf()에 해당
        results = await asyncio.gather(
            fetch(client, "https://api.example.com/users"),
            fetch(client, "https://api.example.com/orders"),
            fetch(client, "https://api.example.com/products"),
        )
    return results

asyncio.run(main())
```

**Java 비교:**

```java
CompletableFuture<String> f1 = fetchAsync("https://api.example.com/users");
CompletableFuture<String> f2 = fetchAsync("https://api.example.com/orders");
CompletableFuture<String> f3 = fetchAsync("https://api.example.com/products");

CompletableFuture.allOf(f1, f2, f3).join();
List<String> results = List.of(f1.join(), f2.join(), f3.join());
```

### `asyncio.wait()` - 타임아웃, 첫 번째 완료 대기

```python
import asyncio

async def task(n: int) -> int:
    await asyncio.sleep(n)
    return n

async def main():
    tasks = [asyncio.create_task(task(i)) for i in [3, 1, 2]]

    # FIRST_COMPLETED: 첫 번째 완료 즉시 반환
    done, pending = await asyncio.wait(
        tasks,
        timeout=1.5,
        return_when=asyncio.FIRST_COMPLETED  # 또는 ALL_COMPLETED, FIRST_EXCEPTION
    )

    for t in done:
        print(f"완료: {t.result()}")
    for t in pending:
        t.cancel()  # 미완료 태스크 취소

asyncio.run(main())
```

### `asyncio.create_task()` - 백그라운드 태스크

```python
import asyncio

async def background_job():
    while True:
        print("백그라운드 작업 실행")
        await asyncio.sleep(60)

async def main():
    # 백그라운드 태스크 생성 (즉시 실행 시작, 결과 대기 안 함)
    task = asyncio.create_task(background_job())

    # 메인 작업 계속 진행
    await do_main_work()

    # 종료 시 태스크 취소
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
```

### `asyncio.run_coroutine_threadsafe()` - 스레드에서 코루틴 실행

동기 코드(Thread)에서 이벤트 루프에 코루틴을 제출해야 할 때 사용합니다.

```python
import asyncio
import threading

async def async_task(value: int) -> int:
    await asyncio.sleep(1)
    return value * 2

# 이벤트 루프를 별도 스레드에서 실행
loop = asyncio.new_event_loop()
thread = threading.Thread(target=loop.run_forever, daemon=True)
thread.start()

# 동기 코드에서 코루틴 제출
future = asyncio.run_coroutine_threadsafe(async_task(21), loop)
result = future.result(timeout=5)  # concurrent.futures.Future 반환
print(result)  # 42
```

> FastAPI에서 `sync def` 엔드포인트 내부에서 비동기 함수를 호출할 때 활용됩니다.

---

## 6. `threading` 모듈 핵심

### `Thread` 생성

```python
import threading
import time

def worker(name: str):
    print(f"스레드 {name} 시작")
    time.sleep(1)
    print(f"스레드 {name} 완료")

# 스레드 생성 및 시작
t1 = threading.Thread(target=worker, args=("A",))
t2 = threading.Thread(target=worker, args=("B",))

t1.start()
t2.start()

t1.join()  # Java thread.join()과 동일
t2.join()
```

### `Lock` - 상호 배제

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    with lock:  # Java synchronized(lock) { ... } 에 해당
        counter += 1

threads = [threading.Thread(target=increment) for _ in range(1000)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)  # 1000
```

**Java 비교:**

```java
// synchronized 메서드
synchronized void increment() {
    counter++;
}

// ReentrantLock
ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    counter++;
} finally {
    lock.unlock();
}
```

### `Event` - 스레드 간 신호

```python
import threading
import time

event = threading.Event()

def waiter():
    print("이벤트 대기 중...")
    event.wait()  # Java CountDownLatch.await()와 유사
    print("이벤트 수신!")

def setter():
    time.sleep(2)
    event.set()   # Java CountDownLatch.countDown()와 유사

t1 = threading.Thread(target=waiter)
t2 = threading.Thread(target=setter)
t1.start(); t2.start()
t1.join(); t2.join()
```

### `Semaphore` - 동시 접근 제한

```python
import threading
import time

# 동시에 최대 3개 스레드만 진입 허용
semaphore = threading.Semaphore(3)

def limited_access(n: int):
    with semaphore:  # Java Semaphore.acquire() / release()
        print(f"스레드 {n} 진입")
        time.sleep(1)
        print(f"스레드 {n} 종료")

threads = [threading.Thread(target=limited_access, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

**Java 비교:**

```java
Semaphore semaphore = new Semaphore(3);
semaphore.acquire();
try {
    // 제한된 자원 사용
} finally {
    semaphore.release();
}
```

---

## 7. 선택 가이드

### 작업 유형별 권장 도구

```
작업 유형 판단
│
├── I/O 바운드 (HTTP, DB, 파일)
│   ├── FastAPI async def → asyncio (가장 권장)
│   ├── 동기 코드 + 병렬화 → ThreadPoolExecutor
│   └── 레거시 동기 라이브러리 → loop.run_in_executor()
│
└── CPU 바운드 (계산, 이미지 처리)
    ├── ProcessPoolExecutor (GIL 우회)
    └── C 확장 (NumPy 등) → ThreadPoolExecutor 가능
```

### FastAPI에서의 패턴

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI

app = FastAPI()
executor = ThreadPoolExecutor(max_workers=10)

# 패턴 1: 순수 async I/O - 가장 효율적
@app.get("/async-io")
async def async_io_endpoint():
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
    return response.json()

# 패턴 2: 동기 블로킹 함수를 스레드 풀에서 실행
def sync_db_query(user_id: int) -> dict:
    # 동기 ORM (SQLAlchemy sync) 사용
    return {"user_id": user_id, "name": "홍길동"}

@app.get("/run-in-executor/{user_id}")
async def run_in_executor_endpoint(user_id: int):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, sync_db_query, user_id)
    return result

# 패턴 3: sync def 엔드포인트 - FastAPI가 자동으로 스레드 풀에서 실행
@app.get("/sync/{user_id}")
def sync_endpoint(user_id: int):
    # FastAPI는 sync def를 threadpool에서 자동 실행
    return sync_db_query(user_id)
```

> FastAPI에서 `async def`는 이벤트 루프에서 직접 실행되고, `def`는 자동으로 스레드 풀에서 실행됩니다. 따라서 `def` 안에서 `await`를 쓸 수 없으며, `async def` 안에서 블로킹 I/O를 직접 호출하면 이벤트 루프가 블록됩니다.

### 요약 비교표

| Java                        | Python                         | 비고                            |
|-----------------------------|--------------------------------|---------------------------------|
| `Executors.newFixedThreadPool()` | `ThreadPoolExecutor(max_workers=N)` | I/O 바운드          |
| `ForkJoinPool`              | `ProcessPoolExecutor`          | CPU 바운드                      |
| `CompletableFuture`         | `asyncio.gather()` / `asyncio.create_task()` | 비동기 체이닝  |
| `Future<T>.get()`           | `future.result()`              | 블로킹 결과 획득                |
| `synchronized`              | `threading.Lock()` + `with`    | 상호 배제                       |
| `CountDownLatch`            | `threading.Event`              | 스레드 간 신호                  |
| `Semaphore`                 | `threading.Semaphore`          | 동시 접근 제한                  |
| `@Async` (Spring)           | `async def` (FastAPI/asyncio)  | 비동기 메서드                   |
