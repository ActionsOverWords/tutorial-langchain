# enum - 열거형

> 공식 문서: https://docs.python.org/3/library/enum.html

Python의 `enum` 모듈은 Java의 `enum` 타입과 매우 유사합니다. 상수 집합을 타입 안전하게 표현하고, 메서드 추가, 값 검색 등을 지원합니다. Pydantic/FastAPI와의 통합도 자연스러워 API 스키마 정의에 널리 사용됩니다.

---

## 1. 기본 `Enum`

### Python

```python
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

# 멤버 접근
color = Color.RED
print(color)         # Color.RED
print(color.name)    # 'RED'    (Java: color.name())
print(color.value)   # 1       (Java: color.ordinal() 또는 커스텀 getValue())
print(type(color))   # <enum 'Color'>

# 값으로 멤버 조회
c = Color(2)
print(c)             # Color.GREEN

# 이름으로 멤버 조회
c = Color["BLUE"]
print(c)             # Color.BLUE

# 비교
print(color == Color.RED)    # True
print(color is Color.RED)    # True (enum은 싱글턴)
print(color == 1)            # False (기본 Enum은 값과 직접 비교 불가)
```

**Java 비교:**

```java
public enum Color {
    RED, GREEN, BLUE;
}

Color color = Color.RED;
System.out.println(color.name());    // "RED"
System.out.println(color.ordinal()); // 0 (Python .value와 다름: Java는 선언 순서)

// 이름으로 조회
Color c = Color.valueOf("BLUE");     // Color["BLUE"]에 해당
```

### 모든 멤버 열거

```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"

# 모든 멤버 순회
for status in Status:
    print(f"{status.name}: {status.value}")
# PENDING: pending
# ACTIVE: active
# INACTIVE: inactive

# 리스트 변환
all_statuses = list(Status)
print(all_statuses)  # [<Status.PENDING: 'pending'>, ...]

# 값 리스트
values = [s.value for s in Status]
print(values)  # ['pending', 'active', 'inactive']
```

**Java 비교:**

```java
// Java - values() 메서드
for (Status s : Status.values()) {
    System.out.println(s.name() + ": " + s.getValue());
}
```

---

## 2. `IntEnum` / `StrEnum`

### `IntEnum` - 정수와 직접 비교 가능

```python
from enum import IntEnum

class HttpStatus(IntEnum):
    OK = 200
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

status = HttpStatus.OK

# IntEnum은 int의 서브클래스이므로 정수와 직접 비교 가능
print(status == 200)       # True (기본 Enum은 False)
print(status > 400)        # False
print(status + 0)          # 200 (산술 연산도 가능)

# 딕셔너리 키로 사용 시 정수와 동일하게 동작
response_map = {200: "성공", 404: "미발견"}
print(response_map[HttpStatus.OK])  # "성공"
```

**Java 비교:**

```java
// Java enum에서 int 값 가져오기 (getValue() 직접 정의)
public enum HttpStatus {
    OK(200), NOT_FOUND(404), INTERNAL_ERROR(500);

    private final int code;
    HttpStatus(int code) { this.code = code; }
    public int getValue() { return code; }
}

// Java는 enum과 int를 직접 비교 불가; getValue()를 통해 비교
HttpStatus.OK.getValue() == 200  // true
```

### `StrEnum` - 문자열과 직접 비교 가능 (Python 3.11+)

```python
from enum import StrEnum

class Direction(StrEnum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

d = Direction.NORTH

# str의 서브클래스
print(d == "north")       # True
print(d.upper())          # "NORTH" (str 메서드 사용 가능)
print(f"방향: {d}")       # "방향: north" (자동으로 value 출력)

# Python 3.10 이하에서는 str + Enum 믹스인으로 동일 효과
class DirectionCompat(str, Enum):
    NORTH = "north"
    SOUTH = "south"
```

> Pydantic/FastAPI에서 API 응답에 문자열 값을 직접 사용할 때 `StrEnum` 또는 `str, Enum` 믹스인이 자주 사용됩니다.

---

## 3. `auto()` - 자동 값 할당

```python
from enum import Enum, auto

class Permission(Enum):
    READ = auto()    # 1
    WRITE = auto()   # 2
    DELETE = auto()  # 3
    ADMIN = auto()   # 4

print(Permission.READ.value)    # 1
print(Permission.WRITE.value)   # 2
```

**Java 비교:**

```java
// Java enum의 ordinal() - 0부터 시작
public enum Permission {
    READ, WRITE, DELETE, ADMIN
}
Permission.READ.ordinal()   // 0 (Python auto()는 1부터 시작)
Permission.WRITE.ordinal()  // 1
```

> Python `auto()`는 기본적으로 1부터 증가합니다. Java `ordinal()`은 0부터 시작하는 점이 다릅니다.

### `auto()` 동작 커스터마이징

```python
from enum import Enum, auto

class UpperStrEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        # auto() 호출 시 멤버 이름을 소문자로 사용
        return name.lower()

class Color(UpperStrEnum):
    RED = auto()    # 'red'
    GREEN = auto()  # 'green'
    BLUE = auto()   # 'blue'

print(Color.RED.value)  # 'red'
```

