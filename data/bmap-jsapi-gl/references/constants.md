# 通用常量

## 搜索状态常量

所有 LBS 服务（LocalSearch、Geocoder、路径规划等）共用的状态码。

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_STATUS_SUCCESS | 0 | 检索成功 |
| BMAP_STATUS_CITY_LIST | 1 | 返回城市列表（需选择城市后重新检索） |
| BMAP_STATUS_UNKNOWN_LOCATION | 2 | 位置未知 |
| BMAP_STATUS_UNKNOWN_ROUTE | 3 | 路线未知/无法规划 |
| BMAP_STATUS_INVALID_KEY | 4 | 非法密钥 |
| BMAP_STATUS_INVALID_REQUEST | 5 | 非法请求 |
| BMAP_STATUS_PERMISSION_DENIED | 6 | 没有权限 |
| BMAP_STATUS_SERVICE_UNAVAILABLE | 7 | 服务不可用 |
| BMAP_STATUS_TIMEOUT | 8 | 超时 |

## POI 类型常量

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_POI_TYPE_NORMAL | 0 | 普通 POI |
| BMAP_POI_TYPE_BUSSTOP | 1 | 公交站 |
| BMAP_POI_TYPE_SUBSTOP | 2 | 地铁站 |
