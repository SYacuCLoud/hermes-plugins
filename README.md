# hermes-plugins

[Hermes Agent](https://github.com/NousResearch/hermes-agent)용 SkyMin 플러그인입니다. 말투를 매 턴 한 블록으로 넣거나, 터미널 명령을 실행 전에 고칩니다.

원본은 이 저장소입니다. 폴더를 `$HERMES_HOME/plugins/`에 두세요. 그 안에서 `git init` 하지 마세요.

- Windows 기본: `%LOCALAPPDATA%\hermes\plugins\`
- 그 외: `~/.hermes/plugins/`
- 이름 있는 프로필: `$HERMES_HOME/profiles/<이름>/plugins/`

## 플러그인

| 폴더 | 버전 | 하는 일 |
| --- | --- | --- |
| `speech-core` | 0.1.0 | 해요체, 다음 행동, 최소 코드를 한 블록으로 주입합니다. |
| `rtk-rewrite` | 0.2.0 | `terminal` 실행 전에 RTK로 명령을 고칩니다. 실패하면 원 명령을 그대로 실행합니다. |

`caveman`, `i-have-adhd`, `ponytail`은 이 저장소에서 뺐습니다. 말투는 `speech-core` 하나만 씁니다. 원래 아이디어는 각 업스트림에 있습니다.

- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
- [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)
- [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)
- [rtk-ai/rtk](https://github.com/rtk-ai/rtk) (`hooks/hermes/`)

## 설치

```bash
hermes plugins enable speech-core
hermes plugins enable rtk-rewrite
```

훅을 바꾼 뒤에는 Hermes를 다시 켜고 새 세션을 여세요.

`speech-core`와 구형 말투 플러그인을 같이 켜지 마세요. 문단이 겹칩니다.

## 요구 사항

- `plugin.yaml`과 `plugins.enabled`가 있는 Hermes Agent.
- `rtk-rewrite`만 PATH에 `rtk`가 필요합니다. 없으면 훅을 등록하지 않습니다. 기본 허용 백엔드는 `local`입니다. `RTK_HERMES_BACKENDS`로 바꿉니다 (`local`, 쉼표 목록, 또는 `all`). 이미 `rtk ` 또는 `: RTK && `로 시작하는 명령은 건드리지 않습니다.

## 라이선스

[MIT](LICENSE). 저작자 SkyMin (`syacucloud`).
