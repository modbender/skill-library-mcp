# Scrapling recipes

## Extract text list (CSS)
```python
quotes = page.css('.quote .text::text').getall()
```

## Extract links (href)
```python
links = page.css('a::attr(href)').getall()
```

## Extract first match
```python
h1 = page.css('h1::text').get()
```

## JSON/JSONL export (Spider result)
Scrapling spiders commonly return a result object with items you can serialize.

Typical pattern:
```python
result = MySpider().start()
result.items.to_jsonl('out.jsonl')
```

## Adaptive selection
```python
els = page.css('.product', auto_save=True)
# later
els = page.css('.product', adaptive=True)
```
