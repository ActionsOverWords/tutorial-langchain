# re - 정규표현식

> 공식 문서: https://docs.python.org/3/library/re.html

Python의 `re` 모듈은 Java의 `java.util.regex` 패키지(`Pattern`, `Matcher`)와 같은 역할을 합니다. 문법 자체는 대부분 동일하지만, API 구조와 Python 특유의 raw string 처리 방식에서 차이가 납니다.

---

## 1. 기본 함수

### 함수 개요

| Python 함수         | Java 대응                                 | 설명                              |
|---------------------|-------------------------------------------|-----------------------------------|
| `re.search()`       | `matcher.find()`                          | 문자열 어디서든 첫 번째 매치 탐색 |
| `re.match()`        | `matcher.find()` (문자열 시작 앵커)       | 문자열 시작부터 매치 탐색         |
| `re.fullmatch()`    | `matcher.matches()`                       | 전체 문자열이 패턴과 일치 여부    |
| `re.findall()`      | 루프로 `matcher.find()` 반복              | 모든 매치 문자열 리스트 반환      |
| `re.finditer()`     | 루프로 `matcher.find()` 반복              | 모든 매치 `Match` 객체 이터레이터 |
| `re.sub()`          | `matcher.replaceAll()`                    | 매치된 부분 치환                  |
| `re.subn()`         | `replaceAll()` + 치환 횟수 반환           | 치환 결과와 치환 횟수 튜플 반환   |
| `re.split()`        | `Pattern.compile(p).split(s)`             | 패턴으로 분리                     |

### `re.search()` vs `re.match()` vs `re.fullmatch()`

```python
import re

text = "Hello, World!"

# search: 문자열 전체에서 패턴 탐색
result = re.search(r"World", text)
print(result)           # <re.Match object; span=(7, 12), match='World'>
print(result.group())   # 'World'

# match: 문자열 시작부터만 탐색
result = re.match(r"World", text)
print(result)           # None (시작이 'World'가 아니므로)

result = re.match(r"Hello", text)
print(result.group())   # 'Hello'

# fullmatch: 전체 문자열이 패턴과 일치해야 함
result = re.fullmatch(r"Hello, World!", text)
print(result.group())   # 'Hello, World!'

result = re.fullmatch(r"Hello", text)
print(result)           # None
```

**Java 비교:**

```java
import java.util.regex.*;

String text = "Hello, World!";
Pattern pattern = Pattern.compile("World");
Matcher matcher = pattern.matcher(text);

// find() = re.search()
if (matcher.find()) {
    System.out.println(matcher.group()); // "World"
}

// matches() = re.fullmatch()
boolean full = Pattern.matches("Hello, World!", text); // true
```

> `re.match()`는 `^` 앵커를 붙인 `re.search()`와 동일하게 동작합니다. 혼동을 피하려면 항상 `re.search()`를 사용하고 필요 시 `^`를 명시하는 것이 낫습니다.

### `re.findall()` vs `re.finditer()`

```python
import re

text = "사과: 3개, 바나나: 5개, 오렌지: 2개"

# findall: 매치된 문자열 리스트 반환
numbers = re.findall(r"\d+", text)
print(numbers)  # ['3', '5', '2']

# 그룹이 있으면 그룹 내용만 반환
pairs = re.findall(r"(\w+): (\d+)", text)
print(pairs)  # [('사과', '3'), ('바나나', '5'), ('오렌지', '2')]

# finditer: Match 객체 이터레이터 반환 (대용량 텍스트에서 메모리 효율적)
for match in re.finditer(r"\d+", text):
    print(f"값: {match.group()}, 위치: {match.span()}")
# 값: 3, 위치: (4, 5)
# 값: 5, 위치: (12, 13)
# 값: 2, 위치: (20, 21)
```

### `re.sub()` / `re.subn()` - 치환

```python
import re

text = "2024-01-15"

# sub: 치환 (Java replaceAll에 해당)
result = re.sub(r"-", "/", text)
print(result)  # "2024/01/15"

# 치환 횟수 제한
result = re.sub(r"-", "/", text, count=1)
print(result)  # "2024/01-15"

# 콜백 함수로 치환
def double_number(match):
    return str(int(match.group()) * 2)

result = re.sub(r"\d+", double_number, "a=3, b=5")
print(result)  # "a=6, b=10"

# subn: 치환 결과와 치환 횟수 튜플 반환
result, count = re.subn(r"-", "/", text)
print(result, count)  # "2024/01/15" 2
```

