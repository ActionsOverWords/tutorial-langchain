# LangChain Basic Chat Usage

## Install

```shell
# pip install python-dotenv langchain-openai

pip install langchain-openai
```

## Usage

### environment

- `.env` 파일

```text
OPENAI_API_KEY=...
```

### Jupyter Notebook

- VS Code 에서 사용하려면 `Jupyter` Extention 설치
- 확장자를 `ipynb`로 파일 생성 시 Notebook 실행

```python
# load environment
from dotenv import load_dotenv
load_dotenv()
```

### OpenAI

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI()

response = llm.invoke("[user message]")
response.content
```

### Upstage

- Ref Documents
  - [Upstage Console](https://console.upstage.ai/docs/getting-started?api=chat-reasoning)
  - [LangChain](https://docs.langchain.com/oss/python/integrations/chat/upstage)

```python
from langchain_upstage import ChatUpstage
llm = ChatUpstage()

response = llm.invoke("[user message]")
response.content
```

### [Ollama](https://ollama.com/)

#### Install

- MacBook M4 Pro 여서 네이티브로 설치
  - Docker 기반으로 실행해도 되나 `GPU 가속 미지원` 등 성능 이슈가 있음

```shell
brew install ollama

# 수동 실행
ollama serve

# 자동 실행
brew services start ollama
```

#### [Models](https://ollama.com/search)

- qwen2.5 모델에서 `7b` 또는 `14b`

```shell
ollama pull qwen2.5:7b
```

- GPU 가속 확인

```shell
ollama ps

#NAME          ID              SIZE      PROCESSOR    CONTEXT    UNTIL
#qwen2.5:7b    845dbda0ea48    4.8 GB    100% GPU     4096       3 minutes from now
```

#### LangChain package install

```shell
pip install -qU langchain-ollama
```

#### Running

```shell
from langchain_ollama import ChatOllama
llm = ChatOllama(
  model = "qwen2.5:7b"
)

response = llm.invoke("[user message]")
response.content
```

#### KeepAlive

- Ollama에서 마지막 요청 후 5분 동안 응답이 없으면 메모리에서 모델을 자동 언로드

```shell
# 영구적으로 메모리에 유지 (-1:무한)
OLLAMA_KEEP_ALIVE=-1 ollama serve

# 시간 지정
OLLAMA_KEEP_ALIVE=12h ollama serve
```

- ~/Library/LaunchAgents/homebrew.mxcl.ollama.plist 수정

```xml
<plist version="1.0">
<dict>
    <key>EnvironmentVariables</key>
    <dict>
        <!-- 추가 -->
        <key>OLLAMA_KEEP_ALIVE</key>
        <string>12h</string>
        <!-- // 추가 -->
    </dict>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

- brew services restart 시 `plist` 초기화
```shell
launchctl unload ~/Library/LaunchAgents/homebrew.mxcl.ollama.plist
launchctl load ~/Library/LaunchAgents/homebrew.mxcl.ollama.plist

ollama run qwen2.5:7b

ollama ps
NAME          ID              SIZE      PROCESSOR    CONTEXT    UNTIL
qwen2.5:7b    845dbda0ea48    4.8 GB    100% GPU     4096       12 hours from now
```

#### [ChatOllama integration](https://docs.langchain.com/oss/python/integrations/chat/ollama)

### LangChain ChatModels

- [Chat model integrations](https://docs.langchain.com/oss/python/integrations/chat)