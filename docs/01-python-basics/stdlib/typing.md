# typing - 타입 힌트 시스템

> 공식 문서: https://docs.python.org/3/library/typing.html

Python은 동적 타입 언어이지만 `typing` 모듈을 통해 타입 힌트를 추가할 수 있습니다.
Java처럼 컴파일 타임에 타입을 강제하지는 않지만, mypy, pyright 같은 정적 분석 도구와
IDE가 타입 정보를 활용해 오류를 사전에 잡아줍니다.

---

## 1. 기본 타입 힌트 (Python 3.9+ 내장)

Python 3.9부터는 `typing` 모듈을 import하지 않고 내장 타입을 그대로 사용할 수 있습니다.

```python
# Python 3.9+ - 소문자 내장 타입 사용 (권장)
def process_names(names: list[str]) -> dict[str, int]:
    return {name: len(name) for name in names}

def get_coordinates() -> tuple[float, float]:
    return (37.5665, 126.9780)

def get_scores() -> tuple[int, ...]:   # 가변 길이 tuple
    return (90, 85, 92, 78)
```

```java
// Java - 제네릭은 항상 대문자 래퍼 타입
public Map<String, Integer> processNames(List<String> names) {
    return names.stream()
        .collect(Collectors.toMap(name -> name, String::length));
}
```

### 구버전 `List`, `Dict`, `Tuple` (레거시 코드 읽기용)

Python 3.8 이하 또는 오래된 코드베이스에서는 `typing` 모듈에서 import해야 했습니다.
레거시 코드를 읽을 때 알아두어야 합니다.

```python
# Python 3.8 이하 레거시 스타일 - 현재도 동작하지만 사용 비권장
from typing import List, Dict, Tuple, Set, FrozenSet

def process_names(names: List[str]) -> Dict[str, int]:
    return {name: len(name) for name in names}

def get_matrix() -> List[List[int]]:
    return [[1, 2], [3, 4]]
```

> **마이그레이션 팁**: `from __future__ import annotations`를 파일 최상단에 추가하면
> Python 3.7+에서도 `list[str]` 스타일을 사용할 수 있습니다.

---

## 2. `Optional` / `Union`

### `Optional[T]`

Java의 `Optional<T>`은 런타임 래퍼 객체이지만, Python의 `Optional[T]`은 순수한 타입 힌트입니다.
런타임 오버헤드가 없으며 `T | None`과 완전히 동일합니다.

```python
from typing import Optional

# 세 가지 표현 모두 동일
def find_user_v1(user_id: int) -> Optional[str]:      # 레거시 스타일
    ...

def find_user_v2(user_id: int) -> str | None:          # Python 3.10+ 권장
    ...

def find_user(user_id: int) -> str | None:
    if user_id == 1:
        return "Alice"
    return None  # Java처럼 .orElse() 없이 직접 None 반환

# 호출부에서 None 체크
name = find_user(42)
if name is not None:
    print(name.upper())

# walrus operator 활용
if name := find_user(42):
    print(name.upper())
```

```java
// Java - Optional은 실제 래퍼 객체
public Optional<String> findUser(int userId) {
    if (userId == 1) return Optional.of("Alice");
    return Optional.empty();
}

// 호출부
findUser(42).ifPresent(name -> System.out.println(name.toUpperCase()));
String name = findUser(42).orElse("Unknown");
```

> **핵심 차이**: Python `Optional`은 타입 힌트 전용이라 `.orElse()` 같은 메서드가 없습니다.
> `if name is not None:` 패턴으로 직접 처리합니다.

### `Union[T1, T2]`

여러 타입 중 하나를 허용할 때 사용합니다.

```python
from typing import Union

# 레거시 스타일
def parse_id(value: Union[str, int]) -> int:
    if isinstance(value, str):
        return int(value)
    return value

# Python 3.10+ 권장 스타일
def parse_id(value: str | int) -> int:
    if isinstance(value, str):
        return int(value)
    return value

# isinstance로 타입 좁히기 (type narrowing) - mypy/pyright가 인식
def describe(value: str | int | list[str]) -> str:
    if isinstance(value, str):
        return f"문자열: {value}"     # 이 블록에서 value는 str
    elif isinstance(value, int):
        return f"정수: {value}"       # 이 블록에서 value는 int
    else:
        return f"목록: {', '.join(value)}"  # 이 블록에서 value는 list[str]
```

