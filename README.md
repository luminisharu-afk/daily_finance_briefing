# daily_finance_briefing

매일 오전에 전일 국내 시장 요약 정보를 HTML과 JSON으로 저장하는 서비스입니다.

## 기능

- FinanceDataReader로 코스피(`KS11`)와 코스닥(`KQ11`) 지수를 조회합니다.
- 기준일 이전의 마지막 두 거래일 종가를 비교해 등락률을 계산합니다.
- 스크린샷과 비슷한 섹션형 HTML 리포트를 생성합니다.
- GitHub Actions로 매주 월요일부터 토요일까지 오전 10시(Asia/Seoul)에 자동 실행합니다.

## 로컬 실행

```bash
python -m pip install -e .
python -m market_summary
```

특정 실행일 기준으로 다시 만들려면 다음처럼 실행합니다.

```bash
python -m market_summary --as-of 2026-10-06
```

생성 결과는 다음 위치에 저장됩니다.

- `reports/YYYY-MM-DD.html`
- `reports/latest.html`
- `data/YYYY-MM-DD.json`

## 설정

조회 항목은 `config/markets.toml`에서 관리합니다.

```toml
[[sections]]
name = "국내"
columns = 2

[[sections.items]]
label = "코스피"
symbol = "KS11"
precision = 2
```

`symbol`은 FinanceDataReader의 `DataReader`에서 지원하는 심볼을 사용합니다.
현재 1차 범위는 코스피와 코스닥입니다.

## 자동 실행

`.github/workflows/daily-summary.yml`이 매일 국내 지수 리포트를 생성하고, 변경된 `data/`와 `reports/` 파일을 저장소에 커밋합니다.
