# collections - 고급 자료구조

> 공식 문서: https://docs.python.org/3/library/collections.html

`collections` 모듈은 Python 내장 자료구조(`list`, `dict`, `set`, `tuple`)를 확장한
특수 목적 컨테이너를 제공합니다.
Java의 `java.util` 패키지에 있는 자료구조들과 비교하며 살펴봅니다.

---

## 1. `defaultdict` - 기본값 있는 딕셔너리

### 개념

존재하지 않는 키에 접근할 때 `KeyError` 대신 미리 지정한 타입의 기본값을 자동으로 생성합니다.
Java의 `Map.getOrDefault()` 또는 `computeIfAbsent()`와 유사하지만,
`defaultdict`는 모든 접근에서 자동으로 적용된다는 차이가 있습니다.

### Java vs Python 비교

**Java - `getOrDefault` / `computeIfAbsent`**

```java
import java.util.*;

Map<String, Integer> counts = new HashMap<>();

// getOrDefault: 읽기 전용 (맵에 저장하지 않음)
int count = counts.getOrDefault("apple", 0);  // 0 반환, 맵은 그대로

// computeIfAbsent: 없으면 삽입
counts.merge("apple", 1, Integer::sum);       // 우아하지 않음
counts.compute("apple", (k, v) -> v == null ? 1 : v + 1); // 장황함

// 그룹핑: Collectors.groupingBy()
List<String> words = Arrays.asList("apple", "ant", "banana", "bear", "cherry");
Map<Character, List<String>> grouped = words.stream()
    .collect(Collectors.groupingBy(w -> w.charAt(0)));
// {'a': ["apple", "ant"], 'b': ["banana", "bear"], 'c': ["cherry"]}
```

**Python - `defaultdict`**

```python
from collections import defaultdict

# int 기본값: 없는 키 접근 시 int() = 0 이 자동 삽입
counts = defaultdict(int)
counts["apple"] += 1   # KeyError 없음, 자동으로 0 → 1
counts["apple"] += 1   # 2
counts["banana"] += 1  # 0 → 1
print(dict(counts))    # {"apple": 2, "banana": 1}

# list 기본값: 없는 키 접근 시 list() = [] 이 자동 삽입
grouped = defaultdict(list)
words = ["apple", "ant", "banana", "bear", "cherry"]
for word in words:
    grouped[word[0]].append(word)   # 키 없어도 [] 자동 생성 후 append
print(dict(grouped))
# {'a': ['apple', 'ant'], 'b': ['banana', 'bear'], 'c': ['cherry']}

# set 기본값
unique_per_key = defaultdict(set)
data = [("user1", "page_a"), ("user1", "page_b"), ("user2", "page_a"), ("user1", "page_a")]
for user, page in data:
    unique_per_key[user].add(page)
print(dict(unique_per_key))
# {'user1': {'page_a', 'page_b'}, 'user2': {'page_a'}}
```

### 그룹핑 패턴 (Java `Collectors.groupingBy()` 대응)

```python
from collections import defaultdict

# 주문 데이터를 고객 ID 기준으로 그룹핑
orders = [
    {"customer": "Alice", "amount": 100},
    {"customer": "Bob",   "amount": 200},
    {"customer": "Alice", "amount": 150},
    {"customer": "Bob",   "amount": 50},
]

# Java: orders.stream().collect(Collectors.groupingBy(o -> o.getCustomer()))
by_customer = defaultdict(list)
for order in orders:
    by_customer[order["customer"]].append(order)

# 고객별 총 주문 금액
totals = {
    customer: sum(o["amount"] for o in order_list)
    for customer, order_list in by_customer.items()
}
print(totals)  # {'Alice': 250, 'Bob': 250}

# 중첩 defaultdict: 트리 구조 생성
tree = defaultdict(lambda: defaultdict(list))
tree["fruits"]["tropical"].append("mango")
tree["fruits"]["tropical"].append("papaya")
tree["fruits"]["citrus"].append("lemon")
print(dict(tree["fruits"]))
# {'tropical': ['mango', 'papaya'], 'citrus': ['lemon']}
```