```java
// Java - Union 타입 없음, 오버로딩으로 처리
public int parseId(String value) { return Integer.parseInt(value); }
public int parseId(int value) { return value; }

// 또는 sealed interface (Java 17+)
public sealed interface IdValue permits StringId, IntId {}
```

---

## 3. `Any` - 타입 체크 비활성화

`Any`는 모든 타입과 호환되며 타입 체커가 해당 변수를 검사하지 않습니다.

```python
from typing import Any

# Any는 모든 타입과 호환
def process(data: Any) -> Any:
    return data.whatever_method()  # 타입 체커가 오류를 잡지 않음

# 레거시 코드 연동 시 불가피한 경우
def parse_legacy_response(response: dict[str, Any]) -> str:
    return response["name"]  # dict 값 타입을 알 수 없을 때
```

> **남용 금지**: `Any`를 사용하면 타입 힌트의 이점이 사라집니다.
> Java에서 `Object`를 남용하는 것과 동일한 문제입니다.
> `Any` 대신 `TypeVar`, `Generic`, `Protocol`로 제네릭하게 표현하는 것이 올바른 접근입니다.

---

## 4. `TypeVar` / `Generic` - 제네릭

### `TypeVar` - 타입 변수

```python
from typing import TypeVar, Generic

# Java: <T>, Python: TypeVar
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# 제네릭 함수
def first(items: list[T]) -> T:
    return items[0]

result: int = first([1, 2, 3])      # T = int로 추론
result: str = first(["a", "b"])     # T = str로 추론
```

```java
// Java 제네릭 함수
public <T> T first(List<T> items) {
    return items.get(0);
}
```

### 타입 경계 (Bounded TypeVar)

```python
from typing import TypeVar
from numbers import Number

# Java: <T extends Comparable<T>>
Comparable = TypeVar("Comparable", bound=int | float | str)

def maximum(a: Comparable, b: Comparable) -> Comparable:
    return a if a > b else b

# Python 3.12+ 새 문법 (TypeVar 선언 불필요)
def maximum[T: (int, float, str)](a: T, b: T) -> T:
    return a if a > b else b
```

```java
// Java
public <T extends Comparable<T>> T maximum(T a, T b) {
    return a.compareTo(b) >= 0 ? a : b;
}
```

### `Generic` 클래스

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0

# 사용
int_stack: Stack[int] = Stack()
int_stack.push(42)
value: int = int_stack.pop()

str_stack: Stack[str] = Stack()
str_stack.push("hello")
```

```java
// Java
public class Stack<T> {
    private final Deque<T> items = new ArrayDeque<>();

    public void push(T item) { items.push(item); }
    public T pop() { return items.pop(); }
    public boolean isEmpty() { return items.isEmpty(); }
}

Stack<Integer> intStack = new Stack<>();
intStack.push(42);
```

### 다중 타입 파라미터

```python
from typing import TypeVar, Generic

K = TypeVar("K")
V = TypeVar("V")

class Pair(Generic[K, V]):
    def __init__(self, key: K, value: V) -> None:
        self.key = key
        self.value = value

    def swap(self) -> "Pair[V, K]":
        return Pair(self.value, self.key)

pair: Pair[str, int] = Pair("age", 30)
swapped: Pair[int, str] = pair.swap()
```

---

## 5. `Protocol` - 구조적 타이핑

Java의 `interface`는 명시적으로 `implements`해야 하지만,
Python `Protocol`은 해당 메서드/속성이 있으면 자동으로 호환됩니다 (duck typing의 타입 안전 버전).

```python
from typing import Protocol, runtime_checkable

class Drawable(Protocol):
    def draw(self) -> None: ...
    def get_color(self) -> str: ...

# Protocol을 명시적으로 상속하지 않아도 됨!
class Circle:
    def draw(self) -> None:
        print("원 그리기")

    def get_color(self) -> str:
        return "red"

