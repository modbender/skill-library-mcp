# 매경 리뷰 원고 템플릿

> 이 파일을 복사해서 `mk-review-YYYY-MM-DD.md`로 저장 후 작성
> 작성 후 런북 `-1단계` 완료로 표시하고 0단계로 진행

---

## 메타

```
title: [매경] YYYY.MM.DD(요일) - 키워드1, 키워드2, 키워드3
date: YYYY-MM-DD
```

---

## buildBlogHTML() 파라미터 (3단계에서 직접 사용)

> 아래 JavaScript 객체를 3단계 `buildBlogHTML()` 호출 시 그대로 사용:

```javascript
const intro = `
<p data-ke-size="size16">들어가며 첫 문단. 오늘의 흐름을 2~3문장으로 요약.</p>
<p data-ke-size="size16">선택한 기사들의 공통 맥락이나 관점 설명.</p>
`;

const articles = [
  {
    title: "① 기사1 제목",
    url: "https://www.mk.co.kr/news/분류/기사번호",
    body: `<p data-ke-size="size16">기사 본문 요약. 문단을 너무 잘게 쪼개지 말고 6~7문장 단위로 묶어서 하나의 &lt;p&gt; 태그로 작성할 것. (절대 1~2문장 단위로 &lt;p&gt; 태그 남발 금지)</p>`,
    comment: "가리봉뉘우스 코멘트 1~2문장. 투자·경제 관점으로."
  },
  {
    title: "② 기사2 제목",
    url: "https://www.mk.co.kr/news/분류/기사번호",
    body: `<p data-ke-size="size16">기사 본문 요약. 문단을 너무 잘게 쪼개지 말고 6~7문장 정도 모아서 하나의 &lt;p&gt; 태그로 작성할 것.</p>`,
    comment: "코멘트."
  },
  {
    title: "③ 기사3 제목",
    url: "https://www.mk.co.kr/news/분류/기사번호",
    body: `<p data-ke-size="size16">기사 본문 요약. 문단을 너무 잘게 쪼개지 말고 6~7문장 정도 모아서 하나의 &lt;p&gt; 태그로 작성할 것.</p>`,
    comment: "코멘트."
  },
  {
    title: "④ 기사4 제목",
    url: "https://www.mk.co.kr/news/분류/기사번호",
    body: `<p data-ke-size="size16">기사 본문 요약. 문단을 너무 잘게 쪼개지 말고 6~7문장 정도 모아서 하나의 &lt;p&gt; 태그로 작성할 것.</p>`,
    comment: "코멘트. 끝."
  }
];

// 3단계에서 사용:
const html = buildBlogHTML({ intro, articles });
insertContent(html);
```

---

## 태그 (7단계에서 사용)

```javascript
// 기사 내용에 맞게 태그4~태그10 교체
setTags(["매경", "매일경제", "신문리뷰", "태그4", "태그5", "태그6", "태그7", "태그8", "태그9", "태그10"])
```

---

## 체크리스트 (작성 완료 확인)

- [ ] title 형식: `[매경] YYYY.MM.DD(요일) - 키워드1, 키워드2, 키워드3`
- [ ] intro: 2~3문단, `<p data-ke-size="size16">` 태그로 감쌈
- [ ] articles[0~3]: title(①②③④), url(mk.co.kr), body, comment 모두 채움
- [ ] 마지막 기사 comment 끝에 "끝." 포함
- [ ] 태그 10개 준비 (매경/매일경제/신문리뷰 필수)
