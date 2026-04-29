# itertools - 반복자 도구

> 공식 문서: https://docs.python.org/3/library/itertools.html

Java의 Stream API처럼 Python은 `itertools` 모듈로 고성능 반복자 도구를 제공합니다.
핵심 차이점: `itertools`의 모든 함수는 **lazy evaluation** (지연 평가)으로 동작합니다.
즉, 값을 실제로 소비하기 전까지는 메모리에 데이터를 올리지 않습니다.

```python
import itertools
```

---

## 1. 무한 반복자 (Infinite Iterators)

무한 반복자는 명시적으로 멈추지 않으면 영원히 값을 생성합니다.
반드시 `islice`, `takewhile`, 또는 `break`와 함께 사용해야 합니다.

### `count(start=0, step=1)` - 무한 카운터

Java의 `IntStream.iterate()`와 가장 유사합니다.

```java
// Java
IntStream.iterate(10, n -> n + 2)
         .limit(5)
         .forEach(System.out::println);
// 10, 12, 14, 16, 18
```

```python
# Python
import itertools

# count(start, step) - 무한히 증가하는 숫자 생성
counter = itertools.count(10, 2)

# islice로 5개만 추출
for n in itertools.islice(counter, 5):
    print(n)
# 10, 12, 14, 16, 18

# 실전 예: 고유 ID 생성기
id_generator = itertools.count(1)
user_id = next(id_generator)  # 1
order_id = next(id_generator)  # 2
```

### `cycle(iterable)` - 순환 반복

시퀀스가 끝나면 처음부터 다시 반복합니다.

```java
// Java - 직접 구현 필요
List<String> colors = List.of("Red", "Green", "Blue");
int index = 0;
for (int i = 0; i < 7; i++) {
    System.out.println(colors.get(index % colors.size()));
    index++;
}
```

```python
# Python
import itertools

colors = ["Red", "Green", "Blue"]
cycler = itertools.cycle(colors)

# 7개만 추출
for color in itertools.islice(cycler, 7):
    print(color)
# Red, Green, Blue, Red, Green, Blue, Red

# 실전 예: 라운드 로빈 로드 밸런서
servers = ["server-1", "server-2", "server-3"]
load_balancer = itertools.cycle(servers)

for request_id in range(9):
    server = next(load_balancer)
    print(f"Request {request_id} -> {server}")
```

### `repeat(object, times=None)` - 동일 값 반복

Java의 `Collections.nCopies()`와 유사합니다.

```java
// Java
Collections.nCopies(3, "hello")
// ["hello", "hello", "hello"]
```

```python
# Python
import itertools

# 유한 반복
list(itertools.repeat("hello", 3))
# ['hello', 'hello', 'hello']

# 무한 반복 (map과 함께 자주 사용)
# map()의 두 번째 인자로 고정값을 넘길 때 유용
result = list(map(pow, range(5), itertools.repeat(2)))
# [0, 1, 4, 9, 16]  -> 각 요소의 제곱

# Java: IntStream.range(0, 5).map(n -> (int) Math.pow(n, 2))
```

---

## 2. 유한 반복자 (Finite Iterators)

### `chain(*iterables)` - 여러 이터러블 연결

Java의 `Stream.concat()`처럼 여러 시퀀스를 하나로 연결합니다.

```java
// Java
Stream.concat(
    Stream.of(1, 2, 3),
    Stream.of(4, 5, 6)
).forEach(System.out::println);

// 여러 스트림: Stream.of(s1, s2, s3).flatMap(s -> s)
```

```python
# Python
import itertools

# 두 리스트 연결
result = list(itertools.chain([1, 2, 3], [4, 5, 6]))
# [1, 2, 3, 4, 5, 6]

# 여러 컬렉션 연결
list_a = [1, 2]
list_b = [3, 4]
list_c = [5, 6]
result = list(itertools.chain(list_a, list_b, list_c))
# [1, 2, 3, 4, 5, 6]

# chain.from_iterable: 중첩 리스트 평탄화 (flatten)
nested = [[1, 2], [3, 4], [5, 6]]
flat = list(itertools.chain.from_iterable(nested))
# [1, 2, 3, 4, 5, 6]

# Java: nestedList.stream().flatMap(Collection::stream)
```

