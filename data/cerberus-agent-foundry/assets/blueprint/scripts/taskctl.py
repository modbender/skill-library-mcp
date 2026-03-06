#!/usr/bin/env python3
import argparse, json, os, glob
from datetime import datetime
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK_DIR = os.path.join(ROOT, 'control-plane', 'tasks')
EVENTS = os.path.join(ROOT, 'control-plane', 'logs', 'events.jsonl')

VALID = {'INBOX','CLAIMED','IN_PROGRESS','REVIEW','DONE','BLOCKED','FAILED'}
TRANSITIONS = {
    'INBOX': {'CLAIMED'},
    'CLAIMED': {'IN_PROGRESS','INBOX'},
    'IN_PROGRESS': {'REVIEW','BLOCKED','FAILED'},
    'REVIEW': {'DONE','BLOCKED','FAILED'},
    'DONE': set(),'BLOCKED': set(),'FAILED': set()
}

def now():
    return datetime.now().astimezone().isoformat()

def load(path):
    with open(path,'r',encoding='utf-8') as f:
        return yaml.safe_load(f)

def save(path,data):
    with open(path,'w',encoding='utf-8') as f:
        yaml.safe_dump(data,f,sort_keys=False,allow_unicode=True)

def event(rec):
    with open(EVENTS,'a',encoding='utf-8') as f:
        f.write(json.dumps(rec,ensure_ascii=False)+"\n")

def find(task_id):
    for p in glob.glob(os.path.join(TASK_DIR,'*.yaml')):
        d = load(p)
        if d.get('task_id') == task_id:
            return p,d
    raise SystemExit(f'task not found: {task_id}')

def cmd_list(_):
    rows=[]
    for p in sorted(glob.glob(os.path.join(TASK_DIR,'*.yaml'))):
        d=load(p)
        rows.append((d.get('task_id'),d.get('status'),d.get('owner'),os.path.basename(p)))
    for r in rows:
        print('\t'.join([str(x) for x in r]))

def cmd_transition(a):
    p,d=find(a.task_id)
    cur=d.get('status')
    nxt=a.to
    if nxt not in VALID:
        raise SystemExit('invalid target status')
    if nxt not in TRANSITIONS.get(cur,set()):
        raise SystemExit(f'invalid transition: {cur}->{nxt}')
    if nxt=='CLAIMED' and not a.actor:
        raise SystemExit('CLAIMED requires --actor owner')
    if cur=='IN_PROGRESS' and nxt=='REVIEW' and (a.actor and a.actor==d.get('owner')):
        raise SystemExit('self-review forbidden')
    d['status']=nxt
    d['updated_at']=now()
    if nxt=='CLAIMED':
        d['owner']=a.actor
        d['claimed_at']=now()
    save(p,d)
    event({'ts':now(),'type':'task_transition','task_id':a.task_id,'from':cur,'to':nxt,'actor':a.actor})
    print(f'{a.task_id}: {cur} -> {nxt}')

def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(required=True)
    l=sp.add_parser('list'); l.set_defaults(func=cmd_list)
    t=sp.add_parser('transition')
    t.add_argument('--task-id',required=True)
    t.add_argument('--to',required=True)
    t.add_argument('--actor',required=False)
    t.set_defaults(func=cmd_transition)
    a=ap.parse_args(); a.func(a)

if __name__=='__main__':
    main()