---

## 2. `Counter` - 빈도 계산

### 개념

시퀀스의 각 요소 출현 빈도를 딕셔너리로 관리합니다.
Java에서는 `Map<T, Integer>`와 `merge()` 또는 스트림 + `groupingBy(counting())`으로
직접 구현해야 하지만, Python은 한 줄로 끝납니다.

### Java vs Python 비교

**Java - 빈도 계산 직접 구현**

```java
import java.util.*;
import java.util.stream.Collectors;

List<String> words = Arrays.asList("apple", "banana", "apple", "cherry", "banana", "apple");

// 방법 1: 직접 구현
Map<String, Long> freq = new HashMap<>();
for (String w : words) {
    freq.merge(w, 1L, Long::sum);
}

// 방법 2: 스트림 사용
Map<String, Long> freq2 = words.stream()
    .collect(Collectors.groupingBy(w -> w, Collectors.counting()));

// 가장 많은 요소 찾기: 추가 작업 필요
String most = freq.entrySet().stream()
    .max(Map.Entry.comparingByValue())
    .map(Map.Entry::getKey)
    .orElseThrow();
```

**Python - `Counter`**

```python
from collections import Counter

words = ["apple", "banana", "apple", "cherry", "banana", "apple"]

# 생성 방법 3가지
counter = Counter(words)              # 리스트/이터러블 직접 전달
print(counter)  # Counter({'apple': 3, 'banana': 2, 'cherry': 1})

counter2 = Counter("abracadabra")    # 문자열 → 각 문자 빈도
counter3 = Counter({"a": 4, "b": 2}) # 딕셔너리 → Counter

# 없는 키는 0 반환 (KeyError 없음)
print(counter["durian"])  # 0
```

### `most_common()` - 가장 빈번한 요소

```python
from collections import Counter

text = "the quick brown fox jumps over the lazy dog the fox"
word_freq = Counter(text.split())

# 상위 N개 반환 (내부적으로 힙 사용, O(n log k))
top3 = word_freq.most_common(3)
print(top3)  # [('the', 3), ('fox', 2), ('quick', 1)]

# 인수 없이 호출하면 전체를 내림차순으로 반환
all_sorted = word_freq.most_common()

# 가장 적은 요소 (슬라이싱으로 뒤에서 접근)
least3 = word_freq.most_common()[:-4:-1]
print(least3)  # 빈도 최하위 3개
```

### 덧셈 / 뺄셈 연산

```python
from collections import Counter

inventory_a = Counter({"apple": 10, "banana": 5, "cherry": 2})
inventory_b = Counter({"apple": 3,  "banana": 7, "mango": 4})

# 합산: 각 항목 수량 합산
combined = inventory_a + inventory_b
print(combined)
# Counter({'banana': 12, 'apple': 13, 'mango': 4, 'cherry': 2})

# 차감: 양수인 항목만 유지 (음수/0은 제거)
diff = inventory_a - inventory_b
print(diff)
# Counter({'apple': 7, 'cherry': 2})  ← banana는 음수(-2)이므로 제거

# 교집합 (최솟값), 합집합 (최댓값)
intersection = inventory_a & inventory_b  # min(a[k], b[k])
union         = inventory_a | inventory_b  # max(a[k], b[k])
print(intersection)  # Counter({'apple': 3, 'banana': 5})
print(union)         # Counter({'apple': 10, 'banana': 7, 'mango': 4, 'cherry': 2})
```

### 단어 빈도 분석 예시

```python
from collections import Counter
import re

def analyze_text(text: str, top_n: int = 10) -> dict:
    """텍스트에서 상위 N개 단어와 빈도를 반환"""
    # 소문자 변환 + 단어만 추출
    words = re.findall(r"\b[a-z]+\b", text.lower())

    # 불용어(stopwords) 제거
    stopwords = {"the", "a", "an", "is", "in", "on", "at", "to", "for", "of", "and"}
    words = [w for w in words if w not in stopwords]

    counter = Counter(words)
    return dict(counter.most_common(top_n))

sample = """
Python is a versatile programming language. Python supports object-oriented,
functional, and procedural programming styles. Many developers love Python
for its simplicity and readability.
"""
print(analyze_text(sample, top_n=5))
# {'python': 3, 'programming': 3, 'and': ... (불용어 제거 후)}
```

