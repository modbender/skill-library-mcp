#!/usr/bin/env python3
"""
기상청 격자좌표 변환 (위경도 ↔ 격자)
Lambert Conformal Conic (LCC) DFS 좌표계
"""

import math
import sys
import json

# 격자 변환 상수
RE = 6371.00877     # 지구 반경(km)
GRID = 5.0          # 격자 간격(km)
SLAT1 = 30.0        # 투영 위도1(degree)
SLAT2 = 60.0        # 투영 위도2(degree)
OLON = 126.0        # 기준점 경도(degree)
OLAT = 38.0         # 기준점 위도(degree)
XO = 43             # 기준점 X좌표(GRID)
YO = 136            # 기준점 Y좌표(GRID)

def latlon_to_grid(lat, lon):
    """위경도 → 기상청 격자좌표 변환"""
    DEGRAD = math.pi / 180.0
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD
    
    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    
    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn
    
    x = int(ra * math.sin(theta) + XO + 0.5)
    y = int(ro - ra * math.cos(theta) + YO + 0.5)
    
    return x, y

def grid_to_latlon(x, y):
    """기상청 격자좌표 → 위경도 변환"""
    DEGRAD = math.pi / 180.0
    RADDEG = 180.0 / math.pi
    
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD
    
    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    
    xn = x - XO
    yn = ro - y + YO
    ra = math.sqrt(xn * xn + yn * yn)
    if sn < 0.0:
        ra = -ra
    alat = math.pow((re * sf / ra), (1.0 / sn))
    alat = 2.0 * math.atan(alat) - math.pi * 0.5
    
    theta = 0.0
    if abs(xn) <= 0.0:
        theta = 0.0
    else:
        if abs(yn) <= 0.0:
            theta = math.pi * 0.5
            if xn < 0.0:
                theta = -theta
        else:
            theta = math.atan2(xn, yn)
    
    alon = theta / sn + olon
    lat = alat * RADDEG
    lon = alon * RADDEG
    
    return lat, lon

def main():
    if len(sys.argv) < 3:
        print("Usage: grid_convert.py <lat> <lon>  # 위경도 → 격자", file=sys.stderr)
        print("       grid_convert.py -r <nx> <ny>  # 격자 → 위경도", file=sys.stderr)
        sys.exit(1)
    
    if sys.argv[1] == '-r':
        # 역변환
        nx = int(sys.argv[2])
        ny = int(sys.argv[3])
        lat, lon = grid_to_latlon(nx, ny)
        result = {
            "nx": nx,
            "ny": ny,
            "lat": round(lat, 6),
            "lon": round(lon, 6)
        }
    else:
        # 정변환
        lat = float(sys.argv[1])
        lon = float(sys.argv[2])
        nx, ny = latlon_to_grid(lat, lon)
        result = {
            "lat": lat,
            "lon": lon,
            "nx": nx,
            "ny": ny
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
