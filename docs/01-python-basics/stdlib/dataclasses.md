# dataclasses - 데이터 클래스

> 공식 문서: https://docs.python.org/3/library/dataclasses.html

`dataclasses` 모듈은 데이터를 담는 클래스를 간결하게 작성할 수 있게 해줍니다.
Java의 Lombok `@Data` 또는 Java 16+ `record`와 유사하게,
`__init__`, `__repr__`, `__eq__` 같은 보일러플레이트 메서드를 자동으로 생성합니다.

---

## 1. `@dataclass` 기본

### Java record / Lombok @Data와 비교

```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str

# 자동 생성되는 메서드들
user1 = User(id=1, name="Alice", email="alice@example.com")
user2 = User(id=1, name="Alice", email="alice@example.com")

print(user1)              # User(id=1, name='Alice', email='alice@example.com')
print(user1 == user2)     # True  - __eq__ 자동 생성
print(repr(user1))        # User(id=1, name='Alice', email='alice@example.com')

# 필드 접근 - getter 없이 직접 접근
print(user1.name)         # "Alice"
user1.name = "Bob"        # 기본은 가변(mutable)
```

```java
// Java 16+ record - 불변, getter 자동 생성
public record User(long id, String name, String email) {}

User user1 = new User(1L, "Alice", "alice@example.com");
User user2 = new User(1L, "Alice", "alice@example.com");
System.out.println(user1);           // User[id=1, name=Alice, email=alice@example.com]
System.out.println(user1.equals(user2)); // true
System.out.println(user1.name());    // "Alice" - getter 자동 생성
```

```java
// Lombok @Data - 가변, getter/setter 자동 생성
@Data
public class User {
    private long id;
    private String name;
    private String email;
}

// Lombok @Value - 불변
@Value
public class User {
    long id;
    String name;
    String email;
}
```

### 자동 생성 메서드 목록

| 메서드 | 생성 여부 | Java 대응 |
|--------|-----------|-----------|
| `__init__` | 항상 | 생성자 |
| `__repr__` | 항상 | `toString()` |
| `__eq__` | `eq=True` (기본값) | `equals()` |
| `__hash__` | `frozen=True` 또는 `eq=False`일 때 | `hashCode()` |
| `__lt__`, `__le__`, `__gt__`, `__ge__` | `order=True`일 때 | `Comparable` |

---

## 2. `field()` - 필드 세부 설정

### 기본값과 `default_factory`

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Order:
    order_id: int
    status: str = "pending"                    # 단순 기본값
    tags: list[str] = field(default_factory=list)   # 가변 기본값 - 필수!
    metadata: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

order1 = Order(order_id=1)
order2 = Order(order_id=2)
order1.tags.append("urgent")
print(order1.tags)  # ["urgent"]
print(order2.tags)  # []  - 각 인스턴스가 독립된 list를 가짐
```

> **함정 주의**: `tags: list[str] = []` 처럼 가변 객체를 직접 기본값으로 사용하면
> 모든 인스턴스가 같은 객체를 공유합니다. Java에서 `static List<String> tags = new ArrayList<>()`와
> 동일한 문제입니다. 반드시 `default_factory`를 사용하세요.

```python
# 잘못된 예시 - 모든 인스턴스가 같은 list 공유 (dataclass가 오류 발생시킴)
@dataclass
class BadOrder:
    tags: list[str] = []  # ValueError: mutable default is not allowed
```

### `repr=False` - 민감 정보 숨기기

```python
from dataclasses import dataclass, field

@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str = field(repr=False)   # repr에서 제외 - 로그에 비밀번호 노출 방지
    api_key: str = field(repr=False)