---

## 3. `deque` - 양방향 큐

### 개념

양쪽 끝에서 O(1) 시간에 삽입/삭제가 가능한 자료구조입니다.
Java의 `ArrayDeque`와 동일한 역할이며, Python `list`의 `insert(0, x)` (O(n))을 O(1)로 대체합니다.

### Java vs Python 비교

| 연산 | Java `ArrayDeque` | Python `deque` |
|---|---|---|
| 앞에 추가 | `addFirst(e)` | `appendleft(e)` |
| 뒤에 추가 | `addLast(e)` | `append(e)` |
| 앞에서 제거 | `pollFirst()` | `popleft()` |
| 뒤에서 제거 | `pollLast()` | `pop()` |
| 크기 제한 | 없음 | `maxlen` 옵션 |

```python
from collections import deque

dq = deque([1, 2, 3])

dq.append(4)       # 뒤에 추가: deque([1, 2, 3, 4])
dq.appendleft(0)   # 앞에 추가: deque([0, 1, 2, 3, 4])
dq.pop()           # 뒤에서 제거: 4 반환, deque([0, 1, 2, 3])
dq.popleft()       # 앞에서 제거: 0 반환, deque([1, 2, 3])

# 확장
dq.extend([4, 5])           # 뒤에 여러 항목: deque([1, 2, 3, 4, 5])
dq.extendleft([0, -1])      # 앞에 여러 항목 (역순 삽입!): deque([-1, 0, 1, 2, 3, 4, 5])
```

### `rotate()` - 회전

```python
from collections import deque

dq = deque([1, 2, 3, 4, 5])

dq.rotate(2)   # 오른쪽으로 2칸 회전
print(dq)      # deque([4, 5, 1, 2, 3])

dq.rotate(-1)  # 왼쪽으로 1칸 회전
print(dq)      # deque([5, 1, 2, 3, 4])

# 실전: 라운드 로빈 스케줄러
tasks = deque(["task_a", "task_b", "task_c"])
for _ in range(6):
    current = tasks[0]
    print(f"실행: {current}")
    tasks.rotate(-1)  # 다음 태스크로
```

### `maxlen`으로 슬라이딩 윈도우 구현

```python
from collections import deque

# maxlen 설정: 크기를 초과하면 반대쪽 항목이 자동으로 제거됨
# Java: LinkedList + 수동 size 체크
window = deque(maxlen=3)

stream = [1, 2, 3, 4, 5, 6, 7]
for value in stream:
    window.append(value)
    if len(window) == 3:
        avg = sum(window) / len(window)
        print(f"window={list(window)}, avg={avg:.1f}")

# window=[1, 2, 3], avg=2.0
# window=[2, 3, 4], avg=3.0
# window=[3, 4, 5], avg=4.0
# window=[4, 5, 6], avg=5.0
# window=[5, 6, 7], avg=6.0

# 최근 N개 로그 유지
recent_logs = deque(maxlen=100)
recent_logs.append("2024-01-01 ERROR: ...")  # 101번째 추가 시 가장 오래된 것 자동 삭제
```

### BFS 구현 예시

```python
from collections import deque

def bfs(graph: dict, start: str) -> list:
    """너비 우선 탐색 - deque 활용"""
    visited = set()
    queue = deque([start])  # list 대신 deque 사용 → popleft() O(1)
    result = []

    while queue:
        node = queue.popleft()  # list.pop(0)은 O(n), deque.popleft()는 O(1)
        if node in visited:
            continue
        visited.add(node)
        result.append(node)
        queue.extend(graph.get(node, []))

    return result
```

---

## 4. `OrderedDict` - 순서 보장 딕셔너리

### 개념

