# functools - 함수형 프로그래밍 도구

> 공식 문서: https://docs.python.org/3/library/functools.html

`functools` 모듈은 고차 함수(higher-order function)와 함수를 다루는 유틸리티를 제공합니다.
Java의 `java.util.function` 패키지나 Spring의 AOP 기능과 유사한 개념을 다루지만,
Python에서는 훨씬 간결하고 직관적으로 사용할 수 있습니다.

---

## 1. `partial` - 인수 고정

### 개념

`partial`은 기존 함수의 일부 인수를 미리 고정해 새 함수를 만듭니다.
Java에서 메서드 오버로딩이나 빌더 패턴으로 해결하던 문제를 단 한 줄로 처리할 수 있습니다.

### Java vs Python 비교

**Java - 메서드 오버로딩으로 기본값 흉내내기**

```java
// Java: 오버로딩으로 기본값을 제공
public class MathUtils {
    public static double power(double base, double exp) {
        return Math.pow(base, exp);
    }

    // exp=2 고정 버전을 별도 메서드로 정의
    public static double square(double base) {
        return power(base, 2);
    }

    // exp=3 고정 버전
    public static double cube(double base) {
        return power(base, 3);
    }
}

double result = MathUtils.square(5); // 25.0
```

**Python - `partial`로 인수 고정**

```python
from functools import partial

def power(base, exp):
    return base ** exp

# exp=2 를 고정한 새 함수 생성 - 단 한 줄!
square = partial(power, exp=2)
cube   = partial(power, exp=3)

print(square(5))  # 25
print(cube(3))    # 27

# 키워드 인수뿐 아니라 위치 인수도 고정 가능
double = partial(power, exp=2)   # exp 고정
two_power = partial(power, 2)    # base=2 고정 → 2의 n제곱

print(two_power(10))  # 1024 (2^10)
```

### Java 빌더 패턴 대응

```java
// Java: Builder 패턴으로 기본값을 미리 설정
HttpClient client = HttpClient.newBuilder()
    .connectTimeout(Duration.ofSeconds(10))
    .build();

// 동일한 설정으로 여러 요청
client.send(request1, bodyHandler);
client.send(request2, bodyHandler);
```

```python
import urllib.request
from functools import partial

def fetch(url, timeout=5, headers=None):
    """간단한 HTTP GET 요청"""
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

# timeout=10, headers 고정한 "특화된" fetch 함수 생성
fetch_internal = partial(fetch, timeout=10, headers={"X-Internal": "true"})

# 이제 url 만 넘기면 됨
data1 = fetch_internal("https://api.example.com/users")
data2 = fetch_internal("https://api.example.com/orders")
```

### FastAPI `Depends`와 함께 사용하는 실전 패턴

FastAPI에서 `partial`은 의존성(dependency)을 파라미터화할 때 매우 유용합니다.
Java Spring의 `@Qualifier` + `@Bean` 조합과 유사합니다.

```python
from fastapi import FastAPI, Depends, Query
from functools import partial

app = FastAPI()

# 범용 페이지네이션 의존성
def get_pagination(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    max_size: int = 100,          # 이 값을 고정하고 싶음
):
    size = min(size, max_size)
    return {"skip": (page - 1) * size, "limit": size}

# max_size 를 엔드포인트별로 다르게 고정
paginate_users  = partial(get_pagination, max_size=50)
paginate_logs   = partial(get_pagination, max_size=1000)

@app.get("/users")
def list_users(pagination=Depends(paginate_users)):
    # pagination = {"skip": ..., "limit": ...}
    return pagination

@app.get("/logs")
def list_logs(pagination=Depends(paginate_logs)):
    return pagination
```

> Spring 비교: `@Bean` 메서드를 여러 개 정의해 `@Qualifier`로 구분하는 것과 같은 역할을
> Python에서는 `partial` 한 줄로 처리합니다.

---

## 2. `lru_cache` / `cache` - 메모이제이션

### 개념

함수 호출 결과를 캐시하여 동일한 인수로 재호출할 때 즉시 반환합니다.
Java Spring의 `@Cacheable`과 동일한 목적이지만, 외부 라이브러리 없이 표준 라이브러리만으로 사용 가능합니다.

