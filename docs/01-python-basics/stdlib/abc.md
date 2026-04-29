# abc - 추상 클래스

> 공식 문서: https://docs.python.org/3/library/abc.html

`abc` 모듈(Abstract Base Classes)은 Python에서 추상 클래스와 추상 메서드를 정의하는 공식 메커니즘입니다.
Java의 `abstract class` + `interface`와 유사하지만,
Python에는 별도의 `interface` 키워드가 없어 `ABC`와 `Protocol` 두 가지 방식으로 분담합니다.

---

## 1. `ABC` / `ABCMeta`

### 기본 사용법

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    """도형의 추상 베이스 클래스"""

    def __init__(self, color: str = "black") -> None:
        self.color = color  # 공통 상태 - 구체 클래스와 공유

    @abstractmethod
    def area(self) -> float:
        """면적 계산 - 반드시 구현해야 함"""
        ...

    @abstractmethod
    def perimeter(self) -> float:
        """둘레 계산 - 반드시 구현해야 함"""
        ...

    # 일반 메서드는 그대로 상속 가능
    def describe(self) -> str:
        return f"{self.color} {type(self).__name__}: 면적={self.area():.2f}"

# 추상 클래스는 직접 인스턴스화 불가
# shape = Shape()  # TypeError: Can't instantiate abstract class Shape
```

```java
// Java abstract class
public abstract class Shape {
    protected String color;

    public Shape(String color) {
        this.color = color;
    }

    public abstract double area();
    public abstract double perimeter();

    public String describe() {
        return color + " " + getClass().getSimpleName() + ": 면적=" + String.format("%.2f", area());
    }
}
```

### 구체 클래스 구현

```python
import math
from abc import ABC, abstractmethod

class Shape(ABC):
    def __init__(self, color: str = "black") -> None:
        self.color = color

    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

class Circle(Shape):
    def __init__(self, radius: float, color: str = "black") -> None:
        super().__init__(color)
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius

class Rectangle(Shape):
    def __init__(self, width: float, height: float, color: str = "black") -> None:
        super().__init__(color)
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

c = Circle(radius=5.0, color="red")
r = Rectangle(width=3.0, height=4.0)
print(c.describe())   # red Circle: 면적=78.54
print(r.describe())   # black Rectangle: 면적=12.00
```

### `ABCMeta` - 메타클래스 직접 사용

`ABC`는 내부적으로 `ABCMeta`를 사용하는 편의 클래스입니다.
다른 메타클래스와 충돌이 있을 때 직접 `ABCMeta`를 사용합니다.

```python
from abc import ABCMeta, abstractmethod

# ABC 상속 방식 (일반적)
class MyABC(ABC):
    @abstractmethod
    def do_something(self) -> None: ...

# ABCMeta 직접 사용 방식 (다중 상속 충돌 해결 시)
class MyABC(metaclass=ABCMeta):
    @abstractmethod
    def do_something(self) -> None: ...

# 다른 메타클래스와 혼용 시
class OtherMeta(type): ...

class CombinedMeta(ABCMeta, OtherMeta): ...  # 메타클래스 합성

class MyClass(metaclass=CombinedMeta):
    @abstractmethod
    def do_something(self) -> None: ...
```

---

## 2. `@abstractmethod`

### 구현하지 않으면 `TypeError` 발생

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self) -> str: ...

    @abstractmethod
    def move(self) -> None: ...

class Cat(Animal):
    def speak(self) -> str:
        return "야옹"
    # move()를 구현하지 않음

# Cat은 move()를 구현하지 않았으므로 인스턴스화 불가
# cat = Cat()  # TypeError: Can't instantiate abstract class Cat
#              # with abstract method move

class FullCat(Animal):
    def speak(self) -> str:
        return "야옹"

    def move(self) -> None:
        print("걷기")

cat = FullCat()  # OK
```

```java
// Java - 컴파일 타임에 오류 발생
abstract class Animal {
    public abstract String speak();
    public abstract void move();
}

class Cat extends Animal {
    @Override
    public String speak() { return "야옹"; }
    // move() 미구현 -> 컴파일 오류
}
```

> **차이점**: Java는 컴파일 타임에 오류를 잡지만, Python은 클래스 정의 시점이 아닌
> **인스턴스화 시점**에 `TypeError`가 발생합니다.

### 부분 구현 허용 - super() 호출

```python
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    @abstractmethod
    def process(self, data: str) -> str:
        # 추상 메서드도 기본 구현을 가질 수 있음
        return data.strip()  # 기본 전처리

class TrimProcessor(BaseProcessor):
    def process(self, data: str) -> str:
        data = super().process(data)  # 부모의 추상 메서드 구현 호출
        return data.lower()

p = TrimProcessor()
print(p.process("  Hello World  "))  # "hello world"
```

---

## 3. `@abstractproperty` / `@abstractclassmethod`

### `@abstractmethod` + `@property` 조합

Python 3.3부터 `@abstractproperty`는 deprecated되었습니다.
`@abstractmethod`와 `@property`를 조합해서 사용합니다.

