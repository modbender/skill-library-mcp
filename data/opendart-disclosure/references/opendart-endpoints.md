# OpenDART endpoints (quick reference)

## 1) Company code archive

- URL: `https://opendart.fss.or.kr/api/corpCode.xml`
- Params: `crtfc_key=<API_KEY>`
- Response: ZIP containing `CORPCODE.xml`
- Use this to map company name ↔ `corp_code`.

## 2) Disclosure list

- URL: `https://opendart.fss.or.kr/api/list.json`
- Key params:
  - `crtfc_key`
  - `corp_code`
  - `bgn_de` (`YYYYMMDD`)
  - `end_de` (`YYYYMMDD`)
  - `page_no`, `page_count`
  - optional `pblntf_ty`, `pblntf_detail_ty`, `last_reprt_at`

## 3) DART document URL pattern

- `https://dart.fss.or.kr/dsaf001/main.do?rcpNo=<rcept_no>`

## API status handling

- `status == "000"`: success
- Others: failure (rate limit/auth/param problems etc.)
- Always include `message` from API in error output.
