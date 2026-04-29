# [pyenv](https://github.com/pyenv/pyenv) - Simple Python Version Management

## Install

### install pyenv

- 파이썬 버전 관리 도구
> JAVA의 jENV, SDKMAN

```shell
brew install pyenv
```

### Set up shell environment for Pyenv 

```shell
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zprofile
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zprofile
echo 'eval "$(pyenv init - zsh)"' >> ~/.zprofile
```

### install Python version

- pyenv에서 사용할 버전 설치

```shell
# 가장 최신 버전 5개만 출력
pyenv install --list | grep -v -E '[a-zA-Z]' | tail -n 5

# 3.x 버전
pyenv install --list | grep -E "^  3\.[0-9]+\.[0-9]+$"

# 3.13 버전
pyenv install --list | grep -E "^  3\.13\.[0-9]+$"

pyenv install [VERSION] #최신버전(3.14.4) 이나 Upstage 설치 시 버전 문제로 3.13.13 설치
```

- 로컬에 설치된 버전 확인

```shell
python3 --version
```

### install pyenv-virtualenv

- 가상환경을 생성하는 확장 플러그인

```shell
brew install pyenv-virtualenv
```

### create Virtual Environment

- 해당 디렉토리 접근 시 가상환경 `자동 활성화`

```shell
mkdir [VIRTUAL-ENV-NAME] #tutorial-langchain
cd [VIRTUAL-ENV-NAME]

pyenv virtualenv 3.13.13 [VIRTUAL-ENV-NAME]

cat .python-version

pyenv local [VIRTUAL-ENV-NAME]
```

- 수동 활성/비활성화
```shell
pyenv activate [VIRTUAL-ENV-NAME]

pyenv deactivate
```