config = DatabaseConfig(
    host="localhost",
    port=5432,
    username="admin",
    password="secret123",
    api_key="sk-xxxx"
)
print(config)
# DatabaseConfig(host='localhost', port=5432, username='admin')
# password와 api_key는 출력되지 않음
```

```java
// Java Lombok - @ToString.Exclude
@Data
public class DatabaseConfig {
    private String host;
    private int port;
    private String username;
    @ToString.Exclude private String password;
    @ToString.Exclude private String apiKey;
}
```

### `compare=False` - 비교에서 제외

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Entity:
    id: int
    name: str
    # 타임스탬프는 동등 비교에서 제외
    created_at: datetime = field(
        default_factory=datetime.now,
        compare=False
    )
    updated_at: datetime = field(
        default_factory=datetime.now,
        compare=False,
        repr=False
    )

e1 = Entity(id=1, name="Alice")
e2 = Entity(id=1, name="Alice")
print(e1 == e2)  # True - created_at 차이 무시
```

### `init=False` - 생성자 파라미터 제외

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AuditLog:
    action: str
    user_id: int
    # 생성자에 파라미터 없음, __post_init__에서 설정
    timestamp: datetime = field(init=False, default_factory=datetime.now)
    log_id: str = field(init=False)

    def __post_init__(self) -> None:
        import uuid
        self.log_id = str(uuid.uuid4())

log = AuditLog(action="LOGIN", user_id=42)
# log = AuditLog(action="LOGIN", user_id=42, timestamp=...)  # TypeError!
print(log.log_id)    # 자동 생성된 UUID
```

---

## 3. `@dataclass` 파라미터

### `frozen=True` - 불변 객체

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

p = Point(3.0, 4.0)
print(p.distance_from_origin())  # 5.0

p.x = 10.0  # FrozenInstanceError: cannot assign to field 'x'

# frozen=True이면 __hash__가 자동 생성됨 -> dict key, set 원소로 사용 가능
points = {Point(0, 0), Point(1, 1), Point(0, 0)}
print(len(points))  # 2 - 중복 제거됨
```

```java
// Java record - 불변
public record Point(double x, double y) {
    public double distanceFromOrigin() {
        return Math.sqrt(x * x + y * y);
    }
}
// record는 자동으로 equals, hashCode 구현
```

### `order=True` - 비교 연산자 자동 생성

```python
from dataclasses import dataclass

@dataclass(order=True)
class Version:
    major: int
    minor: int
    patch: int

v1 = Version(1, 2, 3)
v2 = Version(1, 3, 0)
v3 = Version(2, 0, 0)

print(v1 < v2)   # True  - 필드 순서대로 비교 (major -> minor -> patch)
print(v2 < v3)   # True
versions = [v3, v1, v2]
print(sorted(versions))
# [Version(major=1, minor=2, patch=3),
#  Version(major=1, minor=3, patch=0),
#  Version(major=2, minor=0, patch=0)]
```

```java
// Java - Comparable 구현 필요
public record Version(int major, int minor, int patch)
        implements Comparable<Version> {
    @Override
    public int compareTo(Version other) {
        int c = Integer.compare(this.major, other.major);
        if (c != 0) return c;
        c = Integer.compare(this.minor, other.minor);
        if (c != 0) return c;
        return Integer.compare(this.patch, other.patch);
    }
}
```

### `slots=True` - 메모리 최적화 (Python 3.10+)

```python
from dataclasses import dataclass
import sys

@dataclass
class RegularPoint:
    x: float
    y: float

@dataclass(slots=True)  # __slots__ 자동 생성
class SlottedPoint:
    x: float
    y: float

r = RegularPoint(1.0, 2.0)
s = SlottedPoint(1.0, 2.0)

print(sys.getsizeof(r))  # 약 48 bytes (dict 포함)
print(sys.getsizeof(s))  # 약 40 bytes (slots 사용)

# slots=True이면 동적 속성 추가 불가
s.z = 3.0  # AttributeError: 'SlottedPoint' object has no attribute 'z'
```

> **성능 팁**: 대량의 객체를 생성하는 경우 `slots=True`로 메모리 절약과 속도 향상 가능합니다.
> Java의 값 타입(Value Type, Project Valhalla)과 유사한 효과입니다.

### `eq=False` - 동등성 비교 비활성화