**Java 비교:**

```java
String text = "2024-01-15";
String result = text.replaceAll("-", "/");  // "2024/01/15"
String first = text.replaceFirst("-", "/"); // "2024/01-15" (count=1에 해당)
```

### `re.split()` - 분리

```python
import re

# 여러 구분자로 분리
text = "사과,바나나;오렌지 포도"
parts = re.split(r"[,; ]+", text)
print(parts)  # ['사과', '바나나', '오렌지', '포도']

# 캡처 그룹 포함 시 구분자도 결과에 포함
parts = re.split(r"([,; ]+)", text)
print(parts)  # ['사과', ',', '바나나', ';', '오렌지', ' ', '포도']
```

**Java 비교:**

```java
String[] parts = "사과,바나나;오렌지 포도".split("[,; ]+");
// ["사과", "바나나", "오렌지", "포도"]
```

---

## 2. 패턴 문법

### Java와 동일한 부분

대부분의 정규표현식 문법은 Java와 동일합니다.

| 패턴      | 의미                              | 예시                      |
|-----------|-----------------------------------|---------------------------|
| `.`       | 임의의 문자 1개 (개행 제외)       | `a.c` → `abc`, `a1c`     |
| `*`       | 0회 이상 반복                     | `ab*` → `a`, `ab`, `abb` |
| `+`       | 1회 이상 반복                     | `ab+` → `ab`, `abb`      |
| `?`       | 0회 또는 1회                      | `ab?` → `a`, `ab`        |
| `{n}`     | 정확히 n회                        | `a{3}` → `aaa`           |
| `{n,m}`   | n~m회                             | `a{2,4}` → `aa`~`aaaa`   |
| `^`       | 문자열 시작                       | `^Hello`                  |
| `$`       | 문자열 끝                         | `World$`                  |
| `[abc]`   | a, b, c 중 하나                   | `[aeiou]`                 |
| `[^abc]`  | a, b, c 제외                      | `[^0-9]`                  |
| `[a-z]`   | a~z 범위                          | `[A-Za-z0-9]`             |
| `()`      | 그룹 캡처                         | `(ab)+`                   |
| `\|`      | OR                                | `cat\|dog`                |
| `\d`      | 숫자 `[0-9]`                      |                           |
| `\w`      | 단어 문자 `[a-zA-Z0-9_]`          |                           |
| `\s`      | 공백 문자                         |                           |
| `\D`, `\W`, `\S` | 각각의 부정              |                           |

### Python 특유: raw string `r"패턴"` 사용 필수

Python에서 정규표현식은 반드시 raw string(`r"..."`)으로 작성해야 합니다.

```python
import re

# 문제: 일반 문자열에서 \d는 Python이 먼저 이스케이프 처리
pattern_bad = "\d+"     # Python이 \d를 해석 시도 → 실제로는 d+가 됨
pattern_good = r"\d+"   # raw string: 백슬래시를 그대로 전달

# 특히 \b (단어 경계)의 경우 더 위험
# "\b"는 Python에서 백스페이스 문자!
pattern_bad2 = "\bword\b"    # \b = 백스페이스 → 의도와 전혀 다름
pattern_good2 = r"\bword\b"  # 올바른 단어 경계 패턴

text = "word in a sentence"
print(re.search(pattern_bad2, text))   # None
print(re.search(pattern_good2, text))  # Match 객체
```

**Java와 비교:**

```java
// Java에서도 \d는 \\d로 이스케이프 필요
Pattern p = Pattern.compile("\\d+");   // Java에서는 \\d
Pattern p = Pattern.compile("\\bword\\b");

// Python raw string이 Java의 이스케이프를 대체
// Python: r"\d+"  ←→  Java: "\\d+"
```

> Java 개발자가 Python 정규표현식에서 가장 많이 실수하는 부분입니다. **항상 `r"..."` raw string을 사용**하세요.

---

## 3. 컴파일 (`re.compile()`)

### 기본 사용

```python
import re

# 패턴을 한 번만 컴파일하여 재사용
EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

emails = [
    "user@example.com",
    "invalid-email",
    "admin@company.co.kr",
]

for email in emails:
    if EMAIL_PATTERN.match(email):
        print(f"유효한 이메일: {email}")

# 컴파일된 패턴 객체로 모든 re 함수 사용 가능
matches = EMAIL_PATTERN.findall("연락처: user@example.com, admin@co.kr")
print(matches)  # ['user@example.com', 'admin@co.kr']
```

