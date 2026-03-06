---
name: rent-odessa
description: Поиск долгосрочной аренды 2-комнатных квартир в Одессе
---

# rent-odessa

Поиск долгосрочной аренды 2-комнатных квартир в Одессе

## Триггеры

- `/rent`
- "найди квартиру", "что по аренде", "квартиры в одессе", "что по кв"

## Фильтры

- 2 комнаты
- До 15 000 грн/мес
- Все районы кроме Суворовский/Пересыпский
- С животными
- Новострой
- Этаж не важно
- Жилая площадь от 40 м²
- Отопление не важно
- С мебелью

## Источники

- OLX https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/?currency=UAH
- DOM.RIA https://dom.ria.com/uk/search/?category=1&realty_type=2&operation=3&state_id=12&price_cur=1&wo_dupl=1&sort=inspected_sort&firstIteraction=false&limit=20&market=3&excludeSold=1&type=map&without_entity_group=1&city_ids=12&ch=246_244#map_state=30.72139_46.48608_0.0_10.0
- flatfy https://flatfy.ua/%D0%B0%D1%80%D0%B5%D0%BD%D0%B4%D0%B0-%D0%BA%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80-%D0%BE%D0%B4%D0%B5%D1%81%D1%81%D0%B0
- rieltor https://rieltor.ua/ru/odessa/flats-rent/#10.5/0/0
- lun https://lun.ua/rent/odesa/flats/ru?srsltid=AfmBOopj60sLsMOT7sdNo_rAx-Cwj4dAttnTGCIg4ms30rFTkdykFNjx
- Atlanta https://www.atlanta.ua/odessa/filters/arenda/kvartiry
- REM https://rem.ua/arenda-kvartir-odessa

## Шаги

1. Выполни agent-browser --help чтобы узнать как использовать agent-browser для сбора данных с сайтов
2. Используй agent-browser чтобы перейти по каждому источнику выбрать нужные фильтры, для этого вызови agent-browser open <link>
3. Пройтись по первым двум страницам и собрать данные о квартирах
4. Ответить пользователю сообщением с найденными квартирами используя шаблон ниже

## Шаблон ответа

```Найдены следующие квартиры:
1. [Название квартиры](ссылка) - цена грн/мес, район, этаж, площадь м²
2. [Название квартиры](ссылка) - цена грн/мес, район, этаж, площадь м²
...
```

## Дополнительно

- Если по одному из источников не удалось найти квартиры, то указать это в ответе
- Если по всем источникам не удалось найти квартиры, то сообщить об этом пользователю
