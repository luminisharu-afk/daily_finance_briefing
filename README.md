# daily_finance_briefing

매일 오전에 전일 시장 요약 정보를 HTML과 JSON으로 저장하는 서비스입니다.

## 기능

- FinanceDataReader로 국내 지수, 주요 해외 지수, 환율, 상품 가격을 조회합니다.
- 현재 조회 항목은 코스피(`KS11`), 코스닥(`KQ11`), 다우 산업(`DJI`), 나스닥 종합(`IXIC`), 상해 종합(`SSEC`), 니케이225(`N225`), 원/달러(`USD/KRW`), 중국 위안/달러(`USD/CNY`), 금(`GC=F`), 은(`SI=F`), WTI(`CL=F`)입니다.
- 기준일 이전의 마지막 두 거래일 종가를 비교해 등락률을 계산합니다.
- 스크린샷과 비슷한 섹션형 HTML 리포트를 생성합니다.
- 매일 실행 결과를 날짜별 HTML 파일로 저장하고, 최신 HTML 파일도 함께 갱신합니다.
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

특정 시장 기준일을 직접 지정하려면 다음처럼 실행합니다.

```bash
python -m market_summary --target-date 2026-10-05
```

생성 결과는 다음 위치에 저장됩니다. 매일 실행 결과의 HTML 파일은 `output/reports/YYYY-MM-DD.html`입니다.

- `output/reports/YYYY-MM-DD.html`
- `output/reports/latest.html`
- `output/reports/index.html`
- `output/data/YYYY-MM-DD.json`

GitHub 저장소 화면에서 HTML 파일을 클릭하면 소스 코드가 보입니다.
브리핑 화면으로 보려면 GitHub Pages 배포 URL을 열거나, 로컬에서 HTML 파일을 브라우저로 열어야 합니다.

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
현재 범위는 국내 지수 2개, 해외 지수 4개, 환율 2개, 상품 3개입니다.

## 자동 실행

`.github/workflows/daily-summary.yml`이 매일 시장 요약 리포트를 생성하고, 변경된 `output/` 파일을 저장소에 커밋합니다.
같은 워크플로가 `output/reports`를 GitHub Pages로 배포하므로 최신 브리핑은 Pages URL에서 렌더링된 HTML로 볼 수 있습니다.
GitHub Actions에서 수동 실행할 때는 `target_date` 입력으로 요약할 시장 기준일을 직접 지정할 수 있습니다.
