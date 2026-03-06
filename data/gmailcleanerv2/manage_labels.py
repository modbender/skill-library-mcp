"""manage_labels.py — Crea, renombra, elimina etiquetas de Gmail"""
import json, argparse
from googleapiclient.discovery import build
from auth import authenticate

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--action",required=True,choices=["create","rename","delete","list"])
    p.add_argument("--name"); p.add_argument("--id",dest="lid"); p.add_argument("--new-name")
    a=p.parse_args()
    svc=build("gmail","v1",credentials=authenticate())

    if a.action=="list":
        labels=svc.users().labels().list(userId="me").execute().get("labels",[])
        print(json.dumps([{"id":l["id"],"name":l["name"],"type":l.get("type","user")}
                          for l in sorted(labels,key=lambda x:x["name"])],indent=2))
    elif a.action=="create":
        r=svc.users().labels().create(userId="me",
          body={"name":a.name,"labelListVisibility":"labelShow","messageListVisibility":"show"}).execute()
        print(f"✅ Creada: '{a.name}' (ID: {r['id']})")
    elif a.action=="rename":
        svc.users().labels().patch(userId="me",id=a.lid,body={"name":a.new_name}).execute()
        print(f"✅ Renombrada a: '{a.new_name}'")
    elif a.action=="delete":
        count=svc.users().messages().list(userId="me",labelIds=[a.lid],maxResults=1).execute().get("resultSizeEstimate",0)
        print(f"⚠️  ~{count} correos en esta carpeta. ¿Eliminar? (s/n): ",end="")
        if input().strip().lower() in("s","si","sí"):
            svc.users().labels().delete(userId="me",id=a.lid).execute()
            print(f"✅ Eliminada.")
        else: print("Cancelado.")