```python
from dataclasses import dataclass

@dataclass(eq=False)  # __eq__ 자동 생성 안 함 -> 기본 object identity 비교
class Service:
    name: str
    host: str

s1 = Service("web", "localhost")
s2 = Service("web", "localhost")
print(s1 == s2)  # False - 같은 데이터지만 다른 객체
print(s1 is s1)  # True
```

---

## 4. `__post_init__` - 생성자 후처리

`__init__` 실행 후 자동으로 호출됩니다. Java 생성자 내 검증 로직이나 계산 필드 초기화에 대응합니다.

```python
from dataclasses import dataclass, field

@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)  # 생성자 파라미터 제외

    def __post_init__(self) -> None:
        # 검증
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"너비와 높이는 양수여야 합니다: width={self.width}, height={self.height}")
        # 계산 필드 초기화
        self.area = self.width * self.height

r = Rectangle(width=3.0, height=4.0)
print(r.area)   # 12.0

Rectangle(width=-1, height=4)  # ValueError 발생
```

```java
// Java 생성자 내 검증
public record Rectangle(double width, double height) {
    // compact constructor (Java 16+)
    public Rectangle {
        if (width <= 0 || height <= 0) {
            throw new IllegalArgumentException("너비와 높이는 양수여야 합니다");
        }
    }

    public double area() { return width * height; }
}
```

### `InitVar` - 초기화 전용 파라미터

```python
from dataclasses import dataclass, field
from typing import ClassVar
from dataclasses import InitVar

@dataclass
class HashedPassword:
    raw_password: InitVar[str]    # __init__에는 있지만 필드로 저장되지 않음
    hashed: str = field(init=False)

    def __post_init__(self, raw_password: str) -> None:
        import hashlib
        self.hashed = hashlib.sha256(raw_password.encode()).hexdigest()

user = HashedPassword(raw_password="secret123")
print(user.hashed)        # SHA-256 해시값
# user.raw_password       # AttributeError - 필드 없음
print(user)               # HashedPassword(hashed='...')
```

---

## 5. 상속

### 기본 상속

```python
from dataclasses import dataclass

@dataclass
class Animal:
    name: str
    species: str

@dataclass
class Dog(Animal):
    breed: str
    age: int = 0

dog = Dog(name="Max", species="Canis lupus", breed="Labrador", age=3)
print(dog)
# Dog(name='Max', species='Canis lupus', breed='Labrador', age=3)
```

### 기본값 순서 문제 주의

```python
from dataclasses import dataclass, field

# 문제 상황: 부모에 기본값 있는 필드가 있으면 자식의 필수 필드 추가 불가
@dataclass
class Parent:
    name: str
    value: int = 0  # 기본값 있음

# @dataclass
# class Child(Parent):
#     extra: str  # TypeError! 기본값 없는 필드가 기본값 있는 필드 뒤에 올 수 없음

# 해결법 1: 자식도 기본값 제공
@dataclass
class Child1(Parent):
    extra: str = ""

# 해결법 2: kw_only 사용 (Python 3.10+)
@dataclass(kw_only=True)
class Child2(Parent):
    extra: str  # keyword-only이므로 위치 무관

c = Child2(name="test", extra="hello")  # 모두 키워드 인자로
```

### `kw_only` 파라미터

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    host: str
    port: int
    # keyword-only 필드들
    timeout: int = field(default=30, kw_only=True)
    max_retries: int = field(default=3, kw_only=True)

# host, port는 위치 인자 가능, timeout/max_retries는 키워드만
config = Config("localhost", 5432, timeout=60, max_retries=5)
config2 = Config("localhost", 5432)  # timeout=30, max_retries=3 (기본값)
```

---

## 6. `asdict()` / `astuple()` - 직렬화

### JSON 직렬화 패턴

```python
from dataclasses import dataclass, field, asdict, astuple
import json
from datetime import datetime

@dataclass
class Address:
    street: str
    city: str
    country: str = "KR"

@dataclass
class User:
    id: int
    name: str
    address: Address
    tags: list[str] = field(default_factory=list)

user = User(
    id=1,
    name="Alice",
    address=Address(street="테헤란로 123", city="서울"),
    tags=["admin", "user"]
)