**Java 비교:**

```java
// Java Pattern.compile() - Python re.compile()과 동일한 목적
private static final Pattern EMAIL_PATTERN = Pattern.compile(
    "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
);

public boolean isValid(String email) {
    return EMAIL_PATTERN.matcher(email).matches();
}
```

### 성능 최적화

```python
import re

# 나쁜 예: 루프 안에서 매번 컴파일 (내부적으로 캐싱되지만 명시적 관리 불가)
def process_items_bad(items: list[str]) -> list[str]:
    return [item for item in items if re.match(r"\d{4}-\d{2}-\d{2}", item)]

# 좋은 예: 모듈 레벨에서 미리 컴파일
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")

def process_items_good(items: list[str]) -> list[str]:
    return [item for item in items if DATE_PATTERN.match(item)]
```

> Python `re` 모듈은 내부적으로 최근 컴파일된 패턴을 캐시(기본 128개)하지만, 많은 패턴을 반복 사용하는 경우 명시적 `re.compile()`이 안전합니다.

---

## 4. 그룹 캡처

### 일반 그룹 `()`

```python
import re

text = "2024-01-15"
match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)

if match:
    print(match.group())    # '2024-01-15' (전체 매치)
    print(match.group(0))   # '2024-01-15' (group()과 동일)
    print(match.group(1))   # '2024'
    print(match.group(2))   # '01'
    print(match.group(3))   # '15'
    print(match.groups())   # ('2024', '01', '15') - 모든 그룹 튜플
```

**Java 비교:**

```java
Pattern p = Pattern.compile("(\\d{4})-(\\d{2})-(\\d{2})");
Matcher m = p.matcher("2024-01-15");
if (m.find()) {
    System.out.println(m.group());   // "2024-01-15"
    System.out.println(m.group(1));  // "2024"
    System.out.println(m.group(2));  // "01"
    System.out.println(m.group(3));  // "15"
}
```

### 이름 있는 그룹 `(?P<name>)`

```python
import re

text = "2024-01-15"
match = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", text)

if match:
    print(match.group("year"))    # '2024'
    print(match.group("month"))   # '01'
    print(match.group("day"))     # '15'
    print(match.groupdict())      # {'year': '2024', 'month': '01', 'day': '15'}

# 이름 있는 그룹으로 치환
result = re.sub(
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})",
    r"\g<day>/\g<month>/\g<year>",  # 역참조
    "날짜: 2024-01-15"
)
print(result)  # "날짜: 15/01/2024"
```

**Java 비교:**

```java
// Java도 이름 있는 그룹 지원 (Java 7+)
Pattern p = Pattern.compile("(?<year>\\d{4})-(?<month>\\d{2})-(?<day>\\d{2})");
Matcher m = p.matcher("2024-01-15");
if (m.find()) {
    System.out.println(m.group("year"));  // "2024"
}
```

### 비캡처 그룹 `(?:...)`

```python
import re

# (?:...)는 그룹을 만들되 캡처하지 않음
text = "http://example.com"
match = re.search(r"(?:https?|ftp)://(\w+\.\w+)", text)
if match:
    print(match.group(1))  # 'example.com' (그룹 1 = 도메인, 프로토콜은 비캡처)
```

---

## 5. 플래그

```python
import re

text = "Hello\nWORLD"

# re.IGNORECASE (re.I): 대소문자 무시
re.search(r"hello", text, re.IGNORECASE)  # Match

# re.MULTILINE (re.M): ^ $ 가 각 줄의 시작/끝에 매치
re.findall(r"^\w+", text, re.MULTILINE)  # ['Hello', 'WORLD']

# re.DOTALL (re.S): . 이 개행 문자도 포함
re.search(r"Hello.WORLD", text, re.DOTALL)  # Match

# 플래그 여러 개 조합: | 로 결합
re.search(r"hello.world", text, re.IGNORECASE | re.DOTALL)

# 컴파일 시 플래그 지정
pattern = re.compile(r"hello", re.IGNORECASE)
```

**Java 비교:**

```java
// Java Pattern 플래그
Pattern p = Pattern.compile("hello", Pattern.CASE_INSENSITIVE);
Pattern p = Pattern.compile("^\\w+", Pattern.MULTILINE);
Pattern p = Pattern.compile("hello.world", Pattern.DOTALL);

// 여러 플래그 조합
Pattern p = Pattern.compile("hello.world",
    Pattern.CASE_INSENSITIVE | Pattern.DOTALL);
```

