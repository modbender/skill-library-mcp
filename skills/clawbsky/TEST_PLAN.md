# Clawbsky Test Plan

Credentials to be used:
BLUESKY_HANDLE="sugataai.bsky.social"
BLUESKY_APP_PASSWORD="[REDACTED]"

## Procedure
For each step, I will notify you before executing, execute the command, save the output, and wait for your confirmation to proceed so you can check it live.

## Reading & User Info
1. `clawbsky user sugataai.bsky.social` (Check profile)
2. `clawbsky user-posts sugataai.bsky.social -n 5` (Check recent posts)

## Timelines
3. `clawbsky home -n 5`
4. `clawbsky mentions -n 5`

## Search
5. `clawbsky search "testing" -n 5`
6. `clawbsky search "#test"`

## Posting & Threads
7. `clawbsky add "Hello world! This is an automated test from Clawbsky CLI."` (Save URI)
8. `clawbsky read <uri>` (Check the post)
9. `clawbsky reply <uri> "This is a reply to the test post."` (Save reply URI)
10. `clawbsky quote <uri> "Quoting the original test post!"` (Save quote URI)
11. `clawbsky thread <uri>` (View thread of original post)
12. `clawbsky replies <uri>` (View replies)
13. `clawbsky thread "Thread part 1" "Thread part 2" "Thread part 3"`

## Engagement
14. `clawbsky like <reply_uri>`
15. `clawbsky likes sugataai.bsky.social` (Verify the like appears)
16. `clawbsky unlike <reply_uri>`
17. `clawbsky repost <reply_uri>`
18. `clawbsky unrepost <reply_uri>`

## Following
19. `clawbsky follow someone.bsky.social` (Find a test account to follow)
20. `clawbsky following sugataai.bsky.social -n 5`
21. `clawbsky followers sugataai.bsky.social -n 5`
22. `clawbsky unfollow someone.bsky.social`

## Lists
23. `clawbsky lists`
24. `clawbsky list-timeline <list-id>` (If a list exists)

## Media formatting (Optional)
25. `clawbsky add "Test with media" <path-to-image>` (If an image is available)
26. `clawbsky add "Test with video" <path-to-video>` (If a video is available)
