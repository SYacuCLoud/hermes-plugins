# hermes-plugins

[Hermes Agent](https://github.com/NousResearch/hermes-agent)에 붙이는 SkyMin 플러그인입니다. 모델 가중치를 바꾸지 않습니다. 하는 일은 둘입니다. 답을 쓰기 전에 말투 문단을 하나 넣거나, `terminal` 도구가 명령을 실행하기 전에 그 명령을 RTK로 바꿉니다.

이 저장소가 원본입니다. 쓸 때는 플러그인 폴더 이름을 유지한 채 `$HERMES_HOME/plugins/`로 복사합니다. 그 경로는 설치본입니다. 그 안에서 `git init` 하지 마세요.

- Windows 기본 프로필: `%LOCALAPPDATA%\hermes\plugins\`
- 그 외: `~/.hermes/plugins/`
- 이름 있는 프로필: `$HERMES_HOME/profiles/<이름>/plugins/`

`plugins.enabled`는 프로필마다 따로입니다. 다른 프로필에서 쓰려면 그 프로필에서 다시 켜야 합니다.

## 플러그인

| 폴더 | 버전 | 훅 | 목적 |
| --- | --- | --- | --- |
| [`speech-core`](speech-core/) | 0.1.0 | `pre_llm_call` | 매 턴 붙는 말투 지시를 문단 하나로 둡니다. |
| [`rtk-rewrite`](rtk-rewrite/) | 0.2.0 | `pre_tool_call` | `terminal` 명령을 실행 전에 RTK 명령으로 바꿉니다. |

슬래시 명령은 없습니다. 켜고 끄는 일은 `hermes plugins`가 합니다.

## speech-core

말투 플러그인을 여러 개 켜면, 매 턴 사용자 메시지에 문단이 여러 개 붙습니다. 뒤 문단이 앞의 한국어 규칙을 덮어서 해요체가 깨집니다. `speech-core`는 그 겹침을 없애려고 만들었습니다. 새 말투를 만든 플러그인이 아닙니다.

`pre_llm_call`에서 `SPEECH CORE ACTIVE` 문단 하나만 넣습니다. 모델 설정과 도구는 건드리지 않습니다. 문단 원문은 [`speech-core/__init__.py`](speech-core/__init__.py)에 있습니다. 시키는 일은 이것입니다.

1. 답은 조사와 어미가 있는 해요체 문장으로 씁니다. 합니다체를 섞지 않습니다. 영어를 직역해서 없는 말을 만들지 않습니다. 짧게 쓴다고 이유, 조건, 예외를 빼지 않습니다. 이 문체 자체를 설명하지 않습니다.
2. 답이나 다음 행동을 먼저 말합니다. 여러 단계는 번호를 매기고, 한 단계에 행동 하나만 적습니다. 목록은 다섯 개를 넘기지 않습니다. 서론, 앞에서 한 말의 반복, 맺음말을 붙이지 않습니다. 시간은 분이나 초처럼 구체적 단위로 말합니다. 오류는 원인 다음에 고치는 방법을 말합니다. 문체 규칙이 작업과 부딪히면 작업이 이깁니다. 되돌리기 어려운 일은 확인을 받습니다.
3. 코드는 이미 있는 것, 표준 라이브러리, 가장 작은 변경 순으로 고릅니다. 요청하지 않은 추상화는 넣지 않습니다. 신뢰할 수 없는 입력을 검사하는 코드는 빼지 않습니다. 코드를 고친 뒤, 넣지 않은 것은 최대 세 줄로만 적고, 그 줄은 코드에 대한 말만 합니다.

`caveman`, `i-have-adhd`, `ponytail`은 이 저장소에서 뺐습니다. 그 플러그인을 따로 설치해서 `speech-core`와 같이 켜면 문단이 다시 겹칩니다. 원본이 필요하면 업스트림을 보세요.

- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
- [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)
- [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)

## rtk-rewrite

[RTK](https://github.com/rtk-ai/rtk)는 `git status`나 `ls` 같은 명령을, 더 짧은 출력이 나오는 명령으로 바꿉니다. 이 플러그인은 그 일을 Hermes에 연결합니다. `terminal`이 실행되기 전에 `command`만 바꿉니다. 출력 문자열을 이 플러그인이 자르지는 않습니다.

규칙은 이 파이썬에 없습니다. `rtk rewrite`가 정합니다. RTK가 규칙을 바꿔도 이 저장소를 고치지 않아도 그 동작이 따라옵니다. 업스트림 설명은 [hooks/hermes](https://github.com/rtk-ai/rtk/tree/master/hooks/hermes)에 있습니다.

이 저장소의 복사본은 백엔드 허용 목록을 더 갖고 있습니다. 실행은 이렇습니다.

1. 도구가 `terminal`이 아니면 그대로 둡니다.
2. 백엔드가 허용 목록에 없으면 그대로 둡니다. 기본은 `local`입니다. `RTK_HERMES_BACKENDS`로 바꿉니다. `local,docker`처럼 쉼표로 여러 개를 주거나, `all`이면 백엔드를 가리지 않습니다. 비어 있으면 `local`로 봅니다.
3. 명령이 이미 `rtk ` 또는 `: RTK && `로 시작하면 다시 감싸지 않습니다.
4. `rtk rewrite`를 최대 2초 돌립니다. 시간이 넘거나, 예외가 나거나, 바꿀 결과가 없으면 원래 명령을 실행합니다. 실패해도 셸을 막지 않습니다.
5. 종료 코드가 `0` 또는 `3`이고 표준 출력이 원 명령과 다를 때만 `command`를 바꿉니다. `1`과 `2`는 바꿀 것이 없다는 뜻이라 경고하지 않습니다.

`rtk`가 PATH에 없으면 훅을 등록하지 않습니다. 그때 Hermes 터미널은 평소와 같습니다. `rtk rewrite`가 건너뛰는 명령도 그대로 둡니다. 이미 `rtk`로 시작하는 명령, 이어 붙인 셸 명령, heredoc, 필터가 없는 명령이 거기 들어갑니다.

## 설치

폴더를 `$HERMES_HOME/plugins/`에 복사한 다음 켭니다.

```bash
hermes plugins enable speech-core
hermes plugins enable rtk-rewrite
```

켠 뒤에는 Hermes 프로세스를 다시 시작하고 새 세션을 여세요. 이미 켜 둔 프로세스에서 새 채팅만 열면 플러그인을 다시 읽지 않습니다. 이미 열린 대화도 이전 문단을 계속 봅니다.

`speech-core`는 추가 프로그램이 필요 없습니다. `rtk-rewrite`만 PATH에 `rtk`가 있어야 훅이 등록됩니다.

## 요구 사항

`plugin.yaml`과 `plugins.enabled`가 있는 Hermes Agent가 필요합니다.

## 라이선스

[MIT](LICENSE). 저작자는 SkyMin (`syacucloud`)입니다.
