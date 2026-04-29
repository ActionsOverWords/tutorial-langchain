# datetime - 날짜와 시간

> 공식 문서: https://docs.python.org/3/library/datetime.html

Python의 `datetime` 모듈은 Java의 `java.time` 패키지(Java 8+)에 해당합니다.
Java 8 이전의 `java.util.Date`가 혼란스럽듯, Python도 timezone 처리에 주의가 필요합니다.

```python
from datetime import date, time, datetime, timedelta, timezone
```

---

## 1. 핵심 클래스

### Java vs Python 클래스 대응표

| Python `datetime` | Java `java.time` | 설명 |
|---|---|---|
| `date` | `LocalDate` | 날짜만 (년/월/일) |
| `time` | `LocalTime` | 시간만 (시/분/초/마이크로초) |
| `datetime` | `LocalDateTime` / `ZonedDateTime` | 날짜 + 시간 |
| `timedelta` | `Duration` / `Period` | 시간 간격 |
| `timezone` | `ZoneOffset` | 고정 오프셋 타임존 |
| `zoneinfo.ZoneInfo` | `ZoneId` | IANA 타임존 (Python 3.9+) |

```python
from datetime import date, time, datetime, timedelta, timezone

# date: 날짜만
d = date(2024, 3, 15)
print(d)               # 2024-03-15
print(d.year)          # 2024
print(d.month)         # 3
print(d.day)           # 15

# time: 시간만
t = time(14, 30, 0, 500000)  # 14:30:00.500000
print(t)               # 14:30:00.500000
print(t.hour)          # 14
print(t.minute)        # 30
print(t.second)        # 0
print(t.microsecond)   # 500000  (Java의 nanosecond와 달리 마이크로초 단위)

# datetime: 날짜 + 시간 조합
dt = datetime(2024, 3, 15, 14, 30, 0)
print(dt)              # 2024-03-15 14:30:00

# timedelta: 시간 간격
delta = timedelta(days=7, hours=3, minutes=30)
print(delta)           # 7 days, 3:30:00
```

---

## 2. 현재 시각

### `now()` vs `utcnow()` vs `now(timezone.utc)`

이 세 가지 중 무엇을 써야 할지 헷갈리는 경우가 많습니다.

```java
// Java
LocalDateTime now = LocalDateTime.now();                    // 로컬 시각 (naive)
ZonedDateTime nowUtc = ZonedDateTime.now(ZoneOffset.UTC);   // UTC (aware)
Instant instant = Instant.now();                            // UTC epoch
```

```python
from datetime import datetime, timezone

# 1. datetime.now() - 시스템 로컬 시각, timezone 정보 없음 (naive)
local_now = datetime.now()
print(local_now)         # 2024-03-15 23:30:00.123456
print(local_now.tzinfo)  # None <- timezone 정보 없음!

# 2. datetime.utcnow() - UTC 시각이지만 timezone 정보 없음 (naive)
# 주의: Python 3.12에서 deprecated 예정
utc_now_naive = datetime.utcnow()
print(utc_now_naive)         # 2024-03-15 14:30:00.123456
print(utc_now_naive.tzinfo)  # None <- UTC인데 표시가 안 됨! 혼란의 근원

# 3. datetime.now(timezone.utc) - UTC 시각, timezone 정보 있음 (aware) [권장]
utc_now = datetime.now(timezone.utc)
print(utc_now)         # 2024-03-15 14:30:00.123456+00:00
print(utc_now.tzinfo)  # UTC <- 명시적으로 UTC임을 표시
```

### timezone-aware vs naive datetime

Java와의 핵심 차이점이자 Python datetime의 가장 큰 함정입니다.

```java
// Java: LocalDateTime은 항상 naive, ZonedDateTime은 항상 aware
// 두 타입이 명확히 분리되어 있어 혼동이 적음
LocalDateTime naive = LocalDateTime.now();
ZonedDateTime aware = ZonedDateTime.now(ZoneOffset.UTC);
```

```python
from datetime import datetime, timezone

# naive datetime: tzinfo가 None
naive = datetime(2024, 3, 15, 14, 30, 0)
print(naive.tzinfo)  # None

# aware datetime: tzinfo가 설정됨
aware = datetime(2024, 3, 15, 14, 30, 0, tzinfo=timezone.utc)
print(aware.tzinfo)  # UTC

# 핵심 문제: naive와 aware를 비교하면 TypeError 발생
try:
    result = naive < aware  # TypeError!
except TypeError as e:
    print(f"Error: {e}")
    # can't compare offset-naive and offset-aware datetimes

# naive를 aware로 변환 (localize)
# 주의: replace()는 실제 변환이 아닌 tzinfo 태그만 붙임
# 즉, "이 naive datetime이 UTC임을 선언"하는 것
utc_aware = naive.replace(tzinfo=timezone.utc)
print(utc_aware)  # 2024-03-15 14:30:00+00:00

# 권장 패턴: 처음부터 aware datetime 사용
utc_now = datetime.now(timezone.utc)  # 항상 이렇게 생성
```

