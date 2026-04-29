# Python 기초 튜토리얼 - Java/Spring Boot 개발자를 위한 가이드

> Java/Spring Boot 경력 20년 개발자가 Python을 처음 배우는 상황을 위한 실용적인 가이드입니다.
> Java 코드와 Python 코드를 나란히 비교하며 설명합니다.

---

## 목차

1. [Python 기본 문법](#1-python-기본-문법)
   - 1.1 [변수와 타입](#11-변수와-타입)
   - 1.2 [문자열](#12-문자열)
   - 1.3 [조건문과 반복문](#13-조건문과-반복문)
   - 1.4 [컬렉션 자료구조](#14-컬렉션-자료구조)
   - 1.5 [함수 정의](#15-함수-정의)
   - 1.6 [클래스](#16-클래스)
   - 1.7 [모듈과 패키지](#17-모듈과-패키지)
   - 1.8 [예외 처리](#18-예외-처리)
   - 1.9 [컨텍스트 매니저](#19-컨텍스트-매니저)
   - 1.10 [타입 힌트](#110-타입-힌트)
   - 1.11 [데코레이터](#111-데코레이터)
   - 1.12 [제너레이터](#112-제너레이터)
   - 1.13 [비동기 프로그래밍](#113-비동기-프로그래밍)
2. [pyproject.toml - 프로젝트 설정 파일](#2-pyprojecttoml---프로젝트-설정-파일)
   - 2.1 [Maven/Gradle과의 비교](#21-mavengradle과의-비교)
   - 2.2 [pyenv - Python 버전 관리](#22-pyenv---python-버전-관리)
   - 2.3 [pyenv + uv 함께 사용하기](#23-pyenv--uv-함께-사용하기)
   - 2.4 [uv 패키지 매니저](#24-uv-패키지-매니저)
   - 2.5 [pyproject.toml 전체 예시](#25-pyprojecttoml-전체-예시)
   - 2.6 [프로젝트 디렉토리 구조 (Maven과 비교)](#26-프로젝트-디렉토리-구조-maven과-비교)
3. [pytest - 테스트 프레임워크](#3-pytest---테스트-프레임워크)
   - 3.1 [JUnit과 pytest 비교](#31-junit과-pytest-비교)
   - 3.2 [기본 테스트 작성](#32-기본-테스트-작성)
   - 3.3 [Fixture - @BeforeEach, @AfterEach 대응](#33-fixture---beforeeach-aftereach-대응)
   - 3.4 [conftest.py - 전역 Fixture](#34-conftestpy---전역-fixture)
   - 3.5 [pytest.mark - 어노테이션](#35-pytestmark---어노테이션)
   - 3.6 [파라미터화 테스트](#36-파라미터화-테스트)
   - 3.7 [모킹 (Mocking)](#37-모킹-mocking)
   - 3.8 [pytest-asyncio - 비동기 테스트](#38-pytest-asyncio---비동기-테스트)
   - 3.9 [pytest 실행 명령어](#39-pytest-실행-명령어)
4. [Java 개발자가 주의할 Python 특징](#4-java-개발자가-주의할-python-특징)

---

## 1. Python 기본 문법

### 1.1 변수와 타입

#### 1) Java: 강타입 (Statically Typed)

Java는 컴파일 타임에 타입이 결정되며, 변수 선언 시 반드시 타입을 명시해야 합니다.

```java
// Java - 타입을 반드시 명시
int age = 30;
String name = "Alice";
double salary = 95000.50;
boolean isActive = true;

// Java 10+: var 키워드로 타입 추론 가능 (하지만 컴파일 타임에 고정됨)
var count = 10;  // int로 추론, 이후 String 대입 불가

// 타입 변환은 명시적으로
String ageStr = String.valueOf(age);
int parsed = Integer.parseInt("42");
```

#### 2) Python: 동적 타입 (Dynamically Typed)

Python은 런타임에 타입이 결정되며, 변수에 어떤 값이든 재할당할 수 있습니다.

```python
# Python - 타입 명시 없이 바로 대입
age = 30
name = "Alice"
salary = 95000.50
is_active = True

# 같은 변수에 다른 타입 재할당 가능 (권장하지 않음)
count = 10
count = "hello"  # 문자열로 바꿔도 오류 없음

# 타입 변환
age_str = str(age)       # String.valueOf(age)
parsed = int("42")       # Integer.parseInt("42")
parsed_f = float("3.14") # Double.parseDouble("3.14")
```

#### 3) 타입 확인

```python
# Python에서 타입 확인
print(type(age))        # <class 'int'>
print(type(name))       # <class 'str'>
print(isinstance(age, int))   # True  (Java의 instanceof)
print(isinstance(name, str))  # True

# 기본 타입들
x = 42          # int
y = 3.14        # float
z = 3 + 4j      # complex (Java에는 없음)
b = True        # bool (True/False, 대문자!)
n = None        # null에 해당
```

#### 4) Type Hints (타입 힌트) - Python 3.5+

Python도 타입 힌트를 사용하면 Java처럼 명시적 타입 표기가 가능합니다. 단, 런타임 강제는 아니며 IDE와 mypy 같은 정적 분석 도구에서 활용됩니다.

```python
# 타입 힌트 사용 (Java 스타일에 익숙한 개발자에게 권장)
age: int = 30
name: str = "Alice"
salary: float = 95000.50
is_active: bool = True
items: list[str] = ["a", "b", "c"]
mapping: dict[str, int] = {"a": 1, "b": 2}
```

---

### 1.2 문자열

#### 1) Java의 문자열 포매팅

```java
// Java - String.format
String name = "Alice";
int age = 30;
String msg1 = String.format("이름: %s, 나이: %d", name, age);

// Java 15+: Text Block
String json = """
    {
        "name": "%s",
        "age": %d
    }
    """.formatted(name, age);
```

#### 2) Python의 f-string

Python의 f-string은 Java의 `String.format`보다 훨씬 간결하고 직관적입니다.

```python
name = "Alice"
age = 30
salary = 95000.50

# f-string (Python 3.6+) - 가장 권장
msg1 = f"이름: {name}, 나이: {age}"
msg2 = f"연봉: {salary:,.2f}원"  # 천 단위 구분자, 소수점 2자리

# 표현식도 직접 사용 가능
msg3 = f"10년 후 나이: {age + 10}"
msg4 = f"대문자: {name.upper()}"

# 멀티라인 문자열 (Java의 Text Block과 동일)
json_str = f"""
{{
    "name": "{name}",
    "age": {age}
}}
"""

# 구식 방법들 (레거시 코드에서 볼 수 있음)
msg_old1 = "이름: %s, 나이: %d" % (name, age)  # C 스타일
msg_old2 = "이름: {}, 나이: {}".format(name, age)  # format 메서드

# 문자열 메서드 (Java String 메서드와 비교)
s = "  Hello, World!  "
print(s.strip())          # trim()
print(s.lower())          # toLowerCase()
print(s.upper())          # toUpperCase()
print(s.replace("Hello", "Hi"))  # replace()
print(s.split(","))       # split()
print("Hello" in s)       # contains()
print(s.startswith("  Hello"))   # startsWith()
print(len(s))             # length() - 함수 호출 방식!
```

---

### 1.3 조건문과 반복문

#### 1) 조건문

```java
// Java
int score = 85;
if (score >= 90) {
    System.out.println("A");
} else if (score >= 80) {
    System.out.println("B");
} else {
    System.out.println("C");
}

// 삼항 연산자
String grade = score >= 90 ? "Pass" : "Fail";
```

```python
# Python - 중괄호 대신 들여쓰기!
score = 85
if score >= 90:
    print("A")
elif score >= 80:   # else if 가 아니라 elif
    print("B")
else:
    print("C")

# 삼항 표현식 (Java 삼항과 순서가 다름!)
grade = "Pass" if score >= 90 else "Fail"
# Java:  조건 ? true값 : false값
# Python: true값 if 조건 else false값

# match-case (Python 3.10+) - Java의 switch와 유사
command = "quit"
match command:
    case "quit":
        print("종료")
    case "help":
        print("도움말")
    case _:            # default
        print("알 수 없는 명령")
```

#### 2) for 반복문

```java
// Java
// 인덱스 기반
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}

// enhanced for
List<String> names = List.of("Alice", "Bob", "Charlie");
for (String name : names) {
    System.out.println(name);
}

// 인덱스와 값 동시 - Stream으로 번거롭게
IntStream.range(0, names.size())
    .forEach(i -> System.out.println(i + ": " + names.get(i)));
```

```python
# Python

# range() - Java의 for(int i=0; i<5; i++)
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 8):       # 2, 3, 4, 5, 6, 7
    print(i)

for i in range(0, 10, 2):   # 0, 2, 4, 6, 8 (step=2)
    print(i)

# enhanced for - Java의 for-each
names = ["Alice", "Bob", "Charlie"]
for name in names:
    print(name)

# enumerate() - 인덱스와 값 동시 (Java Stream보다 훨씬 간결)
for i, name in enumerate(names):
    print(f"{i}: {name}")

for i, name in enumerate(names, start=1):  # 1부터 시작
    print(f"{i}: {name}")

# zip() - 두 리스트를 동시에 순회
scores = [95, 87, 92]
for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

#### 3) while 반복문

```python
# Python while
count = 0
while count < 5:
    print(count)
    count += 1   # count++는 없음! ++ 연산자 없음

# break, continue - Java와 동일
for i in range(10):
    if i == 3:
        continue    # 건너뜀
    if i == 7:
        break       # 종료
    print(i)
```

#### 4) List Comprehension (리스트 컴프리헨션)

Java 개발자에게는 생소하지만, Python에서 가장 자주 쓰는 패턴 중 하나입니다.

```java
// Java Stream (비교용)
List<String> names = List.of("alice", "bob", "charlie");

// 필터링 + 변환
List<String> result = names.stream()
    .filter(n -> n.length() > 3)
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```

```python
# Python List Comprehension
names = ["alice", "bob", "charlie"]

# 기본 변환 - map
upper_names = [name.upper() for name in names]

# 필터링 - filter
long_names = [name for name in names if len(name) > 3]

# 필터링 + 변환 - filter + map
result = [name.upper() for name in names if len(name) > 3]

# 중첩 루프
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 딕셔너리 컴프리헨션
word_lengths = {word: len(word) for word in names}
# {"alice": 5, "bob": 3, "charlie": 7}

# 셋 컴프리헨션
unique_lengths = {len(word) for word in names}
# {3, 5, 7}
```

---

### 1.4 컬렉션 자료구조

#### 1) List (리스트) - Java의 ArrayList

```java
// Java
List<String> fruits = new ArrayList<>(Arrays.asList("apple", "banana", "cherry"));
fruits.add("date");
fruits.remove("banana");
System.out.println(fruits.get(0));  // "apple"
System.out.println(fruits.size());  // 3
fruits.sort(Comparator.naturalOrder());
```

```python
# Python - List
fruits = ["apple", "banana", "cherry"]
fruits.append("date")          # add()
fruits.remove("banana")        # remove()
print(fruits[0])               # get(0) - 인덱스로 직접 접근
print(len(fruits))             # size() - 함수 호출
fruits.sort()                  # sort()
fruits.sort(reverse=True)      # 역순 정렬

# Python 특유의 슬라이싱 (Java에는 없음)
print(fruits[1:3])    # 인덱스 1~2 (3 미포함)
print(fruits[-1])     # 마지막 요소
print(fruits[::-1])   # 전체 역순

# 리스트 연산
combined = ["a", "b"] + ["c", "d"]  # 두 리스트 합치기
repeated = [0] * 5                   # [0, 0, 0, 0, 0]

# 리스트 컴프리헨션 (Java Stream의 map/filter를 한 줄로)
squares = [x ** 2 for x in range(1, 6)]          # [1, 4, 9, 16, 25]
evens = [x for x in range(10) if x % 2 == 0]    # [0, 2, 4, 6, 8]
```

```java
// Java Stream 버전 (비교용)
List<Integer> squares = IntStream.rangeClosed(1, 5)
    .map(x -> x * x)
    .boxed()
    .collect(Collectors.toList());
```

#### 2) Dictionary (딕셔너리) - Java의 HashMap

```java
// Java
Map<String, Integer> scores = new HashMap<>();
scores.put("Alice", 95);
scores.put("Bob", 87);
System.out.println(scores.get("Alice"));           // 95
System.out.println(scores.getOrDefault("Charlie", 0)); // 0
scores.containsKey("Bob");  // true
for (Map.Entry<String, Integer> entry : scores.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}
```

```python
# Python - Dictionary
scores = {"Alice": 95, "Bob": 87}
scores["Charlie"] = 100         # put()
print(scores["Alice"])          # get() - 키 없으면 KeyError!
print(scores.get("Dave", 0))    # getOrDefault()
print("Bob" in scores)          # containsKey()
del scores["Bob"]               # remove()

# 순회 방법
for key in scores:              # keySet()
    print(key)

for value in scores.values():   # values()
    print(value)

for key, value in scores.items():  # entrySet()
    print(f"{key}: {value}")

# 딕셔너리 컴프리헨션
squared = {k: v ** 2 for k, v in scores.items()}

# 딕셔너리 병합 (Python 3.9+)
dict1 = {"a": 1}
dict2 = {"b": 2}
merged = dict1 | dict2          # {a: 1, b: 2}
```

#### 3) Tuple (튜플) - 불변 리스트

Java에는 직접적인 대응이 없습니다. `List.of()`와 유사하지만 언패킹 기능이 강력합니다.

```python
# Tuple - 생성 후 변경 불가
point = (10, 20)
# point[0] = 30  # TypeError 발생!

# 언패킹 (구조 분해)
x, y = point
print(f"x={x}, y={y}")

# 함수에서 여러 값 반환할 때 자주 사용
def get_min_max(numbers):
    return min(numbers), max(numbers)  # 튜플 반환

low, high = get_min_max([3, 1, 4, 1, 5, 9])
print(f"최소: {low}, 최대: {high}")

# Named Tuple - Java의 record와 유사
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(x=10, y=20)
print(p.x, p.y)
# p.x = 30  # AttributeError - 불변!

# dataclass - 튜플처럼 구조화된 데이터, 하지만 가변
from dataclasses import dataclass

@dataclass
class PointDC:
    x: int
    y: int

p2 = PointDC(x=10, y=20)
print(p2.x, p2.y)  # 10 20
p2.x = 30          # 가변 - 수정 가능

# frozen=True 로 튜플처럼 불변으로 만들기
@dataclass(frozen=True)
class ImmutablePoint:
    x: int
    y: int

p3 = ImmutablePoint(x=10, y=20)
# p3.x = 30  # FrozenInstanceError - 불변!
print(p3)   # ImmutablePoint(x=10, y=20) - __repr__ 자동 생성
```

#### 4) Set (셋) - Java의 HashSet

```java
// Java
Set<String> tags = new HashSet<>(Arrays.asList("python", "java", "go"));
tags.add("rust");
tags.contains("java");  // true
Set<String> other = new HashSet<>(Arrays.asList("java", "kotlin"));
tags.retainAll(other);  // 교집합
```

```python
# Python - Set
tags = {"python", "java", "go"}
tags.add("rust")
print("java" in tags)     # contains()

other = {"java", "kotlin"}
print(tags & other)        # 교집합 (intersection)
print(tags | other)        # 합집합 (union)
print(tags - other)        # 차집합 (difference)
print(tags ^ other)        # 대칭 차집합
```

---

### 1.5 함수 정의

#### 1) 기본 함수

```java
// Java - 반환 타입과 매개변수 타입 모두 명시 필수
public String greet(String name, int age) {
    return String.format("안녕하세요, %s님! %d살이시군요.", name, age);
}

// void 메서드
public void printInfo(String message) {
    System.out.println(message);
}
```

```python
# Python - def 키워드, 타입 힌트는 선택 사항
def greet(name: str, age: int) -> str:
    return f"안녕하세요, {name}님! {age}살이시군요."

# 반환값 없는 함수 (Java void에 해당, None을 암묵적으로 반환)
def print_info(message: str) -> None:
    print(message)

# 여러 값 반환 (Java는 불가, 튜플로 반환)
def get_stats(numbers: list[int]) -> tuple[int, int, float]:
    return min(numbers), max(numbers), sum(numbers) / len(numbers)

low, high, avg = get_stats([1, 2, 3, 4, 5])
```

#### 2) 기본값 매개변수

```java
// Java - 오버로딩으로 구현
public String connect(String host, int port, boolean ssl) { ... }
public String connect(String host, int port) {
    return connect(host, port, false);
}
public String connect(String host) {
    return connect(host, 3306, false);
}
```

```python
# Python - 기본값 매개변수로 간단하게
def connect(host: str, port: int = 3306, ssl: bool = False) -> str:
    return f"{'ssl://' if ssl else ''}{host}:{port}"

# 호출 방법
connect("localhost")                   # host="localhost", port=3306, ssl=False
connect("localhost", 5432)             # port만 변경
connect("localhost", ssl=True)         # ssl만 변경 (키워드 인수)
connect(host="db.example.com", port=5432, ssl=True)  # 전체 명시
```

#### 3) *args와 **kwargs

```java
// Java - 가변 인수
public int sum(int... numbers) {
    int total = 0;
    for (int n : numbers) total += n;
    return total;
}
// 이름 지정 가변 인수는 Java에서 지원하지 않음
```

```python
# Python
# *args - 위치 가변 인수 (Java varargs와 유사)
def sum_all(*numbers: int) -> int:
    return sum(numbers)   # numbers는 tuple

sum_all(1, 2, 3)          # 6
sum_all(1, 2, 3, 4, 5)   # 15

# **kwargs - 키워드 가변 인수 (Java에 없음)
def create_user(**kwargs: str) -> dict:
    return kwargs

create_user(name="Alice", age="30", role="admin")
# {"name": "Alice", "age": "30", "role": "admin"}

# 혼합 사용
def complex_func(required: str, *args, keyword_only: int = 0, **kwargs):
    print(f"required={required}, args={args}")
    print(f"keyword_only={keyword_only}, kwargs={kwargs}")

complex_func("hello", 1, 2, 3, keyword_only=5, extra="value")

# 언패킹으로 전달
numbers = [1, 2, 3]
options = {"ssl": True, "timeout": 30}
sum_all(*numbers)                          # 리스트 언패킹
connect("localhost", **options)            # 딕셔너리 언패킹
```

#### 4) Lambda (람다)

```java
// Java Lambda
Comparator<String> byLength = (a, b) -> a.length() - b.length();
List<Integer> nums = Arrays.asList(3, 1, 4, 1, 5);
nums.sort((a, b) -> a - b);
```

```python
# Python Lambda - 단순 표현식만 가능
by_length = lambda a, b: len(a) - len(b)
square = lambda x: x ** 2

# 정렬에서 key 함수로 자주 사용
names = ["Charlie", "Alice", "Bob"]
names.sort(key=lambda name: len(name))      # 길이로 정렬
names.sort(key=lambda name: name.lower())   # 대소문자 무시 정렬

# 복잡한 경우 일반 함수 권장
from functools import partial

def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
cube = partial(power, exp=3)
```

---

### 1.6 클래스

Java 개발자에게 가장 생소한 부분 중 하나입니다. Python의 `self`는 Java의 `this`이고, `__init__`은 생성자입니다.

#### 1) 기본 클래스

```java
// Java
public class BankAccount {
    private String owner;
    private double balance;

    public BankAccount(String owner, double initialBalance) {
        this.owner = owner;
        this.balance = initialBalance;
    }

    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("금액은 양수여야 합니다");
        this.balance += amount;
    }

    public double getBalance() {
        return balance;
    }

    public String toString() {
        return String.format("BankAccount{owner='%s', balance=%.2f}", owner, balance);
    }
}
```

```python
# Python
class BankAccount:
    # 클래스 변수 (Java의 static 필드)
    interest_rate: float = 0.03

    def __init__(self, owner: str, initial_balance: float) -> None:
        # self = Java의 this
        # __ (언더스코어 2개)로 시작하면 name mangling (private 유사)
        self.owner = owner          # public 필드
        self._balance = initial_balance  # _ 1개 = 관례상 protected (강제 아님)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("금액은 양수여야 합니다")  # throw 대신 raise
        self._balance += amount

    def get_balance(self) -> float:
        return self._balance

    # __str__ = Java의 toString()
    def __str__(self) -> str:
        return f"BankAccount(owner='{self.owner}', balance={self._balance:.2f})"

    # __repr__ = 개발자용 표현 (디버깅)
    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, initial_balance={self._balance!r})"


# 사용
account = BankAccount("Alice", 1000.0)  # new 키워드 없음!
account.deposit(500.0)
print(account)  # __str__ 호출
print(account.get_balance())
```

#### 2) `__str__` vs `__repr__` 차이

| | `__str__` | `__repr__` |
|---|---|---|
| 호출 시점 | `print()`, `str()`, f-string `{obj}` | `repr()`, 디버거, REPL, 로그 |
| 대상 | **사용자** (읽기 좋게) | **개발자** (정확하게) |
| Java 대응 | `toString()` | `toString()` (디버그용) |
| 없을 때 | `__repr__` 로 대체 | `<클래스명 object at 0x...>` |

```python
class User:
    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __str__(self):
        # 사용자에게 보여줄 때 - 민감정보 숨김
        return f"User(name={self.name})"

    def __repr__(self):
        # 개발자가 디버깅할 때 - 모든 정보 표시
        return f"User(name={self.name!r}, password={self.password!r})"


u = User("Alice", "secret123")

print(u)        # User(name=Alice)                              ← __str__ 호출
repr(u)         # User(name='Alice', password='secret123')      ← __repr__ 호출
f"{u}"          # User(name=Alice)                              ← __str__ 호출
f"{u!r}"        # User(name='Alice', password='secret123')      ← __repr__ 강제 호출

# 리스트 안에 넣으면 __repr__ 호출
users = [u]
print(users)    # [User(name='Alice', password='secret123')]    ← __repr__ !
```

**폴백 순서** (`__str__` 없을 때):
```
print(obj) 호출
    ↓
__str__ 있음? → 사용
    ↓ 없으면
__repr__ 있음? → 사용
    ↓ 없으면
<__main__.User object at 0x10f3a2b50>
```

> `@dataclass`는 `__repr__`만 자동 생성합니다. `__str__`은 생성하지 않으므로
> `print()` 호출 시 `__repr__`로 폴백되어 출력됩니다.

#### 3) 접근 제어와 Name Mangling

Java와 달리 Python에는 `public` / `protected` / `private` 키워드가 없습니다. 모두 **네이밍 관례**로 표현합니다.

```python
class BankAccount:
    def __init__(self) -> None:
        self.owner = "Alice"        # public   - 외부 자유롭게 접근
        self._balance = 1000        # protected - "_" 1개: "건드리지 마세요" 신호 (강제 아님)
        self.__pin = "1234"         # private 유사 - "__" 2개: name mangling 적용
        #  ↑ 내부적으로 _BankAccount__pin 으로 저장됨
```

`__` (언더스코어 2개)로 시작하는 속성에는 **name mangling**이 적용됩니다. Python이 `_ClassName__속성명` 형태로 이름을 자동 변환하여, 상속 시 자식 클래스가 실수로 같은 이름을 덮어쓰는 것을 방지합니다.

```python
account = BankAccount()
account.__pin               # AttributeError! - 이 이름으로는 접근 불가
account._BankAccount__pin   # "1234" - 실제 저장된 이름으로는 접근 가능 (권장 안 함)

# 상속 시 충돌 방지
class SavingsAccount(BankAccount):
    def __init__(self) -> None:
        super().__init__()
        self.__pin = "5678"   # _SavingsAccount__pin 으로 저장 → 부모의 _BankAccount__pin 과 별개
```

Java의 `private`처럼 완전히 차단하는 것이 아니라, 이름을 변환하여 충돌을 피하는 방식입니다.

| 표기 | Java 대응 | 비고 |
|------|---------|------|
| `owner` | `public` | 강제 없음 (관례) |
| `_balance` | `protected` | 강제 없음 (관례) |
| `__pin` | `private` 유사 | name mangling으로 우회 가능 |

#### 4) @property - Getter/Setter

```java
// Java - Getter/Setter 패턴 (Lombok 이전 스타일)
private double balance;

public double getBalance() { return balance; }
public void setBalance(double balance) {
    if (balance < 0) throw new IllegalArgumentException();
    this.balance = balance;
}
```

```python
# Python - @property 데코레이터
class BankAccount:
    def __init__(self, initial_balance: float) -> None:
        self._balance = initial_balance

    @property
    def balance(self) -> float:
        """Java의 getBalance()"""
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        """Java의 setBalance()"""
        if value < 0:
            raise ValueError("잔액은 음수가 될 수 없습니다")
        self._balance = value

    @balance.deleter
    def balance(self) -> None:
        """del account.balance 호출 시"""
        del self._balance


account = BankAccount(1000.0)
print(account.balance)   # getBalance() 호출 방식이 아니라 필드처럼!
account.balance = 2000   # setBalance() 호출 방식이 아니라 대입처럼!
```

#### 5) @classmethod와 @staticmethod

```java
// Java - static 메서드
public class User {
    private String name;
    private int age;

    // 팩토리 메서드 (static)
    public static User fromString(String str) {
        String[] parts = str.split(",");
        return new User(parts[0], Integer.parseInt(parts[1]));
    }

    // 유틸리티 메서드 (static)
    public static boolean isValidAge(int age) {
        return age >= 0 && age <= 150;
    }
}
```

```python
# Python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    @classmethod
    def from_string(cls, s: str) -> "User":
        """팩토리 메서드 - cls는 클래스 자체 (Java의 static factory)
        cls를 통해 상속 시 서브클래스 인스턴스 생성 가능"""
        parts = s.split(",")
        return cls(parts[0], int(parts[1]))

    @staticmethod
    def is_valid_age(age: int) -> bool:
        """유틸리티 메서드 - self도 cls도 없음 (순수 Java static 메서드)"""
        return 0 <= age <= 150

    def __repr__(self) -> str:
        return f"User(name={self.name!r}, age={self.age})"


# 사용
user = User.from_string("Alice,30")  # 팩토리 메서드
print(User.is_valid_age(200))        # False
```

#### 6) 상속

```java
// Java
public abstract class Animal {
    protected String name;

    public Animal(String name) { this.name = name; }

    public abstract String speak();  // 추상 메서드

    public String introduce() {
        return String.format("저는 %s이고, %s라고 합니다.", name, speak());
    }
}

public class Dog extends Animal {
    public Dog(String name) { super(name); }

    @Override
    public String speak() { return "멍멍"; }
}
```

```python
# Python - 추상 클래스는 abc 모듈 사용
from abc import ABC, abstractmethod

class Animal(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def speak(self) -> str:  # 추상 메서드
        pass

    def introduce(self) -> str:
        return f"저는 {self.name}이고, {self.speak()}라고 합니다."


class Dog(Animal):
    def speak(self) -> str:  # @Override 없음, 그냥 재정의
        return "멍멍"


class Cat(Animal):
    def __init__(self, name: str, indoor: bool = True) -> None:
        super().__init__(name)   # super().__init__() - Java의 super()
        self.indoor = indoor

    def speak(self) -> str:
        return "야옹"


dog = Dog("바둑이")
print(dog.introduce())

# isinstance - Java의 instanceof
print(isinstance(dog, Animal))  # True
print(isinstance(dog, Dog))     # True
print(isinstance(dog, Cat))     # False
```

#### 7) dataclass - Java의 record/Lombok @Data

```java
// Java record (Java 16+)
public record Point(int x, int y) {}

// Lombok @Data (레거시)
@Data
public class User {
    private String name;
    private int age;
}
```

```python
# Python dataclass (Python 3.7+)
from dataclasses import dataclass, field

@dataclass
class Point:
    x: int
    y: int
    # __init__, __repr__, __eq__ 자동 생성


@dataclass
class User:
    name: str
    age: int
    tags: list[str] = field(default_factory=list)  # 가변 기본값은 field() 사용


@dataclass(frozen=True)  # 불변 객체 - Java record와 동일
class ImmutablePoint:
    x: int
    y: int


p = Point(1, 2)
u = User("Alice", 30)
print(p)    # Point(x=1, y=2)
print(u)    # User(name='Alice', age=30, tags=[])
```

---

### 1.7 모듈과 패키지

```java
// Java import
import java.util.List;
import java.util.ArrayList;
import com.example.myapp.service.UserService;
import static java.lang.Math.PI;  // 정적 import
```

```python
# Python import
import os                          # 모듈 전체
import os.path                     # 서브모듈
from os import path                # 특정 항목만
from os.path import join, exists   # 여러 항목
from math import pi                # Java의 static import

# 별칭 사용 (관례적으로 자주 쓰는 별칭들)
import numpy as np
import pandas as pd
from datetime import datetime as dt

# 모든 공개 항목 import (권장하지 않음)
from math import *


# 패키지 구조 예시:
# my_app/
# ├── __init__.py        # Java의 package-info.java와 유사
# ├── models/
# │   ├── __init__.py
# │   └── user.py
# └── services/
#     ├── __init__.py
#     └── user_service.py

# my_app/models/user.py에서 import
from my_app.models.user import User
from my_app.services import UserService

# 상대 경로 import (같은 패키지 내)
from .user import User             # 현재 패키지
from ..services import UserService  # 상위 패키지
```

---

### 1.8 예외 처리

```java
// Java
try {
    int result = divide(10, 0);
} catch (ArithmeticException e) {
    System.err.println("0으로 나누기 오류: " + e.getMessage());
} catch (IllegalArgumentException e) {
    System.err.println("잘못된 인수: " + e.getMessage());
} finally {
    System.out.println("항상 실행");
}

// 커스텀 예외
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String userId) {
        super("User not found: " + userId);
    }
}
```

```python
# Python
try:
    result = 10 / 0
except ZeroDivisionError as e:         # ArithmeticException
    print(f"0으로 나누기 오류: {e}")
except (ValueError, TypeError) as e:   # 여러 예외를 한 번에 (Java의 multi-catch)
    print(f"타입/값 오류: {e}")
except Exception as e:                 # Exception (최상위 예외)
    print(f"예상치 못한 오류: {e}")
    raise                              # 예외 재발생 (Java의 throw e)
else:
    # 예외가 발생하지 않았을 때만 실행 (Java에 없는 기능!)
    print(f"성공: {result}")
finally:
    print("항상 실행")

# 예외 발생시키기
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("0으로 나눌 수 없습니다")  # throw new
    return a / b

# 예외 체이닝 (Java의 initCause와 유사)
try:
    int("abc")
except ValueError as e:
    raise RuntimeError("파싱 실패") from e  # cause 설정


# 커스텀 예외
class UserNotFoundException(Exception):
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")


class InsufficientFundsError(ValueError):
    def __init__(self, amount: float, balance: float) -> None:
        self.amount = amount
        self.balance = balance
        super().__init__(f"잔액 부족: 요청={amount}, 현재={balance}")


# Python 주요 예외 계층 (Java와 비교)
# Exception          <- Java의 Exception
# ├── ValueError     <- IllegalArgumentException
# ├── TypeError      <- ClassCastException
# ├── KeyError       <- NoSuchElementException
# ├── IndexError     <- IndexOutOfBoundsException
# ├── AttributeError <- NullPointerException (유사)
# ├── FileNotFoundError <- IOException
# ├── IOError        <- IOException
# └── RuntimeError   <- RuntimeException
```

---

### 1.9 컨텍스트 매니저

Java의 `try-with-resources`와 동일한 개념입니다. `AutoCloseable` 인터페이스와 유사한 `__enter__`/`__exit__` 프로토콜을 사용합니다.

```java
// Java try-with-resources
try (FileWriter writer = new FileWriter("output.txt");
     BufferedReader reader = new BufferedReader(new FileReader("input.txt"))) {
    String line;
    while ((line = reader.readLine()) != null) {
        writer.write(line + "\n");
    }
}  // 자동으로 close() 호출
```

```python
# Python with문 - Java try-with-resources와 동일
with open("output.txt", "w") as writer:
    writer.write("Hello, World!\n")
# 블록 종료 시 자동으로 close() 호출

# 여러 리소스 동시 관리
with open("input.txt", "r") as reader, open("output.txt", "w") as writer:
    for line in reader:
        writer.write(line)

# 커스텀 컨텍스트 매니저 - __enter__/__exit__ 구현
class DatabaseConnection:
    def __init__(self, host: str) -> None:
        self.host = host
        self.conn = None

    def __enter__(self):
        """Java의 try 블록 진입 시점"""
        print(f"{self.host}에 연결")
        self.conn = f"connection_to_{self.host}"
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Java의 AutoCloseable.close() - 예외 여부와 관계없이 호출"""
        print(f"{self.host} 연결 종료")
        self.conn = None
        return False  # False: 예외를 밖으로 전파 (기본 동작)

with DatabaseConnection("localhost") as conn:
    print(f"작업 중: {conn}")

# ── return False vs return True 비교 ──────────────────────────────────────

# [False] 예외 전파: with 블록 안의 예외가 밖으로 나감 (일반적인 경우)
class StrictConnection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("연결 종료 (strict)")
        return False  # 예외를 그대로 전파

try:
    with StrictConnection():
        raise ValueError("DB 오류!")  # 예외가 밖으로 전파됨
except ValueError as e:
    print(f"예외 잡힘: {e}")          # 여기서 잡힘
# 출력:
#   연결 종료 (strict)
#   예외 잡힘: DB 오류!


# [True] 예외 억제: with 블록 안의 예외를 무시하고 계속 진행
class LenientConnection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("연결 종료 (lenient)")
        return True  # 예외를 억제 → with 블록 이후 코드가 정상 실행됨

with LenientConnection():
    raise ValueError("DB 오류!")  # 예외가 억제됨!
print("예외가 억제되어 이 줄이 실행됨")
# 출력:
#   연결 종료 (lenient)
#   예외가 억제되어 이 줄이 실행됨


# [실용 패턴] 특정 예외만 억제, 나머지는 전파
class SelectiveConnection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("연결 종료 (selective)")
        if exc_type is ConnectionError:
            print(f"네트워크 오류 무시: {exc_val}")
            return True   # ConnectionError만 억제
        return False      # 다른 예외는 전파

with SelectiveConnection():
    raise ConnectionError("일시적 네트워크 오류")  # 억제됨
print("ConnectionError는 무시하고 계속 진행")
# 출력:
#   연결 종료 (selective)
#   네트워크 오류 무시: 일시적 네트워크 오류
#   ConnectionError는 무시하고 계속 진행

# 참고: contextlib.suppress 가 이 패턴을 표준 라이브러리로 제공함
from contextlib import suppress
with suppress(FileNotFoundError):
    open("없는파일.txt")   # FileNotFoundError 자동 억제
print("suppress로 예외 무시 후 계속 실행")


# contextlib 사용 - 더 간단한 방법
from contextlib import contextmanager

@contextmanager
def managed_connection(host: str):
    print(f"{host}에 연결")
    conn = f"connection_to_{host}"
    try:
        yield conn          # with 블록에 값 전달
    finally:
        print(f"{host} 연결 종료")

with managed_connection("localhost") as conn:
    print(f"작업 중: {conn}")
```

---

### 1.10 타입 힌트

Python 3.5+에서 도입된 타입 힌트는 Java의 타입 시스템과 유사한 표현을 가능하게 합니다.

```java
// Java 타입 표현
Optional<String> maybeValue = Optional.of("hello");
List<String> names = new ArrayList<>();
Map<String, List<Integer>> groupedScores = new HashMap<>();
```

```python
# Python typing 모듈 (Python 3.9 이전)
from typing import Optional, Union, List, Dict, Tuple, Any, TypeVar, Generic

# Optional - null 가능 값 (Java의 Optional과 개념 동일)
def find_user(user_id: str) -> Optional[str]:
    return "Alice" if user_id == "1" else None

# Python 3.10+에서는 | 연산자로 더 간결하게
def find_user_v2(user_id: str) -> str | None:
    return "Alice" if user_id == "1" else None

# Union - 여러 타입 허용
def process(value: Union[str, int]) -> str:
    return str(value)

# Python 3.10+
def process_v2(value: str | int) -> str:
    return str(value)

# 컬렉션 타입 (Python 3.9+에서는 소문자 사용 가능)
from typing import TypedDict

names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95}
matrix: list[list[int]] = [[1, 2], [3, 4]]
pair: tuple[str, int] = ("Alice", 30)
coords: tuple[int, ...]  = (1, 2, 3, 4)  # 가변 길이 튜플


# TypedDict - dict에 타입 구조 정의 (Java의 Map 구조 명시와 유사)
class UserDict(TypedDict):
    name: str
    age: int
    email: str

def create_user(data: UserDict) -> UserDict:
    return data

user: UserDict = {"name": "Alice", "age": 30, "email": "alice@example.com"}


# Generic 클래스 (Java의 Generic과 동일)
from typing import TypeVar, Generic

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()


stack: Stack[int] = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())  # 2


# Callable - 함수 타입
from typing import Callable

def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

apply(lambda x, y: x + y, 3, 4)  # 7
```

---

### 1.11 데코레이터

Java의 AOP(Aspect-Oriented Programming)와 어노테이션(`@Transactional`, `@Cacheable`)과 유사한 개념입니다.

```java
// Java AOP (Spring)
@Aspect
@Component
public class LoggingAspect {
    @Around("@annotation(Loggable)")
    public Object logExecution(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = pjp.proceed();
        long elapsed = System.currentTimeMillis() - start;
        System.out.println("실행 시간: " + elapsed + "ms");
        return result;
    }
}
```

```python
# Python 데코레이터
import time
import functools
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec("P")
R = TypeVar("R")

# 기본 데코레이터 - 실행 시간 측정 (Java의 @Around AOP)
def measure_time(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)  # 원본 함수 메타데이터 보존
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} 실행 시간: {elapsed:.4f}초")
        return result
    return wrapper


@measure_time
def slow_function(n: int) -> int:
    time.sleep(0.1)
    return n * 2

slow_function(5)  # "slow_function 실행 시간: 0.1xxx초" 출력


# 인수를 받는 데코레이터 (Java의 어노테이션 속성과 유사)
def retry(max_attempts: int = 3, exceptions: tuple = (Exception,)):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"재시도 {attempt + 1}/{max_attempts}: {e}")
        return wrapper
    return decorator


@retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
def call_api(url: str) -> dict:
    # API 호출 로직
    return {}


# 클래스 데코레이터 (Java의 @Singleton과 유사)
def singleton(cls):
    instances = {}
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


@singleton
class DatabasePool:
    def __init__(self) -> None:
        print("DB 풀 초기화")


db1 = DatabasePool()  # "DB 풀 초기화" 출력
db2 = DatabasePool()  # 출력 없음
print(db1 is db2)     # True

# 여러 데코레이터 스택 (Java의 여러 어노테이션 중첩과 유사)
@measure_time
@retry(max_attempts=2)
def important_task():
    pass
# 실행 순서: measure_time -> retry -> important_task
```

---

### 1.12 제너레이터

Java의 `Iterator`를 구현하는 것보다 훨씬 간결한 방식으로 대용량 데이터를 처리할 수 있습니다.

```java
// Java - Iterator 구현 (복잡함)
public class RangeIterator implements Iterator<Integer> {
    private int current;
    private final int end;

    public RangeIterator(int start, int end) {
        this.current = start;
        this.end = end;
    }

    @Override
    public boolean hasNext() { return current < end; }

    @Override
    public Integer next() {
        if (!hasNext()) throw new NoSuchElementException();
        return current++;
    }
}
```

```python
# Python - yield 키워드로 간단하게
def my_range(start: int, end: int):
    current = start
    while current < end:
        yield current          # 값을 반환하고 일시 정지
        current += 1

# 사용 - for 루프에서 직접 사용 가능
for i in my_range(0, 5):
    print(i)

# next()로 하나씩 가져오기
gen = my_range(0, 3)
print(next(gen))   # 0
print(next(gen))   # 1
print(next(gen))   # 2
# next(gen) -> StopIteration 예외


# 대용량 파일 처리 (메모리 효율적)
def read_large_file(filepath: str):
    """파일 전체를 메모리에 올리지 않고 한 줄씩 처리"""
    with open(filepath, "r") as f:
        for line in f:
            yield line.strip()

for line in read_large_file("big_file.txt"):
    process(line)   # 한 번에 한 줄만 메모리에


# 제너레이터 표현식 (리스트 컴프리헨션과 유사하지만 지연 평가)
# [] = 즉시 계산, 모든 결과를 메모리에 저장
squares_list = [x ** 2 for x in range(1000000)]      # 메모리 많이 사용

# () = 지연 계산, 필요할 때 하나씩 계산
squares_gen = (x ** 2 for x in range(1000000))       # 메모리 거의 사용 안 함
print(next(squares_gen))  # 0
print(sum(squares_gen))   # 나머지 합산


# yield from - 다른 제너레이터에 위임
def flatten(nested: list) -> any:
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)  # 재귀적으로 위임
        else:
            yield item

list(flatten([1, [2, [3, 4]], 5]))  # [1, 2, 3, 4, 5]
```

---

### 1.13 비동기 프로그래밍

Java의 `CompletableFuture`와 개념은 유사하지만, 문법이 훨씬 간결합니다.

```java
// Java CompletableFuture
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> fetchUserFromDB("user1"))
    .thenApplyAsync(user -> fetchOrders(user))
    .thenApply(orders -> formatResult(orders));

String result = future.get();  // 블로킹 대기
```

```python
# Python async/await
import asyncio
import aiohttp

# async def - 비동기 함수 정의
async def fetch_user(user_id: str) -> dict:
    await asyncio.sleep(0.1)  # I/O 대기 시뮬레이션
    return {"id": user_id, "name": "Alice"}

async def fetch_orders(user: dict) -> list:
    await asyncio.sleep(0.1)
    return [{"id": "order1", "item": "book"}]

async def main():
    # 순차 실행
    user = await fetch_user("user1")
    orders = await fetch_orders(user)

    # 병렬 실행 (CompletableFuture.allOf()와 유사)
    user1, user2 = await asyncio.gather(
        fetch_user("user1"),
        fetch_user("user2"),
    )

    # 타임아웃
    try:
        result = await asyncio.wait_for(fetch_user("user3"), timeout=1.0)
    except asyncio.TimeoutError:
        print("타임아웃!")

# 실행 진입점
asyncio.run(main())


# 실제 HTTP 요청 예시 (aiohttp 라이브러리)
async def fetch_multiple_apis():
    async with aiohttp.ClientSession() as session:
        urls = [
            "https://api.example.com/users/1",
            "https://api.example.com/users/2",
        ]
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        results = [await r.json() for r in responses]
    return results
```

---

## 2. pyproject.toml - 프로젝트 설정 파일

### 2.1 Maven/Gradle과의 비교

| Java | Python |
|------|--------|
| `pom.xml` (Maven) | `pyproject.toml` |
| `build.gradle` (Gradle) | `pyproject.toml` |
| `mvn install` | `uv sync` 또는 `pip install -e .` |
| `mvn test` | `pytest` |
| `mvn package` | `uv build` |
| `~/.m2/repository` | `~/.cache/uv` (uv) 또는 `~/.cache/pip` |

### 2.2 pyenv - Python 버전 관리

`pyenv`는 여러 Python 버전을 설치하고 프로젝트별로 다른 버전을 사용할 수 있게 해주는 도구입니다.
Java의 SDKMAN!(`sdk install java 21`) 또는 jenv와 유사한 개념입니다.

#### 1) 설치 및 기본 명령어

```bash
# pyenv 설치 (macOS)
brew install pyenv

# 설치 가능한 Python 버전 목록 조회
pyenv install --list

# 특정 버전 설치
pyenv install 3.11.9
pyenv install 3.12.3

# 설치된 버전 확인
pyenv versions
# * system (현재 사용 중)
#   3.11.9
#   3.12.3

# 전역 기본 버전 설정 (SDKMAN의 sdk default java와 유사)
pyenv global 3.12.3

# 프로젝트 디렉토리 진입 시 자동으로 버전 전환 (.python-version 파일 생성)
cd my-project
pyenv local 3.11.9          # .python-version 파일에 "3.11.9" 기록

# 확인
python --version            # Python 3.11.9

# shell 설정 (~/.zshrc 또는 ~/.bashrc에 추가 필요)
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

#### 2) pyenv-virtualenv - pyenv 전용 가상환경 관리

`pyenv-virtualenv`는 pyenv 플러그인으로, pyenv가 관리하는 Python 버전 기반으로 가상환경을 생성합니다.
uv를 사용하지 않거나, 가상환경을 프로젝트 외부(홈 디렉토리)에서 중앙 관리하고 싶을 때 사용합니다.

```bash
# pyenv-virtualenv 설치 (macOS)
brew install pyenv-virtualenv

# shell 설정에 추가 (~/.zshrc)
eval "$(pyenv virtualenv-init -)"

# 가상환경 생성 - pyenv virtualenv [버전] [가상환경명]
pyenv virtualenv 3.11.9 my-project-env

# 생성된 가상환경 목록 확인
pyenv virtualenvs
#   3.11.9/envs/my-project-env (created from /Users/user/.pyenv/versions/3.11.9)
# * my-project-env (created from /Users/user/.pyenv/versions/3.11.9)

# 프로젝트 디렉토리에서 가상환경 자동 활성화 (.python-version에 가상환경명 기록)
cd my-project
pyenv local my-project-env   # .python-version에 "my-project-env" 기록
                              # 디렉토리 진입 시 자동으로 가상환경 활성화됨

# 수동 활성화/비활성화
pyenv activate my-project-env
pyenv deactivate

# 가상환경 삭제
pyenv virtualenv-delete my-project-env
```

가상환경 저장 위치: `~/.pyenv/versions/3.11.9/envs/my-project-env`
→ 프로젝트 디렉토리 안의 `.venv/`(uv 방식)와 달리 **홈 디렉토리에 중앙 보관**됩니다.

| | pyenv-virtualenv | uv (.venv) |
|---|---|---|
| 가상환경 위치 | `~/.pyenv/versions/.../envs/` | 프로젝트 내 `.venv/` |
| 자동 활성화 | `.python-version`에 가상환경명 기록 | `uv run` 으로 자동 처리 |
| 패키지 설치 | `pip install` | `uv add` |
| 여러 프로젝트 공유 | 가능 (같은 환경명 공유) | 프로젝트별 독립 |

#### 3) .python-version 파일

`.python-version` 파일은 git에 커밋하면 팀 전체가 같은 Python 버전을 사용하도록 강제할 수 있습니다.

```
my-project/
├── .python-version   ← "3.11.9" 또는 "my-project-env" 한 줄 기록
├── pyproject.toml
└── ...
```

### 2.3 pyenv + uv 함께 사용하기

실무에서는 **pyenv로 Python 버전 관리** + **uv로 패키지/가상환경 관리** 조합을 많이 사용합니다.

```
pyenv                    uv
─────────────────────    ──────────────────────────────
Python 3.11 설치        패키지 설치/관리
Python 3.12 설치   →    가상환경(.venv) 생성
프로젝트별 버전 고정      의존성 잠금(uv.lock)
```

```bash
# 1단계: pyenv로 Python 버전 설치 및 고정
pyenv install 3.11.9
cd my-project
pyenv local 3.11.9        # .python-version 생성

# 2단계: uv가 .python-version을 자동으로 읽어 해당 버전으로 가상환경 생성
uv sync                   # pyenv Python 3.11.9 기반 .venv 생성

# uv에서 Python 버전을 직접 지정할 수도 있음 (pyenv 없이)
uv python install 3.11.9  # uv가 자체적으로 Python 다운로드·관리
uv python pin 3.11.9      # .python-version 파일 자동 생성
```

> **Java 개발자 관점**: pyenv ≈ SDKMAN!, uv ≈ Maven/Gradle.
> SDKMAN으로 JDK 버전을 관리하고 Maven으로 빌드/의존성을 관리하는 것과 동일한 역할 분담입니다.

### 2.4 uv 패키지 매니저

`uv`는 Rust로 작성된 초고속 Python 패키지 매니저입니다. pip보다 10~100배 빠릅니다.

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 새 프로젝트 생성 (mvn archetype:generate와 유사)
uv init my-project
cd my-project

# 의존성 추가 (mvn dependency:add와 유사)
uv add langchain openai

# 개발 의존성 추가 (Maven test scope)
uv add --dev pytest pytest-asyncio

# 의존성 설치 (mvn install과 유사)
uv sync

# 스크립트 실행
uv run python main.py
uv run pytest

# 가상환경 직접 활성화 (uv 없이 실행 시)
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

### 2.5 pyproject.toml 전체 예시

```toml
# pyproject.toml
# Maven의 pom.xml 또는 Gradle의 build.gradle에 해당

[project]
# ==========================================
# Maven의 <groupId>:<artifactId>:<version>
# ==========================================
name = "tutorial-langchain"
version = "0.1.0"
description = "LangChain 튜토리얼 프로젝트"
readme = "README.md"
license = { text = "MIT" }
authors = [
    { name = "개발자 이름", email = "dev@example.com" }
]
# Maven의 <java.version>에 해당
requires-python = ">=3.11"

# ==========================================
# Maven의 <dependencies> 섹션
# ==========================================
dependencies = [
    "langchain>=0.3.0",
    "langchain-openai>=0.2.0",
    "langchain-community>=0.3.0",
    "openai>=1.50.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "httpx>=0.27.0",
]

# ==========================================
# Maven의 test scope 의존성
# ==========================================
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "mypy>=1.8.0",
    "ruff>=0.4.0",
]

# ==========================================
# 실행 스크립트 등록 (Maven exec 플러그인과 유사)
# ==========================================
[project.scripts]
# 설치 후 CLI에서 바로 실행 가능
start = "tutorial_langchain.main:main"
migrate = "tutorial_langchain.db.migration:run"

# ==========================================
# 빌드 시스템 설정 (Maven의 <build> 섹션)
# ==========================================
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# ==========================================
# uv 패키지 매니저 설정
# ==========================================
[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
]

# ==========================================
# pytest 설정 (surefire 플러그인과 유사)
# ==========================================
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
]
markers = [
    "slow: 느린 테스트",
    "integration: 통합 테스트",
]

# ==========================================
# 코드 포매터/린터 설정 (Checkstyle/SpotBugs와 유사)
# ==========================================
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]

# ==========================================
# 정적 타입 체커 설정 (Java의 컴파일러 경고와 유사)
# ==========================================
[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
```

### 2.6 프로젝트 디렉토리 구조 (Maven과 비교)

```
# Maven 구조
my-project/
├── pom.xml
└── src/
    ├── main/java/com/example/
    │   └── App.java
    └── test/java/com/example/
        └── AppTest.java

# Python 구조 (pyproject.toml 방식) - src 레이아웃
my-project/
├── pyproject.toml              # pom.xml
├── .python-version             # pyenv 버전/가상환경 고정
├── .env.example                # 환경변수 템플릿
├── src/
│   └── my_project/             # 패키지명은 snake_case (src 레이아웃)
│       ├── __init__.py
│       ├── main.py             # FastAPI 앱 진입점
│       ├── config.py           # 환경변수/설정 관리
│       └── chains/             # 기능별 서브패키지
│           ├── __init__.py
│           └── chat_chain.py
└── tests/
    ├── __init__.py
    ├── conftest.py             # 전역 fixture (JUnit의 @BeforeAll과 유사)
    └── test_main.py

# pyproject.toml 핵심 설정 (src 레이아웃)
# [tool.pytest.ini_options]
# pythonpath = ["src"]          ← pytest가 src/ 아래 패키지를 인식하도록 경로 추가
#
# [tool.hatch.build.targets.wheel]
# packages = ["src/my_project"] ← 빌드 시 src 안의 패키지만 포함
```

---

## 3. pytest - 테스트 프레임워크

### 3.1 JUnit과 pytest 비교

| JUnit 5 | pytest |
|---------|--------|
| `@Test` | `test_` prefix |
| `assertEquals(a, b)` | `assert a == b` |
| `assertThrows(Ex.class, ...)` | `with pytest.raises(Ex):` |
| `@BeforeEach` | `@pytest.fixture` (autouse) |
| `@BeforeAll` | `@pytest.fixture(scope="session")` |
| `@AfterEach` / `@AfterAll` | fixture의 `yield` 이후 코드 |
| `@Tag("slow")` | `@pytest.mark.slow` |
| `@Disabled` | `@pytest.mark.skip` |
| `@ParameterizedTest` | `@pytest.mark.parametrize` |
| `@ExtendWith(MockitoExtension)` | `unittest.mock.patch` |
| `conftest.xml` (surefire) | `conftest.py` |

### 3.2 기본 테스트 작성

#### 1) Java JUnit 5

```java
// Java JUnit 5
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {

    private Calculator calc;

    @BeforeEach
    void setUp() {
        calc = new Calculator();
    }

    @Test
    @DisplayName("두 수의 합 계산")
    void testAdd() {
        assertEquals(5, calc.add(2, 3));
        assertNotNull(calc);
        assertTrue(calc.add(1, 1) > 0);
    }

    @Test
    void testDivideByZero() {
        assertThrows(ArithmeticException.class, () -> calc.divide(10, 0));
    }
}
```

#### 2) Python pytest

```python
# Python pytest
# tests/test_calculator.py

import pytest
from my_app.calculator import Calculator


# 테스트 함수 - test_ prefix가 필수!
def test_add():
    calc = Calculator()
    # assert 하나만으로 JUnit의 모든 assertion 대체
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0
    assert calc.add(0, 0) == 0


def test_add_returns_correct_type():
    calc = Calculator()
    result = calc.add(2, 3)
    assert isinstance(result, int)  # assertInstanceOf


def test_divide_by_zero():
    calc = Calculator()
    # assertThrows에 해당
    with pytest.raises(ValueError) as exc_info:
        calc.divide(10, 0)
    assert "0으로 나눌 수 없습니다" in str(exc_info.value)


# assert 다양한 활용
def test_various_assertions():
    # 동등성
    assert 1 + 1 == 2                  # assertEquals
    assert "hello" != "world"          # assertNotEquals

    # 참/거짓
    assert True                        # assertTrue
    assert not False                   # assertFalse

    # None 체크
    assert None is None                # assertNull
    assert "value" is not None         # assertNotNull

    # 컬렉션
    result = [1, 2, 3]
    assert 2 in result                 # assertTrue(result.contains(2))
    assert len(result) == 3            # assertEquals(3, result.size())

    # 근사값 비교 (부동소수점)
    assert abs(0.1 + 0.2 - 0.3) < 1e-10   # assertEquals(0.3, result, 1e-10)
    assert 3.14 == pytest.approx(3.14159, abs=0.01)  # 더 pythonic한 방식
```

### 3.3 Fixture - @BeforeEach, @AfterEach 대응

#### 1) Java JUnit 5

```java
// Java JUnit 5
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    private UserRepository mockRepo;
    private UserService userService;

    @BeforeEach
    void setUp() {
        mockRepo = Mockito.mock(UserRepository.class);
        userService = new UserService(mockRepo);
    }

    @AfterEach
    void tearDown() {
        // 정리 로직
    }
}
```

#### 2) Python pytest

```python
# Python pytest - fixture
import pytest
from unittest.mock import MagicMock
from my_app.service import UserService
from my_app.repository import UserRepository


# @BeforeEach에 해당 - 각 테스트 함수마다 새로 실행
@pytest.fixture
def mock_repository():
    """UserRepository Mock 객체"""
    return MagicMock(spec=UserRepository)


@pytest.fixture
def user_service(mock_repository):
    """fixture는 다른 fixture를 의존성 주입받을 수 있음"""
    return UserService(repository=mock_repository)


# fixture를 인수로 받으면 자동으로 주입됨
def test_find_user(user_service, mock_repository):
    # Given
    mock_repository.find_by_id.return_value = {"id": "1", "name": "Alice"}

    # When
    result = user_service.find_user("1")

    # Then
    assert result["name"] == "Alice"
    mock_repository.find_by_id.assert_called_once_with("1")


# yield fixture - setUp + tearDown 통합
@pytest.fixture
def db_connection():
    """@BeforeEach + @AfterEach 통합"""
    # setUp 부분
    conn = create_test_db_connection()
    conn.begin_transaction()
    print("DB 연결 완료")

    yield conn  # 테스트 함수에 conn 전달

    # tearDown 부분 (yield 이후)
    conn.rollback()
    conn.close()
    print("DB 연결 종료")


# Scope 설정
@pytest.fixture(scope="session")
def api_client():
    """@BeforeAll - 전체 테스트 세션에서 1번만 실행"""
    client = TestClient()
    yield client
    client.close()


@pytest.fixture(scope="module")
def module_fixture():
    """같은 모듈(파일)에서 1번만 실행"""
    pass


@pytest.fixture(scope="function")   # 기본값
def function_fixture():
    """각 테스트 함수마다 실행 (기본값)"""
    pass


# autouse - 모든 테스트에 자동 적용 (@BeforeEach와 유사)
@pytest.fixture(autouse=True)
def reset_database():
    """모든 테스트 전에 자동으로 DB 초기화"""
    setup_test_db()
    yield
    cleanup_test_db()
```

### 3.4 conftest.py - 전역 Fixture

```python
# tests/conftest.py
# 이 파일의 fixture는 같은 디렉토리와 하위 디렉토리의 모든 테스트에서 사용 가능
# JUnit의 @TestInstance(Lifecycle.PER_CLASS) + @BeforeAll과 유사

import pytest
from my_app.config import Settings
from my_app.database import Database


@pytest.fixture(scope="session")
def settings():
    """전체 테스트 세션에서 공유하는 설정"""
    return Settings(
        database_url="sqlite:///:memory:",
        debug=True,
    )


@pytest.fixture(scope="session")
def database(settings):
    """테스트용 DB 초기화 (1번만)"""
    db = Database(settings.database_url)
    db.create_tables()
    yield db
    db.drop_tables()


@pytest.fixture(scope="function")
def db_session(database):
    """각 테스트마다 트랜잭션으로 격리"""
    session = database.session()
    yield session
    session.rollback()
    session.close()
```

### 3.5 pytest.mark - 어노테이션

```python
# JUnit @Tag, @Disabled와 비교

import pytest


@pytest.mark.skip(reason="아직 구현 중")  # @Disabled
def test_not_implemented():
    pass


@pytest.mark.skipif(
    condition=True,  # 조건부 skip
    reason="이 환경에서는 실행 불가"
)
def test_conditional():
    pass


@pytest.mark.slow           # @Tag("slow") - 커스텀 마크
def test_heavy_computation():
    pass


@pytest.mark.integration    # @Tag("integration")
def test_with_real_db():
    pass


@pytest.mark.xfail(reason="알려진 버그 #123")  # @Disabled + 실패 예상
def test_known_bug():
    assert False  # 실패해도 전체 테스트는 통과


# 실행 시 마크 필터링
# pytest -m slow              # slow 태그만 실행
# pytest -m "not slow"        # slow 제외
# pytest -m "slow or integration"  # slow 또는 integration
```

### 3.6 파라미터화 테스트

#### 1) Java JUnit 5

```java
// Java JUnit 5 @ParameterizedTest
@ParameterizedTest
@CsvSource({
    "2, 3, 5",
    "-1, 1, 0",
    "0, 0, 0"
})
void testAdd(int a, int b, int expected) {
    assertEquals(expected, calculator.add(a, b));
}
```

#### 2) Python pytest

```python
# Python pytest.mark.parametrize
import pytest
from my_app.calculator import add, is_prime


# 단순 파라미터
@pytest.mark.parametrize("n,expected", [
    (2, True),
    (3, True),
    (4, False),
    (17, True),
    (100, False),
])
def test_is_prime(n: int, expected: bool):
    assert is_prime(n) == expected


# 여러 파라미터
@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    pytest.param(999, 999, 1998, marks=pytest.mark.slow),  # 마크 결합
])
def test_add(a: int, b: int, expected: int):
    assert add(a, b) == expected


# ID 지정
@pytest.mark.parametrize("value,expected", [
    pytest.param("hello", True, id="영문"),
    pytest.param("", False, id="빈문자열"),
    pytest.param("123", False, id="숫자"),
], ids=["영문", "빈문자열", "숫자"])  # 또는 ids 파라미터로
def test_is_alpha(value: str, expected: bool):
    assert value.isalpha() == expected
```

### 3.7 모킹 (Mocking)

#### 1) Java Mockito

```java
// Java Mockito
@Mock
UserRepository mockRepo;

when(mockRepo.findById("1")).thenReturn(Optional.of(new User("Alice")));
verify(mockRepo, times(1)).findById("1");
verify(mockRepo, never()).delete(any());
```

#### 2) Python unittest.mock

```python
# Python unittest.mock
from unittest.mock import MagicMock, patch, AsyncMock
import pytest


# MagicMock - Mockito.mock()에 해당
def test_with_mock():
    mock_repo = MagicMock()
    mock_repo.find_by_id.return_value = {"id": "1", "name": "Alice"}

    service = UserService(repository=mock_repo)
    result = service.find_user("1")

    # verify
    mock_repo.find_by_id.assert_called_once_with("1")
    mock_repo.delete.assert_not_called()
    assert result["name"] == "Alice"


# patch - 모듈 내 객체를 교체 (AOP처럼 동작)
def test_with_patch():
    with patch("my_app.service.UserRepository") as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.find_by_id.return_value = {"id": "1"}

        service = UserService()  # 내부적으로 UserRepository() 생성
        result = service.find_user("1")

        assert result["id"] == "1"


# 데코레이터로 patch (더 간결)
@patch("my_app.service.UserRepository")
@patch("my_app.service.Cache")
def test_with_multiple_patches(MockCache, MockRepo):
    # 데코레이터 역순으로 인수 전달됨!
    mock_repo = MockRepo.return_value
    mock_cache = MockCache.return_value

    mock_repo.find_by_id.return_value = None
    mock_cache.get.return_value = {"id": "1", "name": "Cached"}

    service = UserService()
    result = service.find_user("1")

    assert result["name"] == "Cached"


# fixture와 patch 결합
@pytest.fixture
def mock_external_api():
    with patch("my_app.service.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        mock_get.return_value.status_code = 200
        yield mock_get


def test_external_call(mock_external_api):
    service = ExternalService()
    result = service.check_status()
    assert result == "ok"


# 예외 발생 모킹
def test_handles_api_error():
    mock_repo = MagicMock()
    mock_repo.find_by_id.side_effect = ConnectionError("DB 연결 실패")

    service = UserService(repository=mock_repo)

    with pytest.raises(ServiceException):
        service.find_user("1")
```

### 3.8 pytest-asyncio - 비동기 테스트

```python
# pyproject.toml에서 asyncio_mode = "auto" 설정 시
# @pytest.mark.asyncio 생략 가능

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock


@pytest_asyncio.fixture
async def async_client():
    """비동기 fixture"""
    client = AsyncTestClient()
    await client.start()
    yield client
    await client.stop()


# async 테스트 함수
async def test_async_fetch(async_client):
    result = await async_client.fetch("/api/users/1")
    assert result["id"] == "1"


async def test_async_mock():
    mock_service = AsyncMock()
    mock_service.fetch_user.return_value = {"id": "1", "name": "Alice"}

    result = await mock_service.fetch_user("1")
    assert result["name"] == "Alice"
    mock_service.fetch_user.assert_awaited_once_with("1")


# asyncio.gather 병렬 처리 테스트
async def test_parallel_requests():
    results = await asyncio.gather(
        fetch_user("1"),
        fetch_user("2"),
        fetch_user("3"),
    )
    assert len(results) == 3
```

### 3.9 pytest 실행 명령어

```bash
# 전체 테스트 실행 (mvn test와 유사)
pytest

# 상세 출력
pytest -v

# 특정 파일 실행
pytest tests/test_calculator.py

# 특정 테스트 함수 실행
pytest tests/test_calculator.py::test_add

# 특정 클래스의 테스트 실행
pytest tests/test_calculator.py::TestCalculator::test_add

# 마크 필터
pytest -m slow
pytest -m "not slow"
pytest -m "integration and not slow"

# 실패한 테스트만 재실행 (-lf = last failed)
pytest --lf

# 첫 번째 실패에서 중단 (-x)
pytest -x

# N번 실패 시 중단
pytest --maxfail=3

# 코드 커버리지 (mvn jacoco:report와 유사)
pytest --cov=src --cov-report=html

# 키워드로 필터링 (-k)
pytest -k "add or subtract"
pytest -k "not slow"

# 병렬 실행 (pytest-xdist 설치 필요)
pytest -n auto    # CPU 코어 수만큼 병렬
pytest -n 4       # 4개 병렬
```

---

## 4. Java 개발자가 주의할 Python 특징

### 4.1 들여쓰기가 문법이다

Java에서는 중괄호 `{}`가 블록을 구분하지만, Python은 **들여쓰기(indentation)**가 문법입니다.

```python
# 올바른 예
def calculate(x):
    if x > 0:
        return x * 2
    else:
        return 0

# 잘못된 예 - IndentationError 발생!
def bad_function(x):
if x > 0:        # 들여쓰기 없음 -> 오류
    return x

# 혼재 금지 - Tab과 Space를 섞으면 오류
# 팀 표준: Space 4칸 (PEP 8 권고사항)
```

### 4.2 None, True, False (대소문자 주의!)

```java
// Java
null    // Python에서는 None
true    // Python에서는 True
false   // Python에서는 False
```

```python
# Python - 첫 글자 대문자!
value = None    # null
flag = True     # true
other = False   # false

# None 체크 - == 보다 is 사용 권장
if value is None:      # if (value == null) 보다 안전
    print("없음")

if value is not None:  # if (value != null)
    print("있음")

# Falsy 값들 (Java와 다름!)
# 다음 값들은 모두 if문에서 False로 처리됨
falsy_values = [False, None, 0, 0.0, "", [], {}, set()]
for v in falsy_values:
    if not v:
        print(f"{v!r}은 falsy")

# Java 개발자 함정: 빈 리스트와 None 구분!
def process(items: list | None = None):
    if items is None:     # None인지 체크
        items = []
    if not items:         # 빈 리스트인지 체크 (items == [] 보다 pythonic)
        print("항목 없음")
```

### 4.3 네이밍 규칙 (snake_case)

```java
// Java - camelCase 규칙
String firstName = "Alice";
int maxRetryCount = 3;
boolean isUserActive = true;
void getUserById() { }
class UserService { }
static final int MAX_CONNECTIONS = 10;
```

```python
# Python - snake_case 규칙 (PEP 8)
first_name = "Alice"           # 변수: snake_case
max_retry_count = 3
is_user_active = True
def get_user_by_id(): pass     # 함수: snake_case
class UserService: pass        # 클래스: PascalCase (Java와 동일)
MAX_CONNECTIONS = 10           # 상수: UPPER_SNAKE_CASE

# _ 접두사 관례
_private_var = "내부 사용"      # 관례상 private (강제 아님)
__name_mangled = "name mangling 적용"  # 클래스 내에서 _ClassName__name_mangled로 변환

# __ 양쪽 = dunder (double underscore) - 특별한 의미
__init__       # 생성자
__str__        # toString()
__eq__         # equals()
__hash__       # hashCode()
__len__        # size()/length()
__getitem__    # get(index)
__contains__   # contains()
__enter__      # try-with-resources 시작
__exit__       # try-with-resources 종료
```

### 4.4 주요 Dunder 메서드

```python
class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        """print() 호출 시 - Java toString()"""
        return f"Vector({self.x}, {self.y})"

    def __repr__(self) -> str:
        """디버거/REPL에서 - Java toString() 대응 (개발자용)"""
        return f"Vector(x={self.x!r}, y={self.y!r})"

    def __eq__(self, other: object) -> bool:
        """== 연산자 - Java equals()"""
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        """dict key, set 원소로 사용 시 - Java hashCode()"""
        return hash((self.x, self.y))

    def __len__(self) -> int:
        """len() 함수 호출 시 - Java size()/length()"""
        return 2  # x, y 두 성분

    def __add__(self, other: "Vector") -> "Vector":
        """+ 연산자 오버로딩 - Java에서는 불가!"""
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> "Vector":
        """* 연산자 오버로딩"""
        return Vector(self.x * scalar, self.y * scalar)

    def __bool__(self) -> bool:
        """if vector: 같은 조건문에서 사용"""
        return self.x != 0 or self.y != 0


v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)     # Vector(4, 6)
print(v1 * 2)      # Vector(2, 4)
print(v1 == v2)    # False
print(len(v1))     # 2
```

### 4.5 GIL (Global Interpreter Lock)

Java의 멀티스레딩과 다르게, Python의 CPython 구현체는 GIL로 인해 동시에 하나의 스레드만 Python 코드를 실행할 수 있습니다.

```
Java 멀티스레딩:
Thread 1 ─── 실행 ─── 실행 ─── 실행 ───>  (진정한 병렬)
Thread 2 ─────── 실행 ─────── 실행 ──>

Python (CPython) 멀티스레딩:
Thread 1 ─── 실행 ─── 대기 ─── 실행 ───>  (GIL로 인해 교대 실행)
Thread 2 ─────── 대기 ─── 실행 ─── 대기>
```

```python
import threading
import multiprocessing
import asyncio

# CPU 집약적 작업: GIL로 인해 멀티스레딩 효과 없음
def cpu_task(n):
    return sum(i * i for i in range(n))

# threading - I/O 작업에는 효과 있음 (I/O 중 GIL 해제)
# (파일 읽기, 네트워크 요청 등)
def io_task(url):
    import requests
    return requests.get(url).text

threads = [
    threading.Thread(target=io_task, args=(url,))
    for url in urls
]

# multiprocessing - CPU 집약적 작업에 사용 (GIL 우회)
# 각 프로세스는 독립적인 Python 인터프리터를 가짐
with multiprocessing.Pool() as pool:
    results = pool.map(cpu_task, [10**6] * 4)

# asyncio - I/O 작업의 최선 (단일 스레드, 이벤트 루프)
# GIL 문제 없이 높은 동시성 달성
async def async_io_task(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# Python 3.13+: No-GIL 실험 버전 출시됨
```

### 4.6 가상환경 (Virtual Environment)

Java는 Maven/Gradle이 프로젝트별 의존성을 `.m2`에 버전별로 관리하지만, Python은 전역 패키지 충돌을 피하기 위해 프로젝트별 가상환경이 필수입니다.

```
Java (Maven):
~/.m2/repository/                    # 전역 저장소, 버전별로 구분됨
├── junit/junit/4.13/
└── com/example/library/1.0.0/

Python (가상환경 없이):
/usr/local/lib/python3.11/site-packages/  # 전역 - 버전 하나만 설치 가능!
├── requests-2.28.0/                      # requests 2.29가 필요한 프로젝트와 충돌!
└── langchain-0.1.0/

Python (가상환경 사용):
project-a/.venv/lib/python3.11/site-packages/  # 프로젝트 A 전용
├── requests-2.28.0/
project-b/.venv/lib/python3.11/site-packages/  # 프로젝트 B 전용
└── requests-2.31.0/
```

pyenv 환경에서는 **pyenv로 Python 버전을 고정**하고, **uv로 가상환경(.venv)과 패키지를 관리**하는 조합을 권장합니다.
(자세한 내용은 [2.2 pyenv](#22-pyenv---python-버전-관리), [2.3 pyenv + uv](#23-pyenv--uv-함께-사용하기) 참고)

```bash
# ── [권장] pyenv + uv 조합 ──────────────────────────────────────────────────

# 1. 프로젝트 루트에서 Python 버전 고정 (.python-version 파일 생성)
pyenv local 3.11.9

# 2. uv가 .python-version을 읽어 해당 버전으로 .venv 자동 생성
uv sync                   # 의존성 설치 + .venv 생성
uv run python main.py     # 가상환경 내 Python 실행
uv run pytest             # 가상환경 내 pytest 실행

# 패키지 추가 (uv가 자동으로 .venv에 설치)
uv add langchain openai
uv add --dev pytest


# ── [대안] pyenv-virtualenv (uv 없이 중앙 관리할 때) ─────────────────────────

# 가상환경 생성 및 프로젝트에 연결 (pyenv-virtualenv 플러그인 필요)
pyenv virtualenv 3.11.9 my-project-env
pyenv local my-project-env    # 디렉토리 진입 시 자동으로 가상환경 활성화

# 패키지 설치
pip install -r requirements.txt


# ── 현재 환경 확인 ────────────────────────────────────────────────────────────
pyenv version          # pyenv가 인식하는 현재 버전/가상환경명
which python           # 실제 Python 경로 확인 (가상환경 여부 확인)
python --version       # 버전 확인


# ── .gitignore에 반드시 추가! ─────────────────────────────────────────────────
# .venv/
# __pycache__/
# *.pyc
# .mypy_cache/
# .pytest_cache/
# dist/
# *.egg-info/
```

| | pyenv + uv | pyenv-virtualenv |
|---|---|---|
| 가상환경 위치 | 프로젝트 내 `.venv/` | `~/.pyenv/versions/.../envs/` |
| 패키지 설치 | `uv add` | `pip install` |
| 자동 활성화 | `uv run` 으로 자동 처리 | `.python-version`에 환경명 기록 |
| 속도 | 매우 빠름 (Rust 구현) | 일반적 |

### 4.7 Java 개발자를 위한 빠른 참조표

| Java | Python | 비고 |
|------|--------|------|
| `null` | `None` | 대문자 주의 |
| `true` / `false` | `True` / `False` | 대문자 주의 |
| `System.out.println()` | `print()` | |
| `System.err.println()` | `print(..., file=sys.stderr)` | |
| `// 주석` | `# 주석` | |
| `/* 블록 주석 */` | `"""docstring"""` 또는 `# 여러 줄` | |
| `instanceof` | `isinstance()` | |
| `(String) obj` | 해당 없음 (duck typing) | |
| `this` | `self` | |
| `super()` | `super().__init__()` | |
| `new MyClass()` | `MyClass()` | new 없음 |
| `throw new Exception()` | `raise Exception()` | |
| `catch (Exception e)` | `except Exception as e:` | |
| `finally` | `finally:` | |
| `interface` | `Protocol` (typing 모듈) | |
| `abstract class` | `ABC` (abc 모듈) | |
| `enum` | `Enum` (enum 모듈) | |
| `++i` / `i++` | `i += 1` | ++ 연산자 없음 |
| `i += 1` | `i += 1` | 동일 |
| `x > 0 ? a : b` | `a if x > 0 else b` | 순서 다름! |
| `String.format()` | `f"{value}"` | f-string |
| `equals()` | `==` | Python은 ==이 값 비교 |
| `==` (참조) | `is` | 참조 비교는 is |
| `List.of()` | `[...]` (불변은 tuple) | |
| `Map.of()` | `{...}` | |
| `Optional<T>` | `T \| None` 또는 `Optional[T]` | |
| `Stream.filter()` | List comprehension | |
| `Stream.map()` | List comprehension | |
| `Stream.collect()` | `list()` / `dict()` | |
| `@Override` | 없음 (자동) | |
| `public` / `private` | 없음 (관례로 `_` 사용) | 강제 불가 |
| `final` | 없음 (관례로 대문자 상수) | `frozen=True` dataclass |
| `static` | `@staticmethod` / `@classmethod` | |

---

## 마무리

Java/Spring Boot 20년 경력자가 Python을 배울 때 핵심 포인트:

1. **동적 타입에 익숙해지되, 타입 힌트를 적극 사용**하세요. mypy로 정적 분석을 하면 Java의 컴파일 타임 안전성을 상당 부분 확보할 수 있습니다.

2. **들여쓰기는 절대 법칙**입니다. 에디터에서 Tab/Space 혼용을 방지하는 설정을 꼭 하세요.

3. **`None`, `True`, `False` 대문자**를 습관으로 만드세요. 소문자를 쓰면 변수로 인식됩니다.

4. **가상환경(`.venv`)은 필수**입니다. uv를 사용하면 Maven/Gradle처럼 자동으로 관리됩니다.

5. **`with` 문을 적극 활용**하세요. 리소스 관리에서 Java의 `try-with-resources`보다 훨씬 간결합니다.

6. **List comprehension**은 Java의 Stream API보다 훨씬 읽기 쉽습니다. 적극 활용하세요.

7. **pytest의 `assert`** 하나로 JUnit의 모든 assertion을 대체할 수 있습니다.

8. **`@dataclass`**를 적극 활용하세요. Lombok `@Data`와 매우 유사합니다.