삽입 순서를 기억하는 딕셔너리입니다.
Python 3.7부터 일반 `dict`도 삽입 순서를 보장하지만, `OrderedDict`는 추가 기능을 제공합니다.

### Python 3.7+ `dict`와의 차이

```python
from collections import OrderedDict

# Python 3.7+: 일반 dict도 삽입 순서 보장
d = {"c": 3, "a": 1, "b": 2}
print(list(d.keys()))  # ['c', 'a', 'b'] ← 삽입 순서 유지

# OrderedDict 고유 기능:
od = OrderedDict([("c", 3), ("a", 1), ("b", 2)])

# 1. 순서 기반 동등성 비교
od1 = OrderedDict([("a", 1), ("b", 2)])
od2 = OrderedDict([("b", 2), ("a", 1)])
print(od1 == od2)  # False (순서 다름)

d1 = {"a": 1, "b": 2}
d2 = {"b": 2, "a": 1}
print(d1 == d2)    # True (일반 dict는 순서 무관)

# 2. move_to_end()
od = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
od.move_to_end("a")          # "a" 를 맨 뒤로
print(list(od.keys()))       # ['b', 'c', 'a']

od.move_to_end("a", last=False)  # "a" 를 맨 앞으로
print(list(od.keys()))           # ['a', 'b', 'c']
```

### LRU 캐시 직접 구현 예시

`OrderedDict`의 `move_to_end()`를 활용하면 LRU(Least Recently Used) 캐시를 직접 구현할 수 있습니다.
Java에서 `LinkedHashMap`의 `accessOrder=true` 옵션으로 구현하는 것과 동일합니다.

```java
// Java: LinkedHashMap 으로 LRU 구현
LinkedHashMap<Integer, Integer> lruCache = new LinkedHashMap<>(16, 0.75f, true) {
    protected boolean removeEldestEntry(Map.Entry<Integer, Integer> eldest) {
        return size() > CAPACITY;
    }
};
```

```python
from collections import OrderedDict

class LRUCache:
    """OrderedDict 기반 LRU 캐시 (Thread-unsafe 버전)"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # 접근한 항목을 맨 뒤로 이동 (가장 최근 사용)
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # 맨 앞 항목 제거 (가장 오래 사용 안 한 항목)
            self.cache.popitem(last=False)

# 사용
cache = LRUCache(capacity=3)
cache.put(1, 10)
cache.put(2, 20)
cache.put(3, 30)
print(cache.get(1))  # 10 (1이 최근 사용으로 이동)
cache.put(4, 40)     # 2가 제거됨 (가장 오래된 미사용)
print(cache.get(2))  # -1 (이미 제거됨)
```

> **실전 팁**: 단순 LRU 캐시는 `functools.lru_cache`를 사용하세요.
> `OrderedDict` 구현은 커스텀 로직(TTL, 캐시 통계 등)이 필요할 때 사용합니다.

---

## 5. `namedtuple` vs `dataclass` 비교표

### 개념

둘 다 필드 이름이 있는 튜플/클래스를 만들지만, 사용 목적과 특성이 다릅니다.
Java의 `record` (Java 16+)와 일반 POJO 클래스의 차이와 유사합니다.

### 비교표

| 특성 | `namedtuple` | `dataclass` |
|---|---|---|
| Java 대응 | `record` (불변 데이터 클래스) | POJO / `@Data` (Lombok) |
| 불변성 | 불변(immutable), 변경 불가 | 기본 가변(mutable), `frozen=True`로 불변 가능 |
| 메모리 | 튜플 기반으로 더 가벼움 | 일반 클래스 |
| 상속 | 튜플 상속 (제한적) | 일반 클래스 상속 가능 |
| 기본값 | Python 3.6.1+ 지원 | 완벽 지원 |
| 메서드 추가 | 가능하나 어색함 | 자연스러움 |
| 타입 힌트 | `NamedTuple` 클래스로 지원 | 기본 지원 |
| JSON 직렬화 | `._asdict()` → dict | `dataclasses.asdict()` |
| 언패킹 | 가능 (`x, y = point`) | 불가 |
| 인덱스 접근 | 가능 (`point[0]`) | 불가 |
| `__slots__` | 자동 | `slots=True` (Python 3.10+) |

