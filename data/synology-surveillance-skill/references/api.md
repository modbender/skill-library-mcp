# Synology Surveillance Station API Reference

Offizielle API-Dokumentation: https://global.download.synology.com/download/Document/Software/DeveloperGuide/Package/SurveillanceStation/All/enu/SurveillanceStation_Web_API.pdf

## Basis-URL

```
http://<NAS-IP>:<PORT>/webapi/
```

Standard-Ports:
- HTTP: 5000
- HTTPS: 5001

## Authentifizierung

### Login
```
GET /webapi/auth.cgi
  ?api=SYNO.API.Auth
  &method=login
  &version=3
  &account=<user>
  &passwd=<pass>
  &session=SurveillanceStation
  &format=cookie
```

Response:
```json
{
  "success": true,
  "data": {
    "sid": "SESSION_ID"
  }
}
```

### Logout
```
GET /webapi/auth.cgi
  ?api=SYNO.API.Auth
  &method=logout
  &version=1
  &session=SurveillanceStation
```

## Kamera-API

### Kamera-Liste abrufen
```
GET /webapi/entry.cgi
  ?api=SYNO.SurveillanceStation.Camera
  &method=List
  &version=1
  &_=<timestamp>
```

### Snapshot erstellen
```
GET /webapi/entry.cgi
  ?api=SYNO.SurveillanceStation.Camera
  &method=GetSnapshot
  &version=1
  &cameraId=<ID>
  &_=<timestamp>
```

### Live-Stream URL
```
GET /webapi/entry.cgi
  ?api=SYNO.SurveillanceStation.Streaming
  &method=LiveStream
  &version=1
  &cameraId=<ID>
  &format=mjpeg|hls|mxpeg
```

## Ereignis-API

### Ereignisse abrufen
```
GET /webapi/entry.cgi
  ?api=SYNO.SurveillanceStation.Event
  &method=List
  &version=1
  &timeStart=<unix_timestamp>
  &timeEnd=<unix_timestamp>
  &limit=<count>
```

### Letzte Ereignisse
```
GET /webapi/entry.cgi
  ?api=SYNO.SurveillanceStation.Event
  &method=List
  &version=1
  &limit=10
```

## Aufnahme-API

### Aufnahme starten
```
GET /webapi/entry.cgi
  ?api=SYNO.SurveillanceStation.Recording
  &method=Record
  &version=1
  &cameraId=<ID>
```

### Aufnahme stoppen
```
GET /webapi/entry.cgi
  ?api=SYNO.SurveillanceStation.Recording
  &method=Stop
  &version=1
  &cameraId=<ID>
```

## PTZ-API (für bewegliche Kameras)

### PTZ Steuerung
```
GET /webapi/entry.cgi
  ?api=SYNO.SurveillanceStation.PTZ
  &method=Move
  &version=1
  &cameraId=<ID>
  &direction=left|right|up|down|zoomin|zoomout
  &speed=<1-5>
```

### Voreinstellung anfahren
```
GET /webapi/entry.cgi
  ?api=SYNO.SurveillanceStation.PTZ
  &method=GoPreset
  &version=1
  &cameraId=<ID>
  &position=<1-100>
```

## Fehler-Codes

| Code | Beschreibung |
|------|--------------|
| 100 | Unknown error |
| 101 | Invalid parameters |
| 102 | API does not exist |
| 103 | Method does not exist |
| 104 | This API version is not supported |
| 105 | Insufficient user privilege |
| 106 | Connection time out |
| 107 | Multiple login detected |
| 400 | Invalid credential |
| 401 | Account disabled |
| 402 | Permission denied |
| 403 | 2-step verification needed |

## Hinweise

- Session-Cookie `id` nach Login speichern
- Bei jeder Anfrage Session-Cookie mitgeben
- 2FA muss für den API-User deaktiviert sein
- HTTPS empfohlen für produktive Umgebungen
