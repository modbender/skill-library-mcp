"""list_folders.py — Lista todas las etiquetas/carpetas de Gmail"""
import json
from googleapiclient.discovery import build
from auth import authenticate

if __name__ == "__main__":
    svc = build("gmail","v1",credentials=authenticate())
    labels = svc.users().labels().list(userId="me").execute().get("labels",[])
    result = sorted([{"id":l["id"],"name":l["name"],"type":l.get("type","user"),
                      "total":l.get("messagesTotal",0),"unread":l.get("messagesUnread",0)}
                     for l in labels], key=lambda x:(x["type"]!="system",x["name"]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
