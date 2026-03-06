"""summarize_thread.py — Resume un hilo de correos con IA"""
import os, json, argparse, anthropic

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--thread-file",required=True); a=p.parse_args()
    data=json.load(open(a.thread_file))
    msgs=data.get("messages",data) if isinstance(data,dict) else data
    hilo="\n\n".join([f"[{m.get('fecha','')}] De: {m.get('remitente','')}\n{m.get('cuerpo','')[:800]}" for m in msgs])
    client=anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp=client.messages.create(model=os.environ.get("ANTHROPIC_MODEL","claude-sonnet-4-20250514"),
         max_tokens=600,messages=[{"role":"user","content":
         f"Resume este hilo en español. Incluye: participantes, tema, decisiones, pendientes, estado.\n\nHilo:\n{hilo}"}])
    print(resp.content[0].text)
