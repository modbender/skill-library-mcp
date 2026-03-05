#!/usr/bin/env node
/**
 * News fetcher - grouped by topic, output as simple list
 */

const puppeteer = require('puppeteer');

// Blacklist
const BLACKLIST = new Set([
    "sport", "sportlich", "sports",
    "trump", "usa", "vereinigte staaten",
    "spd", "sozialdemokrat",
    "iran",
    "bürgergeld", "buergergeld",
    "mietreform", "miet-reform", "mieterschutz",
    "regenpause",
    "ukraine", "ukrainisch",
    "putin", "russland",
    "epstein", "jeffrey epstein",
    "bilder des tages", "bild des tages",
    "karrierefrage", "karriere frage",
    "streik", "streiks", "streikende",
    "ivanti",
    "fortinet",
    "solarwinds"
]);

// Navigation patterns to exclude
const NAV_PATTERNS = [
    /^\/(thema|rubrik|kategorie|section|archive|archiv|alle|index|startseite)/i,
    /\/abo|\/subscribe|\/login|\/newsletter/i,
    /wetter|horoskop|unterhaltung/i,
    /stellenmarkt|jobs?-|karriere/i
];

// News sources
const SOURCES = {
    Allgemeines: [
        { name: "Tagesschau", url: "https://www.tagesschau.de/" },
        { name: "FAZ", url: "https://www.faz.net/aktuell/" },
        { name: "WiWo", url: "https://www.wiwo.de/" },
        { name: "Süddeutsche", url: "https://www.sueddeutsche.de/" },
        { name: "Spiegel", url: "https://www.spiegel.de/" },
        { name: "Mittelbayerische", url: "https://www.mittelbayerische.de/lokales/stadt-regensburg" },
    ],
    IT: [
        { name: "Heise", url: "https://www.heise.de/" },
        { name: "Golem", url: "https://www.golem.de/" },
        { name: "Slashdot", url: "https://slashdot.org/" },
    ],
    Cybersecurity: [
        { name: "The Hacker News", url: "https://thehackernews.com/" },
        { name: "BleepingComputer", url: "https://www.bleepingcomputer.com/" },
        { name: "Logbuch Netzpolitik", url: "https://logbuch-netzpolitik.de/" },
    ]
};

function isFiltered(text) {
    if (!text) return true;
    const lower = text.toLowerCase();
    for (const word of BLACKLIST) {
        if (lower.includes(word)) return true;
    }
    return false;
}

function isNavigation(url, title) {
    for (const pattern of NAV_PATTERNS) {
        if (pattern.test(url)) return true;
    }
    const genericTitles = ['startseite', 'alle nachrichten', 'neueste nachrichten' ];
    if (genericTitles.includes(title.toLowerCase())) return true;
    return false;
}

async function fetchSource(url, sourceName) {
    let browser = null;
    try {
        browser = await puppeteer.launch({
            headless: true,
            executablePath: '/usr/bin/chromium',
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        });
        
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 800 });
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
        
        const headlines = await page.evaluate(() => {
            const links = [];
            document.querySelectorAll('a').forEach(a => {
                const href = a.getAttribute('href');
                const text = a.innerText.trim();
                if (href && text && text.length > 25 && text.length < 180) {
                    links.push({ href, text });
                }
            });
            return links;
        });
        
        const articles = [];
        for (const h of headlines) {
            if (isNavigation(h.href, h.text)) continue;
            if (isFiltered(h.text) || isFiltered(h.href)) continue;
            
            let fullUrl = h.href;
            try {
                if (h.href.startsWith('/')) {
                    fullUrl = new URL(h.href, url).href;
                } else if (h.href.startsWith('http')) {
                    fullUrl = h.href;
                } else {
                    continue;
                }
            } catch (e) {
                continue;
            }
            
            articles.push({
                title: h.text,
                url: fullUrl,
                source: sourceName
            });
        }
        
        return articles.slice(0, 10);
        
    } catch (error) {
        console.error(`  [Error ${sourceName}: ${error.message}]`);
        return [];
    } finally {
        if (browser) await browser.close();
    }
}