---

## 4. `@unique` - 중복 값 방지

```python
from enum import Enum, unique

# @unique: 동일한 값을 가진 멤버가 있으면 ValueError 발생
@unique
class Status(Enum):
    ACTIVE = 1
    INACTIVE = 2
    # DELETED = 1  # ValueError: duplicate values found in <enum 'Status'>: DELETED -> ACTIVE

# @unique 없이 중복 값 사용 시 - alias(별칭)로 처리됨
class StatusWithAlias(Enum):
    ACTIVE = 1
    ENABLED = 1  # ACTIVE의 별칭 (alias)

print(StatusWithAlias.ACTIVE is StatusWithAlias.ENABLED)  # True
print(list(StatusWithAlias))  # [<StatusWithAlias.ACTIVE: 1>] (별칭은 제외됨)
```

**Java 비교:**

```java
// Java는 enum 값 중복 자체가 문법적으로 불가능
// 각 상수는 독립적이며 ordinal()도 고유
```

---

## 5. 메서드 추가

Python enum에 메서드를 추가하는 것은 Java와 매우 유사합니다.

```python
from enum import Enum

class Planet(Enum):
    MERCURY = (3.303e+23, 2.4397e6)
    VENUS   = (4.869e+24, 6.0518e6)
    EARTH   = (5.976e+24, 6.37814e6)

    def __init__(self, mass: float, radius: float):
        self.mass = mass
        self.radius = radius

    @property
    def surface_gravity(self) -> float:
        G = 6.67430e-11
        return G * self.mass / (self.radius ** 2)

    def weight_on(self, earth_weight: float) -> float:
        return earth_weight * self.surface_gravity / Planet.EARTH.surface_gravity

    def __str__(self) -> str:
        return f"{self.name} (중력: {self.surface_gravity:.2f} m/s²)"

print(Planet.EARTH)                         # EARTH (중력: 9.80 m/s²)
print(Planet.MARS if hasattr(Planet, 'MARS') else "없음")
print(Planet.MERCURY.weight_on(75))         # 수성에서의 체중
```

**Java 비교:**

```java
public enum Planet {
    MERCURY(3.303e+23, 2.4397e6),
    VENUS(4.869e+24, 6.0518e6),
    EARTH(5.976e+24, 6.37814e6);

    private final double mass;
    private final double radius;
    static final double G = 6.67430e-11;

    Planet(double mass, double radius) {
        this.mass = mass;
        this.radius = radius;
    }

    double surfaceGravity() {
        return G * mass / (radius * radius);
    }

    double weightOn(double earthWeight) {
        return earthWeight * surfaceGravity() / EARTH.surfaceGravity();
    }
}
```

### 상태 전이 로직 포함

```python
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    def can_transition_to(self, next_status: "OrderStatus") -> bool:
        """허용된 상태 전이 검증"""
        transitions = {
            OrderStatus.PENDING:   {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
            OrderStatus.CONFIRMED: {OrderStatus.SHIPPED,   OrderStatus.CANCELLED},
            OrderStatus.SHIPPED:   {OrderStatus.DELIVERED},
            OrderStatus.DELIVERED: set(),
            OrderStatus.CANCELLED: set(),
        }
        return next_status in transitions[self]

    @property
    def is_terminal(self) -> bool:
        return self in {OrderStatus.DELIVERED, OrderStatus.CANCELLED}

status = OrderStatus.PENDING
print(status.can_transition_to(OrderStatus.CONFIRMED))  # True
print(status.can_transition_to(OrderStatus.SHIPPED))    # False
```

---

## 6. Pydantic + FastAPI에서 enum 사용

### 기본 통합

```python
from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserCreate(BaseModel):
    name: str
    role: UserRole = UserRole.USER  # 기본값 설정

class UserResponse(BaseModel):
    id: int
    name: str
    role: UserRole

app = FastAPI()

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    # user.role은 UserRole enum 타입
    print(user.role)          # UserRole.ADMIN
    print(user.role.value)    # 'admin'

    return UserResponse(id=1, name=user.name, role=user.role)
```

### Swagger UI에서 드롭다운 표시

`str, Enum` 또는 `StrEnum`을 사용하면 Swagger UI에서 자동으로 드롭다운 선택기로 표시됩니다.

```
POST /users
Request body:
{
  "name": "홍길동",
  "role": "admin"  ← Swagger UI에서 [admin, user, guest] 드롭다운
}
```

### 쿼리 파라미터에서 enum 사용

```python
from enum import Enum
from fastapi import FastAPI

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class FilterStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ALL = "all"

app = FastAPI()

@app.get("/users")
def list_users(
    sort: SortOrder = SortOrder.ASC,
    status: FilterStatus = FilterStatus.ALL,
):
    # GET /users?sort=desc&status=active
    return {"sort": sort, "status": status}
```

### 응답에서 enum 값 직렬화