| 구분 | Java | Python |
|---|---|---|
| 어노테이션/데코레이터 | `@Cacheable("cacheName")` | `@lru_cache(maxsize=128)` |
| 캐시 무효화 | `@CacheEvict` | `func.cache_clear()` |
| 캐시 통계 | 별도 설정 필요 | `func.cache_info()` |
| 설정 위치 | `application.yml` + `@EnableCaching` | 함수 선언부 바로 위 |

### Java vs Python 비교

**Java - Spring `@Cacheable`**

```java
@Service
public class UserService {

    @Cacheable(value = "users", key = "#userId")
    public User findById(Long userId) {
        // DB 조회 (캐시 미스일 때만 실행)
        return userRepository.findById(userId).orElseThrow();
    }

    @CacheEvict(value = "users", key = "#userId")
    public void evict(Long userId) { }
}
```

**Python - `lru_cache`**

```python
from functools import lru_cache, cache
import time

# maxsize=None 이면 크기 제한 없음 (= @cache 와 동일)
@lru_cache(maxsize=128)
def find_user(user_id: int) -> dict:
    """DB 조회를 흉내낸 함수 (캐시 미스일 때만 실행)"""
    time.sleep(0.1)  # 느린 DB 조회 시뮬레이션
    return {"id": user_id, "name": f"User-{user_id}"}

# Python 3.9+ 에서는 @cache 로 더 간결하게 (maxsize=None 과 동일)
@cache
def get_config(key: str) -> str:
    print(f"[CACHE MISS] Loading config: {key}")
    return f"value-of-{key}"
```

### `maxsize` 파라미터

```python
from functools import lru_cache

# maxsize=None: 무제한 캐시 (메모리 주의!)
@lru_cache(maxsize=None)
def expensive_calc(n):
    return n ** 2

# maxsize=128: 최근 128개만 유지 (LRU = Least Recently Used)
# 128개 초과 시 가장 오래된 항목 제거
@lru_cache(maxsize=128)
def fetch_data(key: str):
    ...

# maxsize=1: 마지막 호출 결과 하나만 캐시
@lru_cache(maxsize=1)
def get_latest():
    ...
```

### `cache_info()` 와 `cache_clear()`

```python
from functools import lru_cache

@lru_cache(maxsize=32)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

fib(30)

# 캐시 통계 확인
info = fib.cache_info()
print(info)
# CacheInfo(hits=28, misses=31, maxsize=32, currsize=32)
# hits:    캐시에서 바로 반환된 횟수
# misses:  실제 함수가 실행된 횟수
# maxsize: 최대 캐시 크기
# currsize: 현재 저장된 항목 수

# 캐시 전체 초기화 (Spring @CacheEvict(allEntries=true) 와 동일)
fib.cache_clear()
print(fib.cache_info())
# CacheInfo(hits=0, misses=0, maxsize=32, currsize=0)
```

### 재귀 함수 성능 개선 예시 (fibonacci)

```python
from functools import lru_cache
import time

# 캐시 없음: O(2^n) 시간 복잡도
def fib_slow(n):
    if n < 2:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)

# 캐시 있음: O(n) 시간 복잡도
@lru_cache(maxsize=None)
def fib_fast(n):
    if n < 2:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)

# 성능 비교
start = time.perf_counter()
fib_slow(35)
print(f"캐시 없음: {time.perf_counter() - start:.3f}s")  # 약 2~5초

start = time.perf_counter()
fib_fast(35)
print(f"캐시 있음: {time.perf_counter() - start:.6f}s")  # 0.000001초 미만
```

> **주의**: `lru_cache`는 인수가 hashable(불변)해야 합니다.
> `list`, `dict` 같은 mutable 타입은 인수로 사용할 수 없습니다.
> Java의 `Map` 키가 `equals()`/`hashCode()`를 구현해야 하는 것과 같은 이유입니다.

### FastAPI에서 싱글톤 의존성으로 활용

```python
from functools import lru_cache
from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str = "postgresql://localhost/mydb"
    secret_key: str = "dev-secret"

    class Config:
        env_file = ".env"

# @lru_cache 로 Settings 인스턴스를 싱글톤으로 관리
# Spring의 @Bean + @Scope("singleton") 과 동일
@lru_cache
def get_settings() -> Settings:
    print("Settings 로딩 (최초 1회만 출력됨)")
    return Settings()

app = FastAPI()

@app.get("/info")
def read_info(settings: Settings = Depends(get_settings)):
    return {"db_url": settings.db_url}
```

