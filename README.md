# hermes-plugins

[Hermes Agent](https://github.com/NousResearch/hermes-agent)용 SkyMin 플러그인입니다. 말투·출력 형태를 매 턴 주입하거나, 터미널 명령을 실행 전에 고칩니다.

원본은 이 저장소입니다. 플러그인 폴더를 `$HERMES_HOME/plugins/`에 복사하세요.

- Windows 기본: `%LOCALAPPDATA%\hermes\plugins\`
- 그 외: `~/.hermes/plugins/`
- 이름 있는 프로필: `$HERMES_HOME/profiles/<이름>/plugins/`

`$HERMES_HOME/plugins/` 안에서 `git init` 하지 마세요. 이 저장소를 다른 곳에 클론한 뒤 폴더만 복사합니다.

## 플러그인

| 폴더 | 버전 | 하는 일 | 슬래시 커맨드 |
| --- | --- | --- | --- |
| `caveman` | 0.1.0 | 매 LLM 호출에 짧은 caveman 말투 규칙을 넣음 | `/caveman lite` / `full` / `ultra` / `off` |
| `i-have-adhd` | 0.1.0 | ADHD용 출력: 다음 행동 먼저, 단계 번호, 군더더기 없음 | `/i-have-adhd on` / `off` |
| `ponytail` | 4.9.0 | 게으른 시니어 모드 + review/audit/debt/gain 스킬 | `/ponytail`, `/ponytail-review`, `/ponytail-audit`, `/ponytail-debt`, `/ponytail-gain`, `/ponytail-help` |
| `rtk-rewrite` | 0.2.0 | Hermes가 `terminal`을 실행하기 전에 RTK로 명령을 고침. 실패하면 원본 그대로 실행 | (훅만) |

`caveman` 추가 단계: `wenyan-lite`, `wenyan-full`, `wenyan-ultra`. 기본값은 `lite`.

## 원본

이 저장소는 Hermes용 어댑터입니다. 스킬·도구 원본:

- `caveman` — [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
- `i-have-adhd` — [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)
- `ponytail` — [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)
- `rtk-rewrite` — [rtk-ai/rtk](https://github.com/rtk-ai/rtk) (`hooks/hermes/`)

## 설치

1. 플러그인 폴더 이름을 유지한 채 `$HERMES_HOME/plugins/`로 복사합니다.
2. 켭니다.

```bash
hermes plugins enable caveman
hermes plugins enable i-have-adhd
hermes plugins enable ponytail
hermes plugins enable rtk-rewrite
```

3. Hermes(또는 게이트웨이)를 재시작합니다. 훅 변경은 세션 재시작이 필요합니다.

## 요구 사항

- Python 플러그인 시스템(`plugin.yaml`, `plugins.enabled`)이 있는 Hermes Agent.
- `rtk-rewrite`만: PATH에 `rtk`가 있어야 합니다. 없으면 훅을 등록하지 않습니다. 기본 허용 백엔드는 `local`입니다. `RTK_HERMES_BACKENDS`로 바꿉니다 (`local`, 쉼표 목록, 또는 `all`). 이미 `rtk ` 또는 `: RTK && `로 시작하는 명령은 건드리지 않습니다.

## 라이선스

[MIT](LICENSE). 저작자 SkyMin (`syacucloud`).
