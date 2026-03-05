Title: Endpoints - Documentation - News API

URL Source: http://newsapi.org/docs/endpoints

Markdown Content:
Endpoints - Documentation - News API
===============

[News API](http://newsapi.org/)

[Get started](http://newsapi.org/docs/get-started)

[Documentation](http://newsapi.org/docs)

[Pricing](http://newsapi.org/pricing)

[Login](http://newsapi.org/login)

[Get API key](http://newsapi.org/register)

_menu_

_close_

*   [Get started](http://newsapi.org/docs/get-started)
*   [Documentation](http://newsapi.org/docs)
*   [Pricing](http://newsapi.org/pricing)
*   [Login](http://newsapi.org/login)
*   [Get API key](http://newsapi.org/register)

Version

*   [Get started](http://newsapi.org/docs/get-started)
    *   [Searching for news articles](http://newsapi.org/docs/get-started#search)
    *   [Get curated breaking news headlines](http://newsapi.org/docs/get-started#top-headlines)

*   [Documentation](http://newsapi.org/docs)
    *   [Authentication](http://newsapi.org/docs/authentication)
    *   [Endpoints](http://newsapi.org/docs/endpoints)
        *   [Everything](http://newsapi.org/docs/endpoints/everything)
        *   [Top headlines](http://newsapi.org/docs/endpoints/top-headlines)
            *   [Sources](http://newsapi.org/docs/endpoints/sources)

    *   [Errors](http://newsapi.org/docs/errors)
    *   [Client libraries](http://newsapi.org/docs/client-libraries)
        *   [Node.js](http://newsapi.org/docs/client-libraries/node-js)
        *   [Ruby](http://newsapi.org/docs/client-libraries/ruby)
        *   [Python](http://newsapi.org/docs/client-libraries/python)
        *   [PHP](http://newsapi.org/docs/client-libraries/php)
        *   [Java](http://newsapi.org/docs/client-libraries/java)
        *   [C#](http://newsapi.org/docs/client-libraries/csharp)

_chevron\_right_

Endpoints
=========

News API has 2 main endpoints:

*   [Everything](http://newsapi.org/docs/endpoints/everything)`/v2/everything` – search every article published by over 150,000 different sources large and small in the last 5 years. This endpoint is ideal for news analysis and article discovery.
*   [Top headlines](http://newsapi.org/docs/endpoints/top-headlines)`/v2/top-headlines` – returns breaking news headlines for countries, categories, and singular publishers. This is perfect for use with news tickers or anywhere you want to use live up-to-date news headlines.

There is also a minor endpoint that can be used to retrieve a small subset of the publishers we can scan:

*   [Sources](http://newsapi.org/docs/endpoints/sources)`/v2/top-headlines/sources` – returns information (including name, description, and category) about the most notable sources available for obtaining top headlines from. This list could be piped directly through to your users when showing them some of the options available.

* * *

[_arrow\_back_ Authentication](http://newsapi.org/docs/authentication)[Endpoint _arrow\_right_ Everything _arrow\_forward_](http://newsapi.org/docs/endpoints/everything)

###### News API

[Get started](http://newsapi.org/docs/get-started)

[Documentation](http://newsapi.org/docs)

[News sources](http://newsapi.org/sources)

[Pricing](http://newsapi.org/pricing)

[Google News API](http://newsapi.org/s/google-news-api)

Title: Top headlines - Documentation - News API

URL Source: http://newsapi.org/docs/endpoints/top-headlines

Markdown Content:
This endpoint provides live top and breaking headlines for a country, specific category in a country, single source, or multiple sources. You can also search with keywords. Articles are sorted by the earliest date published first.

This endpoint is great for retrieving headlines for use with news tickers or similar.

Request parameters
------------------

*   ### apiKey required

Your API key. Alternatively you can provide this via the `X-Api-Key` HTTP header.

*   ### country

The 2-letter ISO 3166-1 code of the country you want to get headlines for. Possible options: `us`. Note: you can't mix this param with the `sources` param.

*   ### category

The category you want to get headlines for. Possible options: `business``entertainment``general``health``science``sports``technology`. Note: you can't mix this param with the `sources` param.

*   ### sources

A comma-seperated string of identifiers for the news sources or blogs you want headlines from. Use the [/top-headlines/sources](https://newsapi.org/docs/endpoints/sources) endpoint to locate these programmatically or look at the [sources index](https://newsapi.org/sources). Note: you can't mix this param with the `country` or `category` params.

*   ### q

Keywords or a phrase to search for.

*   ### pageSize int

The number of results to return per page (request). 20 is the default, 100 is the maximum.

*   ### page int

Use this to page through the results if the total results found is greater than the page size.

Response object
---------------

*   ### status string

If the request was successful or not. Options: `ok`, `error`. In the case of `error` a `code` and `message` property will be populated.

*   ### totalResults int

The total number of results available for your request.

*   ### articles array[article]

The results of the request.

    *   ### source  object

The identifier `id` and a display name `name` for the source this article came from.

    *   ### author  string

The author of the article

    *   ### title  string

The headline or title of the article.

    *   ### description  string

A description or snippet from the article.

    *   ### url  string

The direct URL to the article.

    *   ### urlToImage  string

The URL to a relevant image for the article.

    *   ### publishedAt  string

The date and time that the article was published, in UTC (+000)

    *   ### content  string

The unformatted content of the article, where available. This is truncated to 200 chars.

* * *

Live examples

Top headlines in the US

Definition

`GET https://newsapi.org/v2/top-headlines?country=us&apiKey=API_KEY`
Example response

{

*   "status": "ok",
*   "totalResults": 29,
*   -

"articles": [
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "CNBC"

},
        *   "author": "Amelia Lucas",
        *   "title": "Coca-Cola is about to report earnings. Here's what to expect - CNBC",
        *   "description": "Like rival PepsiCo, Coke has seen demand for its drinks fall as budget-conscious shoppers try to save more on their grocery bills.",
        *   "url": ["https://www.cnbc.com/2026/02/10/coca-cola-ko-q4-2025-earnings.html"](https://www.cnbc.com/2026/02/10/coca-cola-ko-q4-2025-earnings.html),
        *   "urlToImage": ["https://image.cnbcfm.com/api/v1/image/108263212-1770642346999-gettyimages-2246706941-251113_sv_costco_119.jpeg?v=1770642365&w=1920&h=1080"](https://image.cnbcfm.com/api/v1/image/108263212-1770642346999-gettyimages-2246706941-251113_sv_costco_119.jpeg?v=1770642365&w=1920&h=1080),
        *   "publishedAt": "2026-02-10T11:35:02Z",
        *   "content": "Coca-Cola on Tuesday reported mixed quarterly results, although demand for its drinks in North America and Latin America is beginning to show signs of improvement.\r\nLooking ahead to 2026, the company… [+2427 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "politico",
            *   "name": "Politico"

},
        *   "author": "Kyle Cheney",
        *   "title": "How the Trump administration skirts — and defies — court rulings on ICE detentions - Politico",
        *   "description": "A POLITICO review of hundreds of cases brought by ICE detainees shows a pattern of noncompliance that has frustrated judges across the country.",
        *   "url": ["https://www.politico.com/news/2026/02/10/ice-immigration-detention-court-orders-00771727"](https://www.politico.com/news/2026/02/10/ice-immigration-detention-court-orders-00771727),
        *   "urlToImage": ["https://www.politico.com/dims4/default/resize/1200/quality/90/format/jpg?url=https%3A%2F%2Fstatic.politico.com%2F2b%2F3b%2F12c71e954173b3c72d75d7331835%2Fmain-cheney-ice-alt.jpg"](https://www.politico.com/dims4/default/resize/1200/quality/90/format/jpg?url=https%3A%2F%2Fstatic.politico.com%2F2b%2F3b%2F12c71e954173b3c72d75d7331835%2Fmain-cheney-ice-alt.jpg),
        *   "publishedAt": "2026-02-10T10:00:00Z",
        *   "content": "Other judges have raised similar alarms. U.S. District Judge John Gerrard, an Obama appointee based in Nebraska who is helping handle a backlog of Minnesota cases scolded the Trump administration for… [+7424 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "politico",
            *   "name": "Politico"

},
        *   "author": "Eli Stokols, Clea Caulcutt",
        *   "title": "After Greenland, it’s the micro-agressions - Politico",
        *   "description": "President Trump has backed off his threats toward Denmark's territorial sovereignty, but he and aides have continued to irritate much of Europe.",
        *   "url": ["https://www.politico.com/news/2026/02/10/after-greenland-its-the-micro-agressions-00772114"](https://www.politico.com/news/2026/02/10/after-greenland-its-the-micro-agressions-00772114),
        *   "urlToImage": ["https://www.politico.com/dims4/default/resize/1200/quality/90/format/jpg?url=https%3A%2F%2Fstatic.politico.com%2F77%2F1a%2Fd7992f3c4c7f92e025549d60583c%2Fhttps-delivery-gettyimages.com%2Fdownloads%2F2256745286"](https://www.politico.com/dims4/default/resize/1200/quality/90/format/jpg?url=https%3A%2F%2Fstatic.politico.com%2F77%2F1a%2Fd7992f3c4c7f92e025549d60583c%2Fhttps-delivery-gettyimages.com%2Fdownloads%2F2256745286),
        *   "publishedAt": "2026-02-10T10:00:00Z",
        *   "content": "Amid the row over Greenland last month, Trump casually dismissed the sacrifice\r\n of NATO troops who fought beside U.S. forces in Afghanistan, leaving NATO allies disgusted. Subsequently, the U.S. emb… [+6465 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "CNBC"

},
        *   "author": "Elsa Ohlen",
        *   "title": "Gucci-owner Kering jumps 12% as new CEO maps revival, sales beats estimates - CNBC",
        *   "description": "The luxury group said it sees a return to growth this year even as it posted another quarter of sales declines.",
        *   "url": ["https://www.cnbc.com/2026/02/10/gucci-kering-earnings-stock-sales-q4-fy-new-ceo.html"](https://www.cnbc.com/2026/02/10/gucci-kering-earnings-stock-sales-q4-fy-new-ceo.html),
        *   "urlToImage": ["https://image.cnbcfm.com/api/v1/image/108088889-1737363061746-gettyimages-1246741729-Luxury_Brand_In_Shanghai.jpeg?v=1737363083&w=1920&h=1080"](https://image.cnbcfm.com/api/v1/image/108088889-1737363061746-gettyimages-1246741729-Luxury_Brand_In_Shanghai.jpeg?v=1737363083&w=1920&h=1080),
        *   "publishedAt": "2026-02-10T08:15:43Z",
        *   "content": "Customers shop at a GUCCI luxury store in Shanghai, China.\r\nKering said it expects a return to growth this year even as it posted another quarter of sales declines on Tuesday, with its biggest sales … [+3904 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "CNBC"

},
        *   "author": "Sam Meredith",
        *   "title": "BP shares fall 5% after oil major suspends share buyback plan - CNBC",
        *   "description": "BP on Tuesday posted fourth-quarter profit in line with expectations, after crude prices dipped below $60 a barrel for the first time in nearly five years.",
        *   "url": ["https://www.cnbc.com/2026/02/10/bp-earnings-q4-full-year-oil-energy.html"](https://www.cnbc.com/2026/02/10/bp-earnings-q4-full-year-oil-energy.html),
        *   "urlToImage": ["https://image.cnbcfm.com/api/v1/image/108152372-1748602162238-gettyimages-2209616466-bp2-1.jpeg?v=1770637946&w=1920&h=1080"](https://image.cnbcfm.com/api/v1/image/108152372-1748602162238-gettyimages-2209616466-bp2-1.jpeg?v=1770637946&w=1920&h=1080),
        *   "publishedAt": "2026-02-10T07:08:02Z",
        *   "content": "British oil giant BP on Tuesday posted fourth-quarter profit in line with expectations and suspended share buybacks, seeking to shore up its balance sheet as lower crude prices take their toll.\r\nThe … [+2575 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "Daily Beast"

},
        *   "author": "Michael Boyle",
        *   "title": "Jon Stewart Exposes Real Reason for Kid Rock’s Sad Halftime Show - The Daily Beast",
        *   "description": "Stewart mocked Turning Point USA’s “safe space” alternative.",
        *   "url": ["https://www.thedailybeast.com/obsessed/jon-stewart-exposes-real-reason-for-kid-rocks-sad-halftime-show/"](https://www.thedailybeast.com/obsessed/jon-stewart-exposes-real-reason-for-kid-rocks-sad-halftime-show/),
        *   "urlToImage": ["https://www.thedailybeast.com/resizer/v2/7CH4RMS4LNFDFCHQAGWDR7QUVI.png?smart=true&auth=d44fb14e75b2613ebfbce8fa3c2ddfcfc0ea486f8be936c8c67c3ed710f03988&width=1200&height=630"](https://www.thedailybeast.com/resizer/v2/7CH4RMS4LNFDFCHQAGWDR7QUVI.png?smart=true&auth=d44fb14e75b2613ebfbce8fa3c2ddfcfc0ea486f8be936c8c67c3ed710f03988&width=1200&height=630),
        *   "publishedAt": "2026-02-10T06:54:00Z",
        *   "content": "Jon Stewart has bluntly outlined the real reason behind Kid Rocks lip-synced counterprogramming to the Super Bowl halftime show.\r\nIn his monologue on Monday, the recurring Daily Show host detailed th… [+2274 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "CNBC"

},
        *   "author": "Anniek Bao",
        *   "title": "'Despicable and reprehensible': China lashes out at UK expansion of visa scheme following Jimmy Lai conviction - CNBC",
        *   "description": "The diplomatic tensions came after pro-democracy tycoon Jimmy Lai was sentenced to 20 years in one of the city's most prominent prosecutions.",
        *   "url": ["https://www.cnbc.com/2026/02/10/china-uk-hong-kong-visa-jimmy-lai-sentencing-visa-bno.html"](https://www.cnbc.com/2026/02/10/china-uk-hong-kong-visa-jimmy-lai-sentencing-visa-bno.html),
        *   "urlToImage": ["https://image.cnbcfm.com/api/v1/image/108263667-1770701067885-gettyimages-2235026456-AFP_74HV4GD.jpeg?v=1770701085&w=1920&h=1080"](https://image.cnbcfm.com/api/v1/image/108263667-1770701067885-gettyimages-2235026456-AFP_74HV4GD.jpeg?v=1770701085&w=1920&h=1080),
        *   "publishedAt": "2026-02-10T05:16:45Z",
        *   "content": "China's embassy in London on Tuesday criticized the U.K.'s decision to expand a visa program for Hong Kong residents, calling the move an interference in its internal affairs after a court sentenced … [+2827 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "cleveland.com"

},
        *   "author": "Chris Fedor, cleveland.com",
        *   "title": "Donovan Mitchell, James Harden clutch late as Cavs punctuate road trip with 119-117 win over Nuggets - Cleveland.com",
        *   "description": "Going into the game, Cavs coach Kenny Atkinson knew what Cleveland was up against.",
        *   "url": ["https://www.cleveland.com/cavs/2026/02/donovan-mitchell-james-harden-come-through-in-clutch-as-cavs-punctuate-road-trip-with-119-117-win-over-nuggets.html"](https://www.cleveland.com/cavs/2026/02/donovan-mitchell-james-harden-come-through-in-clutch-as-cavs-punctuate-road-trip-with-119-117-win-over-nuggets.html),
        *   "urlToImage": ["https://www.cleveland.com/resizer/v2/V36ZERFGYNA6TAADJE63UAQTJU.jpg?auth=33a50d3212cfea00c8504108dd714c3471a39749b53751acc2f503fe9287bf2d&width=1280&smart=true&quality=90"](https://www.cleveland.com/resizer/v2/V36ZERFGYNA6TAADJE63UAQTJU.jpg?auth=33a50d3212cfea00c8504108dd714c3471a39749b53751acc2f503fe9287bf2d&width=1280&smart=true&quality=90),
        *   "publishedAt": "2026-02-10T04:53:00Z",
        *   "content": "DENVER Cavs coach Kenny Atkinson delivered a frank message to his team Monday night. \r\nEverythings against us. \r\nAnd yet, Cleveland punctuated its road trip with a 119-117 come-from-behind win agains… [+5253 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "YourTango"

},
        *   "author": "Ruby Miranda",
        *   "title": "Luck Improves For 3 Zodiac Signs On February 10, 2026 - YourTango",
        *   "description": "Luck improves for Leo, Virgo, and Aquarius zodiac signs on February 10, 2026, during the Waning Crescent Moon in Sagittarius.",
        *   "url": ["https://www.yourtango.com/2026394049/zodiac-signs-luck-improves-february-10-2026"](https://www.yourtango.com/2026394049/zodiac-signs-luck-improves-february-10-2026),
        *   "urlToImage": ["https://www.yourtango.com/sites/default/files/image_blog/2026-02/zodiac-signs-luck-improves-february-10-2026.png"](https://www.yourtango.com/sites/default/files/image_blog/2026-02/zodiac-signs-luck-improves-february-10-2026.png),
        *   "publishedAt": "2026-02-10T03:05:21Z",
        *   "content": "On February 10, 2026, luck is improving for three zodiac signs. On Tuesday, we may even find ourselves wondering how things got this good.\r\nThe Waning Crescent Moon shifts from Scorpio to Sagittarius… [+2993 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "politico",
            *   "name": "Politico"

},
        *   "author": "Cassandra Dumay",
        *   "title": "House approves housing bill, setting stage for tough Senate negotiations - Politico",
        *   "description": "After a bipartisan House vote, the housing deal faces a bicameral test.",
        *   "url": ["https://www.politico.com/live-updates/2026/02/09/congress/house-approves-housing-bill-setting-stage-for-tough-senate-negotiations-00772552"](https://www.politico.com/live-updates/2026/02/09/congress/house-approves-housing-bill-setting-stage-for-tough-senate-negotiations-00772552),
        *   "urlToImage": ["https://www.politico.com/dims4/default/f4b174a/2147483647/resize/1200x/quality/90/?url=https%3A%2F%2Fstatic.politico.com%2Fc5%2Ff4%2F9f0592eb41aab4037ff42b6519cc%2Fcongress-speaker-65171.jpg"](https://www.politico.com/dims4/default/f4b174a/2147483647/resize/1200x/quality/90/?url=https%3A%2F%2Fstatic.politico.com%2Fc5%2Ff4%2F9f0592eb41aab4037ff42b6519cc%2Fcongress-speaker-65171.jpg),
        *   "publishedAt": "2026-02-10T00:20:30Z",
        *   "content": null

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "Yahoo Entertainment"

},
        *   "author": "Sam Goodwin",
        *   "title": "Fans blown away after Chinese superstar denied gold by move never seen before - Yahoo News Australia",
        *   "description": "Mathilde Gremaud defended her crown from four years ago. Read more here.",
        *   "url": ["https://au.news.yahoo.com/fans-blown-away-after-eileen-gu-denied-gold-by-move-never-seen-before-at-winter-olympics-000234397.html"](https://au.news.yahoo.com/fans-blown-away-after-eileen-gu-denied-gold-by-move-never-seen-before-at-winter-olympics-000234397.html),
        *   "urlToImage": ["https://s.yimg.com/ny/api/res/1.2/O9bZgib2ybF3UD_T5xE67g--/YXBwaWQ9aGlnaGxhbmRlcjt3PTEyMDA7aD02NDY7Y2Y9d2VicA--/https://s.yimg.com/os/creatr-uploaded-images/2026-02/52c3b960-0613-11f1-bc7a-add4f2809d98"](https://s.yimg.com/ny/api/res/1.2/O9bZgib2ybF3UD_T5xE67g--/YXBwaWQ9aGlnaGxhbmRlcjt3PTEyMDA7aD02NDY7Y2Y9d2VicA--/https://s.yimg.com/os/creatr-uploaded-images/2026-02/52c3b960-0613-11f1-bc7a-add4f2809d98),
        *   "publishedAt": "2026-02-10T00:02:00Z",
        *   "content": "Eileen Gu had to settle for silver in the women's slopestyle at the Winter Olympics on Monday after Mathilde Gremaud became the first woman to perform a trick known as the nose butter double cork 126… [+2219 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "BBC News"

},
        *   "author": null,
        *   "title": "Thailand election: The result the polls never saw coming - BBC",
        *   "description": "Why did a youthful, progressive party do so poorly compared to a transactional, old-style party?",
        *   "url": ["https://www.bbc.com/news/articles/c5y6534y3y5o"](https://www.bbc.com/news/articles/c5y6534y3y5o),
        *   "urlToImage": ["https://ichef.bbci.co.uk/news/1024/branded_news/3ec2/live/fd605c80-05e0-11f1-b5e2-dd58fc65f0f6.jpg"](https://ichef.bbci.co.uk/news/1024/branded_news/3ec2/live/fd605c80-05e0-11f1-b5e2-dd58fc65f0f6.jpg),
        *   "publishedAt": "2026-02-09T23:58:04Z",
        *   "content": "It was also harder for the reformists to distinguish themselves on a single issue this time. In 2023, after nine years being ruled by the stern, avuncular Prayuth Chan-ocha, the general who led the 2… [+192 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "GSMArena.com"

},
        *   "author": "Siddharth",
        *   "title": "Oppo Find N6 launch date tipped, said to feature industry’s shallowest display crease - GSMArena.com news - GSMArena.com",
        *   "description": "The foldable is tipped to use the Snapdragon 8 Elite Gen 5 chipset. Oppo recently confirmed that it plans to launch its next foldable after the Chinese New...",
        *   "url": ["https://www.gsmarena.com/oppo_find_n6_launch_date_tipped_said_to_feature_industrys_shallowest_display_crease-news-71473.php"](https://www.gsmarena.com/oppo_find_n6_launch_date_tipped_said_to_feature_industrys_shallowest_display_crease-news-71473.php),
        *   "urlToImage": ["https://fdn.gsmarena.com/imgroot/news/26/02/oppo-find-n6-launch-date-leak/-952x498w6/gsmarena_000.jpg"](https://fdn.gsmarena.com/imgroot/news/26/02/oppo-find-n6-launch-date-leak/-952x498w6/gsmarena_000.jpg),
        *   "publishedAt": "2026-02-09T23:49:02Z",
        *   "content": "Oppo recently confirmed that it plans to launch its next foldable after the Chinese New Year. Now, a tipster has revealed the foldables launch timeline for China and select markets. Meanwhile, Oppo h… [+1286 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "ars-technica",
            *   "name": "Ars Technica"

},
        *   "author": "Kyle Orland",
        *   "title": "Just look at Ayaneo's absolute unit of a Windows gaming \"handheld\" - Ars Technica",
        *   "description": "The Ayaneo Next II pushes past 3 pounds, 13 inches wide, and costs up to $4,300.",
        *   "url": ["https://arstechnica.com/gaming/2026/02/just-look-at-ayaneos-absolute-unit-of-a-windows-gaming-handheld/"](https://arstechnica.com/gaming/2026/02/just-look-at-ayaneos-absolute-unit-of-a-windows-gaming-handheld/),
        *   "urlToImage": ["https://cdn.arstechnica.net/wp-content/uploads/2026/02/ayaneonext-1152x648-1770675970.jpeg"](https://cdn.arstechnica.net/wp-content/uploads/2026/02/ayaneonext-1152x648-1770675970.jpeg),
        *   "publishedAt": "2026-02-09T22:51:16Z",
        *   "content": null

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "BBC News"

},
        *   "author": null,
        *   "title": "Instagram and YouTube owners built 'addiction machines', trial told - BBC",
        *   "description": "The tech giants are under scrutiny over social media addiction in a landmark jury trial in Los Angeles",
        *   "url": ["https://www.bbc.com/news/articles/c3wlpqpe2z4o"](https://www.bbc.com/news/articles/c3wlpqpe2z4o),
        *   "urlToImage": ["https://ichef.bbci.co.uk/news/1024/branded_news/d3df/live/62944060-05f7-11f1-b5e2-dd58fc65f0f6.jpg"](https://ichef.bbci.co.uk/news/1024/branded_news/d3df/live/62944060-05f7-11f1-b5e2-dd58fc65f0f6.jpg),
        *   "publishedAt": "2026-02-09T22:20:07Z",
        *   "content": "Over the course of the next several weeks, there will be testimony from experts, family members of children who died, and by Zuckerberg, Adam Mosseri, the head of Instagram, and Neal Mohan, the CEO o… [+9 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "Wink News"

},
        *   "author": "Writer: Nicholas Karsen",
        *   "title": "Over 50 cases of measles confirmed at Ave Maria University - WINK News",
        *   "description": "AVE MARIA, Fla.—Over 50 cases of Measles have been reported at Ave Maria University, according to the Florida Department of Health's latest update.",
        *   "url": ["https://www.winknews.com/news/collier/over-50-cases-of-measles-confirmed-at-ave-maria-university/article_298f2922-a5b2-4b67-a0cd-24009dc56801.html"](https://www.winknews.com/news/collier/over-50-cases-of-measles-confirmed-at-ave-maria-university/article_298f2922-a5b2-4b67-a0cd-24009dc56801.html),
        *   "urlToImage": ["https://bloximages.chicago2.vip.townnews.com/winknews.com/content/tncms/assets/v3/editorial/4/da/4da9fdb9-f204-5ff4-b472-556f52d6a016/67f66bdfe1fd0.image.png?crop=1920%2C1008%2C0%2C35&resize=1200%2C630&order=crop%2Cresize"](https://bloximages.chicago2.vip.townnews.com/winknews.com/content/tncms/assets/v3/editorial/4/da/4da9fdb9-f204-5ff4-b472-556f52d6a016/67f66bdfe1fd0.image.png?crop=1920%2C1008%2C0%2C35&resize=1200%2C630&order=crop%2Cresize),
        *   "publishedAt": "2026-02-09T22:15:00Z",
        *   "content": "AVE MARIA, Fla.Over 50 cases of Measles have been reported at Ave Maria University, according to the Florida Department of Health's latest update.\r\nPer their Friday, February 6, 3 p.m. update, Ave Ma… [+1622 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": null,
            *   "name": "9to5google.com"

},
        *   "author": "Ben Schoon",
        *   "title": "WhatsApp is bringing video and voice calls to its web app - 9to5Google",
        *   "description": "WhatsApp is now rolling out support for video and voice calls through its web app, bringing support for calls to...",
        *   "url": ["http://9to5google.com/2026/02/09/whatsapp-testing-web-app-calls/"](http://9to5google.com/2026/02/09/whatsapp-testing-web-app-calls/),
        *   "urlToImage": ["https://i0.wp.com/9to5google.com/wp-content/uploads/sites/4/2023/09/whatsapp-fi-01.webp?resize=1200%2C628&quality=82&strip=all&ssl=1"](https://i0.wp.com/9to5google.com/wp-content/uploads/sites/4/2023/09/whatsapp-fi-01.webp?resize=1200%2C628&quality=82&strip=all&ssl=1),
        *   "publishedAt": "2026-02-09T21:55:00Z",
        *   "content": "WhatsApp is now rolling out support for video and voice calls through its web app, bringing support for calls to your computer and other devices.\r\nThe WhatsApp web app is a handy way to access your m… [+874 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "abc-news",
            *   "name": "ABC News"

},
        *   "author": "ABC News",
        *   "title": "Howard Lutnick, Trump's commerce secretary, faces calls to resign over Epstein ties - ABC News",
        *   "description": null,
        *   "url": ["https://abcnews.go.com/Politics/howard-lutnick-trumps-commerce-secretary-faces-calls-resign/story?id\\\\u003d130002715"](https://abcnews.go.com/Politics/howard-lutnick-trumps-commerce-secretary-faces-calls-resign/story?id\\u003d130002715),
        *   "urlToImage": null,
        *   "publishedAt": "2026-02-09T21:44:48Z",
        *   "content": null

}

]

}

* * *

Top headlines from BBC News

Definition

`GET https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey=API_KEY`
Example response

{

*   "status": "ok",
*   "totalResults": 10,
*   -

"articles": [
    *   -

{
        *   -

"source": {
            *   "id": "bbc-news",
            *   "name": "BBC News"

},
        *   "author": "BBC News",
        *   "title": "Barnsley man who laid 'Home Alone' style traps at drug den jailed",
        *   "description": "Ian Claughton, 60, fortified his home with tripwires, home-made pipe bombs and a flamethrower.",
        *   "url": ["https://www.bbc.co.uk/news/articles/cx2r5qzre27o"](https://www.bbc.co.uk/news/articles/cx2r5qzre27o),
        *   "urlToImage": ["https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/d790/live/0df0fbf0-0685-11f1-b7e1-afb6d0884c18.jpg"](https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/d790/live/0df0fbf0-0685-11f1-b7e1-afb6d0884c18.jpg),
        *   "publishedAt": "2026-02-10T14:52:17.3237458Z",
        *   "content": "A man who rigged his house with \"Home Alone-style\" booby traps, including a flamethrower and tripwires, to protect his drugs enterprise has been jailed.\r\nIan Claughton, 60, \"heavily fortified\" three … [+493 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "bbc-news",
            *   "name": "BBC News"

},
        *   "author": "BBC News",
        *   "title": "Marc Anthony says Beckham family feud is 'unfortunate' but 'hardly the truth'",
        *   "description": "The 57-year-old performed at Brooklyn and Nicola Peltz Beckham's wedding reception in 2022.",
        *   "url": ["https://www.bbc.co.uk/news/articles/c98gyegzypxo"](https://www.bbc.co.uk/news/articles/c98gyegzypxo),
        *   "urlToImage": ["https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/7203/live/8b6affc0-067d-11f1-9972-d3f265c101c6.jpg"](https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/7203/live/8b6affc0-067d-11f1-9972-d3f265c101c6.jpg),
        *   "publishedAt": "2026-02-10T14:37:26.9188832Z",
        *   "content": "Brooklyn Beckham published a six-page Instagram statement on 19 January, confirming a rift between him and his wife with the wider Beckham family. \r\nHe accused his parents of trying to \"ruin my relat… [+1418 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "bbc-news",
            *   "name": "BBC News"

},
        *   "author": "BBC News",
        *   "title": "Henry Zeffman: Six key questions about Keir Starmer's future",
        *   "description": "There is no doubting the peril the prime minister was in, but while Labour MPs have decided to stick with him, his future is far from certain.",
        *   "url": ["https://www.bbc.co.uk/news/articles/c80jrg08rk3o"](https://www.bbc.co.uk/news/articles/c80jrg08rk3o),
        *   "urlToImage": ["https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/16bb/live/53225f40-0683-11f1-9972-d3f265c101c6.jpg"](https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/16bb/live/53225f40-0683-11f1-9972-d3f265c101c6.jpg),
        *   "publishedAt": "2026-02-10T14:37:17.7000247Z",
        *   "content": "For now, yes.\r\nSir Keir got to a position on Monday afternoon where Anas Sarwar, the Scottish Labour leader, was about to call for his head and most of the cabinet were conspicuously silent. \r\nMany i… [+1388 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "bbc-news",
            *   "name": "BBC News"

},
        *   "author": "BBC News",
        *   "title": "Small Prophets: Sir Michael Palin on his first TV acting role in seven years",
        *   "description": "The actor and presenter said he was attracted by the \"humour and magic\" of BBC series Small Prophets.",
        *   "url": ["https://www.bbc.co.uk/news/articles/czd81vr9dmyo"](https://www.bbc.co.uk/news/articles/czd81vr9dmyo),
        *   "urlToImage": ["https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/29f9/live/fc098400-066d-11f1-b7e1-afb6d0884c18.jpg"](https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/29f9/live/fc098400-066d-11f1-b7e1-afb6d0884c18.jpg),
        *   "publishedAt": "2026-02-10T12:37:24.8112729Z",
        *   "content": "In a five-star review, the Guardian's Jack Seale, external said Small Prophets was \"a pure, pure pleasure\"\r\n\"If there is a message or a moral, it is that there are still wonderful things at hand in a… [+1502 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "bbc-news",
            *   "name": "BBC News"

},
        *   "author": "BBC News",
        *   "title": "US lawmakers accuse justice department of 'inappropriately' redacting Epstein files",
        *   "description": "Republican Thomas Massie and Democrat Ro Khanna say the DOJ is not complying with their transparency law.",
        *   "url": ["https://www.bbc.co.uk/news/articles/cn5gzepnw4lo"](https://www.bbc.co.uk/news/articles/cn5gzepnw4lo),
        *   "urlToImage": ["https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/4540/live/fe1dd650-0673-11f1-b5e2-dd58fc65f0f6.jpg"](https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/4540/live/fe1dd650-0673-11f1-b5e2-dd58fc65f0f6.jpg),
        *   "publishedAt": "2026-02-10T12:07:32.7472831Z",
        *   "content": "After viewing the un-redacted documents, Massie and Khanna, who co-sponsored the law which compelled the release of the Epstein files last year, told reporters they had a list of about 20 people in w… [+2762 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "bbc-news",
            *   "name": "BBC News"

},
        *   "author": "BBC News",
        *   "title": "Wuthering Heights: Margot Robbie and Jacob Elordi film splits critics",
        *   "description": "Emerald Fennell's take on Emily Bronte's classic novel has received a mixed response from film reviewers.",
        *   "url": ["https://www.bbc.co.uk/news/articles/c3wl6vezydeo"](https://www.bbc.co.uk/news/articles/c3wl6vezydeo),
        *   "urlToImage": ["https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/d13c/live/ab3db630-0673-11f1-b5e2-dd58fc65f0f6.jpg"](https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/d13c/live/ab3db630-0673-11f1-b5e2-dd58fc65f0f6.jpg),
        *   "publishedAt": "2026-02-10T12:07:28.3553809Z",
        *   "content": "Publisher Mills &amp; Boon was referenced in more than one review, with the Sun's Dulcie Pearce suggesting, external the film had replaced chunks of Brote's book with pages from the romance novels.\r\n… [+1547 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "bbc-news",
            *   "name": "BBC News"

},
        *   "author": "BBC News",
        *   "title": "Macron urges Europe to start acting like world power",
        *   "description": "The French president warns of growing threats from China, Russia and now the US, saying Europe faces a \"wake-up call\".",
        *   "url": ["https://www.bbc.co.uk/news/articles/ce8n1zdnpd3o"](https://www.bbc.co.uk/news/articles/ce8n1zdnpd3o),
        *   "urlToImage": ["https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/2921/live/75367700-0675-11f1-9972-d3f265c101c6.jpg"](https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/2921/live/75367700-0675-11f1-9972-d3f265c101c6.jpg),
        *   "publishedAt": "2026-02-10T11:52:26.9488916Z",
        *   "content": "Macron repeated his call for EU-wide mutualised loans in order to raise hundreds of billions of euros needed for industrial investment.\r\n\"The time has come to launch a shared debt capacity to fund ou… [+2777 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "bbc-news",
            *   "name": "BBC News"

},
        *   "author": "BBC News",
        *   "title": "Izabela Zablocka death: 'Skilled butcher' guilty of murdering, cutting up and burying partner",
        *   "description": "Anna Podedworna is convicted of the murder of Izabela Zablocka, whose remains were found last year.",
        *   "url": ["https://www.bbc.co.uk/news/articles/cq6qr37z0reo"](https://www.bbc.co.uk/news/articles/cq6qr37z0reo),
        *   "urlToImage": ["https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/fa98/live/ace8ffc0-0674-11f1-9972-d3f265c101c6.jpg"](https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/fa98/live/ace8ffc0-0674-11f1-9972-d3f265c101c6.jpg),
        *   "publishedAt": "2026-02-10T11:52:20.4505087Z",
        *   "content": "The jury was told the two women had moved to the UK together from Poland in search of work and lived in the Normanton area of Derby.\r\nThe prosecution said Zablocka phoned her mother in Poland on 28 A… [+625 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "bbc-news",
            *   "name": "BBC News"

},
        *   "author": "BBC News",
        *   "title": "Island near Portmeirion is for sale - but you may need waders to reach it",
        *   "description": "The 17-acre Ynys Gifftan is available to buy, but waterproofs are a must as it lies in an estuary.",
        *   "url": ["https://www.bbc.co.uk/news/articles/cdx4xkkly9qo"](https://www.bbc.co.uk/news/articles/cdx4xkkly9qo),
        *   "urlToImage": ["https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/d0e0/live/0843f290-05bb-11f1-8336-6d2201ebafb2.jpg"](https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/d0e0/live/0843f290-05bb-11f1-8336-6d2201ebafb2.jpg),
        *   "publishedAt": "2026-02-10T11:07:21.6367372Z",
        *   "content": "A listing on the Rightmove website described the island as set in an \"expansive and unspoilt landscape with uninterrupted panoramic views\" across the coastline and mountains in Eryri National Park.\r\n… [+799 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "bbc-news",
            *   "name": "BBC News"

},
        *   "author": "BBC News",
        *   "title": "Chappell Roan leaves talent agency led by Casey Wasserman after Epstein fallout",
        *   "description": "Wasserman has been criticised after his flirtatious emails to Ghislaine Maxwell were revealed in the Epstein files.",
        *   "url": ["https://www.bbc.co.uk/news/articles/cewz1keql5no"](https://www.bbc.co.uk/news/articles/cewz1keql5no),
        *   "urlToImage": ["https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/d33a/live/55b41960-0651-11f1-aea3-ab6941d946c2.jpg"](https://ichef.bbci.co.uk/ace/branded_news/1200/cpsprodpb/d33a/live/55b41960-0651-11f1-aea3-ab6941d946c2.jpg),
        *   "publishedAt": "2026-02-10T07:52:20.9956823Z",
        *   "content": "Wasserman has said he \"deeply regrets\" the emails exchanged with Maxwell, who is currently serving a 20-year prison sentence for recruiting and trafficking teenage girls to be sexually abused by Epst… [+792 chars]"

}

]

}

* * *

Top business headlines from Germany

Definition

`GET https://newsapi.org/v2/top-headlines?country=de&category=business&apiKey=API_KEY`
Example response

{

*   "status": "ok",
*   "totalResults": 0,
*   "articles": [ ]

}

* * *

Top headlines about Trump

Definition

`GET https://newsapi.org/v2/top-headlines?q=trump&apiKey=API_KEY`
Example response

{

*   "status": "ok",
*   "totalResults": 66,
*   -

"articles": [
    *   -

{
        *   -

"source": {
            *   "id": "bild",
            *   "name": "Bild"

},
        *   "author": "Sebastian Kayser",
        *   "title": "Donald Trump kritisiert Hunter Hess: Olympia-Streit entbrennt | Sport",
        *   "description": "Donald Trumps Kommentar zu Hunter Hess sorgt für Kontroversen bei den Olympischen Spielen. Jetzt kontert der Gouverneur von Utah.",
        *   "url": ["https://www.bild.de/sport/olympia/donald-trump-kritisiert-hunter-hess-olympia-streit-entbrennt-698b3cc33eb21272be953a8a"](https://www.bild.de/sport/olympia/donald-trump-kritisiert-hunter-hess-olympia-streit-entbrennt-698b3cc33eb21272be953a8a),
        *   "urlToImage": ["https://images.bild.de/698b3cc33eb21272be953a8a/318a94dd39d834f8c419726c1ea3e133,684bc4c?w=1280"](https://images.bild.de/698b3cc33eb21272be953a8a/318a94dd39d834f8c419726c1ea3e133,684bc4c?w=1280),
        *   "publishedAt": "2026-02-10T14:49:22Z",
        *   "content": "TTS-Player überspringenArtikel weiterlesenDer Gegenwind wird rauer!\r\nJetzt wird US-Präsident Donald Trump (79) schon aus den eigenen Reihen angegriffen. Der Grund: Er hat sich mal wieder im Ton vergr… [+1824 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "fox-news",
            *   "name": "Fox News"

},
        *   "author": null,
        *   "title": "Republican Sen Susan Collins says she's running for re-election",
        *   "description": "Collins was one of the Senate Republicans who voted to convict Trump after the House impeached him in 2021",
        *   "url": ["https://www.foxnews.com/politics/republican-sen-susan-collins-says-shes-running-re-election"](https://www.foxnews.com/politics/republican-sen-susan-collins-says-shes-running-re-election),
        *   "urlToImage": ["https://static.foxnews.com/foxnews.com/content/uploads/2026/02/susan-collins-july-2025.jpg"](https://static.foxnews.com/foxnews.com/content/uploads/2026/02/susan-collins-july-2025.jpg),
        *   "publishedAt": "2026-02-10T14:37:14.7320131Z",
        *   "content": "GOP Sen. Susan Collins of Maine has announced that she will seek re-election this year.\r\n\"GOOD NEWS! I am ALL-IN for 2026,\" she noted in a Tuesday post on X.\r\nIn a video, the lawmaker pulls a sneaker… [+423 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "cbs-news",
            *   "name": "CBS News"

},
        *   "author": "CBS News",
        *   "title": "Justice Jackson discusses navigating relationships on Supreme Court despite differences",
        *   "description": "Supreme Court Justice Ketanji Brown Jackson, who has been a justice on the high court for four years, speaks to \"CBS Mornings\" about how she navigates relationships on the court despite differences, the upcoming opinion on President Trump's tariffs and the ad…",
        *   "url": ["https://www.cbsnews.com/video/justice-jackson-discusses-navigating-relationships-supreme-court/"](https://www.cbsnews.com/video/justice-jackson-discusses-navigating-relationships-supreme-court/),
        *   "urlToImage": ["https://assets2.cbsnewsstatic.com/hub/i/r/2026/02/10/fcff7b18-54f5-4667-b68b-a63ec4e26d47/thumbnail/1200x630/2a0ac48650db803c90507311f8e3a4c3/cbsn-fusion-justice-jackson-discusses-navigating-relationships-supreme-court-thumbnail.jpg"](https://assets2.cbsnewsstatic.com/hub/i/r/2026/02/10/fcff7b18-54f5-4667-b68b-a63ec4e26d47/thumbnail/1200x630/2a0ac48650db803c90507311f8e3a4c3/cbsn-fusion-justice-jackson-discusses-navigating-relationships-supreme-court-thumbnail.jpg),
        *   "publishedAt": "2026-02-10T14:36:00+00:00",
        *   "content": "Copyright ©2026 CBS Interactive Inc. All rights reserved."

},
    *   -

{
        *   -

"source": {
            *   "id": "cbs-news",
            *   "name": "CBS News"

},
        *   "author": "CBS News",
        *   "title": "Eye Opener: Savannah Guthrie asks for public's help in search for her mother",
        *   "description": "Savannah Guthrie issues a new plea for help from the public in the search for her missing mother, Nancy Guthrie. Plus, Jeffrey Epstein accomplice Ghislaine Maxwell pleads the Fifth before a House committee, asking for clemency from President Trump. All that a…",
        *   "url": ["https://www.cbsnews.com/video/eye-opener-savannah-guthrie-asks-for-publics-help-in-search-for-her-mother/"](https://www.cbsnews.com/video/eye-opener-savannah-guthrie-asks-for-publics-help-in-search-for-her-mother/),
        *   "urlToImage": ["https://assets2.cbsnewsstatic.com/hub/i/r/2026/02/10/e24c7e7c-be25-4b89-b5bd-d5b8299a4e06/thumbnail/1200x630/182750bf3f6637c7cc8a48238f5c4291/cbsn-fusion-eye-opener-savannah-guthrie-asks-for-publics-help-in-search-for-her-mother-thumbnail.jpg"](https://assets2.cbsnewsstatic.com/hub/i/r/2026/02/10/e24c7e7c-be25-4b89-b5bd-d5b8299a4e06/thumbnail/1200x630/182750bf3f6637c7cc8a48238f5c4291/cbsn-fusion-eye-opener-savannah-guthrie-asks-for-publics-help-in-search-for-her-mother-thumbnail.jpg),
        *   "publishedAt": "2026-02-10T14:26:00+00:00",
        *   "content": "Copyright ©2026 CBS Interactive Inc. All rights reserved."

},
    *   -

{
        *   -

"source": {
            *   "id": "msnbc",
            *   "name": "MSNBC"

},
        *   "author": "Steve Benen",
        *   "title": "Dan Bongino returns to Fox News as the revolving door keeps spinning",
        *   "description": "The former FBI deputy director went from conservative media to the Trump administration and then back to conservative media, all within 10 months.",
        *   "url": ["https://www.ms.now/rachel-maddow-show/maddowblog/dan-bongino-fox-news-fbi-trump"](https://www.ms.now/rachel-maddow-show/maddowblog/dan-bongino-fox-news-fbi-trump),
        *   "urlToImage": ["https://res.cloudinary.com/msnow/images/t_nbcnews-fp-1200-630/f_auto,q_auto/v1770729574/260210-don-bongino-pi/260210-don-bongino-pi.jpg?_i=AA"](https://res.cloudinary.com/msnow/images/t_nbcnews-fp-1200-630/f_auto,q_auto/v1770729574/260210-don-bongino-pi/260210-don-bongino-pi.jpg?_i=AA),
        *   "publishedAt": "2026-02-10T13:53:33Z",
        *   "content": "A month ago, after Senate Republicans confirmed Sara Carter as the nations new drug czar, she likely recognized many of her new colleagues in the executive branch. Carter, who didnt have any of the r… [+2105 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "time",
            *   "name": "Time"

},
        *   "author": "Callum Sutherland",
        *   "title": "Trump Threatens to Block Opening of Bridge Between U.S. and Canada, Demands Compensation",
        *   "description": "One Canadian official has referred to Trump's threat as \"insane.\"",
        *   "url": ["https://time.com/7377319/trump-threatens-canada-ontario-michigan-bridge/"](https://time.com/7377319/trump-threatens-canada-ontario-michigan-bridge/),
        *   "urlToImage": ["https://api.time.com/wp-content/uploads/2026/02/GettyImages-2240467708.jpg?quality=85&w=1200&h=628&crop=1"](https://api.time.com/wp-content/uploads/2026/02/GettyImages-2240467708.jpg?quality=85&w=1200&h=628&crop=1),
        *   "publishedAt": "2026-02-10T13:43:10Z",
        *   "content": "President Donald Trump has threatened to block the opening of a $4.7 billion bridge connecting Detroit, Michigan, to Windsor, Ontario, in the latest display of frayed relations between the U.S. and C… [+4040 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "cnn",
            *   "name": "CNN"

},
        *   "author": null,
        *   "title": "Trump administration latest: DOJ un-redacts more names in Epstein files after pressure from lawmakers",
        *   "description": "The Justice Department un-redacted some more names in the Jeffrey Epstein files last night after pressure from lawmakers. Follow for the latest updates.",
        *   "url": ["https://www.cnn.com/politics/live-news/trump-administration-epstein-files-02-10-26"](https://www.cnn.com/politics/live-news/trump-administration-epstein-files-02-10-26),
        *   "urlToImage": ["https://media.cnn.com/api/v1/images/stellar/prod/gettyimages-2258696523.jpg?c=16x9&q=w_800,c_fill"](https://media.cnn.com/api/v1/images/stellar/prod/gettyimages-2258696523.jpg?c=16x9&q=w_800,c_fill),
        *   "publishedAt": "2026-02-10T13:16:44Z",
        *   "content": "President Donald Trump threatened yesterday to block the opening of a new bridge connecting the US and Canada, again lashing out at his countrys northern neighbor over a range of economic issues as t… [+1569 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "the-verge",
            *   "name": "The Verge"

},
        *   "author": "David Pierce",
        *   "title": "Could the Trump Phone be a good phone?",
        *   "description": "The Trump Mobile T1 Phone 8002 appears to be actually nearing launch, plus the latest on Moltbook and OpenClaw, on The Vergecast.",
        *   "url": ["https://www.theverge.com/podcast/876188/trump-phone-specs-price-date-moltbook-openclaw-vergecast"](https://www.theverge.com/podcast/876188/trump-phone-specs-price-date-moltbook-openclaw-vergecast),
        *   "urlToImage": ["https://platform.theverge.com/wp-content/uploads/sites/2/2026/02/VRG_VST_021026_Site.jpg?quality=90&strip=all&crop=0%2C10.732984293194%2C100%2C78.534031413613&w=1200"](https://platform.theverge.com/wp-content/uploads/sites/2/2026/02/VRG_VST_021026_Site.jpg?quality=90&strip=all&crop=0%2C10.732984293194%2C100%2C78.534031413613&w=1200),
        *   "publishedAt": "2026-02-10T13:10:02+00:00",
        *   "content": "<ul><li></li><li></li><li></li></ul>\r\nOn The Vergecast: phone specs, Tesla cars, and buying a Mac Mini for your AI agents.\r\nOn The Vergecast: phone specs, Tesla cars, and buying a Mac Mini for your A… [+3244 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "news24",
            *   "name": "News24"

},
        *   "author": "news24",
        *   "title": "Trump demands ‘fairness and respect that we deserve’, threatens to block US-Canada bridge",
        *   "description": "US President Donald Trump threatened to stop the opening of a new bridge between the United States and Canada, in a fresh salvo against the country he has suggested should become the 51st US state.",
        *   "url": ["https://www.news24.com/world/trump-demands-fairness-and-respect-that-we-deserve-threatens-to-block-us-canada-bridge-20260210-0678"](https://www.news24.com/world/trump-demands-fairness-and-respect-that-we-deserve-threatens-to-block-us-canada-bridge-20260210-0678),
        *   "urlToImage": ["https://news24cobalt.24.co.za/resources/02a2-1fe462ea0452-267071f088f1-1000/format/inline/gordie_howe_international_bridge.jpeg"](https://news24cobalt.24.co.za/resources/02a2-1fe462ea0452-267071f088f1-1000/format/inline/gordie_howe_international_bridge.jpeg),
        *   "publishedAt": "2026-02-10T12:55:27",
        *   "content": "<ul><li>US President Donald Trump threatened to stop the opening of a bridge linking Ontario with Michigan.</li><li>The Gordie Howe International Bridge is set to open in 2026 and was financed by Can… [+5164 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "financial-post",
            *   "name": "Financial Post"

},
        *   "author": "Bloomberg News",
        *   "title": "Trump threatens to block new Detroit-Windsor bridge in new row",
        *   "description": "U.S. President Donald Trump is threatening to block a new bridge that connects Michigan and Ontario until the U.S. Read more.",
        *   "url": ["https://financialpost.com/news/trump-threatens-block-detroit-canada-bridge-new-trade-row"](https://financialpost.com/news/trump-threatens-block-detroit-canada-bridge-new-trade-row),
        *   "urlToImage": ["https://smartcdn.gprod.postmedia.digital/financialpost/wp-content/uploads/2026/02/0211-bc-howe-.jpg"](https://smartcdn.gprod.postmedia.digital/financialpost/wp-content/uploads/2026/02/0211-bc-howe-.jpg),
        *   "publishedAt": "2026-02-10T12:52:16.3567072Z",
        *   "content": "U.S. President Donald Trump said he would start negotiations with Canada over a new bridge that connects Michigan and Ontario, threatening to block its opening until the U.S. was given compensation a… [+5349 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "nbc-news",
            *   "name": "NBC News"

},
        *   "author": "NBC News",
        *   "title": "Trump administration live updates: Key senators say they won't support short-term DHS spending bill",
        *   "description": "Trump administration live updates: Key senators say they won't support short-term DHS spending bill",
        *   "url": ["https://www.nbcnews.com/politics/trump-administration/live-blog/trump-congress-ice-dhs-shutdown-elections-epstein-files-live-updates-rcna257950"](https://www.nbcnews.com/politics/trump-administration/live-blog/trump-congress-ice-dhs-shutdown-elections-epstein-files-live-updates-rcna257950),
        *   "urlToImage": ["https://media-cldnry.s-nbcnews.com/image/upload/t_nbcnews-fp-1200-630,f_auto,q_auto:best/rockcms/2026-02/260207-trump-ch-1614-e49920.jpg"](https://media-cldnry.s-nbcnews.com/image/upload/t_nbcnews-fp-1200-630,f_auto,q_auto:best/rockcms/2026-02/260207-trump-ch-1614-e49920.jpg),
        *   "publishedAt": "2026-02-10T12:37:35Z",
        *   "content": "Americans are souring on the Trump administrations immigration crackdown, complicating an already messy dynamic on Capitol Hill as emboldened Democrats draw a hard line against another short-term fun… [+886 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "newsweek",
            *   "name": "Newsweek"

},
        *   "author": "James Rushton",
        *   "title": "Student Loan Payment Could Triple Under New Trump Rules—Here’s When",
        *   "description": "Millions of federal student loan borrowers could soon face higher payments as the Education Department moves to implement new regulations.",
        *   "url": ["https://www.newsweek.com/student-loan-repayments-2026-rap-11495017"](https://www.newsweek.com/student-loan-repayments-2026-rap-11495017),
        *   "urlToImage": ["https://assets.newsweek.com/wp-content/uploads/2026/02/GettyImages-2243388337.jpg?w=1200crop=1"](https://assets.newsweek.com/wp-content/uploads/2026/02/GettyImages-2243388337.jpg?w=1200crop=1),
        *   "publishedAt": "2026-02-10T12:35:31Z",
        *   "content": "Millions of federal student loan borrowers could soon face higher monthly payments as the Education Department moves to implement new repayment regulations tied to last summer's Republican-led overha… [+4692 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "newsweek",
            *   "name": "Newsweek"

},
        *   "author": "Sam Stevenson",
        *   "title": "Donald Trump’s Disapproval Rating Breaks New Record",
        *   "description": "President hits another unwelcome milestone as his polling sinks further, marking a new low in public support.",
        *   "url": ["https://www.newsweek.com/donald-trump-approval-rating-record-nate-silver-11495027"](https://www.newsweek.com/donald-trump-approval-rating-record-nate-silver-11495027),
        *   "urlToImage": ["https://assets.newsweek.com/wp-content/uploads/2026/02/GettyImages-2260131051.jpg?w=1200crop=1"](https://assets.newsweek.com/wp-content/uploads/2026/02/GettyImages-2260131051.jpg?w=1200crop=1),
        *   "publishedAt": "2026-02-10T12:28:16Z",
        *   "content": "Donald Trumps disapproval rating has reached a new high this week, according to fresh analysis from polling aggregator the Silver Bulletin.\r\nIt comes despite his overall approval appearing to have st… [+3819 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "associated-press",
            *   "name": "Associated Press"

},
        *   "author": "Rebecca Santana",
        *   "title": "Trump's immigration chiefs are set to testify in Congress",
        *   "description": "The heads of agencies enforcing President Donald Trump's immigration agenda are set to testify before Congress. This comes amid scrutiny over the shooting deaths of two protesters in Minneapolis by Homeland Security officers. Todd Lyons of Immigration and Cus…",
        *   "url": ["https://apnews.com/article/immigration-customs-enforcement-border-patrol-trump-congress-1fa0cc0c9297479fcc02b1dc5a706d37"](https://apnews.com/article/immigration-customs-enforcement-border-patrol-trump-congress-1fa0cc0c9297479fcc02b1dc5a706d37),
        *   "urlToImage": ["https://dims.apnews.com/dims4/default/92fefb5/2147483647/strip/true/crop/3000x1999+0+1/resize/980x653!/quality/90/?url=https%3A%2F%2Fassets.apnews.com%2F6e%2F63%2F310a95a22bd7e458f4394602dfee%2F4ee27af1affe42aea8264eca07eb06ee"](https://dims.apnews.com/dims4/default/92fefb5/2147483647/strip/true/crop/3000x1999+0+1/resize/980x653!/quality/90/?url=https%3A%2F%2Fassets.apnews.com%2F6e%2F63%2F310a95a22bd7e458f4394602dfee%2F4ee27af1affe42aea8264eca07eb06ee),
        *   "publishedAt": "2026-02-10T12:02:54Z",
        *   "content": "WASHINGTON (AP) The heads of the agencies carrying out President Donald Trumps mass deportation agenda will testify in Congress Tuesday and face questions over how they are prosecuting immigration en… [+3328 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "the-huffington-post",
            *   "name": "The Huffington Post"

},
        *   "author": null,
        *   "title": "GOP Rep Has Probably The Most Outrageous Reaction To Bad Bunny Super Bowl Show",
        *   "description": "The right-wing congressman made Trump's criticism look tame.",
        *   "url": ["https://www.huffpost.com/entry/andy-ogles-bad-bunny-gay-pornography_n_698b06b5e4b0073b47aa4340"](https://www.huffpost.com/entry/andy-ogles-bad-bunny-gay-pornography_n_698b06b5e4b0073b47aa4340),
        *   "urlToImage": ["https://img.huffingtonpost.com/asset/698b0d6d1b00001b6c6ff36c.jpeg?cache=ruVHxlzbzC&ops=500_281%2Cscalefit_1200_630"](https://img.huffingtonpost.com/asset/698b0d6d1b00001b6c6ff36c.jpeg?cache=ruVHxlzbzC&ops=500_281%2Cscalefit_1200_630),
        *   "publishedAt": "2026-02-10T11:46:04Z",
        *   "content": "Of all theconservativeoutrage at Bad Bunnys Super Bowl halftime show, Rep. Andy Ogles (R-Tenn.) may have topped them all.\r\nOn Monday the Tennessee congressman branded the performance gay pornography … [+2227 chars]"

},
    *   -

{
        *   -

"source": {
            *   "id": "the-washington-post",
            *   "name": "The Washington Post"

},
        *   "author": "Victoria Craw",
        *   "title": "Trump threatens to block opening of bridge between U.S. and Canada",
        *   "description": "As the Gordie Howe bridge neared its completion, Trump, in his latest salvo against Canada, suggested he would “not allow” it to open, saying Canada had treated the U.S. “very unfairly.”",
        *   "url": ["https://www.washingtonpost.com/politics/2026/02/10/trump-us-canada-michigan-ontario-bridge/"](https://www.washingtonpost.com/politics/2026/02/10/trump-us-canada-michigan-ontario-bridge/),
        *   "urlToImage": ["https://www.washingtonpost.com/wp-apps/imrs.php?src=https://arc-anglerfish-washpost-prod-washpost.s3.amazonaws.com/public/MLVYZYF3TRB4SYRYRUVLAARJQU.JPG&w=1440"](https://www.washingtonpost.com/wp-apps/imrs.php?src=https://arc-anglerfish-washpost-prod-washpost.s3.amazonaws.com/public/MLVYZYF3TRB4SYRYRUVLAARJQU.JPG&w=1440),
        *   "publishedAt": "2026-02-10T11:38:16Z",
        *   "content": "As the Gordie Howe bridge neared its completion, Trump, in his latest salvo against Canada, suggested he would not allow it to open, saying Canada had treated the U.S. very unfairly.\r\nFebruary 10, 20… [+31 chars]"

},