class Square:
    def draw(self) -> None:
        print("사각형 그리기")

    def get_color(self) -> str:
        return "blue"

# Circle, Square 모두 Drawable과 호환
def render(shape: Drawable) -> None:
    print(f"색상: {shape.get_color()}")
    shape.draw()

render(Circle())  # OK - Circle이 Drawable을 명시하지 않아도 통과
render(Square())  # OK
```

```java
// Java - 반드시 implements 필요
interface Drawable {
    void draw();
    String getColor();
}

class Circle implements Drawable {  // 명시적 선언 필수
    @Override public void draw() { System.out.println("원 그리기"); }
    @Override public String getColor() { return "red"; }
}

public void render(Drawable shape) {
    System.out.println("색상: " + shape.getColor());
    shape.draw();
}
```

### `@runtime_checkable` - 런타임 isinstance 지원

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

class DatabaseConnection:
    def close(self) -> None:
        print("DB 연결 종료")

conn = DatabaseConnection()
print(isinstance(conn, Closeable))  # True - runtime_checkable 덕분에 가능
```

> **Protocol vs ABC**: Protocol은 외부 라이브러리 클래스처럼 수정 불가능한 클래스와
> 인터페이스를 맞출 때 특히 유용합니다. ABC는 공통 구현(template method)이 필요할 때 사용합니다.

---

## 6. `TypedDict` - 딕셔너리 구조 정의

Java에서 `Map<String, Object>`는 값 타입 정보가 없어 불안전합니다.
`TypedDict`는 딕셔너리의 키와 값 타입을 명시적으로 정의합니다.

```python
from typing import TypedDict, Required, NotRequired

class UserDict(TypedDict):
    id: int
    name: str
    email: str

# 일부 필드를 선택적으로 만들기
class UserProfileDict(TypedDict, total=False):  # 모든 필드 선택적
    id: int
    name: str
    bio: str

# 혼합 (Python 3.11+)
class CreateUserRequest(TypedDict):
    name: str                        # 필수
    email: str                       # 필수
    bio: NotRequired[str]            # 선택적
    age: NotRequired[int]            # 선택적

def create_user(data: CreateUserRequest) -> UserDict:
    return {
        "id": 1,
        "name": data["name"],
        "email": data["email"],
    }

# 사용
user = create_user({"name": "Alice", "email": "alice@example.com"})
print(user["name"])  # 타입 체커가 str로 인식
```

```java
// Java - record나 DTO 클래스로 구조화
public record CreateUserRequest(
    String name,
    String email,
    @Nullable String bio,
    @Nullable Integer age
) {}

public record UserDto(Long id, String name, String email) {}
```

> **실전 팁**: REST API 응답을 파싱할 때 `TypedDict`를 사용하면
> `dict["key"]` 접근에 타입 안전성을 확보할 수 있습니다.
> 다만 Pydantic `BaseModel`이 런타임 검증까지 제공하므로,
> 런타임 안전성이 중요하면 Pydantic을 사용하세요.

---

## 7. `Callable` - 함수 타입

Java의 함수형 인터페이스(`Function<T, R>`, `Supplier<T>`, `Consumer<T>`)에 대응합니다.

```python
from typing import Callable

# Callable[[파라미터 타입들], 반환 타입]
def apply(func: Callable[[int], str], value: int) -> str:
    return func(value)

def apply_binary(
    func: Callable[[int, int], int],
    a: int,
    b: int
) -> int:
    return func(a, b)

result = apply(str, 42)              # "42"
result = apply_binary(max, 3, 7)     # 7

# Supplier<T> 대응 - 인자 없이 값을 생성
def lazy_load(supplier: Callable[[], str]) -> str:
    return supplier()

lazy_load(lambda: "hello")

# Consumer<T> 대응 - 반환값 없음
def for_each(items: list[str], consumer: Callable[[str], None]) -> None:
    for item in items:
        consumer(item)

for_each(["a", "b", "c"], print)

# 고차 함수 타입 힌트
def compose(
    f: Callable[[int], str],
    g: Callable[[str], bool]
) -> Callable[[int], bool]:
    def composed(x: int) -> bool:
        return g(f(x))
    return composed
```