```python
from abc import ABC, abstractmethod

class Vehicle(ABC):
    @property
    @abstractmethod
    def max_speed(self) -> float:
        """최고 속도 (km/h) - 반드시 property로 구현"""
        ...

    @property
    @abstractmethod
    def fuel_type(self) -> str:
        """연료 타입 - 반드시 property로 구현"""
        ...

class ElectricCar(Vehicle):
    @property
    def max_speed(self) -> float:
        return 250.0

    @property
    def fuel_type(self) -> str:
        return "electric"

class GasCar(Vehicle):
    @property
    def max_speed(self) -> float:
        return 200.0

    @property
    def fuel_type(self) -> str:
        return "gasoline"

car = ElectricCar()
print(car.max_speed)   # 250.0
print(car.fuel_type)   # "electric"
```

```java
// Java interface의 추상 getter
public interface Vehicle {
    double getMaxSpeed();
    String getFuelType();
}
```

### `@abstractmethod` + `@classmethod` 조합

```python
from abc import ABC, abstractmethod

class Serializable(ABC):
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "Serializable":
        """딕셔너리에서 인스턴스 생성 - 팩토리 메서드"""
        ...

    @abstractmethod
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        ...

class User(Serializable):
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}

user = User.from_dict({"id": 1, "name": "Alice"})
print(user.to_dict())  # {'id': 1, 'name': 'Alice'}
```

---

## 4. `ABC` vs `Protocol` 선택 기준

Python에는 추상화를 표현하는 두 가지 방법이 있습니다:
`ABC`(명시적 상속)와 `Protocol`(구조적 타이핑).

### 비교표

| 항목 | `ABC` | `Protocol` |
|------|-------|------------|
| 상속 방식 | 명시적 `class Foo(MyABC)` | 불필요 (duck typing) |
| 구현 강제 | 인스턴스화 시 `TypeError` | 정적 분석만 (mypy/pyright) |
| 공통 구현 | 가능 (template method) | 불가 (구현 없음) |
| 외부 라이브러리 클래스 | 어댑터 필요 | 그대로 사용 가능 |
| `isinstance` 체크 | 가능 | `@runtime_checkable` 필요 |
| Java 대응 | `abstract class` | `interface` |

### `ABC` 사용 권장 상황

```python
from abc import ABC, abstractmethod

# 1. 공통 구현(template method)이 있을 때
class DataLoader(ABC):
    def load(self, path: str) -> list[dict]:
        raw = self._read_raw(path)        # 공통 로직
        data = self._parse(raw)           # 추상 메서드
        return self._validate(data)       # 공통 로직

    def _read_raw(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    @abstractmethod
    def _parse(self, raw: bytes) -> list[dict]: ...

    def _validate(self, data: list[dict]) -> list[dict]:
        return [row for row in data if row]  # 빈 행 제거

class JsonLoader(DataLoader):
    def _parse(self, raw: bytes) -> list[dict]:
        import json
        return json.loads(raw)

class CsvLoader(DataLoader):
    def _parse(self, raw: bytes) -> list[dict]:
        import csv
        import io
        reader = csv.DictReader(io.StringIO(raw.decode()))
        return list(reader)

# 2. 상속 계층이 명확하고 is-a 관계일 때
class Animal(ABC):
    @abstractmethod
    def speak(self) -> str: ...

class Dog(Animal):
    def speak(self) -> str: return "멍멍"
```

### `Protocol` 사용 권장 상황

```python
from typing import Protocol

# 1. 외부 라이브러리 클래스와 인터페이스 정의 시
class Closeable(Protocol):
    def close(self) -> None: ...

# 외부 라이브러리의 클래스도 수정 없이 호환
import socket

def cleanup(resource: Closeable) -> None:
    resource.close()

sock = socket.socket()
cleanup(sock)  # socket.socket은 Closeable을 상속하지 않지만 close()가 있으므로 호환

# 2. has-a 관계, 기능 단위의 인터페이스
class Readable(Protocol):
    def read(self, n: int = -1) -> bytes: ...

class Writable(Protocol):
    def write(self, data: bytes) -> int: ...

class ReadWritable(Readable, Writable, Protocol): ...
```

### 선택 플로우차트

```
공통 구현(template method)이 필요한가?
  ├── YES → ABC 사용
  └── NO → 계속...

외부 라이브러리 클래스와 인터페이스를 맞춰야 하는가?
  ├── YES → Protocol 사용
  └── NO → 계속...

명시적인 상속 계층이 필요한가?
  ├── YES → ABC 사용
  └── NO → Protocol 사용 (더 유연)
```

---

## 5. 실전 예시

### Repository 패턴

Java의 `@Repository` 인터페이스 패턴을 Python ABC로 표현합니다.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: str

# Repository 인터페이스 - Java의 JpaRepository와 유사
class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        ...

    @abstractmethod
    def find_all(self) -> list[User]:
        ...

    @abstractmethod
    def save(self, user: User) -> User:
        ...

    @abstractmethod
    def delete(self, user_id: int) -> None:
        ...

    # 공통 구현 - 서브클래스에서 재사용
    def find_by_name(self, name: str) -> list[User]:
        return [u for u in self.find_all() if u.name == name]

