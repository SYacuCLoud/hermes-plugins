# hermes-plugins

[Hermes Agent](https://github.com/NousResearch/hermes-agent)에 붙이는 SkyMin 플러그인입니다. 모델 가중치를 바꾸지 않습니다. 하는 일은 둘입니다. 채팅 턴에 설치된 스킬 본문을 넣거나, `terminal` 도구가 명령을 실행하기 전에 그 명령을 RTK로 바꿉니다.

이 저장소가 원본입니다. 쓸 때는 플러그인 폴더 이름을 유지한 채 `$HERMES_HOME/plugins/`에 이 저장소 폴더를 가리키는 링크를 만듭니다. 복사하지 않으므로 원본을 고치면 설치본도 바로 같아집니다. 설치본 쪽에서 `git init` 하지 마세요.

- Windows 기본 프로필: `%LOCALAPPDATA%\hermes\plugins\`
- 그 외: `~/.hermes/plugins/`
- 이름 있는 프로필: `$HERMES_HOME/profiles/<이름>/plugins/`

`plugins.enabled`는 프로필마다 따로입니다. 다른 프로필에서 쓰려면 그 프로필에서 다시 켜야 합니다.

## 플러그인

| 폴더 | 버전 | 훅 | 목적 |
| --- | --- | --- | --- |
| [`speech-core`](speech-core/) | 0.1.3 | `pre_llm_call` | 설치된 스킬 본문 셋을 넣고, 한글 말투 수정을 덧붙입니다. |
| [`rtk-rewrite`](rtk-rewrite/) | 0.3.0 | `pre_tool_call` | `terminal` 명령을 실행 전에 RTK 명령으로 바꿉니다. |

슬래시 명령은 없습니다. 켜고 끄는 일은 `hermes plugins`가 합니다.

## speech-core

`pre_llm_call`에서 설치된 `caveman`, `i-have-adhd`, `ponytail` 스킬 본문을 읽어 채팅 턴에 넣습니다. 본문을 요약으로 바꾸지 않습니다. 그 뒤에 한글 말투 수정만 덧붙입니다. 세 본문을 같이 넣으면 한글이 깨지기 때문입니다.

스킬은 지금 프로필의 `skills/`에서만 읽습니다. 다른 프로필의 스킬을 빌려 오지 않습니다. 스킬 파일이 없으면 그 이름만 알립니다. 빠진 본문을 다른 문단으로 대체하지 않습니다. 모델 설정과 도구는 바꾸지 않습니다. 수정 원문은 [`speech-core/__init__.py`](speech-core/__init__.py)에 있습니다.

이 저장소는 그 세 스킬 폴더를 담지 않습니다. 그 폴더를 플러그인으로 다시 넣고 `speech-core`와 같이 켜면 문단이 겹칩니다.

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
6. 바꾼 명령은 `{"action": "modify", "args": {"command": ...}}`로 돌려줍니다. Hermes가 넘긴 `args`를 직접 고치지 않습니다. `rtk` 출력은 UTF-8로 읽으므로 한글이 든 명령도 깨지지 않습니다.

`rtk`가 PATH에 없으면 훅을 등록하지 않습니다. 그때 Hermes 터미널은 평소와 같습니다. `rtk rewrite`가 건너뛰는 명령도 그대로 둡니다. 이미 `rtk`로 시작하는 명령, 이어 붙인 셸 명령, heredoc, 필터가 없는 명령이 거기 들어갑니다.

## 설치

`$HERMES_HOME/plugins/`에 링크를 만든 다음 켭니다. Windows에서는 관리자 권한이 필요 없는 디렉터리 정션을 씁니다. 저장소 폴더에서 PowerShell로 실행하세요.

```powershell
foreach ($p in 'speech-core','rtk-rewrite') {
  New-Item -ItemType Junction -Path "$env:LOCALAPPDATA\hermes\plugins\$p" -Target (Resolve-Path $p)
}
```

그 외 OS에서는 `ln -s "$PWD/speech-core" ~/.hermes/plugins/speech-core`처럼 심볼릭 링크를 만듭니다.

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
