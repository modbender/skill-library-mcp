# Usage examples

Natural language -> API mapping examples

1) "Search my Zotero for 'deep learning' and sort by year"
   - Action: items endpoint with q='deep learning', sort='date', direction='desc'

2) "Add a note to item 12345: 'Expand methods section'"
   - Action: POST to /items with itemType=note and parentItem=12345

3) "Upload /home/user/papers/foo.pdf as an attachment to item 67890"
   - Action: POST file to /items/<parent>/children with multipart/form-data

4) "Create a new journalArticle in Group library 99999 with title X, authors Y, DOI Z"
   - Action: POST to /groups/99999/items with item JSON for journalArticle

Security-sensitive operations require confirmation flags when executed via CLI or agent.