### 언제 무엇을 쓸지 가이드

**`namedtuple` 사용 권장 상황**

```python
from collections import namedtuple
from typing import NamedTuple

# 1. 간단한 불변 데이터 + 언패킹이 필요할 때
Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)
x, y = p        # 언패킹 가능
print(p[0])     # 인덱스 접근 가능

# 2. 타입 힌트 포함 (NamedTuple 클래스 문법 권장)
class Coordinate(NamedTuple):
    latitude:  float
    longitude: float
    altitude:  float = 0.0  # 기본값

seoul = Coordinate(37.5665, 126.9780)
print(seoul._asdict())  # {'latitude': 37.5665, 'longitude': 126.978, 'altitude': 0.0}

# 3. 함수 반환값으로 여러 값을 구조화할 때
def get_statistics(data: list) -> NamedTuple:
    class Stats(NamedTuple):
        mean: float
        std:  float
        min:  float
        max:  float

    return Stats(
        mean=sum(data) / len(data),
        std=0.0,  # 실제 계산 생략
        min=min(data),
        max=max(data),
    )

stats = get_statistics([1, 2, 3, 4, 5])
print(stats.mean)  # 3.0
```

**`dataclass` 사용 권장 상황**

```python
from dataclasses import dataclass, field
from datetime import datetime

# 1. 가변 상태가 필요하거나 메서드가 있을 때
@dataclass
class ShoppingCart:
    user_id: int
    items: list = field(default_factory=list)  # 가변 기본값은 반드시 field() 사용
    created_at: datetime = field(default_factory=datetime.now)

    def add_item(self, item: dict) -> None:
        self.items.append(item)

    @property
    def total(self) -> float:
        return sum(item["price"] for item in self.items)

cart = ShoppingCart(user_id=1)
cart.add_item({"name": "apple", "price": 1.5})
print(cart.total)  # 1.5

# 2. 상속이 필요할 때
@dataclass
class BaseEvent:
    event_id: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class UserLoginEvent(BaseEvent):
    user_id: int = 0
    ip_address: str = ""

# 3. 불변성이 필요할 때 (Java record 와 동일)
@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "KRW"

    def __add__(self, other: "Money") -> "Money":
        assert self.currency == other.currency
        return Money(self.amount + other.amount, self.currency)

price = Money(10000)
tax   = Money(1000)
total = price + tax
print(total)  # Money(amount=11000, currency='KRW')
```

---

## 6. `ChainMap` - 여러 딕셔너리를 하나처럼

### 개념

여러 딕셔너리를 실제로 병합(복사)하지 않고 하나처럼 조회할 수 있게 합니다.
첫 번째 딕셔너리부터 순서대로 키를 탐색하며, 쓰기 연산은 항상 첫 번째 딕셔너리에만 적용됩니다.
Java의 `Properties` 파일 계층 구조나 Spring의 `Environment` 추상화와 유사합니다.

### 기본 사용법

```python
from collections import ChainMap

# 세 딕셔너리를 하나처럼 조회
defaults  = {"color": "blue",  "size": "medium", "debug": False}
user_pref = {"color": "green",                   "debug": True}
cli_args  = {"size":  "large"}

# 우선순위: cli_args > user_pref > defaults
config = ChainMap(cli_args, user_pref, defaults)

print(config["color"])  # "green"  ← user_pref 에서
print(config["size"])   # "large"  ← cli_args 에서
print(config["debug"])  # True     ← user_pref 에서

# 쓰기는 항상 첫 번째 맵(cli_args)에만 적용
config["font"] = "monospace"
print(cli_args)   # {"size": "large", "font": "monospace"}
print(defaults)   # {"color": "blue", "size": "medium", "debug": False} ← 변경 없음
```

### 설정 오버라이드 패턴 (환경별 설정)

Spring의 `application.yml` → `application-prod.yml` 계층 구조와 동일한 패턴입니다.

