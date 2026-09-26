# speech-core

코드 0.1.7 반영됨. README 반영됨.

세 스킬 본문은 유지한다. 그 뒤에 한글 말투 수정만 덧붙인다. 스킬 파일이 없으면 이름만 알리고, 수정 문단으로 대체하지 않는다.

0.1.7: 끄기·레벨 명령 반영, 본문 전체가 남아 있을 때만 알림으로 줄임, 모델에 보낸 내용(api_content 우선)만 검사, 머리말 구분자는 독립된 줄만 인정.

남은 일:

- Hermes 프로세스를 완전히 끈 다음 다시 켠다. 새 채팅만 열면 이미 불러온 모듈을 다시 읽지 않는다.
- 기본 프로필에서는 전체 본문(약 18.7k자)이 `hooks.output_spill.max_chars` 기본값 10k를 넘어 디스크로 빠진다. 기본 프로필에서 켤 때는 max_chars를 올리거나 caveman을 skip한다. musk는 16000이라 12.5k가 들어간다.

배포본은 원본과 같다.

- `%LOCALAPPDATA%\hermes\plugins\speech-core\`
- `%LOCALAPPDATA%\hermes\profiles\musk\plugins\speech-core\`

