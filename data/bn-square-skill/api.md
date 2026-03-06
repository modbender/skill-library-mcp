────────┬────────────────────────────────────────────────┐
  │  功能   │                      端點                      │
  ├─────────┼────────────────────────────────────────────────┤
  │ Session │ GET /bapi/accounts/v1/private/account/user/use │
  │  驗證   │ rInfo                                          │
  ├─────────┼────────────────────────────────────────────────┤
  │ 發短文  │ POST /bapi/composite/v1/private/pgc/content/sh │
  │         │ ort/create                                     │
  ├─────────┼────────────────────────────────────────────────┤
  │ 發文章  │ POST /bapi/composite/v1/private/pgc/content/ar │
  │         │ ticle/create                                   │
  ├─────────┼────────────────────────────────────────────────┤
  │ 發布內  │ POST                                           │
  │ 容      │ /bapi/composite/v1/private/pgc/content/publish │
  ├─────────┼────────────────────────────────────────────────┤
  │ 圖片上  │ POST /bapi/composite/v1/private/pgc/content/im │
  │ 傳      │ age/upload                                     │
  ├─────────┼────────────────────────────────────────────────┤
  │ 貼文詳  │ POST                                           │
  │ 情      │ /bapi/composite/v1/public/pgc/content/detail   │
  ├─────────┼────────────────────────────────────────────────┤
  │ 草稿保  │ POST /bapi/composite/v1/private/pgc/content/dr │
  │ 存      │ aft/save                                       │
  ├─────────┼────────────────────────────────────────────────┤
  │ 投票建  │ POST /bapi/composite/v1/private/pgc/content/vo │
  │ 立      │ te/create                                      │
  ├─────────┼────────────────────────────────────────────────┤
  │ 發文預  │ POST /bapi/composite/v1/private/pgc/content/pr │
  │ 檢      │ e-check                                        │
  └─────────┴───────────────────────────────────────────────