```python
from collections import ChainMap
import os

def load_config(env: str = "development") -> ChainMap:
    """
    우선순위 (높음 → 낮음):
    1. 환경 변수 (os.environ)
    2. 환경별 설정 (prod/dev/test)
    3. 기본 설정 (defaults)
    """
    # 기본 설정 (application.yml 해당)
    defaults = {
        "db_host":    "localhost",
        "db_port":    5432,
        "db_name":    "myapp",
        "log_level":  "INFO",
        "cache_ttl":  300,
    }

    # 환경별 설정 (application-{env}.yml 해당)
    env_configs = {
        "development": {
            "db_name":   "myapp_dev",
            "log_level": "DEBUG",
        },
        "production": {
            "db_host":   "prod-db.internal",
            "db_name":   "myapp_prod",
            "log_level": "WARNING",
            "cache_ttl": 3600,
        },
        "test": {
            "db_name":   "myapp_test",
            "log_level": "DEBUG",
            "cache_ttl": 0,
        },
    }

    env_config = env_configs.get(env, {})

    # 환경 변수 (가장 높은 우선순위)
    # DB_HOST, DB_PORT 등 환경 변수가 있으면 모든 설정을 오버라이드
    env_overrides = {
        k.lower(): v
        for k, v in os.environ.items()
        if k.startswith("APP_")  # APP_ 접두사로 필터링
    }

    return ChainMap(env_overrides, env_config, defaults)

# 사용
dev_config  = load_config("development")
prod_config = load_config("production")

print(dev_config["db_host"])   # "localhost" (defaults 에서)
print(dev_config["log_level"]) # "DEBUG"    (env_config 에서)

print(prod_config["db_host"])  # "prod-db.internal" (env_config 에서)
print(prod_config["cache_ttl"])# 3600               (env_config 에서)
```

### 스코프 체인 구현

Python 인터프리터 내부적으로도 지역/전역/내장 스코프를 ChainMap과 유사하게 관리합니다.

```python
from collections import ChainMap

# 변수 스코프 시뮬레이션
builtin_scope = {"print": print, "len": len, "range": range}
global_scope  = {"PI": 3.14159, "APP_NAME": "MyApp"}
local_scope   = {}

scope_chain = ChainMap(local_scope, global_scope, builtin_scope)

# 로컬 변수 할당 (local_scope 에만 추가됨)
scope_chain["x"] = 10
scope_chain["PI"] = 3.0  # 로컬에서 전역 PI 를 가림

print(scope_chain["x"])       # 10   (local_scope 에서)
print(scope_chain["PI"])      # 3.0  (local_scope 에서, global 의 3.14159 가 가려짐)
print(scope_chain["APP_NAME"])# "MyApp" (global_scope 에서)

# 부모 맵 접근 (로컬 스코프 없이 전역만)
parent_view = scope_chain.parents
print(parent_view["PI"])      # 3.14159 (global_scope 의 원본)

# 새 스코프 생성 (중첩 함수 진입)
inner_scope = scope_chain.new_child({"y": 20})
print(inner_scope["x"])       # 10 (부모 스코프에서 상속)
print(inner_scope["y"])       # 20 (현재 스코프)
```

---

## 요약 비교표

| collections | 대응 Java 클래스/기능 | 핵심 용도 |
|---|---|---|
| `defaultdict` | `computeIfAbsent()`, `HashMap.getOrDefault()` | 없는 키 자동 초기화 |
| `Counter` | `Map<T, Long>` + `Collectors.counting()` | 빈도 계산, 집합 연산 |
| `deque` | `ArrayDeque` | O(1) 양방향 삽입/삭제, 슬라이딩 윈도우 |
| `OrderedDict` | `LinkedHashMap(accessOrder=true)` | 삽입 순서 보장 + `move_to_end()` |
| `namedtuple` | `record` (Java 16+) | 불변 경량 데이터 구조 |
| `dataclass` | Lombok `@Data`, POJO | 가변/불변 데이터 클래스 |
| `ChainMap` | Spring `Environment` 계층 | 다중 딕셔너리 우선순위 조회 |
