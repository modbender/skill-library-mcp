#!/usr/bin/env python3
"""
Movie skill for OpenClaw.
基于极速数据电影影讯 API：
https://www.jisuapi.com/api/movie/
"""

import sys
import json
import os
import requests


MOVIE_ON_URL = "https://api.jisuapi.com/movie/on"
MOVIE_MOVIETHEATER_URL = "https://api.jisuapi.com/movie/movietheater"
MOVIE_THEATERMOVIE_URL = "https://api.jisuapi.com/movie/theatermovie"
MOVIE_DETAIL_URL = "https://api.jisuapi.com/movie/detail"
MOVIE_THEATER_URL = "https://api.jisuapi.com/movie/theater"
MOVIE_CITY_URL = "https://api.jisuapi.com/movie/city"


def _call_movie_api(url: str, appkey: str, params: dict | None = None):
    query = {"appkey": appkey}
    if params:
        for k, v in params.items():
            if v not in (None, ""):
                query[k] = v

    try:
        resp = requests.get(url, params=query, timeout=10)
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

    if resp.status_code != 200:
        return {
            "error": "http_error",
            "status_code": resp.status_code,
            "body": resp.text,
        }

    try:
        data = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

    if data.get("status") != 0:
        return {
            "error": "api_error",
            "code": data.get("status"),
            "message": data.get("msg"),
        }

    return data.get("result", {})


def movies_on(appkey: str, req: dict):
    """
    当前城市上映电影 /movie/on

    请求 JSON 示例：
    {
        "cityid": "382",
        "city": "杭州",
        "date": "2018-07-08"
    }
    cityid 和 city 至少需要提供一个。
    """
    cityid = req.get("cityid")
    city = req.get("city")
    if not cityid and not city:
        return {"error": "missing_param", "message": "cityid or city is required"}

    params = {
        "cityid": cityid,
        "city": city,
        "date": req.get("date"),
    }
    return _call_movie_api(MOVIE_ON_URL, appkey, params)


def movie_theaters_for_movie(appkey: str, req: dict):
    """
    电影放映的电影院 /movie/movietheater

    请求 JSON 示例：
    {
        "cityid": "382",
        "city": "杭州",
        "movieid": "137363",
        "date": "2018-07-08"
    }
    """
    movieid = req.get("movieid")
    if not movieid:
        return {"error": "missing_param", "message": "movieid is required"}

    cityid = req.get("cityid")
    city = req.get("city")
    if not cityid and not city:
        return {"error": "missing_param", "message": "cityid or city is required"}

    params = {
        "cityid": cityid,
        "city": city,
        "movieid": movieid,
        "date": req.get("date"),
    }
    return _call_movie_api(MOVIE_MOVIETHEATER_URL, appkey, params)


def movies_in_theater(appkey: str, req: dict):
    """
    电影院放映的电影 /movie/theatermovie

    请求 JSON 示例：
    {
        "theaterid": "2059",
        "date": "2018-07-08"
    }
    """
    theaterid = req.get("theaterid")
    if not theaterid:
        return {"error": "missing_param", "message": "theaterid is required"}

    params = {
        "theaterid": theaterid,
        "date": req.get("date"),
    }
    return _call_movie_api(MOVIE_THEATERMOVIE_URL, appkey, params)


def movie_detail(appkey: str, req: dict):
    """
    电影详情 /movie/detail

    请求 JSON 示例：
    {
        "movieid": "14",
        "moviename": "盗梦空间"
    }
    movieid 和 moviename 任填其一。
    """
    movieid = req.get("movieid")
    moviename = req.get("moviename")
    if not movieid and not moviename:
        return {"error": "missing_param", "message": "movieid or moviename is required"}

    params = {
        "movieid": movieid,
        "moviename": moviename,
    }
    return _call_movie_api(MOVIE_DETAIL_URL, appkey, params)


def theaters_in_city(appkey: str, req: dict):
    """
    按城市获取电影院 /movie/theater

    请求 JSON 示例：
    {
        "cityid": "382",
        "city": "杭州",
        "keyword": "万达"
    }
    """
    cityid = req.get("cityid")
    city = req.get("city")
    if not cityid and not city:
        return {"error": "missing_param", "message": "cityid or city is required"}

    params = {
        "cityid": cityid,
        "city": city,
        "keyword": req.get("keyword"),
    }
    return _call_movie_api(MOVIE_THEATER_URL, appkey, params)


def movie_cities(appkey: str, req: dict):
    """
    获取电影城市列表 /movie/city

    请求 JSON 示例：
    {
        "parentid": "0"
    }
    """
    params = {}
    if "parentid" in req and req["parentid"] not in (None, ""):
        params["parentid"] = req["parentid"]
    return _call_movie_api(MOVIE_CITY_URL, appkey, params)


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  movie.py on '{\"cityid\":\"382\",\"city\":\"杭州\",\"date\":\"2018-07-08\"}'          # 当前城市上映电影\n"
            "  movie.py movietheater '{\"cityid\":\"382\",\"city\":\"杭州\",\"movieid\":\"137363\",\"date\":\"2018-07-08\"}'  # 电影放映的电影院\n"
            "  movie.py theatermovie '{\"theaterid\":\"2059\",\"date\":\"2018-07-08\"}'             # 电影院放映的电影\n"
            "  movie.py detail '{\"movieid\":\"14\",\"moviename\":\"盗梦空间\"}'                     # 电影详情\n"
            "  movie.py theater '{\"cityid\":\"382\",\"city\":\"杭州\",\"keyword\":\"万达\"}'        # 按城市获取电影院\n"
            "  movie.py city '{\"parentid\":\"0\"}'                                              # 获取电影城市",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")

    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd not in ("on", "movietheater", "theatermovie", "detail", "theater", "city"):
        print(f"Error: unknown command '{cmd}'", file=sys.stderr)
        sys.exit(1)

    if cmd in ("on", "movietheater", "theatermovie", "detail", "theater", "city"):
        if len(sys.argv) < 3:
            print("Error: JSON body is required.", file=sys.stderr)
            sys.exit(1)
        raw = sys.argv[2]
        try:
            req = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        req = {}

    if cmd == "on":
        result = movies_on(appkey, req)
    elif cmd == "movietheater":
        result = movie_theaters_for_movie(appkey, req)
    elif cmd == "theatermovie":
        result = movies_in_theater(appkey, req)
    elif cmd == "detail":
        result = movie_detail(appkey, req)
    elif cmd == "theater":
        result = theaters_in_city(appkey, req)
    elif cmd == "city":
        result = movie_cities(appkey, req)
    else:
        # 理论上不会走到这里
        print(f"Error: unhandled command '{cmd}'", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