---

## 3. `cached_property` - 지연 계산 프로퍼티

### 개념

클래스 프로퍼티를 최초 접근 시 한 번만 계산하고 이후에는 인스턴스에 캐시합니다.
Java의 lazy initialization 패턴을 데코레이터 하나로 대체합니다.

### Java vs Python 비교

**Java - Lazy Initialization 패턴**

```java
public class Circle {
    private final double radius;
    private Double area;       // nullable, lazy
    private Double perimeter;  // nullable, lazy

    public Circle(double radius) {
        this.radius = radius;
    }

    public double getArea() {
        if (area == null) {                       // 최초 접근 시 계산
            area = Math.PI * radius * radius;
        }
        return area;
    }

    public double getPerimeter() {
        if (perimeter == null) {
            perimeter = 2 * Math.PI * radius;
        }
        return perimeter;
    }
}
```

**Python - `cached_property`**

```python
from functools import cached_property
import math

class Circle:
    def __init__(self, radius: float):
        self.radius = radius

    @cached_property
    def area(self) -> float:
        print("area 계산 중...")   # 최초 1회만 출력
        return math.pi * self.radius ** 2

    @cached_property
    def perimeter(self) -> float:
        print("perimeter 계산 중...")
        return 2 * math.pi * self.radius

c = Circle(5)
print(c.area)       # "area 계산 중..." 출력 후 78.53...
print(c.area)       # 캐시에서 즉시 반환, 출력 없음
print(c.perimeter)  # "perimeter 계산 중..." 출력 후 31.41...
```

### `cached_property` vs `property` vs `lru_cache` 차이

```python
from functools import cached_property, lru_cache

class DataProcessor:

    def __init__(self, data: list):
        self.data = data

    # @property: 매번 재계산 (캐시 없음)
    @property
    def mean(self) -> float:
        return sum(self.data) / len(self.data)

    # @cached_property: 인스턴스별 1회 계산 후 인스턴스 __dict__ 에 저장
    @cached_property
    def std_dev(self) -> float:
        avg = self.mean
        variance = sum((x - avg) ** 2 for x in self.data) / len(self.data)
        return variance ** 0.5

# cached_property 캐시 무효화: 직접 __dict__ 에서 삭제
proc = DataProcessor([1, 2, 3, 4, 5])
_ = proc.std_dev          # 계산 및 캐시
proc.data = [10, 20, 30]  # data 변경
del proc.__dict__["std_dev"]  # 캐시 삭제 → 다음 접근 시 재계산
print(proc.std_dev)           # 재계산됨
```

> **주의**: `cached_property`는 스레드 안전(thread-safe)하지 않습니다.
> 멀티스레드 환경에서는 `threading.Lock`을 별도로 사용하거나, `lru_cache`를 사용하세요.

---

## 4. `wraps` - 데코레이터 메타데이터 보존

### 개념

Python 데코레이터를 작성할 때 원본 함수의 `__name__`, `__doc__`, `__annotations__` 등이
래퍼 함수에 의해 덮어씌워지는 문제를 방지합니다.
Java의 AOP 프록시가 원본 빈의 메타데이터를 유지하는 것과 유사한 목적입니다.

### `wraps` 없을 때의 문제

```python
import time

# wraps 미사용 - 잘못된 데코레이터
def timer_bad(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"실행 시간: {time.perf_counter() - start:.4f}s")
        return result
    return wrapper  # wrapper 함수 자체를 반환

@timer_bad
def fetch_data(user_id: int) -> dict:
    """사용자 데이터를 가져옵니다."""
    return {"id": user_id}

# 메타데이터가 손실됨!
print(fetch_data.__name__)  # "wrapper"   ← 원래는 "fetch_data" 여야 함
print(fetch_data.__doc__)   # None        ← 원래 docstring 사라짐

# FastAPI, pytest, logging 등에서 함수 이름을 사용하면 잘못된 이름이 출력됨
```

### `wraps` 사용 - 올바른 데코레이터 패턴