# 인메모리 구현 - 테스트용
class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._store: dict[int, User] = {}
        self._next_id = 1

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self._store.get(user_id)

    def find_all(self) -> list[User]:
        return list(self._store.values())

    def save(self, user: User) -> User:
        if user.id == 0:
            user = User(id=self._next_id, name=user.name, email=user.email)
            self._next_id += 1
        self._store[user.id] = user
        return user

    def delete(self, user_id: int) -> None:
        self._store.pop(user_id, None)

# PostgreSQL 구현 - 실제 DB 연동
class PostgresUserRepository(UserRepository):
    def __init__(self, connection_string: str) -> None:
        # import psycopg2 등
        self._conn_str = connection_string

    def find_by_id(self, user_id: int) -> Optional[User]:
        # SQL 쿼리 실행
        ...

    def find_all(self) -> list[User]:
        ...

    def save(self, user: User) -> User:
        ...

    def delete(self, user_id: int) -> None:
        ...

# 서비스 레이어 - 인터페이스에만 의존
class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository  # DI - Java @Autowired와 동일

    def get_user(self, user_id: int) -> User:
        user = self._repo.find_by_id(user_id)
        if user is None:
            raise ValueError(f"사용자를 찾을 수 없습니다: {user_id}")
        return user

    def create_user(self, name: str, email: str) -> User:
        return self._repo.save(User(id=0, name=name, email=email))

# 테스트
repo = InMemoryUserRepository()
service = UserService(repo)
created = service.create_user("Alice", "alice@example.com")
found = service.get_user(created.id)
print(found)  # User(id=1, name='Alice', email='alice@example.com')
```

```java
// Java
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByName(String name);
}

@Repository
public class PostgresUserRepository implements UserRepository { ... }

@Service
public class UserService {
    @Autowired
    private UserRepository repository;
}
```

### Strategy 패턴

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Order:
    total: float
    is_member: bool
    quantity: int

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate_discount(self, order: Order) -> float:
        """할인 금액 반환"""
        ...

    def apply(self, order: Order) -> float:
        """최종 결제 금액 반환"""
        discount = self.calculate_discount(order)
        return max(0.0, order.total - discount)

class NoDiscount(DiscountStrategy):
    def calculate_discount(self, order: Order) -> float:
        return 0.0

class MemberDiscount(DiscountStrategy):
    def __init__(self, rate: float = 0.1) -> None:
        self.rate = rate

    def calculate_discount(self, order: Order) -> float:
        if order.is_member:
            return order.total * self.rate
        return 0.0

class BulkDiscount(DiscountStrategy):
    def __init__(self, min_quantity: int = 10, rate: float = 0.15) -> None:
        self.min_quantity = min_quantity
        self.rate = rate

    def calculate_discount(self, order: Order) -> float:
        if order.quantity >= self.min_quantity:
            return order.total * self.rate
        return 0.0

class CombinedDiscount(DiscountStrategy):
    def __init__(self, strategies: list[DiscountStrategy]) -> None:
        self._strategies = strategies

    def calculate_discount(self, order: Order) -> float:
        return sum(s.calculate_discount(order) for s in self._strategies)

# 런타임에 전략 선택
class OrderProcessor:
    def __init__(self, strategy: DiscountStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: DiscountStrategy) -> None:
        self._strategy = strategy

    def process(self, order: Order) -> float:
        return self._strategy.apply(order)

order = Order(total=100_000, is_member=True, quantity=15)

processor = OrderProcessor(NoDiscount())
print(processor.process(order))  # 100000.0

processor.set_strategy(MemberDiscount(rate=0.1))
print(processor.process(order))  # 90000.0

processor.set_strategy(
    CombinedDiscount([MemberDiscount(0.1), BulkDiscount(10, 0.05)])
)
print(processor.process(order))  # 85000.0 (15% 할인)
```

```java
// Java Strategy 패턴
public interface DiscountStrategy {
    double calculateDiscount(Order order);

    default double apply(Order order) {
        return Math.max(0, order.getTotal() - calculateDiscount(order));
    }
}

public class MemberDiscount implements DiscountStrategy {
    private final double rate;
    public MemberDiscount(double rate) { this.rate = rate; }

    @Override
    public double calculateDiscount(Order order) {
        return order.isMember() ? order.getTotal() * rate : 0;
    }
}
```

---

## ABC 등록 메커니즘 (고급)

`register()` 메서드로 상속 없이 가상 서브클래스를 등록할 수 있습니다.

```python
from abc import ABC

class MySequence(ABC):
    @abstractmethod
    def __getitem__(self, index: int): ...

    @abstractmethod
    def __len__(self) -> int: ...

# 외부 클래스를 가상 서브클래스로 등록
MySequence.register(tuple)
MySequence.register(list)

print(isinstance([], MySequence))    # True - list는 실제 상속 없음
print(isinstance((), MySequence))   # True - tuple도 실제 상속 없음
print(issubclass(list, MySequence)) # True

# 참고: Python 표준 라이브러리의 collections.abc도 이 방식으로 동작
from collections.abc import Sequence
print(isinstance([], Sequence))     # True
```