### `islice(iterable, stop)` / `islice(iterable, start, stop, step)` - 슬라이싱

Java의 `Stream.limit()`, `Stream.skip()`과 유사합니다.

```java
// Java
stream.skip(2).limit(3)
```

```python
# Python
import itertools

data = range(10)  # 0~9

# 앞에서 5개
list(itertools.islice(data, 5))
# [0, 1, 2, 3, 4]

# 2번 인덱스부터 7번 인덱스 전까지
list(itertools.islice(data, 2, 7))
# [2, 3, 4, 5, 6]

# 2번부터 2개씩 건너뛰며
list(itertools.islice(data, 0, 10, 2))
# [0, 2, 4, 6, 8]

# 핵심: 일반 슬라이싱 [start:stop:step]은 시퀀스에만 사용 가능
# islice는 generator 같은 이터레이터에도 사용 가능
def infinite_generator():
    n = 0
    while True:
        yield n
        n += 1

first_5 = list(itertools.islice(infinite_generator(), 5))
# [0, 1, 2, 3, 4]
```

### `filterfalse(predicate, iterable)` - 조건 반전 필터

`filter()`의 반대: 조건이 `False`인 요소만 반환합니다.

```java
// Java
stream.filter(n -> !(n % 2 == 0))  // 홀수만
// = stream.filter(n -> n % 2 != 0)
```

```python
# Python
import itertools

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# filter: 조건이 True인 요소 -> 짝수만
even = list(filter(lambda n: n % 2 == 0, numbers))
# [2, 4, 6, 8, 10]

# filterfalse: 조건이 False인 요소 -> 홀수만 (짝수가 아닌 것)
odd = list(itertools.filterfalse(lambda n: n % 2 == 0, numbers))
# [1, 3, 5, 7, 9]

# 실전 예: 유효하지 않은 항목 걸러내기
def is_valid(item):
    return item is not None and item != ""

data = ["hello", None, "world", "", "python"]
invalid_items = list(itertools.filterfalse(is_valid, data))
# [None, '']
```

### `takewhile(predicate, iterable)` - 조건이 True인 동안 계속

Java 9+의 `Stream.takeWhile()`과 동일합니다.

```java
// Java 9+
Stream.of(1, 2, 3, 4, 5, 1, 2)
      .takeWhile(n -> n < 4)
      .collect(Collectors.toList());
// [1, 2, 3]
```

```python
# Python
import itertools

numbers = [1, 2, 3, 4, 5, 1, 2]

# 4보다 작은 동안만 반환, 조건이 False가 되면 즉시 중단
result = list(itertools.takewhile(lambda n: n < 4, numbers))
# [1, 2, 3]  <- 4가 나오면 뒤의 1, 2도 포함되지 않음

# 실전 예: 로그 파일에서 특정 이벤트까지만 읽기
log_lines = [
    "INFO: start",
    "INFO: processing",
    "ERROR: something failed",
    "INFO: more processing",  # 이 줄부터는 읽지 않음
]

pre_error = list(itertools.takewhile(
    lambda line: not line.startswith("ERROR"),
    log_lines
))
# ['INFO: start', 'INFO: processing']
```

### `dropwhile(predicate, iterable)` - 조건이 True인 동안 건너뜀

Java 9+의 `Stream.dropWhile()`과 동일합니다.

```java
// Java 9+
Stream.of(1, 2, 3, 4, 5, 1, 2)
      .dropWhile(n -> n < 4)
      .collect(Collectors.toList());
// [4, 5, 1, 2]
```