```python
import time
from functools import wraps

# wraps 사용 - 올바른 데코레이터
def timer(func):
    @wraps(func)          # ← 핵심! 원본 함수의 메타데이터를 복사
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"[{func.__name__}] 실행 시간: {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

def retry(max_attempts: int = 3, delay: float = 1.0):
    """파라미터가 있는 데코레이터 팩토리"""
    def decorator(func):
        @wraps(func)      # ← 중첩 데코레이터에서도 반드시 사용
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"[{func.__name__}] 재시도 {attempt}/{max_attempts}: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

@timer
@retry(max_attempts=3, delay=0.5)
def fetch_data(user_id: int) -> dict:
    """사용자 데이터를 가져옵니다."""
    return {"id": user_id}

# 메타데이터가 보존됨
print(fetch_data.__name__)  # "fetch_data"
print(fetch_data.__doc__)   # "사용자 데이터를 가져옵니다."
```

### 실전: FastAPI 미들웨어 패턴

```python
from functools import wraps
from fastapi import HTTPException, Request

def require_admin(func):
    """관리자 권한을 검사하는 데코레이터"""
    @wraps(func)
    async def wrapper(*args, request: Request, **kwargs):
        user = getattr(request.state, "user", None)
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="관리자 권한 필요")
        return await func(*args, request=request, **kwargs)
    return wrapper
```

---

## 5. `reduce` - 누적 계산

### 개념

시퀀스의 모든 요소를 순서대로 누적 적용해 단일 값으로 줄입니다.
Java의 `Stream.reduce()`와 완전히 동일한 개념입니다.

### Java vs Python 비교

**Java - `Stream.reduce()`**

```java
import java.util.List;
import java.util.stream.Stream;

List<Integer> numbers = List.of(1, 2, 3, 4, 5);

// 합계
int sum = numbers.stream()
    .reduce(0, Integer::sum);  // 0 + 1 + 2 + 3 + 4 + 5 = 15

// 곱
int product = numbers.stream()
    .reduce(1, (a, b) -> a * b);  // 1 * 2 * 3 * 4 * 5 = 120

// 최댓값
int max = numbers.stream()
    .reduce(Integer.MIN_VALUE, Integer::max);
```

**Python - `functools.reduce()`**

```python
from functools import reduce
import operator

numbers = [1, 2, 3, 4, 5]

# 합계 (사실 sum() 이 더 pythonic 하지만, reduce 예시로)
total = reduce(lambda acc, x: acc + x, numbers, 0)
print(total)  # 15

# 곱
product = reduce(lambda acc, x: acc * x, numbers, 1)
print(product)  # 120

# 초기값 없이 호출하면 첫 번째 요소가 초기값으로 사용됨
maximum = reduce(lambda a, b: a if a > b else b, numbers)
print(maximum)  # 5
```

### `operator` 모듈과 함께 사용

`lambda` 대신 `operator` 모듈의 함수를 사용하면 더 명확하고 빠릅니다.
Java의 메서드 참조(`Integer::sum`)와 동일한 스타일입니다.

```python
from functools import reduce
import operator

numbers = [1, 2, 3, 4, 5]

# operator 모듈 함수 사용 (lambda 보다 빠르고 가독성 높음)
total   = reduce(operator.add, numbers, 0)      # 15
product = reduce(operator.mul, numbers, 1)      # 120
maximum = reduce(operator.gt, numbers)          # (잘못된 사용 예시)

# 실전: 딕셔너리 병합
configs = [
    {"host": "localhost"},
    {"port": 8080},
    {"debug": True},
]
merged = reduce(operator.or_, configs)  # Python 3.9+ dict 병합 연산자
print(merged)  # {"host": "localhost", "port": 8080, "debug": True}

# 실전: 중첩 딕셔너리에서 값 가져오기 (optional chaining 대체)
data = {"user": {"profile": {"name": "Alice"}}}
keys = ["user", "profile", "name"]
value = reduce(lambda d, k: d[k], keys, data)
print(value)  # "Alice"
```

> **Python 관용구**: 단순 합계·최대·최소는 내장 함수 `sum()`, `max()`, `min()`을
> 사용하는 것이 더 pythonic 합니다. `reduce`는 커스텀 누적 로직이 필요할 때 사용하세요.

---

## 6. `total_ordering` - 비교 메서드 자동 완성

### 개념