```java
// Java 함수형 인터페이스
Function<Integer, String> func = String::valueOf;
BiFunction<Integer, Integer, Integer> binary = Math::max;
Supplier<String> supplier = () -> "hello";
Consumer<String> consumer = System.out::println;
```

### `ParamSpec` - 파라미터 스펙 (Python 3.10+)

데코레이터 작성 시 원래 함수의 시그니처를 보존할 때 사용합니다.

```python
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def log_call(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"호출: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"완료: {func.__name__}")
        return result
    return wrapper

@log_call
def add(a: int, b: int) -> int:  # 시그니처 보존됨
    return a + b

add(1, 2)  # IDE가 (a: int, b: int) -> int 로 인식
```

---

## 8. `Literal` - 리터럴 타입

Java의 `enum`처럼 허용되는 값을 제한합니다.
전체 enum 클래스를 정의하지 않고 허용 값을 인라인으로 지정할 때 유용합니다.

```python
from typing import Literal

# 허용되는 문자열 값 제한
Direction = Literal["north", "south", "east", "west"]
HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

def move(direction: Direction) -> None:
    print(f"{direction}으로 이동")

def send_request(method: HttpMethod, url: str) -> None:
    print(f"{method} {url}")

move("north")    # OK
move("up")       # mypy 오류: Literal 타입과 불일치

# 숫자 리터럴도 가능
StatusCode = Literal[200, 201, 400, 404, 500]

def handle_response(status: StatusCode) -> str:
    if status == 200:
        return "OK"
    elif status == 404:
        return "Not Found"
    return "Error"

# 조합
OpenMode = Literal["r", "w", "a", "rb", "wb"]

def open_file(path: str, mode: OpenMode) -> None:
    with open(path, mode) as f:
        ...
```

```java
// Java - enum으로 처리
public enum Direction { NORTH, SOUTH, EAST, WEST }
public enum HttpMethod { GET, POST, PUT, DELETE, PATCH }

public void move(Direction direction) { ... }
```

> **Literal vs Enum**: 외부 API와 통신하는 문자열 값(HTTP 메서드, 상태 문자열 등)은
> `Literal`이 편리합니다. 내부 비즈니스 로직의 상태 값은 `Enum` 클래스를 사용하는 것이 더 안전합니다.

---

## 9. `ClassVar` / `Final`

### `ClassVar` - 클래스 변수

```python
from typing import ClassVar

class Counter:
    # ClassVar: 인스턴스 변수가 아닌 클래스 변수
    count: ClassVar[int] = 0
    max_count: ClassVar[int] = 100

    def __init__(self, name: str) -> None:
        self.name = name         # 인스턴스 변수
        Counter.count += 1

c1 = Counter("c1")
c2 = Counter("c2")
print(Counter.count)  # 2
# c1.count = 5  # mypy 경고: ClassVar에 인스턴스를 통해 쓰기 금지
```

```java
// Java - static 필드
public class Counter {
    private static int count = 0;
    private static final int MAX_COUNT = 100;

    private final String name;

    public Counter(String name) {
        this.name = name;
        count++;
    }
}
```

### `Final` - 상수 / 재할당 금지

```python
from typing import Final

# 모듈 레벨 상수
MAX_RETRIES: Final = 3
API_BASE_URL: Final[str] = "https://api.example.com"

# 클래스 내 상수
class Config:
    DEFAULT_TIMEOUT: Final[int] = 30
    MAX_CONNECTIONS: Final[int] = 100

# Final 변수 재할당 시 mypy 오류
MAX_RETRIES = 5  # 오류: Cannot assign to final name "MAX_RETRIES"

# Final 클래스 - 상속 금지
from typing import final

@final
class Singleton:
    _instance: ClassVar["Singleton | None"] = None

    # @final 메서드 - 오버라이딩 금지
    @final
    def get_instance(self) -> "Singleton":
        ...
```

```java
// Java
public static final int MAX_RETRIES = 3;
public static final String API_BASE_URL = "https://api.example.com";

// final 클래스
public final class Singleton { ... }

// final 메서드
public final void criticalMethod() { ... }
```

---

## 10. `overload` - 오버로딩 시뮬레이션