---

## 3. 파싱과 포매팅

### `strptime()` / `strftime()` - Java `DateTimeFormatter`와 비교

```java
// Java
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
LocalDateTime dt = LocalDateTime.parse("2024-03-15 14:30:00", formatter);
String formatted = dt.format(formatter);
```

```python
from datetime import datetime

# strptime: 문자열 -> datetime (parse)
dt = datetime.strptime("2024-03-15 14:30:00", "%Y-%m-%d %H:%M:%S")
print(dt)   # 2024-03-15 14:30:00

# strftime: datetime -> 문자열 (format)
formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
print(formatted)   # 2024-03-15 14:30:00

# 다양한 포맷 예시
dt.strftime("%Y/%m/%d")                  # 2024/03/15
dt.strftime("%d %b %Y")                  # 15 Mar 2024
dt.strftime("%A, %B %d, %Y")             # Friday, March 15, 2024
dt.strftime("%Y-%m-%dT%H:%M:%S")        # 2024-03-15T14:30:00
```

### 자주 쓰는 포맷 문자열

| 코드 | 의미 | 예시 | Java 대응 |
|---|---|---|---|
| `%Y` | 4자리 연도 | `2024` | `yyyy` |
| `%m` | 2자리 월 | `03` | `MM` |
| `%d` | 2자리 일 | `15` | `dd` |
| `%H` | 24시간 시 | `14` | `HH` |
| `%M` | 분 | `30` | `mm` |
| `%S` | 초 | `00` | `ss` |
| `%f` | 마이크로초 | `123456` | `SSSSSS` |
| `%Z` | 타임존 이름 | `UTC`, `KST` | `z` |
| `%z` | UTC 오프셋 | `+0000`, `+0900` | `Z` |
| `%A` | 요일 전체 | `Friday` | `EEEE` |
| `%a` | 요일 축약 | `Fri` | `EEE` |
| `%B` | 월 전체 | `March` | `MMMM` |
| `%b` | 월 축약 | `Mar` | `MMM` |

### ISO 8601 포맷

```python
from datetime import datetime, timezone

dt = datetime.now(timezone.utc)

# isoformat(): ISO 8601 문자열 생성
iso_str = dt.isoformat()
print(iso_str)   # 2024-03-15T14:30:00.123456+00:00

# timespec 파라미터로 정밀도 조정
dt.isoformat(timespec="seconds")       # 2024-03-15T14:30:00+00:00
dt.isoformat(timespec="milliseconds")  # 2024-03-15T14:30:00.123+00:00
dt.isoformat(timespec="minutes")       # 2024-03-15T14:30+00:00

# fromisoformat(): ISO 8601 문자열 파싱 (Python 3.7+)
parsed = datetime.fromisoformat("2024-03-15T14:30:00+00:00")
print(parsed)   # 2024-03-15 14:30:00+00:00

# Python 3.11+: Z 접미사도 지원
# parsed = datetime.fromisoformat("2024-03-15T14:30:00Z")

# Python 3.10 이하에서 Z 접미사 처리
iso_with_z = "2024-03-15T14:30:00Z"
parsed = datetime.strptime(iso_with_z, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
```

---

## 4. 날짜 계산

### `timedelta` 덧셈/뺄셈

```java
// Java
LocalDate future = LocalDate.now().plusDays(7);
LocalDateTime past = LocalDateTime.now().minusHours(3);
Duration duration = Duration.between(start, end);
Period period = Period.between(startDate, endDate);
```

```python
from datetime import datetime, date, timedelta, timezone

now = datetime.now(timezone.utc)

# timedelta 생성 파라미터
delta = timedelta(
    weeks=1,          # 7일
    days=3,
    hours=2,
    minutes=30,
    seconds=15,
    milliseconds=500,
    microseconds=1000
)

# 날짜 더하기/빼기
future = now + timedelta(days=7)
past = now - timedelta(hours=3)

# date에도 동일하게 적용
today = date.today()
next_week = today + timedelta(weeks=1)
yesterday = today - timedelta(days=1)

print(f"오늘: {today}")
print(f"다음 주: {next_week}")
print(f"어제: {yesterday}")
```

### 두 날짜 차이 계산

```java
// Java
long days = ChronoUnit.DAYS.between(start, end);
Duration duration = Duration.between(startDt, endDt);
long hours = duration.toHours();
```

