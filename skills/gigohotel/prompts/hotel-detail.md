# 酒店详情查询提示词

当用户需要查看具体酒店房型价格时，调用 getHotelDetail：

## 参数
- hotelId: 从搜索结果获取
- name: 酒店名称（与hotelId二选一）
- checkInDate/checkOutDate: 入离日期
- adultCount: 成人数，默认2
- roomCount: 房间数，默认1

## 响应处理
展示房型列表：房型名称、床型、价格、取消政策