```python
# Python
import itertools

numbers = [1, 2, 3, 4, 5, 1, 2]

# 4보다 작은 동안 건너뛰고, 조건이 False가 된 이후부터 반환
result = list(itertools.dropwhile(lambda n: n < 4, numbers))
# [4, 5, 1, 2]  <- 조건이 False가 된 4부터 끝까지

# 실전 예: 헤더 건너뛰고 데이터만 읽기
file_lines = [
    "# Comment line",
    "# Another comment",
    "data1,value1",
    "data2,value2",
]

data_lines = list(itertools.dropwhile(
    lambda line: line.startswith("#"),
    file_lines
))
# ['data1,value1', 'data2,value2']
```

### `zip_longest(*iterables, fillvalue=None)` - 길이가 다른 zip

Python 내장 `zip()`은 가장 짧은 이터러블 기준으로 멈추지만,
`zip_longest`는 가장 긴 것 기준으로 진행하고 짧은 쪽은 `fillvalue`로 채웁니다.

```java
// Java - 직접 구현 필요 (표준 라이브러리에 zip_longest 없음)
// Apache Commons Lang: IterableUtils.zippingIterable()
```

```python
# Python
import itertools

a = [1, 2, 3]
b = ["a", "b"]

# 기본 zip: 짧은 쪽 기준 (b가 더 짧으므로 2개만)
list(zip(a, b))
# [(1, 'a'), (2, 'b')]

# zip_longest: 긴 쪽 기준, 짧은 쪽은 fillvalue로 채움
list(itertools.zip_longest(a, b, fillvalue=0))
# [(1, 'a'), (2, 'b'), (3, 0)]

# 실전 예: 두 시계열 데이터 비교
dates = ["2024-01", "2024-02", "2024-03"]
sales = [100, 150]  # 데이터가 덜 들어온 경우

for date, sale in itertools.zip_longest(dates, sales, fillvalue="N/A"):
    print(f"{date}: {sale}")
# 2024-01: 100
# 2024-02: 150
# 2024-03: N/A
```

### `groupby(iterable, key=None)` - 연속된 요소 그룹화

Java의 `Collectors.groupingBy()`와 유사하지만 **중요한 차이**가 있습니다.
`groupby`는 연속된 동일한 key를 가진 요소만 묶습니다.
**반드시 먼저 정렬해야** 예상대로 동작합니다.

```java
// Java: 한 번에 모든 그룹을 Map으로 수집
Map<String, List<Person>> byDept = persons.stream()
    .collect(Collectors.groupingBy(Person::getDepartment));
```

```python
# Python
import itertools

data = [
    {"name": "Alice", "dept": "Engineering"},
    {"name": "Bob",   "dept": "Engineering"},
    {"name": "Carol", "dept": "Marketing"},
    {"name": "Dave",  "dept": "Engineering"},  # 주의: 다시 Engineering
]

# 정렬 없이 사용하면 연속된 Engineering 두 개만 묶임
for key, group in itertools.groupby(data, key=lambda x: x["dept"]):
    members = [item["name"] for item in group]
    print(f"{key}: {members}")
# Engineering: ['Alice', 'Bob']
# Marketing: ['Carol']
# Engineering: ['Dave']   <- Dave가 별도 그룹!

print("--- 정렬 후 ---")

# 반드시 key 기준으로 정렬 먼저!
sorted_data = sorted(data, key=lambda x: x["dept"])
for key, group in itertools.groupby(sorted_data, key=lambda x: x["dept"]):
    members = [item["name"] for item in group]
    print(f"{key}: {members}")
# Engineering: ['Alice', 'Bob', 'Dave']
# Marketing: ['Carol']

# Java처럼 dict로 수집하려면
from collections import defaultdict
result = defaultdict(list)
for key, group in itertools.groupby(sorted_data, key=lambda x: x["dept"]):
    result[key].extend(group)
```

---

## 3. 조합 반복자 (Combinatoric Iterators)

### `product(*iterables, repeat=1)` - 데카르트 곱 (중첩 for문 대체)

중첩된 for 루프를 하나의 표현식으로 대체합니다.