```python
from datetime import datetime, date, timezone

# 두 datetime의 차이 -> timedelta 반환
start = datetime(2024, 1, 1, tzinfo=timezone.utc)
end = datetime(2024, 3, 15, 14, 30, tzinfo=timezone.utc)

diff = end - start  # timedelta 객체

print(diff)                         # 74 days, 14:30:00
print(diff.days)                    # 74  (정수 일수)
print(diff.seconds)                 # 52200  (일 단위 제외한 나머지 초)
print(diff.total_seconds())         # 6444600.0  (전체를 초로 환산)

# 시간으로 환산
total_hours = diff.total_seconds() / 3600
print(f"{total_hours:.1f}시간")    # 1790.2시간

# 날짜만 비교
d1 = date(2024, 1, 1)
d2 = date(2024, 3, 15)
date_diff = d2 - d1
print(date_diff.days)  # 74

# 비교 연산자 사용 가능
if end > start:
    print("end가 start 이후")
```

---

## 5. 타임존 처리

### `timezone.utc` 사용법

```python
from datetime import datetime, timezone, timedelta

# UTC
utc = timezone.utc
now_utc = datetime.now(utc)

# 고정 오프셋 타임존 생성
kst = timezone(timedelta(hours=9))    # UTC+9 (한국 표준시)
jst = timezone(timedelta(hours=9))    # UTC+9 (일본 표준시, KST와 동일)
est = timezone(timedelta(hours=-5))   # UTC-5 (미국 동부)

# UTC -> KST 변환
now_kst = now_utc.astimezone(kst)
print(f"UTC: {now_utc}")
print(f"KST: {now_kst}")

# aware datetime의 타임존 변환
utc_dt = datetime(2024, 3, 15, 14, 30, tzinfo=timezone.utc)
kst_dt = utc_dt.astimezone(kst)
print(f"UTC: {utc_dt}")         # 2024-03-15 14:30:00+00:00
print(f"KST: {kst_dt}")         # 2024-03-15 23:30:00+09:00
```

### `zoneinfo` 모듈 (Python 3.9+) - Java `ZoneId`와 비교

고정 오프셋(`timezone(timedelta(hours=9))`)과 달리,
`ZoneInfo`는 DST(일광절약시간) 등 IANA 타임존 규칙을 완전히 지원합니다.

```java
// Java
ZoneId kst = ZoneId.of("Asia/Seoul");
ZonedDateTime now = ZonedDateTime.now(kst);
ZonedDateTime converted = utcDateTime.withZoneSameInstant(kst);
```

```python
# Python 3.9+
from datetime import datetime
from zoneinfo import ZoneInfo

# ZoneInfo: IANA 타임존 ID 사용
kst = ZoneInfo("Asia/Seoul")
pst = ZoneInfo("America/Los_Angeles")
utc = ZoneInfo("UTC")

# 현재 시각을 특정 타임존으로
now_kst = datetime.now(kst)
print(now_kst)  # 2024-03-15 23:30:00+09:00

# UTC datetime을 KST로 변환
utc_dt = datetime(2024, 3, 15, 14, 30, tzinfo=ZoneInfo("UTC"))
kst_dt = utc_dt.astimezone(kst)
print(kst_dt)   # 2024-03-15 23:30:00+09:00

# Python 3.8 이하: pytz 라이브러리 사용
# pip install pytz
import pytz
kst_pytz = pytz.timezone("Asia/Seoul")
now_kst_pytz = datetime.now(kst_pytz)
```

### API 응답에서 UTC로 저장, 표시할 때 로컬 변환 패턴

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# 패턴: DB에 UTC로 저장, 표시할 때만 로컬 변환

def save_to_db(event_time: datetime) -> str:
    """
    항상 UTC로 정규화하여 저장.
    DB 컬럼 타입: TIMESTAMP WITH TIME ZONE (권장)
    """
    # aware datetime을 UTC로 변환
    utc_time = event_time.astimezone(timezone.utc)
    # DB에 저장할 ISO 8601 문자열 (또는 datetime 객체 직접 전달)
    return utc_time.isoformat()

def display_to_user(utc_str: str, user_timezone: str = "Asia/Seoul") -> str:
    """
    DB에서 읽어온 UTC 시각을 사용자 타임존으로 변환하여 표시.
    """
    utc_dt = datetime.fromisoformat(utc_str)
    user_tz = ZoneInfo(user_timezone)
    local_dt = utc_dt.astimezone(user_tz)
    return local_dt.strftime("%Y년 %m월 %d일 %H:%M:%S (%Z)")

# 사용 예
user_input = datetime(2024, 3, 15, 23, 30, tzinfo=ZoneInfo("Asia/Seoul"))
stored = save_to_db(user_input)
print(f"DB 저장: {stored}")
# DB 저장: 2024-03-15T14:30:00+00:00

