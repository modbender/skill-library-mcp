BEGIN;
CREATE TABLE IF NOT EXISTS bazi_daily_calendar (
  date TEXT PRIMARY KEY,
  flow_year TEXT NOT NULL,
  flow_month TEXT NOT NULL,
  flow_day TEXT NOT NULL,
  source TEXT,
  updated_at TEXT
);
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-03', '丙午', '庚寅', '丙子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-04', '丙午', '庚寅', '丁丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-05', '丙午', '辛卯', '戊寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-06', '丙午', '辛卯', '己卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-07', '丙午', '辛卯', '庚辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-08', '丙午', '辛卯', '辛巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-09', '丙午', '辛卯', '壬午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-10', '丙午', '辛卯', '癸未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-11', '丙午', '辛卯', '甲申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-12', '丙午', '辛卯', '乙酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-13', '丙午', '辛卯', '丙戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-14', '丙午', '辛卯', '丁亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-15', '丙午', '辛卯', '戊子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-16', '丙午', '辛卯', '己丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-17', '丙午', '辛卯', '庚寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-18', '丙午', '辛卯', '辛卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-19', '丙午', '辛卯', '壬辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-20', '丙午', '辛卯', '癸巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-21', '丙午', '辛卯', '甲午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-22', '丙午', '辛卯', '乙未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-23', '丙午', '辛卯', '丙申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-24', '丙午', '辛卯', '丁酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-25', '丙午', '辛卯', '戊戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-26', '丙午', '辛卯', '己亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-27', '丙午', '辛卯', '庚子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-28', '丙午', '辛卯', '辛丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-29', '丙午', '辛卯', '壬寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-30', '丙午', '辛卯', '癸卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-03-31', '丙午', '辛卯', '甲辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-01', '丙午', '辛卯', '乙巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-02', '丙午', '辛卯', '丙午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-03', '丙午', '辛卯', '丁未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-04', '丙午', '辛卯', '戊申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-05', '丙午', '壬辰', '己酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-06', '丙午', '壬辰', '庚戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-07', '丙午', '壬辰', '辛亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-08', '丙午', '壬辰', '壬子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-09', '丙午', '壬辰', '癸丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-10', '丙午', '壬辰', '甲寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-11', '丙午', '壬辰', '乙卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-12', '丙午', '壬辰', '丙辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-13', '丙午', '壬辰', '丁巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-14', '丙午', '壬辰', '戊午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-15', '丙午', '壬辰', '己未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-16', '丙午', '壬辰', '庚申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-17', '丙午', '壬辰', '辛酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-18', '丙午', '壬辰', '壬戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-19', '丙午', '壬辰', '癸亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-20', '丙午', '壬辰', '甲子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-21', '丙午', '壬辰', '乙丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-22', '丙午', '壬辰', '丙寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-23', '丙午', '壬辰', '丁卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-24', '丙午', '壬辰', '戊辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-25', '丙午', '壬辰', '己巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-26', '丙午', '壬辰', '庚午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-27', '丙午', '壬辰', '辛未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-28', '丙午', '壬辰', '壬申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-29', '丙午', '壬辰', '癸酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-04-30', '丙午', '壬辰', '甲戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-01', '丙午', '壬辰', '乙亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-02', '丙午', '壬辰', '丙子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-03', '丙午', '壬辰', '丁丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-04', '丙午', '壬辰', '戊寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-05', '丙午', '癸巳', '己卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-06', '丙午', '癸巳', '庚辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-07', '丙午', '癸巳', '辛巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-08', '丙午', '癸巳', '壬午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-09', '丙午', '癸巳', '癸未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-10', '丙午', '癸巳', '甲申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-11', '丙午', '癸巳', '乙酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-12', '丙午', '癸巳', '丙戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-13', '丙午', '癸巳', '丁亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-14', '丙午', '癸巳', '戊子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-15', '丙午', '癸巳', '己丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-16', '丙午', '癸巳', '庚寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-17', '丙午', '癸巳', '辛卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-18', '丙午', '癸巳', '壬辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-19', '丙午', '癸巳', '癸巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-20', '丙午', '癸巳', '甲午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-21', '丙午', '癸巳', '乙未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-22', '丙午', '癸巳', '丙申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-23', '丙午', '癸巳', '丁酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-24', '丙午', '癸巳', '戊戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-25', '丙午', '癸巳', '己亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-26', '丙午', '癸巳', '庚子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-27', '丙午', '癸巳', '辛丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-28', '丙午', '癸巳', '壬寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-29', '丙午', '癸巳', '癸卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-30', '丙午', '癸巳', '甲辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-05-31', '丙午', '癸巳', '乙巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-01', '丙午', '癸巳', '丙午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-02', '丙午', '癸巳', '丁未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-03', '丙午', '癸巳', '戊申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-04', '丙午', '癸巳', '己酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-05', '丙午', '甲午', '庚戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-06', '丙午', '甲午', '辛亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-07', '丙午', '甲午', '壬子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-08', '丙午', '甲午', '癸丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-09', '丙午', '甲午', '甲寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-10', '丙午', '甲午', '乙卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-11', '丙午', '甲午', '丙辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-12', '丙午', '甲午', '丁巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-13', '丙午', '甲午', '戊午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-14', '丙午', '甲午', '己未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-15', '丙午', '甲午', '庚申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-16', '丙午', '甲午', '辛酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-17', '丙午', '甲午', '壬戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-18', '丙午', '甲午', '癸亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-19', '丙午', '甲午', '甲子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-20', '丙午', '甲午', '乙丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-21', '丙午', '甲午', '丙寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-22', '丙午', '甲午', '丁卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-23', '丙午', '甲午', '戊辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-24', '丙午', '甲午', '己巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-25', '丙午', '甲午', '庚午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-26', '丙午', '甲午', '辛未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-27', '丙午', '甲午', '壬申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-28', '丙午', '甲午', '癸酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-29', '丙午', '甲午', '甲戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-06-30', '丙午', '甲午', '乙亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-01', '丙午', '甲午', '丙子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-02', '丙午', '甲午', '丁丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-03', '丙午', '甲午', '戊寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-04', '丙午', '甲午', '己卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-05', '丙午', '甲午', '庚辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-06', '丙午', '甲午', '辛巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-07', '丙午', '乙未', '壬午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-08', '丙午', '乙未', '癸未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-09', '丙午', '乙未', '甲申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-10', '丙午', '乙未', '乙酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-11', '丙午', '乙未', '丙戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-12', '丙午', '乙未', '丁亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-13', '丙午', '乙未', '戊子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-14', '丙午', '乙未', '己丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-15', '丙午', '乙未', '庚寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-16', '丙午', '乙未', '辛卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-17', '丙午', '乙未', '壬辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-18', '丙午', '乙未', '癸巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-19', '丙午', '乙未', '甲午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-20', '丙午', '乙未', '乙未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-21', '丙午', '乙未', '丙申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-22', '丙午', '乙未', '丁酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-23', '丙午', '乙未', '戊戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-24', '丙午', '乙未', '己亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-25', '丙午', '乙未', '庚子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-26', '丙午', '乙未', '辛丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-27', '丙午', '乙未', '壬寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-28', '丙午', '乙未', '癸卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-29', '丙午', '乙未', '甲辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-30', '丙午', '乙未', '乙巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-07-31', '丙午', '乙未', '丙午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-01', '丙午', '乙未', '丁未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-02', '丙午', '乙未', '戊申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-03', '丙午', '乙未', '己酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-04', '丙午', '乙未', '庚戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-05', '丙午', '乙未', '辛亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-06', '丙午', '乙未', '壬子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-07', '丙午', '丙申', '癸丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-08', '丙午', '丙申', '甲寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-09', '丙午', '丙申', '乙卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-10', '丙午', '丙申', '丙辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-11', '丙午', '丙申', '丁巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-12', '丙午', '丙申', '戊午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-13', '丙午', '丙申', '己未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-14', '丙午', '丙申', '庚申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-15', '丙午', '丙申', '辛酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-16', '丙午', '丙申', '壬戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-17', '丙午', '丙申', '癸亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-18', '丙午', '丙申', '甲子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-19', '丙午', '丙申', '乙丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-20', '丙午', '丙申', '丙寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-21', '丙午', '丙申', '丁卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-22', '丙午', '丙申', '戊辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-23', '丙午', '丙申', '己巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-24', '丙午', '丙申', '庚午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-25', '丙午', '丙申', '辛未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-26', '丙午', '丙申', '壬申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-27', '丙午', '丙申', '癸酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-28', '丙午', '丙申', '甲戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-29', '丙午', '丙申', '乙亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-30', '丙午', '丙申', '丙子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-08-31', '丙午', '丙申', '丁丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-01', '丙午', '丙申', '戊寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-02', '丙午', '丙申', '己卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-03', '丙午', '丙申', '庚辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-04', '丙午', '丙申', '辛巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-05', '丙午', '丙申', '壬午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-06', '丙午', '丙申', '癸未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-07', '丙午', '丁酉', '甲申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-08', '丙午', '丁酉', '乙酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-09', '丙午', '丁酉', '丙戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-10', '丙午', '丁酉', '丁亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-11', '丙午', '丁酉', '戊子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-12', '丙午', '丁酉', '己丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-13', '丙午', '丁酉', '庚寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-14', '丙午', '丁酉', '辛卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-15', '丙午', '丁酉', '壬辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-16', '丙午', '丁酉', '癸巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-17', '丙午', '丁酉', '甲午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-18', '丙午', '丁酉', '乙未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-19', '丙午', '丁酉', '丙申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-20', '丙午', '丁酉', '丁酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-21', '丙午', '丁酉', '戊戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-22', '丙午', '丁酉', '己亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-23', '丙午', '丁酉', '庚子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-24', '丙午', '丁酉', '辛丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-25', '丙午', '丁酉', '壬寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-26', '丙午', '丁酉', '癸卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-27', '丙午', '丁酉', '甲辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-28', '丙午', '丁酉', '乙巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-29', '丙午', '丁酉', '丙午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-09-30', '丙午', '丁酉', '丁未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-01', '丙午', '丁酉', '戊申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-02', '丙午', '丁酉', '己酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-03', '丙午', '丁酉', '庚戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-04', '丙午', '丁酉', '辛亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-05', '丙午', '丁酉', '壬子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-06', '丙午', '丁酉', '癸丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-07', '丙午', '丁酉', '甲寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-08', '丙午', '戊戌', '乙卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-09', '丙午', '戊戌', '丙辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-10', '丙午', '戊戌', '丁巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-11', '丙午', '戊戌', '戊午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-12', '丙午', '戊戌', '己未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-13', '丙午', '戊戌', '庚申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-14', '丙午', '戊戌', '辛酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-15', '丙午', '戊戌', '壬戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-16', '丙午', '戊戌', '癸亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-17', '丙午', '戊戌', '甲子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-18', '丙午', '戊戌', '乙丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-19', '丙午', '戊戌', '丙寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-20', '丙午', '戊戌', '丁卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-21', '丙午', '戊戌', '戊辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-22', '丙午', '戊戌', '己巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-23', '丙午', '戊戌', '庚午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-24', '丙午', '戊戌', '辛未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-25', '丙午', '戊戌', '壬申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-26', '丙午', '戊戌', '癸酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-27', '丙午', '戊戌', '甲戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-28', '丙午', '戊戌', '乙亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-29', '丙午', '戊戌', '丙子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-30', '丙午', '戊戌', '丁丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-10-31', '丙午', '戊戌', '戊寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-01', '丙午', '戊戌', '己卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-02', '丙午', '戊戌', '庚辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-03', '丙午', '戊戌', '辛巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-04', '丙午', '戊戌', '壬午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-05', '丙午', '戊戌', '癸未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-06', '丙午', '戊戌', '甲申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-07', '丙午', '己亥', '乙酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-08', '丙午', '己亥', '丙戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-09', '丙午', '己亥', '丁亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-10', '丙午', '己亥', '戊子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-11', '丙午', '己亥', '己丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-12', '丙午', '己亥', '庚寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-13', '丙午', '己亥', '辛卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-14', '丙午', '己亥', '壬辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-15', '丙午', '己亥', '癸巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-16', '丙午', '己亥', '甲午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-17', '丙午', '己亥', '乙未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-18', '丙午', '己亥', '丙申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-19', '丙午', '己亥', '丁酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-20', '丙午', '己亥', '戊戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-21', '丙午', '己亥', '己亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-22', '丙午', '己亥', '庚子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-23', '丙午', '己亥', '辛丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-24', '丙午', '己亥', '壬寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-25', '丙午', '己亥', '癸卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-26', '丙午', '己亥', '甲辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-27', '丙午', '己亥', '乙巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-28', '丙午', '己亥', '丙午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-29', '丙午', '己亥', '丁未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-11-30', '丙午', '己亥', '戊申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-01', '丙午', '己亥', '己酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-02', '丙午', '己亥', '庚戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-03', '丙午', '己亥', '辛亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-04', '丙午', '己亥', '壬子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-05', '丙午', '己亥', '癸丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-06', '丙午', '己亥', '甲寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-07', '丙午', '庚子', '乙卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-08', '丙午', '庚子', '丙辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-09', '丙午', '庚子', '丁巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-10', '丙午', '庚子', '戊午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-11', '丙午', '庚子', '己未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-12', '丙午', '庚子', '庚申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-13', '丙午', '庚子', '辛酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-14', '丙午', '庚子', '壬戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-15', '丙午', '庚子', '癸亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-16', '丙午', '庚子', '甲子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-17', '丙午', '庚子', '乙丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-18', '丙午', '庚子', '丙寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-19', '丙午', '庚子', '丁卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-20', '丙午', '庚子', '戊辰', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-21', '丙午', '庚子', '己巳', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-22', '丙午', '庚子', '庚午', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-23', '丙午', '庚子', '辛未', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-24', '丙午', '庚子', '壬申', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-25', '丙午', '庚子', '癸酉', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-26', '丙午', '庚子', '甲戌', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-27', '丙午', '庚子', '乙亥', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-28', '丙午', '庚子', '丙子', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-29', '丙午', '庚子', '丁丑', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-30', '丙午', '庚子', '戊寅', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
INSERT INTO bazi_daily_calendar (date, flow_year, flow_month, flow_day, source, updated_at)
VALUES ('2026-12-31', '丙午', '庚子', '己卯', 'xlsx_2026', '2026-03-03T06:53:15.744273+00:00')
ON CONFLICT(date) DO UPDATE SET
  flow_year=excluded.flow_year,
  flow_month=excluded.flow_month,
  flow_day=excluded.flow_day,
  source=excluded.source,
  updated_at=excluded.updated_at;
COMMIT;