```java
// Java: 3중 for문
for (String color : colors) {
    for (int size : sizes) {
        for (String material : materials) {
            System.out.println(color + "-" + size + "-" + material);
        }
    }
}
```

```python
# Python
import itertools

colors = ["Red", "Blue"]
sizes = ["S", "M", "L"]

# 2중 for문 대체
for color, size in itertools.product(colors, sizes):
    print(f"{color}-{size}")
# Red-S, Red-M, Red-L, Blue-S, Blue-M, Blue-L

# repeat 파라미터: 같은 이터러블을 반복
# 주사위 2개를 던지는 모든 경우의 수
dice = range(1, 7)
all_rolls = list(itertools.product(dice, repeat=2))
# [(1,1), (1,2), ..., (6,6)] -> 36가지

# 실전 예: 하이퍼파라미터 튜닝 그리드 서치
learning_rates = [0.001, 0.01, 0.1]
batch_sizes = [32, 64, 128]
epochs = [10, 50]

configs = list(itertools.product(learning_rates, batch_sizes, epochs))
print(f"총 {len(configs)}개 설정 조합")  # 18개
for lr, bs, ep in configs:
    print(f"lr={lr}, batch={bs}, epochs={ep}")
```

### `permutations(iterable, r=None)` - 순열

순서가 중요한 모든 배열을 생성합니다.

```python
# Python
import itertools

items = ["A", "B", "C"]

# 3개 중 2개를 선택하는 순열 (순서 있음)
result = list(itertools.permutations(items, 2))
# [('A','B'), ('A','C'), ('B','A'), ('B','C'), ('C','A'), ('C','B')]
print(f"P(3,2) = {len(result)}개")  # 6개

# 모든 순열 (r 생략 시 전체 길이)
all_perms = list(itertools.permutations(items))
print(f"P(3,3) = {len(all_perms)}개")  # 6개 = 3!

# 실전 예: 작업 스케줄링 - 모든 실행 순서 탐색
tasks = ["download", "process", "upload"]
for order in itertools.permutations(tasks):
    print(" -> ".join(order))
```

### `combinations(iterable, r)` - 조합

순서가 없는 모든 조합을 생성합니다. 같은 요소를 중복 사용하지 않습니다.

```python
# Python
import itertools

items = ["A", "B", "C", "D"]

# 4개 중 2개를 선택하는 조합 (순서 없음)
result = list(itertools.combinations(items, 2))
# [('A','B'), ('A','C'), ('A','D'), ('B','C'), ('B','D'), ('C','D')]
print(f"C(4,2) = {len(result)}개")  # 6개

# 실전 예: A/B 테스트 그룹 구성
features = ["feature_A", "feature_B", "feature_C", "feature_D"]
# 2개씩 묶어서 테스트할 모든 조합
for combo in itertools.combinations(features, 2):
    print(f"Test group: {combo}")

# 실전 예: 모든 고객 쌍의 유사도 계산
customers = ["user1", "user2", "user3"]
for customer_a, customer_b in itertools.combinations(customers, 2):
    # calculate_similarity(customer_a, customer_b)
    print(f"Similarity between {customer_a} and {customer_b}")
```

### `combinations_with_replacement(iterable, r)` - 중복 조합

같은 요소를 여러 번 사용할 수 있는 조합입니다.

```python
# Python
import itertools

items = ["A", "B", "C"]

# 중복 허용 조합
result = list(itertools.combinations_with_replacement(items, 2))
# [('A','A'), ('A','B'), ('A','C'), ('B','B'), ('B','C'), ('C','C')]
print(f"H(3,2) = {len(result)}개")  # 6개

# combinations와 비교
print("combinations:")
print(list(itertools.combinations(items, 2)))
# [('A','B'), ('A','C'), ('B','C')] -> 3개 (중복 없음)

print("combinations_with_replacement:")
print(list(itertools.combinations_with_replacement(items, 2)))
# [('A','A'), ('A','B'), ('A','C'), ('B','B'), ('B','C'), ('C','C')] -> 6개
```

