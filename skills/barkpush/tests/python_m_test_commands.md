# Python -m 测试命令清单

## 全量测试

```bash
python -m unittest discover -s tests
```

## 单模块测试

```bash
python -m unittest tests.test_bark_api
python -m unittest tests.test_config_manager
python -m unittest tests.test_content_parser
python -m unittest tests.test_history_manager
python -m unittest tests.test_user_manager
```

## 功能示例命名说明

- bark_api：Bark API 请求与响应处理
- config_manager：配置加载与类型校验
- content_parser：内容类型识别与 Markdown 生成
- history_manager：历史记录保存与裁剪
- user_manager：用户别名解析与权限约束

## 功能命令参考

```bash
bark-push --user alice --content "会议将在10分钟后开始"
bark-push --user alice --title "会议提醒" --subtitle "10分钟后" --content "请准时参加"
bark-push --user alice,bob --content "双人通知"
bark-push --user all --title "系统通知" --content "今晚维护"
bark-push --user alice --group work --content "工作提醒"
bark-push --user alice --level critical --volume 10 --content "紧急告警"
bark-push --list-users
bark-push --list-groups
bark-push --list-history --history-limit 20
```