displayed = display_to_user(stored, "Asia/Seoul")
print(f"사용자 표시: {displayed}")
# 사용자 표시: 2024년 03월 15일 23:30:00 (KST)
```

---

## 6. 실전 팁

### API에서 받은 timestamp 문자열 파싱

외부 API는 다양한 형식으로 datetime을 반환합니다.

```python
from datetime import datetime, timezone

# 형식 1: ISO 8601 with timezone (가장 일반적)
s1 = "2024-03-15T14:30:00+09:00"
dt1 = datetime.fromisoformat(s1)
print(dt1)            # 2024-03-15 14:30:00+09:00
print(dt1.tzinfo)     # UTC+09:00

# 형식 2: ISO 8601 with Z (UTC)
s2 = "2024-03-15T14:30:00Z"
# Python 3.11+
# dt2 = datetime.fromisoformat(s2)
# Python 3.10 이하
dt2 = datetime.strptime(s2, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

# 형식 3: 밀리초 포함 ISO 8601
s3 = "2024-03-15T14:30:00.123Z"
dt3 = datetime.strptime(s3, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

# 형식 4: 커스텀 포맷
s4 = "15/Mar/2024 14:30:00 +0900"
dt4 = datetime.strptime(s4, "%d/%b/%Y %H:%M:%S %z")

# 실전: 여러 포맷 시도 (방어적 파싱)
def parse_datetime_flexible(dt_str: str) -> datetime:
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",    # ISO with microseconds
        "%Y-%m-%dT%H:%M:%S%z",        # ISO with timezone
        "%Y-%m-%dT%H:%M:%SZ",         # ISO with Z
        "%Y-%m-%d %H:%M:%S",          # Simple format (naive)
        "%Y-%m-%d",                    # Date only
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str.strip(), fmt)
            # naive datetime이면 UTC로 가정
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    raise ValueError(f"Unable to parse datetime: {dt_str!r}")
```

### DB 저장 시 UTC 권장 이유

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# 문제 상황: naive datetime을 KST로 저장
bad_practice = datetime.now()  # naive, 서버 로컬 시각
# 서버를 다른 지역으로 이전하면? -> 모든 시각이 틀어짐
# DST(일광절약시간) 적용 국가라면? -> 1시간 오차 발생 가능

# 권장: UTC aware datetime으로 저장
good_practice = datetime.now(timezone.utc)

# SQLAlchemy에서 UTC 컬럼 사용 예
# from sqlalchemy import Column, DateTime
# class Event(Base):
#     created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

### `time.time()` (Unix timestamp) 변환

```python
import time
from datetime import datetime, timezone

# Unix timestamp 얻기 (float, 초 단위)
unix_ts = time.time()
print(unix_ts)  # 1710509400.123456

# milliseconds timestamp (JavaScript, Java System.currentTimeMillis()와 호환)
ms_ts = int(time.time() * 1000)
print(ms_ts)    # 1710509400123

# Unix timestamp -> datetime (aware, UTC)
dt_from_ts = datetime.fromtimestamp(unix_ts, tz=timezone.utc)
print(dt_from_ts)   # 2024-03-15 14:30:00.123456+00:00

# datetime -> Unix timestamp
dt = datetime(2024, 3, 15, 14, 30, 0, tzinfo=timezone.utc)
ts = dt.timestamp()
print(ts)   # 1710509400.0

# Java와 비교
# Java: Instant.now().toEpochMilli()  -> milliseconds
# Java: Instant.now().getEpochSecond() -> seconds
# Python: time.time() -> seconds (float)
# Python: datetime.timestamp() -> seconds (float)

# 실전 예: API 응답에서 Unix timestamp 처리
api_response = {
    "event_id": "abc123",
    "created_at": 1710509400,  # Unix timestamp (초)
    "updated_at": 1710509400123  # Unix timestamp (밀리초, JS 스타일)
}

created = datetime.fromtimestamp(api_response["created_at"], tz=timezone.utc)
updated = datetime.fromtimestamp(api_response["updated_at"] / 1000, tz=timezone.utc)

print(f"Created: {created.isoformat()}")
print(f"Updated: {updated.isoformat()}")
```

---

## 핵심 요약

| 상황 | 권장 방법 |
|---|---|
| 현재 시각 가져오기 | `datetime.now(timezone.utc)` |
| DB 저장 | UTC aware datetime |
| API 파싱 | `fromisoformat()` 또는 `strptime()` 후 UTC 정규화 |
| 타임존 변환 | `astimezone(ZoneInfo("Asia/Seoul"))` |
| 날짜 계산 | `timedelta` 덧셈/뺄셈 |
| Unix timestamp | `datetime.fromtimestamp(ts, tz=timezone.utc)` |

> **핵심 원칙**: 내부 처리와 저장은 항상 UTC aware datetime을 사용하고, 사용자에게 표시할 때만 로컬 타임존으로 변환하세요. Java의 `Instant` + `ZonedDateTime` 패턴과 동일한 철학입니다.