---

## 4. 실전 패턴

### 배치 처리 (N개씩 묶기)

대용량 데이터를 N개씩 나눠 처리할 때 자주 사용하는 패턴입니다.

```java
// Java: Guava의 Iterables.partition() 또는 직접 구현
List<List<Integer>> batches = Lists.partition(data, batchSize);
batches.forEach(batch -> processBatch(batch));
```

```python
# Python 3.12+: itertools.batched() 사용 가능
import itertools

data = list(range(10))  # [0, 1, 2, ..., 9]

# Python 3.12+
# for batch in itertools.batched(data, 3):
#     print(list(batch))

# Python 3.11 이하 - 직접 구현
def batched(iterable, n):
    """이터러블을 n개씩 묶어 반환하는 제너레이터"""
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, n))
        if not batch:
            break
        yield batch

for batch in batched(data, 3):
    print(batch)
# [0, 1, 2]
# [3, 4, 5]
# [6, 7, 8]
# [9]

# 실전 예: DB 벌크 인서트
users = list(range(1000))  # 1000명의 user_id

for batch in batched(users, 100):
    # db.bulk_insert(batch)  # 100개씩 INSERT
    print(f"Inserting {len(batch)} users...")
```

### 슬라이딩 윈도우 (Sliding Window)

연속된 N개의 요소를 윈도우 형태로 순회합니다.

```java
// Java - 직접 구현 필요
// Stream.iterate()와 limit() 조합으로 구현
```

```python
# Python 3.10+: itertools.pairwise() (윈도우 크기 2)
import itertools
from collections import deque

data = [1, 2, 3, 4, 5, 6]

# Python 3.10+: 연속된 두 요소 쌍
pairs = list(itertools.pairwise(data))
# [(1,2), (2,3), (3,4), (4,5), (5,6)]

# 일반적인 sliding window (크기 r)
def sliding_window(iterable, n):
    """크기 n의 슬라이딩 윈도우"""
    it = iter(iterable)
    window = deque(itertools.islice(it, n), maxlen=n)
    if len(window) == n:
        yield tuple(window)
    for item in it:
        window.append(item)
        yield tuple(window)

data = [1, 2, 3, 4, 5, 6]
for window in sliding_window(data, 3):
    print(window)
# (1, 2, 3)
# (2, 3, 4)
# (3, 4, 5)
# (4, 5, 6)

# 실전 예: 이동 평균 계산
prices = [10, 12, 11, 14, 13, 15, 16]
window_size = 3

moving_averages = [
    sum(window) / window_size
    for window in sliding_window(prices, window_size)
]
print(moving_averages)
# [11.0, 12.33, 12.67, 14.0, 14.67]
```

---

## Java vs Python 핵심 비교표

| Java Stream API | Python itertools | 비고 |
|---|---|---|
| `IntStream.iterate(n, f)` | `count(n, step)` | Python은 단순 증가만 |
| `Stream.concat(a, b)` | `chain(a, b)` | Python은 n개 연결 가능 |
| `stream.limit(n)` | `islice(it, n)` | |
| `stream.skip(n)` | `islice(it, n, None)` | |
| `stream.filter(pred.negate())` | `filterfalse(pred, it)` | |
| `stream.takeWhile(pred)` | `takewhile(pred, it)` | |
| `stream.dropWhile(pred)` | `dropwhile(pred, it)` | |
| `Collectors.groupingBy(f)` | `groupby(it, key=f)` | **정렬 필수** |
| `Lists.partition(list, n)` | `batched(it, n)` | Python 3.12+ |
| 없음 | `product(*its)` | 중첩 for문 대체 |
| 없음 | `permutations(it, r)` | 수학적 순열 |
| 없음 | `combinations(it, r)` | 수학적 조합 |

> **핵심 주의사항**: `groupby()`는 Java `Collectors.groupingBy()`와 달리 연속된 요소만 그룹화합니다. 반드시 key 기준 정렬 후 사용하세요.