| Python 플래그        | 단축     | Java 플래그                    |
|----------------------|----------|--------------------------------|
| `re.IGNORECASE`      | `re.I`   | `Pattern.CASE_INSENSITIVE`     |
| `re.MULTILINE`       | `re.M`   | `Pattern.MULTILINE`            |
| `re.DOTALL`          | `re.S`   | `Pattern.DOTALL`               |
| `re.VERBOSE`         | `re.X`   | `Pattern.COMMENTS`             |
| `re.ASCII`           | `re.A`   | 없음                           |
| `re.UNICODE`         | `re.U`   | 기본값                         |

### `re.VERBOSE` - 주석 있는 패턴

```python
import re

# 복잡한 패턴을 읽기 쉽게 여러 줄로 작성
EMAIL_PATTERN = re.compile(r"""
    [a-zA-Z0-9._%+-]+   # 로컬 파트
    @                    # @ 구분자
    [a-zA-Z0-9.-]+       # 도메인
    \.                   # 점
    [a-zA-Z]{2,}         # 최상위 도메인
""", re.VERBOSE)
```

---

## 6. 자주 쓰는 패턴 예시

### 이메일 추출

```python
import re

EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

text = "문의: user@example.com, admin@company.co.kr 로 연락주세요."
emails = EMAIL_RE.findall(text)
print(emails)  # ['user@example.com', 'admin@company.co.kr']
```

### URL 추출

```python
import re

URL_RE = re.compile(
    r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    r"(?:/[^\s]*)?"
)

text = "방문: https://www.example.com/path?q=1 또는 http://api.test.io"
urls = URL_RE.findall(text)
print(urls)  # ['https://www.example.com/path?q=1', 'http://api.test.io']
```

### 전화번호 추출 (한국)

```python
import re

PHONE_RE = re.compile(
    r"(?:0\d{1,2})-?(\d{3,4})-?(\d{4})"
)

text = "연락처: 010-1234-5678, 02-987-6543, 031 555 1234"
for match in PHONE_RE.finditer(text):
    print(match.group())
# 010-1234-5678
# 02-987-6543
# 031 555 1234
```

### 날짜 추출 및 변환

```python
import re

DATE_RE = re.compile(
    r"(?P<year>\d{4})[.\-/](?P<month>\d{1,2})[.\-/](?P<day>\d{1,2})"
)

text = "생성일: 2024.01.15, 수정일: 2024-3-5"

for match in DATE_RE.finditer(text):
    d = match.groupdict()
    normalized = f"{d['year']}-{d['month'].zfill(2)}-{d['day'].zfill(2)}"
    print(f"원본: {match.group()} → 정규화: {normalized}")
# 원본: 2024.01.15 → 정규화: 2024-01-15
# 원본: 2024-3-5 → 정규화: 2024-03-05
```

### IP 주소 유효성 검사

```python
import re

IP_RE = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$"
)

ips = ["192.168.1.1", "256.0.0.1", "10.0.0.255", "abc"]
for ip in ips:
    valid = bool(IP_RE.match(ip))
    print(f"{ip}: {'유효' if valid else '무효'}")
# 192.168.1.1: 유효
# 256.0.0.1: 무효
# 10.0.0.255: 유효
# abc: 무효
```

### HTML 태그 제거

```python
import re

HTML_TAG_RE = re.compile(r"<[^>]+>")

html = "<p>안녕하세요, <b>홍길동</b>님!</p>"
plain = HTML_TAG_RE.sub("", html)
print(plain)  # "안녕하세요, 홍길동님!"

# 주의: 복잡한 HTML 파싱에는 BeautifulSoup 등 전용 라이브러리 사용 권장
```

### 빠른 참조 - 자주 쓰는 패턴 모음

```python
import re

PATTERNS = {
    "email":   re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone_kr": re.compile(r"0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}"),
    "date_iso": re.compile(r"\d{4}-\d{2}-\d{2}"),
    "url":     re.compile(r"https?://\S+"),
    "number":  re.compile(r"-?\d+(?:\.\d+)?"),  # 정수 및 소수
    "korean":  re.compile(r"[가-힣]+"),
    "uuid":    re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        re.IGNORECASE
    ),
}
```