function extractKeywords(title) {
    const lower = title.toLowerCase();
    const keywords = new Set();
    
    // Key topics
    const topics = {
        'afd': ['afd', 'generation deutschland', 'alternative für deutschland'],
        'bsw': ['bsw', 'bündnis sahra wagenknecht', 'sahra wagenknecht'],
        'ampel': ['ampel', 'ampelkoalition'],
        'migration': ['migration', 'asyl', 'flüchtlinge', 'grenz'],
        'wirtschaft': ['wirtschaft', 'wirtschaftswachstum', 'bruttoinlandsprodukt'],
        'energie': ['energie', 'strom', 'gas', 'energiekrise', 'erneuerbar'],
        'klima': ['klima', 'klimawandel', 'co2', 'temperaturanstieg'],
        'israel': ['israel', 'gaza', 'palästina', 'nahost', 'herzog'],
        'china': ['china', 'chinesisch', 'peking'],
        'europa': ['europa', 'europäische union', 'eu', 'brüssel'],
        'bahn': ['bahn', 'zug', 'deutsche bahn'],
        'gesundheit': ['gesundheit', 'krankenhaus', 'ärzte', 'pflege'],
        'rente': ['rente', 'altersrente'],
        'bildung': ['bildung', 'schule', 'universität', 'studium'],
        'digital': ['digital', 'ki', 'kuenstliche intelligenz', 'ai'],
        'cybersecurity': ['cybersecurity', 'cyber', 'hack', 'sicherheitslücke', 'cve'],
        'bitcoin': ['bitcoin', 'crypto', 'kryptowährung'],
        'immobilien': ['immobilien', 'immobilienmarkt', 'miete', 'wohnung'],
        'elektromobilitaet': ['elektromobil', 'e-auto', 'elektroauto', 'ev'],
        'sozialstaat': ['sozialstaat', 'sozialleistungen', 'bürgergeld']
    };
    
    for (const [topic, topicKeywords] of Object.entries(topics)) {
        for (const kw of topicKeywords) {
            if (lower.includes(kw)) {
                keywords.add(topic);
                break;
            }
        }
    }
    
    // Add significant words
    const stopWords = new Set(['und', 'die', 'der', 'das', 'für', 'auf', 'von', 'aus', 'mit', 'bei', 'nach', 'wie', 'was', 'auch', 'nur', 'noch', 'sich', 'nicht', 'über', 'zum', 'zur', 'den', 'dem', 'ein', 'eine', 'einer', 'einem', 'einen', 'ist', 'war', 'wird', 'wurden', 'wurde', 'hat', 'haben', 'hatte', 'hatten', 'kann', 'können', 'konnte', 'konnten', 'muss', 'müssen', 'musste', 'mussten', 'soll', 'sollen', 'sollte', 'sollten', 'will', 'wollen', 'wollte', 'wollten', 'darf', 'dürfen', 'durfte', 'durften', 'mag', 'mögen', 'mochte', 'mochten', 'trotz', 'wegen', 'ins', 'ans', 'beim', 'unter', 'gegen', 'zwischen', 'heute', 'gestern', 'morgen', 'jetzt', 'schon', 'immer', 'wieder', 'erst', 'mehr', 'viel', 'wenig', 'alle', 'alles', 'jeder', 'jede', 'jedes', 'niemand', 'jemand', 'etwas', 'nichts', 'kein', 'keine', 'keiner', 'keinem', 'keinen', 'neue', 'neuen', 'neuer', 'neues', 'erste', 'ersten', 'zweite', 'dritte', 'welt', 'land', 'frage', 'antwort', 'jahre', 'jahren', 'tag', 'tagen', 'monat', 'monate', 'politik', 'politikern', 'parteien', 'politik', 'politik', 'video', 'livestream', 'ard', 'faz', 'wiwo', 'süddeutsche', 'sz', 'pro', 'edition', 'epaper', 'digital', 'a+,', ' Sonntagszeitung', 'faz.net']);
    
    const words = lower.split(/\W+/).filter(w => w.length > 4 && !stopWords.has(w));
    words.slice(0, 5).forEach(w => keywords.add(w.slice(0, 10)));
    
    return Array.from(keywords);
}

function groupArticles(articles) {
    const groups = [];
    const used = new Set();
    
    for (let i = 0; i < articles.length; i++) {
        if (used.has(i)) continue;
        
        const a1 = articles[i];
        const kw1 = extractKeywords(a1.title);
        
        const group = {
            title: a1.title.length > 70 ? a1.title.slice(0, 70) + '...' : a1.title,
            keywords: kw1,
            links: [{ source: a1.source, url: a1.url }]
        };
        
        for (let j = i + 1; j < articles.length; j++) {
            if (used.has(j)) continue;
            
            const a2 = articles[j];
            // Skip same source
            if (a2.source === a1.source) continue;
            
            const kw2 = extractKeywords(a2.title);
            
            // Calculate similarity
            const set1 = new Set(kw1);
            const set2 = new Set(kw2);
            const intersection = [...set1].filter(x => set2.has(x));
            const union = new Set([...set1, ...set2]);
            const similarity = union.size > 0 ? intersection.length / union.size : 0;
            
            if (similarity > 0.35) {
                used.add(j);
                group.links.push({ source: a2.source, url: a2.url });
                // Use shorter/better title
                if (a2.title.length < group.title.length && a2.title.length > 25) {
                    group.title = a2.title.length > 70 ? a2.title.slice(0, 70) + '...' : a2.title;
                }
            }
        }
        
        used.add(i);
        groups.push(group);
    }
    
    // Sort by number of links (multi-source first)
    groups.sort((a, b) => b.links.length - a.links.length);
    
    return groups;
}

async function fetchCategory(category, sources) {
    console.log(`\n${category}:`);
    
    let allArticles = [];
    for (const source of sources) {
        console.log(`  ${source.name}...`);
        const articles = await fetchSource(source.url, source.name);
        allArticles = allArticles.concat(articles);
    }
    
    if (allArticles.length === 0) {
        console.log("  (keine Artikel gefunden)");
        return;
    }
    
    const groups = groupArticles(allArticles);
    
    for (const group of groups.slice(0, 12)) {
        const links = group.links.map(l => `${l.url}`).join(' ');
        console.log(`- ${group.title} ${links}`);
    }
}

async function main() {
    const category = process.argv[2]?.toLowerCase();
    
    if (category && !SOURCES[category]) {
        console.log(`Usage: node fetcher.js [general|it|cybersecurity]`);
        console.log(`Categories: ${Object.keys(SOURCES).join(', ')}`);
        process.exit(1);
    }
    
    const categories = category ? [category] : Object.keys(SOURCES);
    
    for (const cat of categories) {
        await fetchCategory(cat, SOURCES[cat]);
    }
}

main().catch(console.error);
