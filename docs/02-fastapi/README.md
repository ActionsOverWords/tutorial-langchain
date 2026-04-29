# FastAPI 튜토리얼 — Java/Spring Boot 개발자를 위한 실전 가이드

> 대상: Spring MVC/Spring Boot 경력 20년 이상의 개발자
> Python 기초 문법은 이미 알고 있다고 가정합니다.

---

## 목차

1. [FastAPI 개요](#1-fastapi-개요)
2. [Pydantic](#2-pydantic)
3. [lifespan (애플리케이션 생명주기)](#3-lifespan-애플리케이션-생명주기)
4. [쓰레드 핸들링 (async/await)](#4-쓰레드-핸들링-asyncawait)
5. [Health Check와 Graceful Shutdown](#5-health-check와-graceful-shutdown)
6. [pytest로 FastAPI 테스트](#6-pytest로-fastapi-테스트)
7. [Spring MVC → FastAPI 대응표](#7-spring-mvc--fastapi-대응표)

---

## 1. FastAPI 개요

### Spring MVC와의 아키텍처 비교

Spring Boot 개발자에게 FastAPI는 낯설지만, 개념 자체는 매우 친숙합니다. 핵심 차이는 **동기(Servlet) 모델 → 비동기(ASGI) 모델**로의 전환입니다.

| 구분 | Spring Boot | FastAPI |
|---|---|---|
| 런타임 모델 | 동기 (Servlet/Tomcat) | 비동기 (ASGI/Uvicorn) |
| 프레임워크 레이어 | Spring MVC on Tomcat | FastAPI on Starlette on Uvicorn |
| 언어 | Java/Kotlin | Python 3.10+ |
| HTTP 서버 | Tomcat, Jetty, Undertow | Uvicorn, Hypercorn, Daphne |
| API 문서 | SpringDoc (springdoc-openapi) | 내장 (자동 생성) |

### Starlette과 ASGI

FastAPI는 **Starlette** 위에 구축되어 있습니다. Starlette은 Python의 ASGI(Asynchronous Server Gateway Interface) 프레임워크입니다. Spring으로 비유하면 Starlette은 Spring MVC 코어이고, FastAPI는 그 위에 타입 힌트 기반의 자동 검증, 직렬화, API 문서화를 추가한 것입니다.

```
[클라이언트]
    ↓ HTTP 요청
[Uvicorn]          ← Tomcat 역할 (ASGI 서버)
    ↓
[Starlette]        ← Spring MVC 코어 역할 (라우팅, 미들웨어)
    ↓
[FastAPI]          ← Spring MVC + SpringDoc 역할 (타입 검증, OpenAPI)
    ↓
[라우터 / 핸들러]  ← @RestController + @RequestMapping 역할
```

### 설치

```bash
pip install fastapi uvicorn

# 개발 환경: 코드 변경 시 자동 재시작
uvicorn main:app --reload

# 프로덕션 환경
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
```

### 첫 번째 애플리케이션 비교

**Spring Boot:**
```java
// UserController.java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUser(@PathVariable Long id) {
        UserResponse user = userService.findById(id);
        return ResponseEntity.ok(user);
    }

    @PostMapping
    public ResponseEntity<UserResponse> createUser(@RequestBody @Valid CreateUserRequest request) {
        UserResponse user = userService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(user);
    }
}
```

**FastAPI:**
```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CreateUserRequest(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    # user_id는 자동으로 int로 변환 및 검증됨
    user = await user_service.find_by_id(user_id)
    return user

@app.post("/api/users", response_model=UserResponse, status_code=201)
async def create_user(request: CreateUserRequest):
    # request는 자동으로 검증됨
    user = await user_service.create(request)
    return user
```

### 자동 API 문서

FastAPI의 가장 강력한 기능 중 하나입니다. 별도 설정 없이 다음 URL에서 접근 가능합니다.

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

Spring Boot에서 `springdoc-openapi` 의존성 추가 + `@Operation`, `@Schema` 등의 어노테이션을 일일이 달아야 했던 것과 달리, FastAPI는 타입 힌트와 Pydantic 모델만으로 자동 문서화됩니다.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="My API",
    description="Spring Boot 개발자를 위한 FastAPI 예제",
    version="1.0.0",
)

class CreateUserRequest(BaseModel):
    name: str = Field(..., description="사용자 이름", example="홍길동")
    email: str = Field(..., description="이메일 주소", example="hong@example.com")

@app.post(
    "/users",
    summary="사용자 생성",
    description="새로운 사용자를 생성합니다.",
    response_description="생성된 사용자 정보",
)
async def create_user(request: CreateUserRequest):
    ...
```

### APIRouter — Spring의 @RequestMapping 모듈화

Spring에서 컨트롤러마다 `@RequestMapping("/api/v1/users")`로 공통 prefix를 지정하듯, FastAPI는 `APIRouter`를 사용합니다.

**Spring Boot:**
```java
// UserController.java
@RestController
@RequestMapping("/api/v1/users")
public class UserController { ... }

// OrderController.java
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController { ... }
```

**FastAPI:**
```python
# routers/users.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/{user_id}")
async def get_user(user_id: int): ...

@router.post("")
async def create_user(): ...

# routers/orders.py
router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

# main.py
from fastapi import FastAPI
from routers import users, orders

app = FastAPI()
app.include_router(users.router)
app.include_router(orders.router)
```

---

## 2. Pydantic

### Spring의 @Valid + DTO 역할

Pydantic은 FastAPI의 핵심입니다. Spring에서 `@Valid` + DTO 클래스 + Bean Validation 어노테이션(`@NotNull`, `@Size`, `@Email` 등)이 하는 역할을 Pydantic이 담당합니다.

| Spring | Pydantic |
|---|---|
| `class UserRequest` (DTO) | `class UserRequest(BaseModel)` |
| `@NotNull` | `Field(...)` (필수 필드) |
| `@Size(min=2, max=50)` | `Field(..., min_length=2, max_length=50)` |
| `@Email` | `EmailStr` 타입 또는 validator |
| `@Min(0)` | `Field(..., ge=0)` |
| `@Max(100)` | `Field(..., le=100)` |
| `@Pattern(regexp="...")` | `Field(..., pattern="...")` |
| `@Valid` | 자동 검증 (별도 어노테이션 불필요) |
| `BindingResult` | `RequestValidationError` 자동 처리 |

### BaseModel 기본 사용법

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# pip install pydantic[email]  — EmailStr 사용 시 필요

class CreateUserRequest(BaseModel):
    # 필수 필드 (= @NotNull)
    name: str = Field(..., min_length=2, max_length=50, description="사용자 이름")
    email: EmailStr = Field(..., description="이메일 주소")

    # 선택 필드 (= @Nullable 또는 Optional)
    age: Optional[int] = Field(None, ge=0, le=150, description="나이")
    bio: Optional[str] = Field(None, max_length=500)

    # 기본값이 있는 필드
    role: str = Field(default="user", pattern="^(user|admin|moderator)$")

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    # Spring의 @JsonProperty와 동일
    class Config:
        # DB ORM 객체를 그대로 반환 가능 (= Spring의 @JsonIgnoreProperties)
        from_attributes = True  # Pydantic v2 (구버전: orm_mode = True)
```

### Field() 상세 옵션

```python
from pydantic import BaseModel, Field

class ProductRequest(BaseModel):
    # 문자열 검증
    name: str = Field(
        ...,                    # ... 는 필수값 (required)
        min_length=1,
        max_length=100,
        description="상품명",
        example="노트북",
    )

    # 숫자 범위 검증
    price: float = Field(
        ...,
        gt=0,       # greater than (= @DecimalMin(exclusive=true))
        lt=10000,   # less than
        # ge=0,     # greater than or equal
        # le=10000, # less than or equal
    )

    # 정규식 검증
    sku: str = Field(
        ...,
        pattern=r"^[A-Z]{3}-\d{6}$",
        description="SKU 코드 (예: ABC-123456)",
    )

    # 리스트 크기 검증
    tags: list[str] = Field(
        default=[],
        min_length=0,   # 리스트 최소 길이
        max_length=10,  # 리스트 최대 길이
    )
```

### SecretStr — 민감 정보 마스킹

Spring에서 비밀번호 같은 민감 정보를 로그에서 가리기 위해 `@JsonIgnore` 또는 커스텀 `toString()`을 작성했던 것처럼, Pydantic은 `SecretStr`를 제공합니다.

```python
from pydantic import BaseModel, SecretStr, SecretBytes

class LoginRequest(BaseModel):
    username: str
    password: SecretStr  # 로그/직렬화 시 ***** 로 마스킹

class ApiKeyConfig(BaseModel):
    api_key: SecretStr
    private_key_pem: SecretBytes  # 바이너리 민감 정보

# 사용 예시
request = LoginRequest(username="admin", password="super_secret_123")

# 로그에서 안전: ***** 출력
print(request)
# username='admin' password=SecretStr('**********')

# 실제 값이 필요할 때는 명시적으로 꺼내야 함
actual_password = request.password.get_secret_value()
print(actual_password)  # "super_secret_123"

# JSON 직렬화 시에도 마스킹
import json
print(request.model_dump())
# {'username': 'admin', 'password': '**********'}

# 실제 값 포함 직렬화가 필요한 경우
print(request.model_dump(context={"reveal_secrets": True}))  # Pydantic v2
```

### model_validator와 field_validator

Spring의 `@AssertTrue` 또는 커스텀 `ConstraintValidator`에 대응합니다.

**Spring Boot:**
```java
public class PasswordChangeRequest {
    @NotBlank
    private String newPassword;

    @NotBlank
    private String confirmPassword;

    @AssertTrue(message = "비밀번호가 일치하지 않습니다")
    public boolean isPasswordMatching() {
        return newPassword != null && newPassword.equals(confirmPassword);
    }
}
```

**FastAPI:**
```python
from pydantic import BaseModel, field_validator, model_validator
from typing import Self

class PasswordChangeRequest(BaseModel):
    new_password: str
    confirm_password: str

    # field_validator: 단일 필드 검증 (= @AssertTrue on field)
    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다")
        if not any(c.isupper() for c in v):
            raise ValueError("대문자를 포함해야 합니다")
        if not any(c.isdigit() for c in v):
            raise ValueError("숫자를 포함해야 합니다")
        return v

    # model_validator: 여러 필드 간 검증 (= @AssertTrue on class level)
    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.new_password != self.confirm_password:
            raise ValueError("비밀번호가 일치하지 않습니다")
        return self

class DateRangeRequest(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode="after")
    def check_date_range(self) -> Self:
        if self.start_date >= self.end_date:
            raise ValueError("종료일은 시작일 이후여야 합니다")
        return self
```

### BaseSettings — 설정 관리 (@ConfigurationProperties 대응)

Spring의 `application.properties` + `@ConfigurationProperties`와 동일한 역할을 합니다.

**Spring Boot:**
```java
// application.properties
// database.url=jdbc:postgresql://localhost:5432/mydb
// database.pool-size=10
// jwt.secret=mysecret
// jwt.expiration=3600

@ConfigurationProperties(prefix = "database")
@Component
public class DatabaseProperties {
    private String url;
    private int poolSize = 10;
    // getters/setters...
}
```

**FastAPI:**
```python
# .env 파일
# DATABASE_URL=postgresql://localhost:5432/mydb
# DATABASE_POOL_SIZE=10
# JWT_SECRET=mysecret
# JWT_EXPIRATION=3600
# DEBUG=false

# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from functools import lru_cache

# pip install pydantic-settings

class Settings(BaseSettings):
    # .env 파일을 자동으로 읽음
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # DATABASE_URL, database_url 둘 다 허용
    )

    # 데이터베이스 설정
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # JWT 설정
    jwt_secret: SecretStr  # 민감 정보는 SecretStr로
    jwt_expiration: int = 3600

    # 앱 설정
    debug: bool = False
    app_name: str = "My FastAPI App"
    allowed_origins: list[str] = ["http://localhost:3000"]

# 싱글톤 패턴 (= Spring @Bean singleton)
@lru_cache
def get_settings() -> Settings:
    return Settings()

# 사용 예시
settings = get_settings()
print(settings.database_url)
print(settings.jwt_secret.get_secret_value())  # SecretStr 꺼내기

# FastAPI Depends()와 연동
from fastapi import Depends

@app.get("/config-info")
async def config_info(settings: Settings = Depends(get_settings)):
    return {"app_name": settings.app_name, "debug": settings.debug}
```

### 환경별 설정 분리

```python
# config.py
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment: str = "development"
    database_url: str
    redis_url: str = "redis://localhost:6379"
    log_level: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

class DevelopmentSettings(Settings):
    model_config = SettingsConfigDict(env_file=".env.development")
    log_level: str = "DEBUG"

class ProductionSettings(Settings):
    model_config = SettingsConfigDict(env_file=".env.production")
    log_level: str = "WARNING"

@lru_cache
def get_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        return ProductionSettings()
    return DevelopmentSettings()
```

---

## 3. lifespan (애플리케이션 생명주기)

### Spring의 @PostConstruct / @PreDestroy 대응

Spring에서 애플리케이션 시작/종료 시 특정 코드를 실행하려면 `@PostConstruct`, `@PreDestroy`, 또는 `ApplicationListener<ContextRefreshedEvent>`를 사용했습니다.

FastAPI는 `lifespan` 컨텍스트 매니저를 사용합니다. `yield` 이전이 startup, 이후가 shutdown입니다.

**Spring Boot:**
```java
@Component
public class DatabaseInitializer {

    private final DataSource dataSource;

    @PostConstruct
    public void init() {
        // 앱 시작 시 실행
        System.out.println("DB 커넥션 풀 초기화");
        // 스키마 마이그레이션 등
    }

    @PreDestroy
    public void cleanup() {
        // 앱 종료 시 실행
        System.out.println("DB 커넥션 정리");
    }
}
```

**FastAPI:**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ===== startup: @PostConstruct =====
    print("앱 시작")
    yield
    # ===== shutdown: @PreDestroy =====
    print("앱 종료")

app = FastAPI(lifespan=lifespan)
```

### 실전 예시: DB 커넥션 풀 + ML 모델 로딩

```python
# lifespan.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncpg
import redis.asyncio as aioredis
from fastapi import FastAPI

# 전역 리소스 저장소 (Spring ApplicationContext의 Bean과 유사)
class AppState:
    db_pool: asyncpg.Pool | None = None
    redis_client: aioredis.Redis | None = None
    ml_model: object | None = None

app_state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # ===== Startup =====
    print("[Startup] 애플리케이션 초기화 시작...")

    # 1. DB 커넥션 풀 생성 (= Spring DataSource 초기화)
    print("[Startup] PostgreSQL 커넥션 풀 생성 중...")
    app_state.db_pool = await asyncpg.create_pool(
        dsn="postgresql://user:pass@localhost:5432/mydb",
        min_size=5,
        max_size=20,
    )
    print(f"[Startup] DB 풀 생성 완료 (min=5, max=20)")

    # 2. Redis 연결 (= Spring RedisConnectionFactory 초기화)
    print("[Startup] Redis 연결 중...")
    app_state.redis_client = aioredis.from_url(
        "redis://localhost:6379",
        encoding="utf-8",
        decode_responses=True,
    )
    await app_state.redis_client.ping()
    print("[Startup] Redis 연결 완료")

    # 3. ML 모델 로딩 (무거운 작업을 startup에서 처리)
    print("[Startup] ML 모델 로딩 중...")
    # app_state.ml_model = load_model("./models/classifier.pkl")
    print("[Startup] ML 모델 로딩 완료")

    print("[Startup] 초기화 완료. 요청 수신 준비됨.")

    # ===== 요청 처리 구간 =====
    yield

    # ===== Shutdown =====
    print("[Shutdown] 애플리케이션 종료 시작...")

    # 역순으로 정리 (= Spring Bean 소멸 순서)
    if app_state.redis_client:
        await app_state.redis_client.close()
        print("[Shutdown] Redis 연결 종료")

    if app_state.db_pool:
        await app_state.db_pool.close()
        print("[Shutdown] DB 커넥션 풀 종료")

    print("[Shutdown] 종료 완료.")

app = FastAPI(lifespan=lifespan)

# app_state를 라우터에서 사용하는 방법
from fastapi import Request

@app.get("/users/{user_id}")
async def get_user(user_id: int, request: Request):
    # request.app.state 또는 전역 app_state 사용
    pool = app_state.db_pool
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )
        return dict(user)
```

### app.state를 활용한 더 깔끔한 방법

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.db_pool = await create_db_pool()
    app.state.cache = {}
    yield
    # shutdown
    await app.state.db_pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/items/{item_id}")
async def get_item(item_id: int, request: Request):
    # request.app.state로 접근
    pool = request.app.state.db_pool
    ...
```

---

## 4. 쓰레드 핸들링 (async/await)

### Spring @Async vs Python async/await

이 부분이 Spring Boot 개발자에게 가장 낯선 영역입니다. 패러다임 자체가 다릅니다.

| 구분 | Spring Boot | FastAPI |
|---|---|---|
| 동시성 모델 | 멀티쓰레드 (Thread-per-request) | 이벤트 루프 (Single-threaded async) |
| 비동기 실행 | `@Async` + `CompletableFuture` | `async def` + `await` |
| 병렬 실행 | `CompletableFuture.allOf()` | `asyncio.gather()` |
| blocking 코드 | 기본 동작 | `run_in_executor()` 로 threadpool 위임 |
| 백그라운드 작업 | `@Async void` 메서드 | `BackgroundTasks` |

### async def vs def 선택 기준

FastAPI에서 가장 중요한 결정 중 하나입니다.

```python
# ✅ async def를 써야 하는 경우: I/O 작업 (await 키워드 사용 가능)
@app.get("/users")
async def get_users():
    # await 가능한 비동기 라이브러리 사용
    users = await db.fetch_all("SELECT * FROM users")  # asyncpg, databases 등
    result = await http_client.get("https://api.example.com/data")  # httpx
    return users

# ✅ def를 써야 하는 경우: 동기 라이브러리 사용 (자동으로 threadpool에서 실행됨)
@app.get("/sync-operation")
def sync_operation():
    # FastAPI가 자동으로 별도 thread에서 실행 (blocking 해도 이벤트 루프 막지 않음)
    result = some_sync_library.call()  # requests, psycopg2 등
    return result

# ❌ 절대 금지: async def 안에서 blocking 코드
@app.get("/bad-example")
async def bad_example():
    import time
    time.sleep(5)  # 이벤트 루프 전체가 5초 동안 블로킹됨!
    result = requests.get("https://api.example.com")  # 동기 HTTP: 역시 블로킹!
    return result
```

### GIL과 asyncio의 관계

Python의 GIL(Global Interpreter Lock)은 한 번에 하나의 Python 코드만 실행할 수 있게 합니다. 그러나 asyncio는 이와 무관하게 I/O 대기 시간을 활용합니다.

```
[GIL 동작 방식]

Thread A: 코드실행─────IO대기(GIL 해제)────────────────코드실행──
Thread B:          ────코드실행──────IO대기(GIL 해제)──코드실행───

[asyncio 동작 방식 - 단일 쓰레드]

EventLoop: 코드실행─IO등록─다른코드실행─IO등록─코드실행─IO완료콜백─코드실행
```

**결론:**
- CPU 집중 작업(계산): `asyncio`로 병렬 처리 불가. `ProcessPoolExecutor` 사용
- I/O 집중 작업(DB, HTTP, 파일): `asyncio`로 효율적 처리 가능

### asyncio.gather() — CompletableFuture.allOf() 대응

**Spring Boot:**
```java
// 여러 비동기 작업 병렬 실행
CompletableFuture<User> userFuture = userService.findByIdAsync(userId);
CompletableFuture<List<Order>> ordersFuture = orderService.findByUserAsync(userId);
CompletableFuture<Address> addressFuture = addressService.findByUserAsync(userId);

CompletableFuture.allOf(userFuture, ordersFuture, addressFuture).join();

User user = userFuture.get();
List<Order> orders = ordersFuture.get();
Address address = addressFuture.get();
```

**FastAPI:**
```python
import asyncio
import httpx

@app.get("/dashboard/{user_id}")
async def get_dashboard(user_id: int):
    # 병렬로 여러 데이터 조회 (= CompletableFuture.allOf)
    user, orders, address = await asyncio.gather(
        user_service.find_by_id(user_id),
        order_service.find_by_user(user_id),
        address_service.find_by_user(user_id),
    )
    return {
        "user": user,
        "orders": orders,
        "address": address,
    }

# 실전 예시: 여러 외부 API 병렬 호출
async def fetch_multiple_apis():
    async with httpx.AsyncClient() as client:
        # 순차 실행: 총 3초 소요
        # r1 = await client.get("https://api1.example.com")  # 1초
        # r2 = await client.get("https://api2.example.com")  # 1초
        # r3 = await client.get("https://api3.example.com")  # 1초

        # 병렬 실행: 총 1초 소요 (가장 오래 걸리는 것 기준)
        r1, r2, r3 = await asyncio.gather(
            client.get("https://api1.example.com"),
            client.get("https://api2.example.com"),
            client.get("https://api3.example.com"),
        )

    return [r1.json(), r2.json(), r3.json()]

# 일부 실패해도 계속 진행 (= CompletableFuture with exceptionally)
async def gather_with_fallback():
    results = await asyncio.gather(
        user_service.find_by_id(1),
        order_service.find_orders(1),
        return_exceptions=True,  # 예외를 결과로 반환
    )
    return [r for r in results if not isinstance(r, Exception)]
```

### run_in_executor() — blocking 코드를 threadpool에서 실행

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from fastapi import FastAPI

app = FastAPI()

# 동기 라이브러리 함수 (예: 레거시 코드, C 확장 라이브러리)
def sync_heavy_io(file_path: str) -> str:
    """동기 방식으로 파일 읽기 (블로킹)"""
    with open(file_path, "r") as f:
        return f.read()

def cpu_intensive_calculation(n: int) -> int:
    """CPU 집중 계산 (예: 이미지 처리, 암호화)"""
    return sum(i * i for i in range(n))

@app.get("/process-file")
async def process_file(file_path: str):
    loop = asyncio.get_event_loop()

    # I/O 블로킹 작업 → ThreadPoolExecutor (GIL 해제됨)
    content = await loop.run_in_executor(
        None,  # None = 기본 ThreadPoolExecutor
        sync_heavy_io,
        file_path,
    )
    return {"content": content[:100]}

@app.get("/cpu-task")
async def cpu_task(n: int):
    loop = asyncio.get_event_loop()

    # CPU 집중 작업 → ProcessPoolExecutor (GIL 완전 우회)
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool,
            cpu_intensive_calculation,
            n,
        )
    return {"result": result}

# asyncio.to_thread() — Python 3.9+ 더 간결한 문법
@app.get("/modern-thread")
async def modern_thread(file_path: str):
    content = await asyncio.to_thread(sync_heavy_io, file_path)
    return {"content": content[:100]}
```

### BackgroundTasks — Spring @Async void 대응

**Spring Boot:**
```java
@Service
public class EmailService {
    @Async
    public void sendWelcomeEmailAsync(String email) {
        // 응답 후 비동기 실행
        emailClient.send(email, "환영합니다!", "...");
    }
}

@RestController
public class UserController {
    @PostMapping("/users")
    public ResponseEntity<UserResponse> createUser(@RequestBody CreateUserRequest req) {
        UserResponse user = userService.create(req);
        emailService.sendWelcomeEmailAsync(user.getEmail()); // fire-and-forget
        return ResponseEntity.status(201).body(user);
    }
}
```

**FastAPI:**
```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

# 백그라운드에서 실행될 함수
async def send_welcome_email(email: str, username: str):
    """응답 반환 후 백그라운드에서 실행"""
    # 실제로는 aiosmtplib 등 비동기 라이브러리 사용
    await asyncio.sleep(1)  # 이메일 발송 시뮬레이션
    print(f"환영 이메일 발송 완료: {email}")

async def save_audit_log(user_id: int, action: str):
    await db.execute("INSERT INTO audit_logs ...", user_id, action)

class CreateUserRequest(BaseModel):
    name: str
    email: str

@app.post("/users", status_code=201)
async def create_user(
    request: CreateUserRequest,
    background_tasks: BackgroundTasks,  # 자동 주입
):
    user = await user_service.create(request)

    # 응답 반환 후 백그라운드에서 실행 (= @Async void)
    background_tasks.add_task(send_welcome_email, request.email, request.name)
    background_tasks.add_task(save_audit_log, user.id, "CREATE_USER")

    return user  # 즉시 응답, 이메일은 백그라운드에서 처리
```

---

## 5. Health Check와 Graceful Shutdown

### Spring Boot Actuator /health 대응

Spring Boot는 `spring-boot-starter-actuator`를 추가하면 `/actuator/health` 엔드포인트가 자동 생성됩니다. FastAPI는 수동으로 구현해야 하지만, 더 유연하게 커스터마이징할 수 있습니다.

### 기본 헬스체크 구현

```python
# health.py
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timezone
import time

router = APIRouter(tags=["health"])

# 앱 시작 시간 기록
START_TIME = time.time()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime_seconds: float
    version: str = "1.0.0"

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="기본 헬스체크",
)
async def health_check():
    """Spring Boot Actuator /health (UP 상태)에 대응"""
    return HealthResponse(
        status="UP",
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=round(time.time() - START_TIME, 2),
    )

# Kubernetes liveness probe용 (단순 OK)
@router.get("/health/live", summary="Liveness probe")
async def liveness():
    return {"status": "OK"}

# Kubernetes readiness probe용 (의존성 포함)
@router.get("/health/ready", summary="Readiness probe")
async def readiness():
    # 실제로는 DB, Redis 등 확인
    return {"status": "READY"}
```

### 외부 의존성 포함 헬스체크

```python
# health_detailed.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal
import asyncpg
import redis.asyncio as aioredis
import httpx

router = APIRouter(tags=["health"])

ComponentStatus = Literal["UP", "DOWN", "DEGRADED"]

class ComponentHealth(BaseModel):
    status: ComponentStatus
    response_time_ms: float | None = None
    error: str | None = None

class DetailedHealthResponse(BaseModel):
    status: ComponentStatus
    components: dict[str, ComponentHealth]

async def check_database(pool: asyncpg.Pool) -> ComponentHealth:
    """DB 헬스체크 (= Spring DataSourceHealthIndicator)"""
    import time
    start = time.time()
    try:
        async with pool.acquire(timeout=5.0) as conn:
            await conn.execute("SELECT 1")
        return ComponentHealth(
            status="UP",
            response_time_ms=round((time.time() - start) * 1000, 2),
        )
    except Exception as e:
        return ComponentHealth(status="DOWN", error=str(e))

async def check_redis(client: aioredis.Redis) -> ComponentHealth:
    """Redis 헬스체크 (= Spring RedisHealthIndicator)"""
    import time
    start = time.time()
    try:
        await client.ping()
        return ComponentHealth(
            status="UP",
            response_time_ms=round((time.time() - start) * 1000, 2),
        )
    except Exception as e:
        return ComponentHealth(status="DOWN", error=str(e))

async def check_external_api(url: str) -> ComponentHealth:
    """외부 API 헬스체크"""
    import time
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
            response.raise_for_status()
        return ComponentHealth(
            status="UP",
            response_time_ms=round((time.time() - start) * 1000, 2),
        )
    except Exception as e:
        return ComponentHealth(status="DOWN", error=str(e))

@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health(request: Request):
    import asyncio

    pool = request.app.state.db_pool
    redis_client = request.app.state.redis_client

    # 모든 헬스체크 병렬 실행
    db_health, redis_health, api_health = await asyncio.gather(
        check_database(pool),
        check_redis(redis_client),
        check_external_api("https://api.partner.com/health"),
    )

    components = {
        "database": db_health,
        "redis": redis_health,
        "partner_api": api_health,
    }

    # 하나라도 DOWN이면 전체 DOWN
    all_statuses = [c.status for c in components.values()]
    if "DOWN" in all_statuses:
        overall = "DOWN"
    elif "DEGRADED" in all_statuses:
        overall = "DEGRADED"
    else:
        overall = "UP"

    response = DetailedHealthResponse(status=overall, components=components)
    http_status = 200 if overall == "UP" else 503

    return JSONResponse(
        content=response.model_dump(),
        status_code=http_status,
    )
```

### Graceful Shutdown

Spring Boot는 `server.shutdown=graceful` 설정만으로 Graceful Shutdown이 활성화됩니다. FastAPI/Uvicorn은 두 가지 레이어에서 처리합니다.

```python
# main.py — lifespan에서 Graceful Shutdown 구현
import asyncio
import signal
from contextlib import asynccontextmanager
from fastapi import FastAPI

# 진행 중인 작업 추적
active_requests = 0
is_shutting_down = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global is_shutting_down

    # Startup
    app.state.db_pool = await create_db_pool()
    print("[Startup] 준비 완료")

    yield  # 요청 처리

    # Shutdown (SIGTERM 수신 시 실행)
    is_shutting_down = True
    print("[Shutdown] 종료 신호 수신. 진행 중인 요청 완료 대기 중...")

    # 최대 30초 대기
    deadline = asyncio.get_event_loop().time() + 30
    while active_requests > 0:
        remaining = deadline - asyncio.get_event_loop().time()
        if remaining <= 0:
            print(f"[Shutdown] 타임아웃. {active_requests}개 요청 강제 종료.")
            break
        await asyncio.sleep(0.1)

    print(f"[Shutdown] 모든 요청 완료. 리소스 정리 중...")
    await app.state.db_pool.close()
    print("[Shutdown] 완료.")

app = FastAPI(lifespan=lifespan)

# 미들웨어로 활성 요청 수 추적
from starlette.middleware.base import BaseHTTPMiddleware

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        global active_requests
        if is_shutting_down:
            return JSONResponse(
                {"detail": "서버가 종료 중입니다. 잠시 후 재시도하세요."},
                status_code=503,
            )
        active_requests += 1
        try:
            response = await call_next(request)
            return response
        finally:
            active_requests -= 1

app.add_middleware(RequestTrackingMiddleware)
```

### Uvicorn 실행 옵션

```bash
# 기본 실행
uvicorn main:app --host 0.0.0.0 --port 8080

# Graceful Shutdown 타임아웃 설정 (= server.shutdown-timeout)
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 4 \
    --timeout-graceful-shutdown 30  # SIGTERM 후 강제 종료까지 대기 시간(초)

# 개발 환경 (코드 변경 시 자동 재시작)
uvicorn main:app --reload --reload-dir ./src
```

```python
# 코드에서 uvicorn 실행 (= SpringApplication.run())
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        workers=4,
        timeout_graceful_shutdown=30,
        log_level="info",
        access_log=True,
    )
```

---

## 6. pytest로 FastAPI 테스트

### Spring MockMvc vs FastAPI TestClient

| 구분 | Spring Boot | FastAPI |
|---|---|---|
| HTTP 테스트 클라이언트 | `MockMvc` | `TestClient` (동기) / `AsyncClient` (비동기) |
| 의존성 주입 교체 | `@MockBean` | `dependency_overrides` |
| 픽스처 설정 | `@BeforeEach`, `@TestConfiguration` | `conftest.py` + pytest fixtures |
| 비동기 테스트 | 별도 설정 거의 불필요 | `pytest-asyncio` |
| 실행 | `@SpringBootTest`, `@WebMvcTest` | `pytest` |

### 설치

```bash
pip install pytest pytest-asyncio httpx
```

### conftest.py — 테스트 픽스처 설정

```python
# conftest.py (프로젝트 루트 또는 tests/ 폴더)
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from main import app
from dependencies import get_db, get_current_user

# ===== 동기 TestClient (= MockMvc) =====
@pytest.fixture
def client():
    """기본 TestClient. 의존성 오버라이드 없음."""
    with TestClient(app) as c:
        yield c

# ===== 의존성 오버라이드 포함 TestClient =====
@pytest.fixture
def client_with_mock_db(mock_db_session):
    """DB를 Mock으로 교체한 TestClient (= @MockBean DataSource)"""
    app.dependency_overrides[get_db] = lambda: mock_db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()  # 테스트 후 반드시 초기화

# ===== 비동기 Client (= MockMvc + async) =====
@pytest.fixture
async def async_client():
    """비동기 테스트용 AsyncClient"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

# ===== Mock DB 세션 =====
@pytest.fixture
def mock_db_session():
    """Mock DB 세션 (= @MockBean JpaRepository)"""
    from unittest.mock import AsyncMock, MagicMock
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session

# ===== 인증 사용자 Mock =====
@pytest.fixture
def authenticated_client():
    """인증된 사용자로 테스트 (= @WithMockUser)"""
    mock_user = {"id": 1, "username": "testuser", "role": "admin"}
    app.dependency_overrides[get_current_user] = lambda: mock_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# pytest-asyncio 설정 (pytest.ini 또는 pyproject.toml 대신 여기서도 가능)
# pyproject.toml에 추가:
# [tool.pytest.ini_options]
# asyncio_mode = "auto"
```

### 엔드포인트 테스트 예시

```python
# tests/test_users.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app

client = TestClient(app)

# ===== GET 테스트 =====
class TestGetUser:
    """Spring의 @Test 클래스 역할"""

    def test_get_user_success(self, client):
        """정상적인 사용자 조회"""
        with patch("services.user_service.find_by_id") as mock:
            mock.return_value = {"id": 1, "name": "홍길동", "email": "hong@test.com"}

            response = client.get("/api/users/1")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["name"] == "홍길동"

    def test_get_user_not_found(self, client):
        """존재하지 않는 사용자 조회 (= 404 응답)"""
        with patch("services.user_service.find_by_id", side_effect=UserNotFoundError()):
            response = client.get("/api/users/9999")
            assert response.status_code == 404
            assert response.json()["detail"] == "사용자를 찾을 수 없습니다"

    def test_get_user_invalid_id(self, client):
        """잘못된 ID 형식 (= 422 Unprocessable Entity)"""
        response = client.get("/api/users/not-a-number")
        assert response.status_code == 422

# ===== POST 테스트 =====
class TestCreateUser:

    def test_create_user_success(self, client):
        """사용자 생성 성공"""
        payload = {
            "name": "김철수",
            "email": "kim@test.com",
            "age": 30,
        }
        with patch("services.user_service.create") as mock:
            mock.return_value = {"id": 100, **payload}

            response = client.post("/api/users", json=payload)

            assert response.status_code == 201
            assert response.json()["id"] == 100

    def test_create_user_invalid_email(self, client):
        """잘못된 이메일 형식 → 422 자동 반환"""
        payload = {"name": "김철수", "email": "not-an-email"}

        response = client.post("/api/users", json=payload)

        assert response.status_code == 422
        errors = response.json()["detail"]
        # Pydantic 검증 오류 내용 확인
        assert any("email" in str(e) for e in errors)

    def test_create_user_missing_required_field(self, client):
        """필수 필드 누락 → 422"""
        payload = {"name": "김철수"}  # email 누락

        response = client.post("/api/users", json=payload)

        assert response.status_code == 422

    def test_create_user_duplicate_email(self, client):
        """중복 이메일 → 409 Conflict"""
        from exceptions import DuplicateEmailError
        with patch("services.user_service.create", side_effect=DuplicateEmailError()):
            response = client.post(
                "/api/users",
                json={"name": "박영희", "email": "existing@test.com"},
            )
            assert response.status_code == 409

# ===== 비동기 테스트 =====
@pytest.mark.asyncio
class TestAsyncEndpoints:

    async def test_dashboard_parallel_fetch(self, async_client):
        """비동기 엔드포인트 테스트"""
        with patch("services.user_service.find_by_id") as mock_user, \
             patch("services.order_service.find_by_user") as mock_orders:

            mock_user.return_value = {"id": 1, "name": "홍길동"}
            mock_orders.return_value = [{"id": 10, "total": 50000}]

            response = await async_client.get("/dashboard/1")

            assert response.status_code == 200
            data = response.json()
            assert "user" in data
            assert "orders" in data

# ===== dependency_overrides 활용 (= @MockBean) =====
class TestWithDependencyOverrides:

    def test_with_mock_service(self):
        """dependency_overrides로 서비스 교체 (= @MockBean)"""
        from dependencies import get_user_service
        from unittest.mock import MagicMock

        mock_service = MagicMock()
        mock_service.find_by_id.return_value = {"id": 1, "name": "테스트유저"}

        # Spring의 @MockBean과 동일한 효과
        app.dependency_overrides[get_user_service] = lambda: mock_service

        try:
            with TestClient(app) as client:
                response = client.get("/api/users/1")
                assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()  # 반드시 정리

# ===== 헤더/인증 테스트 =====
class TestAuthentication:

    def test_protected_endpoint_without_token(self, client):
        """인증 없이 접근 → 401"""
        response = client.get("/api/profile")
        assert response.status_code == 401

    def test_protected_endpoint_with_token(self, client):
        """Bearer 토큰으로 접근"""
        headers = {"Authorization": "Bearer valid-jwt-token-here"}
        with patch("auth.verify_token") as mock_verify:
            mock_verify.return_value = {"sub": "1", "role": "user"}
            response = client.get("/api/profile", headers=headers)
            assert response.status_code == 200
```

### pyproject.toml 설정

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"           # 모든 async def 테스트 자동 처리
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

---

## 7. Spring MVC → FastAPI 대응표

### 완전한 대응 테이블

| Spring MVC / Spring Boot | FastAPI | 설명 |
|---|---|---|
| `@RestController` | `APIRouter` | 라우터 그룹 |
| `@RequestMapping("/api")` | `APIRouter(prefix="/api")` | 공통 경로 prefix |
| `@GetMapping("/{id}")` | `@router.get("/{id}")` | GET 핸들러 |
| `@PostMapping` | `@router.post("")` | POST 핸들러 |
| `@PutMapping("/{id}")` | `@router.put("/{id}")` | PUT 핸들러 |
| `@DeleteMapping("/{id}")` | `@router.delete("/{id}")` | DELETE 핸들러 |
| `@PatchMapping("/{id}")` | `@router.patch("/{id}")` | PATCH 핸들러 |
| `@PathVariable Long id` | `def handler(id: int)` | 경로 파라미터 |
| `@RequestParam String q` | `def handler(q: str)` | 쿼리 파라미터 |
| `@RequestParam(required=false)` | `def handler(q: str = None)` | 선택적 쿼리 파라미터 |
| `@RequestBody UserRequest req` | `def handler(req: UserRequest)` | 요청 본문 (Pydantic) |
| `@RequestHeader String token` | `Header(...)` | 요청 헤더 |
| `@CookieValue String session` | `Cookie(...)` | 쿠키 |
| `@Valid` | 자동 (Pydantic 모델 사용 시) | 요청 검증 |
| `BindingResult` | `RequestValidationError` 자동 처리 | 검증 오류 |
| `@ExceptionHandler` | `@app.exception_handler(SomeError)` | 예외 핸들러 |
| `@ControllerAdvice` | 전역 `exception_handler` | 전역 예외 처리 |
| `ResponseEntity<T>` | `JSONResponse` / `Response` | 커스텀 응답 |
| `ResponseEntity.ok(body)` | `return body` (response_model로) | 200 응답 |
| `ResponseEntity.status(201)` | `status_code=201` (데코레이터에) | 상태 코드 |
| `HttpStatus.NOT_FOUND` | `status.HTTP_404_NOT_FOUND` | HTTP 상태 상수 |
| `@Autowired` | `Depends()` | 의존성 주입 |
| `@Bean` (싱글톤) | `@lru_cache + Depends` | 싱글톤 Bean |
| `@Component`, `@Service` | 일반 Python 클래스 | 서비스 클래스 |
| `@Async` | `async def` | 비동기 메서드 |
| `CompletableFuture.allOf()` | `asyncio.gather()` | 병렬 실행 |
| `@PostConstruct` | `lifespan` (yield 이전) | 시작 훅 |
| `@PreDestroy` | `lifespan` (yield 이후) | 종료 훅 |
| `application.properties` | `.env` + `BaseSettings` | 설정 파일 |
| `@ConfigurationProperties` | `BaseSettings` 클래스 | 설정 바인딩 |
| `spring.profiles.active` | `ENVIRONMENT=production` 환경변수 | 환경 분리 |
| `@MockBean` | `dependency_overrides` | 테스트 Mock |
| `MockMvc` | `TestClient` / `AsyncClient` | HTTP 테스트 |
| `@SpringBootTest` | `pytest` + `conftest.py` | 통합 테스트 |
| `/actuator/health` | 커스텀 `/health` 엔드포인트 | 헬스체크 |
| `server.shutdown=graceful` | `lifespan` + uvicorn 옵션 | Graceful Shutdown |
| `@CrossOrigin` | `CORSMiddleware` | CORS 설정 |
| `Filter` | Middleware | 미들웨어 |
| `HandlerInterceptor` | Middleware / Depends | 인터셉터 |

### 코드 수준 병렬 비교

**예외 처리:**

```java
// Spring Boot
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity
            .status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("USER_NOT_FOUND", e.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException e) {
        List<String> errors = e.getBindingResult().getFieldErrors()
            .stream().map(FieldError::getDefaultMessage).toList();
        return ResponseEntity.badRequest().body(new ErrorResponse("VALIDATION_FAILED", errors));
    }
}
```

```python
# FastAPI
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id

# @ExceptionHandler(UserNotFoundException.class)에 대응
@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"code": "USER_NOT_FOUND", "message": f"User {exc.user_id} not found"},
    )

# @ExceptionHandler(MethodArgumentNotValidException.class)에 대응
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"code": "VALIDATION_FAILED", "detail": exc.errors()},
    )
```

**의존성 주입:**

```java
// Spring Boot
@Service
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;

    @Autowired
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
}

@RestController
public class UserController {
    @Autowired
    private UserService userService;
}
```

```python
# FastAPI
from fastapi import Depends
from functools import lru_cache

class UserRepository:
    async def find_by_id(self, user_id: int): ...

class EmailService:
    async def send(self, email: str): ...

class UserService:
    def __init__(
        self,
        repo: UserRepository = Depends(UserRepository),
        email_svc: EmailService = Depends(EmailService),
    ):
        self.repo = repo
        self.email_svc = email_svc

    async def find_by_id(self, user_id: int):
        return await self.repo.find_by_id(user_id)

# 싱글톤 의존성 (= @Bean singleton scope)
@lru_cache
def get_settings() -> Settings:
    return Settings()

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    user_service: UserService = Depends(UserService),      # 매 요청마다 생성
    settings: Settings = Depends(get_settings),             # 싱글톤
):
    return await user_service.find_by_id(user_id)
```

**CORS 설정:**

```java
// Spring Boot
@Configuration
public class CorsConfig {
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("http://localhost:3000"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
        config.setAllowedHeaders(List.of("*"));
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}
```

```python
# FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 완전한 예제 애플리케이션

모든 개념을 통합한 실전 애플리케이션 구조입니다.

```
my-fastapi-app/
├── main.py              ← SpringApplication 역할
├── config.py            ← application.properties + @ConfigurationProperties
├── lifespan.py          ← @PostConstruct / @PreDestroy
├── dependencies.py      ← @Bean 정의
├── routers/
│   ├── __init__.py
│   ├── users.py         ← UserController
│   └── health.py        ← ActuatorController
├── models/
│   ├── __init__.py
│   ├── requests.py      ← DTO (Request)
│   └── responses.py     ← DTO (Response)
├── services/
│   ├── __init__.py
│   └── user_service.py  ← @Service
├── exceptions.py        ← @ControllerAdvice
├── tests/
│   ├── conftest.py
│   └── test_users.py
├── .env
└── pyproject.toml
```

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lifespan import lifespan
from routers import users, health
from exceptions import register_exception_handlers
from config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

# 미들웨어 등록 (= Filter / @CrossOrigin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록 (= @ComponentScan + @RequestMapping)
app.include_router(health.router)
app.include_router(users.router, prefix="/api/v1")

# 전역 예외 핸들러 등록 (= @ControllerAdvice)
register_exception_handlers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.debug,
        timeout_graceful_shutdown=30,
    )
```

---

## 자주 하는 실수 (Java 개발자 관점)

### 1. async def 안에서 동기 라이브러리 사용

```python
# ❌ 잘못된 코드: 이벤트 루프 전체 블로킹
@app.get("/users")
async def get_users():
    import requests  # 동기 라이브러리
    response = requests.get("https://api.example.com/users")  # 블로킹!
    return response.json()

# ✅ 올바른 코드: 비동기 라이브러리 사용
@app.get("/users")
async def get_users():
    import httpx  # 비동기 라이브러리
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/users")
    return response.json()
```

### 2. Pydantic 모델 반환 시 orm_mode 누락

```python
# ❌ SQLAlchemy ORM 객체를 그냥 반환하면 직렬화 실패
class UserResponse(BaseModel):
    id: int
    name: str
    # Config 없음

# ✅ from_attributes = True 설정 (Pydantic v2)
class UserResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
```

### 3. dependency_overrides 정리 누락

```python
# ❌ 테스트 후 정리 안 함 → 다른 테스트에 영향
def test_something():
    app.dependency_overrides[get_db] = lambda: mock_db
    # ... 테스트
    # 정리 안 함!

# ✅ 반드시 정리
def test_something():
    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        # ... 테스트
    finally:
        app.dependency_overrides.clear()

# 또는 fixture로 자동 관리
@pytest.fixture(autouse=True)
def cleanup_overrides():
    yield
    app.dependency_overrides.clear()
```

### 4. 전역 변수로 상태 공유 (workers > 1 시 문제)

```python
# ❌ workers=4 환경에서는 각 프로세스가 별도 메모리를 가짐
cache = {}  # 프로세스간 공유 안 됨!

@app.get("/items/{id}")
async def get_item(id: int):
    if id in cache:  # 다른 worker가 저장한 것은 못 읽음
        return cache[id]

# ✅ Redis 등 외부 캐시 사용
@app.get("/items/{id}")
async def get_item(id: int, redis = Depends(get_redis)):
    cached = await redis.get(f"item:{id}")
    if cached:
        return json.loads(cached)
```

---

*이 문서는 Spring Boot 경력자가 FastAPI의 핵심 개념을 빠르게 이해할 수 있도록 작성되었습니다. 각 섹션의 코드 예시는 실제 동작하는 코드를 기반으로 하며, 프로덕션 환경에서 필요한 에러 핸들링과 설정을 포함합니다.*