클래스에서 `__eq__`와 `__lt__` (또는 `__le__`, `__gt__`, `__ge__` 중 하나)만 구현하면
나머지 비교 메서드를 자동으로 생성합니다.
Java의 `Comparable<T>` 인터페이스와 `compareTo()` 를 구현하는 것과 유사하지만,
Python은 `==`, `<`, `>`, `<=`, `>=` 를 각각 별도 메서드로 정의합니다.

### Java vs Python 비교

**Java - `Comparable` 구현**

```java
public class Product implements Comparable<Product> {
    private final String name;
    private final double price;

    public Product(String name, double price) {
        this.name = name;
        this.price = price;
    }

    @Override
    public int compareTo(Product other) {
        return Double.compare(this.price, other.price);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Product)) return false;
        return Double.compare(((Product) o).price, this.price) == 0;
    }

    @Override
    public int hashCode() {
        return Double.hashCode(price);
    }
}

// 사용
List<Product> products = Arrays.asList(
    new Product("B", 20.0),
    new Product("A", 10.0)
);
Collections.sort(products); // compareTo 기반 정렬
```

**Python - `total_ordering` 없이 모두 수동 구현**

```python
# total_ordering 없이 구현하면 6개의 메서드가 필요
class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def __eq__(self, other): return self.price == other.price
    def __lt__(self, other): return self.price <  other.price
    def __le__(self, other): return self.price <= other.price  # 반복적인 코드
    def __gt__(self, other): return self.price >  other.price  # 반복적인 코드
    def __ge__(self, other): return self.price >= other.price  # 반복적인 코드
```

**Python - `total_ordering`으로 자동 완성**

```python
from functools import total_ordering

@total_ordering
class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    # __eq__ 와 __lt__ 두 개만 구현하면 충분
    def __eq__(self, other) -> bool:
        if not isinstance(other, Product):
            return NotImplemented
        return self.price == other.price

    def __lt__(self, other) -> bool:
        if not isinstance(other, Product):
            return NotImplemented
        return self.price < other.price

    def __repr__(self):
        return f"Product({self.name!r}, {self.price})"

# 나머지 비교 연산자가 자동으로 동작
products = [
    Product("Laptop", 1500.0),
    Product("Mouse",    25.0),
    Product("Monitor", 400.0),
]

print(sorted(products))  # [Product('Mouse', 25.0), Product('Monitor', 400.0), Product('Laptop', 1500.0)]
print(max(products))     # Product('Laptop', 1500.0)

p1 = Product("A", 100.0)
p2 = Product("B", 200.0)
print(p1 < p2)   # True   (직접 구현)
print(p1 > p2)   # False  (자동 생성: not (p1 < p2 or p1 == p2))
print(p1 <= p2)  # True   (자동 생성)
print(p1 >= p2)  # False  (자동 생성)
```

### `dataclass`와 함께 사용하는 현대적 패턴

```python
from dataclasses import dataclass, field
from functools import total_ordering

# Python 3.7+: dataclass의 order=True 옵션이 total_ordering 과 유사한 역할
@dataclass(order=True)
class VersionedConfig:
    # sort_index 필드 기준으로 자동 정렬 (필드 선언 순서)
    version: int
    name: str = field(compare=False)  # 비교에서 제외

v1 = VersionedConfig(version=1, name="alpha")
v2 = VersionedConfig(version=2, name="beta")
print(v1 < v2)  # True
print(sorted([v2, v1]))  # [VersionedConfig(version=1, ...), VersionedConfig(version=2, ...)]
```

> **권장**: 단순한 데이터 클래스라면 `@dataclass(order=True)`가 더 간결합니다.
> 비교 로직이 복잡하거나 기존 클래스에 추가해야 할 때 `@total_ordering`을 사용하세요.

---

## 요약 비교표

| functools | 대응 Java 기능 | 핵심 용도 |
|---|---|---|
| `partial` | 메서드 오버로딩, 빌더 패턴 | 인수 일부를 미리 고정 |
| `lru_cache` / `cache` | `@Cacheable` (Spring Cache) | 함수 결과 메모이제이션 |
| `cached_property` | Lazy initialization 패턴 | 프로퍼티 지연 계산 및 캐시 |
| `wraps` | AOP 프록시 메타데이터 보존 | 데코레이터 작성 시 필수 |
| `reduce` | `Stream.reduce()` | 시퀀스 누적 계산 |
| `total_ordering` | `Comparable<T>` 인터페이스 | 비교 메서드 자동 완성 |