# asdict - 중첩 dataclass도 재귀적으로 dict 변환
user_dict = asdict(user)
print(user_dict)
# {
#   'id': 1,
#   'name': 'Alice',
#   'address': {'street': '테헤란로 123', 'city': '서울', 'country': 'KR'},
#   'tags': ['admin', 'user']
# }

# JSON 직렬화
json_str = json.dumps(user_dict, ensure_ascii=False)

# astuple
user_tuple = astuple(user)
print(user_tuple)  # (1, 'Alice', ('테헤란로 123', '서울', 'KR'), ['admin', 'user'])
```

### datetime 포함 시 직렬화 커스터마이징

```python
from dataclasses import dataclass, asdict
from datetime import datetime
import json

@dataclass
class Event:
    name: str
    occurred_at: datetime

event = Event(name="login", occurred_at=datetime.now())

# datetime은 JSON 직렬화 불가 - 커스텀 처리 필요
def serialize_event(e: Event) -> dict:
    d = asdict(e)
    d["occurred_at"] = d["occurred_at"].isoformat()  # ISO 8601 형식으로 변환
    return d

json.dumps(serialize_event(event))  # OK
```

---

## 7. dataclass vs Pydantic BaseModel 비교

실무에서 어떤 것을 선택할지는 요구사항에 따라 다릅니다.

### 비교표

| 항목 | `@dataclass` | Pydantic `BaseModel` |
|------|--------------|---------------------|
| 표준 라이브러리 | 예 (별도 설치 불필요) | 아니오 (`pip install pydantic`) |
| 런타임 타입 검증 | 없음 | 있음 (엄격한 검증) |
| 자동 타입 변환 | 없음 | 있음 (`"42"` -> `42`) |
| JSON 직렬화 | `asdict()` + `json.dumps()` | `.model_dump_json()` |
| JSON 역직렬화 | 수동 | `.model_validate()` / `.model_validate_json()` |
| `validators` | `__post_init__` | `@field_validator`, `@model_validator` |
| 성능 | 빠름 | 상대적으로 느림 (검증 비용) |
| FastAPI 통합 | 제한적 | 완전 통합 |
| 설정 / 환경변수 | 직접 구현 | `pydantic-settings` |

### `@dataclass` 사용 권장 상황

```python
from dataclasses import dataclass

# 1. 내부 데이터 구조 - 신뢰할 수 있는 데이터, 검증 불필요
@dataclass
class InternalConfig:
    host: str
    port: int
    debug: bool = False

# 2. 값 객체 (Value Object) - 불변, 동등성 비교
@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "KRW"

# 3. 경량 DTO - 레이어 간 데이터 전달
@dataclass
class UserDTO:
    id: int
    name: str
```

### Pydantic `BaseModel` 사용 권장 상황

```python
from pydantic import BaseModel, field_validator, EmailStr

# 1. API 요청/응답 모델 - 외부 입력 검증 필수
class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr         # 이메일 형식 검증
    age: int                # "30" 문자열이 와도 자동으로 30 int로 변환

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 0 or v > 150:
            raise ValueError("나이는 0~150 사이여야 합니다")
        return v

# 2. 설정 파일 / 환경변수 파싱
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

# 3. FastAPI 엔드포인트
from fastapi import FastAPI

app = FastAPI()

@app.post("/users")
async def create_user(request: CreateUserRequest):  # 자동 검증 + 문서화
    ...
```

### 혼용 패턴

```python
from dataclasses import dataclass
from pydantic import BaseModel

# API 입력은 Pydantic (검증)
class CreateOrderRequest(BaseModel):
    product_id: int
    quantity: int
    user_id: int

# 내부 도메인 객체는 dataclass (빠름)
@dataclass
class Order:
    order_id: str
    product_id: int
    quantity: int
    total_price: float

# 변환
def to_order(req: CreateOrderRequest, price: float) -> Order:
    return Order(
        order_id=generate_id(),
        product_id=req.product_id,
        quantity=req.quantity,
        total_price=price * req.quantity,
    )
```