```python
from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Item(BaseModel):
    name: str
    status: Status

    class Config:
        # enum 값을 문자열로 직렬화 (기본 동작)
        use_enum_values = True

app = FastAPI()

@app.get("/item")
def get_item():
    item = Item(name="테스트", status=Status.ACTIVE)
    return item
# 응답: {"name": "테스트", "status": "active"}
# use_enum_values=True가 없으면: {"name": "테스트", "status": "active"} (str, Enum의 경우 동일)
```

### DB 모델과 enum 통합 (SQLAlchemy)

```python
from enum import Enum as PyEnum
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class UserRole(str, PyEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100))
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole, name="user_role"),  # DB에 ENUM 타입 생성
        default=UserRole.USER,
    )
```

---

## 7. `Flag` - 비트 플래그

여러 옵션을 OR 연산으로 조합할 수 있는 비트 플래그 enum입니다.

### 기본 사용

```python
from enum import Flag, auto

class Permission(Flag):
    NONE    = 0
    READ    = auto()   # 1 (0b0001)
    WRITE   = auto()   # 2 (0b0010)
    EXECUTE = auto()   # 4 (0b0100)
    DELETE  = auto()   # 8 (0b1000)

    # 복합 플래그 정의
    READ_WRITE = READ | WRITE         # 3  (0b0011)
    ALL = READ | WRITE | EXECUTE | DELETE  # 15 (0b1111)

# 플래그 조합
user_perm = Permission.READ | Permission.WRITE
print(user_perm)                        # Permission.READ|WRITE
print(Permission.READ in user_perm)     # True
print(Permission.DELETE in user_perm)   # False

# 플래그 제거
user_perm &= ~Permission.WRITE
print(user_perm)                        # Permission.READ

# 교집합
admin_perm = Permission.ALL
common = user_perm & admin_perm
print(common)                           # Permission.READ
```

**Java `EnumSet` 비교:**

```java
import java.util.EnumSet;

public enum Permission {
    READ, WRITE, EXECUTE, DELETE
}

// EnumSet으로 비트 플래그 효과
EnumSet<Permission> userPerm = EnumSet.of(Permission.READ, Permission.WRITE);
boolean canRead = userPerm.contains(Permission.READ);    // true
boolean canDelete = userPerm.contains(Permission.DELETE); // false

userPerm.remove(Permission.WRITE);  // 플래그 제거

EnumSet<Permission> adminPerm = EnumSet.allOf(Permission.class);
EnumSet<Permission> common = EnumSet.copyOf(userPerm);
common.retainAll(adminPerm);  // 교집합
```

### `IntFlag` - 정수와 직접 연산 가능

```python
from enum import IntFlag, auto

class FileMode(IntFlag):
    R = 4   # os.access 방식 (POSIX 권한)
    W = 2
    X = 1

mode = FileMode.R | FileMode.W
print(mode)          # FileMode.R|W
print(int(mode))     # 6
print(mode & 4)      # FileMode.R (정수와 비트 연산 가능)

# POSIX 권한 파싱
import stat
file_mode = stat.S_IRUSR | stat.S_IWUSR  # 소유자 읽기+쓰기
```

### 실전 예시 - API 권한 체계

```python
from enum import Flag, auto
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class ApiPermission(Flag):
    NONE    = 0
    READ    = auto()
    WRITE   = auto()
    DELETE  = auto()
    ADMIN   = READ | WRITE | DELETE

class ApiKey(BaseModel):
    key: str
    permissions: int  # Flag 값을 정수로 저장

def check_permission(api_key: ApiKey, required: ApiPermission) -> bool:
    current = ApiPermission(api_key.permissions)
    return required in current

# 사용 예
key = ApiKey(key="abc123", permissions=int(ApiPermission.READ | ApiPermission.WRITE))
print(check_permission(key, ApiPermission.READ))    # True
print(check_permission(key, ApiPermission.DELETE))  # False
print(check_permission(key, ApiPermission.ADMIN))   # False
```

---

## 요약 비교표

| Java enum 기능                     | Python 대응                              |
|------------------------------------|------------------------------------------|
| `enum MyEnum { A, B, C }`          | `class MyEnum(Enum): A = 1`             |
| `MyEnum.A.name()`                  | `MyEnum.A.name`                          |
| `MyEnum.A.ordinal()`               | `MyEnum.A.value` (auto() 사용 시 유사)   |
| `MyEnum.valueOf("A")`              | `MyEnum["A"]`                            |
| `MyEnum.values()`                  | `list(MyEnum)`                           |
| `enum`에 메서드 추가               | 클래스 메서드 정의 (동일)                |
| `EnumSet`                          | `Flag` / `IntFlag`                       |
| `int` 직접 비교 (`getValue()`)     | `IntEnum`                                |
| `String` 직접 비교                 | `StrEnum` 또는 `str, Enum` 믹스인        |
| 중복 방지 (언어 레벨)              | `@unique` 데코레이터                     |
| `@JsonValue` (Jackson)             | `str, Enum` + Pydantic 자동 처리         |
