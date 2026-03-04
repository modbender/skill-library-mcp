# Endpoint Index (59 total)

## READ (30 endpoints)
| # | Method | Path | Category |
|---|--------|------|----------|
| 1 | GET | `/twitter/tweet/advanced_search` | tweet |
| 2 | GET | `/twitter/tweets` | tweet |
| 3 | GET | `/twitter/tweet/replies` | tweet |
| 4 | GET | `/twitter/tweet/replies/v2` | tweet |
| 5 | GET | `/twitter/tweet/quotes` | tweet |
| 6 | GET | `/twitter/tweet/retweeters` | tweet |
| 7 | GET | `/twitter/tweet/thread_context` | tweet |
| 8 | GET | `/twitter/article` | tweet |
| 9 | GET | `/twitter/user/info` | user |
| 10 | GET | `/twitter/user_about` | user |
| 11 | GET | `/twitter/user/batch_info_by_ids` | user |
| 12 | GET | `/twitter/user/last_tweets` | user |
| 13 | GET | `/twitter/user/followers` | user |
| 14 | GET | `/twitter/user/followings` | user |
| 15 | GET | `/twitter/user/verifiedFollowers` | user |
| 16 | GET | `/twitter/user/mentions` | user |
| 17 | GET | `/twitter/user/search` | user |
| 18 | GET | `/twitter/user/check_follow_relationship` | user |
| 19 | GET | `/twitter/list/followers` | list |
| 20 | GET | `/twitter/list/members` | list |
| 21 | GET | `/twitter/community/info` | community |
| 22 | GET | `/twitter/community/members` | community |
| 23 | GET | `/twitter/community/moderators` | community |
| 24 | GET | `/twitter/community/tweets` | community |
| 25 | GET | `/twitter/community/get_tweets_from_all_community` | community |
| 26 | GET | `/twitter/trends` | trend |
| 27 | GET | `/twitter/spaces/detail` | other |
| 28 | GET | `/oapi/my/info` | account |
| 29 | GET | `/twitter/get_dm_history_by_user_id` | dm |
| 30 | GET | `/oapi/x_user_stream/get_user_to_monitor_tweet` | stream |

## WRITE V2 (18 endpoints)
| # | Method | Path | Category |
|---|--------|------|----------|
| 31 | POST | `/twitter/user_login_v2` | auth |
| 32 | POST | `/twitter/create_tweet_v2` | action |
| 33 | POST | `/twitter/delete_tweet_v2` | action |
| 34 | POST | `/twitter/like_tweet_v2` | action |
| 35 | POST | `/twitter/unlike_tweet_v2` | action |
| 36 | POST | `/twitter/retweet_tweet_v2` | action |
| 37 | POST | `/twitter/follow_user_v2` | action |
| 38 | POST | `/twitter/unfollow_user_v2` | action |
| 39 | POST | `/twitter/upload_media_v2` | media |
| 40 | PATCH | `/twitter/update_avatar_v2` | profile |
| 41 | PATCH | `/twitter/update_banner_v2` | profile |
| 42 | PATCH | `/twitter/update_profile_v2` | profile |
| 43 | POST | `/twitter/send_dm_to_user` | dm |
| 44 | POST | `/twitter/create_community_v2` | community |
| 45 | POST | `/twitter/delete_community_v2` | community |
| 46 | POST | `/twitter/join_community_v2` | community |
| 47 | POST | `/twitter/leave_community_v2` | community |

## WEBHOOK + STREAM (7 endpoints)
| # | Method | Path | Category |
|---|--------|------|----------|
| 48 | POST | `/oapi/tweet_filter/add_rule` | webhook |
| 49 | GET | `/oapi/tweet_filter/get_rules` | webhook |
| 50 | POST | `/oapi/tweet_filter/update_rule` | webhook |
| 51 | DELETE | `/oapi/tweet_filter/delete_rule` | webhook |
| 52 | POST | `/oapi/x_user_stream/add_user_to_monitor_tweet` | stream |
| 53 | POST | `/oapi/x_user_stream/remove_user_to_monitor_tweet` | stream |

## DEPRECATED V1 (6 endpoints)
| # | Method | Path | Category |
|---|--------|------|----------|
| 54 | POST | `/twitter/login_by_email_or_username` | deprecated |
| 55 | POST | `/twitter/login_by_2fa` | deprecated |
| 56 | POST | `/twitter/create_tweet` | deprecated |
| 57 | POST | `/twitter/like_tweet` | deprecated |
| 58 | POST | `/twitter/retweet_tweet` | deprecated |
| 59 | POST | `/twitter/upload_image` | deprecated |
