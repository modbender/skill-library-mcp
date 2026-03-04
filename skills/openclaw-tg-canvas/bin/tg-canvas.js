#!/usr/bin/env node
"use strict";
const fs = require("fs");

const args = process.argv.slice(2);
const subcmd = args[0];
const BASE_URL = process.env.TG_CANVAS_URL || process.env.CANVAS_URL || "http://127.0.0.1:3721";
const PUSH_TOKEN = process.env.PUSH_TOKEN || "";

function usage(code = 0) {
  console.log(`Usage: tg-canvas <command> [options]
Commands: push | clear | health | terminal
Options (push): --html | --markdown | --text | --a2ui <json|@file> | --format | --content | --url
terminal: activates terminal mode in the Mini App (clear to exit)`);
  process.exit(code);
}

function parseFlag(flag){
  const i = args.indexOf(flag);
  if (i < 0) return null;
  const v = args[i+1];
  if (!v || v.startsWith("--")) return null;
  return v;
}

function readMaybeFile(val, { parseJson=false }={}) {
  let raw = val;
  if (val && val.startsWith("@")) raw = fs.readFileSync(val.slice(1), "utf8");
  return parseJson ? JSON.parse(raw) : raw;
}

async function request(method, url, body){
  const headers = body ? {"Content-Type":"application/json"} : {};
  if (PUSH_TOKEN) headers["X-Push-Token"] = PUSH_TOKEN;
  const res = await fetch(url,{ method, headers, body: body?JSON.stringify(body):undefined });
  const text = await res.text();
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${text}`);
  return text ? JSON.parse(text) : {};
}

async function main(){
  if (!subcmd) usage(1);
  const base = parseFlag("--url") || BASE_URL;
  if (subcmd === "health") return console.log(JSON.stringify(await request("GET", `${base}/health`),null,2));
  if (subcmd === "clear") return console.log(JSON.stringify(await request("POST", `${base}/clear`, {ok:true}),null,2));
  if (subcmd === "terminal") return console.log(JSON.stringify(await request("POST", `${base}/push`, {format:"terminal",content:""}),null,2));
  if (subcmd !== "push") return usage(1);

  const html=parseFlag("--html"), markdown=parseFlag("--markdown"), text=parseFlag("--text"), a2ui=parseFlag("--a2ui");
  const format=parseFlag("--format"), content=parseFlag("--content");
  let body=null;
  if (format && content) body = { format, content: format==="a2ui" ? readMaybeFile(content,{parseJson:true}) : readMaybeFile(content) };
  else if (html) body={html}; else if (markdown) body={markdown}; else if (text) body={text};
  else if (a2ui) body={a2ui: readMaybeFile(a2ui,{parseJson:true})}; else usage(1);

  console.log(JSON.stringify(await request("POST", `${base}/push`, body), null, 2));
}

main().catch(err=>{ console.error(err.message||String(err)); process.exit(1); });