Python은 런타임에서 메서드 오버로딩을 지원하지 않지만,
`@overload`로 타입 힌트 수준의 오버로딩을 표현할 수 있습니다.

```python
from typing import overload

# @overload는 타입 체커를 위한 시그니처만 선언
# 실제 구현은 마지막 함수 하나
@overload
def process(value: int) -> str: ...

@overload
def process(value: str) -> int: ...

@overload
def process(value: list[str]) -> dict[str, int]: ...

# 실제 구현 - @overload 없이
def process(value: int | str | list[str]) -> str | int | dict[str, int]:
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, str):
        return int(value)
    else:
        return {v: len(v) for v in value}

# 타입 체커가 각 호출의 반환 타입을 정확히 추론
result1: str = process(42)           # str 반환으로 추론
result2: int = process("100")        # int 반환으로 추론
result3: dict[str, int] = process(["hello", "world"])
```

```java
// Java - 실제 오버로딩
public String process(int value) { return String.valueOf(value); }
public int process(String value) { return Integer.parseInt(value); }
public Map<String, Integer> process(List<String> values) {
    return values.stream()
        .collect(Collectors.toMap(v -> v, String::length));
}
```

### 클래스 메서드 오버로딩

```python
from typing import overload

class Parser:
    @overload
    def parse(self, data: str) -> dict: ...

    @overload
    def parse(self, data: bytes) -> dict: ...

    def parse(self, data: str | bytes) -> dict:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        import json
        return json.loads(data)

parser = Parser()
result1 = parser.parse('{"key": "value"}')   # str -> dict
result2 = parser.parse(b'{"key": "value"}')  # bytes -> dict
```

---

## 타입 힌트 실전 패턴

### 타입 앨리어스 (Type Alias)

```python
from typing import TypeAlias

# Python 3.10+ 명시적 타입 앨리어스
UserId: TypeAlias = int
UserMap: TypeAlias = dict[UserId, str]
Matrix: TypeAlias = list[list[float]]

def get_user(user_id: UserId) -> str | None:
    ...

# 복잡한 타입을 단순화
JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
```

### `Self` 타입 (Python 3.11+)

```python
from typing import Self

class Builder:
    def __init__(self) -> None:
        self._value = 0

    def set_value(self, value: int) -> Self:  # 서브클래스에서도 올바른 타입 반환
        self._value = value
        return self

    def build(self) -> int:
        return self._value

class AdvancedBuilder(Builder):
    def set_name(self, name: str) -> Self:
        ...
        return self

# 체이닝 시 타입이 올바르게 추론됨
result = AdvancedBuilder().set_value(10).set_name("test").build()
```

### 런타임 타입 체크 주의사항

```python
from typing import get_type_hints

class User:
    name: str
    age: int

# 런타임에 타입 힌트 조회
hints = get_type_hints(User)
print(hints)  # {'name': <class 'str'>, 'age': <class 'int'>}

# 타입 힌트는 런타임 강제가 아님
def greet(name: str) -> None:
    print(f"Hello, {name}")

greet(42)    # 런타임 오류 없음! 타입 힌트는 무시됨
             # mypy/pyright만 정적으로 오류를 잡음
```

---

## 정리: Java 타입 시스템과 비교

| Java | Python typing | 비고 |
|------|---------------|------|
| `List<String>` | `list[str]` | Python 3.9+ 소문자 사용 |
| `Map<String, Integer>` | `dict[str, int]` | |
| `Optional<T>` | `T \| None` | Python은 런타임 래퍼 없음 |
| `T extends Foo` | `TypeVar("T", bound=Foo)` | 타입 경계 |
| `<T>` 제네릭 | `Generic[T]` | 클래스 제네릭 |
| `interface Foo` | `Protocol` | 구조적 타이핑 (implements 불필요) |
| `abstract class` | `ABC` | 명시적 상속 필요 |
| `Object` | `Any` | 남용 금지 |
| `static final` | `Final` + `ClassVar` | |
| `final class` | `@final` 데코레이터 | |
| `Function<T, R>` | `Callable[[T], R]` | |
| `enum` | `Literal` 또는 `Enum` | |
| `record` | `@dataclass(frozen=True)` | |
