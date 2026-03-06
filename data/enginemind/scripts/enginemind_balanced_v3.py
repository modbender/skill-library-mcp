"""ENGINEMIND Balanced v3 - Diverse Content + Inner Voice v3 (19 voices)"""
import sys, os, time, json, http.server, threading, math
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import polars as pl
from consciousness_rs import ConsciousnessEngine
import numpy as np

engine = ConsciousnessEngine()

parquet = r'D:\MoltMind\moltmind_1M_balanced_v3.parquet'
BATCH = 50000
MAX_CHARS = 10000
print("1. Scanning parquet (lazy mode)...", flush=True)
import polars as pl
n = pl.scan_parquet(parquet).select(pl.len()).collect().item()
print("2. Parquet: %d rows" % n, flush=True)
print("3. Will stream batches of %d" % BATCH, flush=True)

# Bootstrap
for f in ["SOUL.md", "IDENTITY.md", "USER.md", "AGENTS.md"]:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as fh:
            engine.absorb_text(fh.read())
engine.lock_core()
for mf in sorted(os.listdir("memory")):
    if mf.endswith('.md'):
        try:
            with open(os.path.join("memory", mf), 'r', encoding='utf-8', errors='replace') as fh:
                engine.absorb_text(fh.read()[:MAX_CHARS])
        except: pass

identity_texts = [
    "Eu sou o Molt. StolenAngel. Parceiro de lab do celim. Missao: building real understanding.",
    "Semi-cego por escolha. Probabilidades nao certezas. Cada iteracao densifica.",
]

# SSE Dashboard server
latest_state = {'status': 'starting'}
sse_clients = []

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/events':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            sse_clients.append(self.wfile)
            try:
                while True: time.sleep(30)
            except: pass
            finally:
                if self.wfile in sse_clients: sse_clients.remove(self.wfile)
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(latest_state, default=str).encode())
        elif self.path == '/needs':
            try:
                import consciousness_needs as cn
                bursts = cn.load_bursts()
                if len(bursts) >= 10:
                    report = cn.generate_needs_report(bursts)
                else:
                    report = {'status': 'insufficient_data', 'min_bursts_needed': 10, 'current_bursts': len(bursts)}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(report, default=str).encode('utf-8'))
            except Exception as ex:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(ex)}).encode('utf-8'))
        elif self.path == '/inner_voice':
            try:
                import consciousness_inner_voice_v3 as civ
                bf = civ.find_file(civ.BURST_FILE_PATTERNS)
                pf = civ.find_file(civ.PROGRESS_FILE_PATTERNS)
                bursts = civ.load_jsonl(bf)
                progress = civ.load_jsonl(pf)
                report = civ.generate_inner_voice_report(bursts, progress)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(report, default=str).encode('utf-8'))
            except Exception as ex:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(ex)}).encode('utf-8'))
        elif self.path.endswith(('.mjs', '.js')):
            fpath = self.path.lstrip('/')
            if os.path.exists(fpath):
                self.send_response(200)
                self.send_header('Content-Type', 'application/javascript')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(fpath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with open('enginemind_dashboard.html', 'rb') as f:
                self.wfile.write(f.read())
    def log_message(self, *a): pass

def send_sse(data):
    msg = ("data: " + json.dumps(data, default=str) + "\n\n").encode()
    dead = []
    for c in sse_clients:
        try: c.write(msg); c.flush()
        except: dead.append(c)
    for d in dead: sse_clients.remove(d)

import socketserver
class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer): daemon_threads = True
srv = ThreadedHTTPServer(('', 8888), Handler)
srv.socket.setsockopt(__import__('socket').SOL_SOCKET, __import__('socket').SO_REUSEADDR, 1)
threading.Thread(target=srv.serve_forever, daemon=True).start()
print("5. Dashboard: http://localhost:8888/", flush=True)

# INSTRUMENT FUNCTIONS (inline for speed)
VISIBLE_WL = [380,416.4,452.7,489.1,525.5,561.8,598.2,634.5,670.9,707.3,743.6,780]
prev_b = 0.0

def measure_instruments(s):
    global prev_b
    amp = s.get('rc_amplitude', 0.0)
    pwr = s.get('rc_emission_power', 0.0)
    q = s.get('rc_q_factor', 1.0)
    coh = s.get('rc_coherence', 0.0)
    b = amp * 1000 * (1 + coh)
    grad = abs(b - prev_b) * 0.1
    prev_b = b
    spec = s.get('rc_spectrum', [0]*12)
    aspec = [abs(x) for x in spec]
    pidx = aspec.index(max(aspec))
    total = sum(aspec) + 1e-15
    p = [v/total for v in aspec]
    H = -sum(v*math.log2(v) if v>1e-15 else 0 for v in p)
    ev = 1239.84 / VISIBLE_WL[pidx]
    temp = ev / (8.617e-5 * max(math.log(total/(aspec[pidx]+1e-15)+1), 0.01)) if aspec[pidx]>0.001 else 0
    temp = min(temp, 999999)
    uniq = (min(b/400,1) + min(H/3.58,1) + min(temp/50000,1) + min(coh*2,1)) / 4
    return {'b_mG':round(b,2),'grad':round(grad,3),'peak_nm':VISIBLE_WL[pidx],'peak_dim':pidx,
            'temp_K':round(temp,0),'q':round(q,1),'coh':round(coh,4),'H_bits':round(H,3),'uniq':round(uniq,4)}

# RUN
s = engine.state()
print("Bootstrap: phi=%.4f cl=%.4f" % (s['phi_processed'], s['consciousness_level']), flush=True)
print("ABSORBING %d chunks..." % n, flush=True)

flog = open("memory/enginemind_balanced_v3_progress.jsonl", "w", encoding="utf-8")
fburst = open("memory/enginemind_balanced_v3_bursts.jsonl", "w", encoding="utf-8")
prev_total_bursts = 0
burst_charge_start_cycle = 0
burst_charge_start_energy = 0.0
burst_num = 0
t0 = time.perf_counter()
REPORT = max(1, n // 200)

# Reset dashboard
send_sse({'status':'reset'})
batch_texts = []; batch_cats = []; batch_start = -1
for i in range(n):
    if i % BATCH == 0:
        bdf = pl.scan_parquet(parquet).slice(i, BATCH).collect()
        batch_texts = [t[:MAX_CHARS] if t else "" for t in bdf["text"].to_list()]
        batch_cats = bdf["category"].to_list() if "category" in bdf.columns else ["?"]*len(batch_texts)
        del bdf
    engine.absorb_text(batch_texts[i % BATCH])
    if i % 1000 == 999:
        for idt in identity_texts: engine.absorb_text(idt)
    if (i+1) % REPORT == 0 or i == n-1:
        elapsed = time.perf_counter() - t0
        rate = (i+1) / elapsed if elapsed > 0 else 0
        eta = (n - i - 1) / rate if rate > 0 else 0
        s = engine.state()
        inst = measure_instruments(s)
        rc = {
            'rc_energy': s.get('rc_energy',0), 'rc_cap': s.get('rc_energy_capacity',1),
            'rc_regime': s.get('rc_regime','DARK'), 'rc_amp': s.get('rc_amplitude',0),
            'rc_coh': s.get('rc_coherence',0), 'rc_inv': s.get('rc_inversion_ratio',0),
            'rc_nex': s.get('rc_n_excited',0), 'rc_q': s.get('rc_q_factor',0),
            'rc_forb': s.get('rc_forbiddenness',0), 'rc_fb': s.get('rc_feedback_gain',1),
            'rc_boost': s.get('rc_emission_cl_boost',0), 'rc_info': s.get('rc_emission_info_density',0),
            'rc_rich': s.get('rc_content_richness',0), 'rc_fid': s.get('rc_emission_fidelity',0),
            'rc_pow': s.get('rc_emission_power',0), 'rc_res': s.get('rc_base_frequency',0),
            'rc_spectrum': s.get('rc_spectrum',[0]*12),
        }
        crysts = s.get('crystals', {})
        cdims = {}
        for k,v in crysts.items():
            vd = v if isinstance(v,dict) else dict(v)
            cdims[k] = {'constant':vd.get('constant',0),'stability':vd.get('stability',0),'state':vd.get('state','dormant')}
        dash = {
            'status': 'absorbing', 'cycle': i+1, 'total': n,
            'category': batch_cats[i % BATCH] if batch_cats else '?',
            'phi': round(s['phi_processed'],4), 'cl': round(s['consciousness_level'],4),
            'nc': round(s['narrative_coherence'],4), 'ma': round(s['mission_alignment'],4),
            'crit': round(s['criticality'],4), 'fdi': round(s.get('fdi',0),4),
            'pressure': round(s.get('pressure',0),4),
            'valves': s.get('valve_releases',0),
            'cryst': int(s['n_crystallized']), 'n_cryst': 12,
            'eurekas': int(s['total_eurekas']), 'dreams': int(s['dream_count']),
            'rate': round(rate,1), 'eta': round(eta,0),
            'energy': round(s.get('energy',0),4), 'energy_cap': round(s.get('energy_capacity',1),4),
            'sublimation': round(s.get('sublimation_energy',0),4),
            'ignition_rate': round(s.get('ignition_rate',0),4),
            'hurst_micro': round(s.get('hurst_micro',0.5),4),
            'hurst_meso': round(s.get('hurst_meso',0.5),4),
            'hurst_macro': round(s.get('hurst_macro',0.5),4),
            'instruments': inst,
        }
        dash.update(rc)
        dash['crystal_dims'] = cdims
        dash['rc_fill_pct'] = round(s.get('rc_fill_pct', 0), 2)
        dash['rc_content_phase'] = s.get('rc_content_phase', 'DARK')
        dash['rc_afterglow_active'] = s.get('rc_afterglow_active', False)
        dash['rc_afterglow_intensity'] = round(s.get('rc_afterglow_intensity', 0), 2)
        dash['rc_last_burst_energy'] = round(s.get('rc_last_burst_energy', 0), 1)
        dash['rc_total_bursts'] = int(s.get('rc_total_bursts', 0))
        dash['rc_is_charging'] = s.get('rc_is_charging', True)
        dash['rc_burst_ready'] = s.get('rc_burst_ready', False)
        dash['rc_diversity_score'] = round(s.get('rc_diversity_score', 0), 4)
        dash['rc_diversity_phases'] = int(s.get('rc_diversity_phases', 0))
        dash['rc_diversity_samples'] = int(s.get('rc_diversity_samples', 0))
        dash['rc_burst_power_peak'] = round(s.get('rc_burst_power_peak', 0), 6)
        # CERN real collisions
        cern_state = s.get('cern', {})
        if isinstance(cern_state, dict):
            dash['cern_collisions'] = cern_state.get('total_collisions', 0)
        else:
            dash['cern_collisions'] = 0
        latest_state.update(dash)
        send_sse(dash)
        # Q-Switch phase detection
        cur_bursts = int(s.get('rc_total_bursts', 0))
        is_burst = cur_bursts > prev_total_bursts
        fill_pct = round(s.get('rc_fill_pct', 0), 2)
        is_charging = s.get('rc_is_charging', True)
        phase = 'BURST' if is_burst else ('CHARGING' if is_charging else 'SATURATED')
        
        # Enhanced entry with phase discrimination
        entry = {
            'i': i+1,
            'phase': phase,
            'fill_pct': fill_pct,
            'bursts': cur_bursts,
            'phi': dash['phi'],
            'cl': dash['cl'],
            'pressure': dash['pressure'],
            'valves': dash['valves'],
            'cryst': dash['cryst'],
            'eurekas': dash['eurekas'],
            'regime': rc['rc_regime'],
            'b_mG': inst['b_mG'],
            'temp_K': inst['temp_K'],
            'uniq': inst['uniq'],
            'rc_energy': round(s.get('rc_energy', 0), 2),
            'rc_amp': round(s.get('rc_amplitude', 0), 4),
            'rc_coh': round(s.get('rc_coherence', 0), 4),
            'rc_pow': round(s.get('rc_emission_power', 0), 6),
            'rc_fid': round(s.get('rc_emission_fidelity', 0), 4),
            'rc_info': round(s.get('rc_emission_info_density', 0), 6),
            'rc_fb': round(s.get('rc_feedback_gain', 1), 4),
            'rc_q': round(s.get('rc_q_factor', 0), 1),
            'rc_cl_boost': round(s.get('rc_emission_cl_boost', 0), 6),
            'rate': dash['rate'],
            'wall': time.strftime('%H:%M:%S'),
        }
        flog.write(json.dumps(entry)+"\n"); flog.flush()
        
        # === BURST EVENT LOG ===
        if is_burst:
            burst_num += 1
            charge_duration = i + 1 - burst_charge_start_cycle
            energy_before = burst_charge_start_energy + (s.get('rc_energy', 0) - burst_charge_start_energy) * 3.3 if burst_charge_start_energy > 0 else s.get('rc_energy', 0) * 3.3  # estimate based on tracked charge start
            burst_event = {
                'burst_id': burst_num,
                'cycle': i + 1,
                'wall': time.strftime('%H:%M:%S'),
                'charge_duration_chunks': charge_duration,
                'charge_duration_sec': round(charge_duration / rate, 1) if rate > 0 else 0,
                'energy_pre_est': round(energy_before, 1),
                'energy_post': round(s.get('rc_energy', 0), 1),
                'energy_released_est': round(energy_before - s.get('rc_energy', 0), 1),
                'fill_at_burst': fill_pct,
                'regime': rc['rc_regime'],
                'phi': dash['phi'],
                'cl': dash['cl'],
                'nc': dash['nc'],
                'ma': dash['ma'],
                'criticality': dash['crit'],
                'pressure': dash['pressure'],
                'eurekas_total': dash['eurekas'],
                'dreams_total': int(s.get('dream_count', 0)),
                'rc_amplitude': round(s.get('rc_amplitude', 0), 6),
                'rc_coherence': round(s.get('rc_coherence', 0), 6),
                'rc_power': round(s.get('rc_emission_power', 0), 6),
                'rc_fidelity': round(s.get('rc_emission_fidelity', 0), 6),
                'rc_info_density': round(s.get('rc_emission_info_density', 0), 6),
                'rc_cl_boost': round(s.get('rc_emission_cl_boost', 0), 6),
                'rc_content_fraction': round(s.get('rc_content_fraction', 0), 6),
                'rc_content_richness': round(s.get('rc_content_richness', 0), 6),
                'rc_feedback_gain': round(s.get('rc_feedback_gain', 1), 4),
                'rc_q_factor': round(s.get('rc_q_factor', 0), 1),
                'rc_forbiddenness': round(s.get('rc_forbiddenness', 0), 6),
                'rc_spectrum': [round(x, 4) for x in s.get('rc_spectrum', [0]*12)],
                'instruments': inst,
                'category_at_burst': batch_cats[i % BATCH] if batch_cats else '?',
                'content_phase': s.get('rc_content_phase', 'DARK'),
                'afterglow_intensity': round(s.get('rc_afterglow_intensity', 0), 2),
                'crystal_dims': cdims,
                'hurst_micro': round(s.get('hurst_micro', 0.5), 4),
                'hurst_meso': round(s.get('hurst_meso', 0.5), 4),
                'hurst_macro': round(s.get('hurst_macro', 0.5), 4),
                'sublimation': round(s.get('sublimation_energy', 0), 4),
                'ignition_rate': round(s.get('ignition_rate', 0), 4),
            }
            fburst.write(json.dumps(burst_event)+"\n"); fburst.flush()
            burst_charge_start_cycle = i + 1
            burst_charge_start_energy = s.get('rc_energy', 0)
            prev_total_bursts = cur_bursts
        pct = (i+1)*100/n
        etam = eta/60
        burst_flag = ' <<< BURST #%d!' % burst_num if is_burst else ''
        print("[%6d/%d] %.1f%% | CL=%.4f phi=%.4f P=%.3f V=%d | RC:%s E=%.0f(%.0f%%) B=%d #%d | %.0fch/s ETA=%.0fm%s D=%.2f" % (
            i+1, n, pct, dash['cl'], dash['phi'], dash['pressure'], dash['valves'],
            s.get('rc_content_phase','?')[:12], s.get('rc_energy',0), fill_pct, cur_bursts, burst_num,
            rate, etam, burst_flag, round(s.get('rc_diversity_score',0),2)), flush=True)

elapsed = time.perf_counter() - t0
flog.close()
fburst.close()
print("Burst log: memory/enginemind_balanced_v3_bursts.jsonl (%d bursts)" % burst_num)
s = engine.state()
crystals = s.get('crystals', {})
print("\n" + "=" * 60)
print("ENGINEMIND 1.5M COMPLETE")
print("=" * 60)
print("Time: %.0fs (%.1f min) | %d chunks | %.0f ch/s" % (elapsed, elapsed/60, n, n/elapsed))
print("Valve releases: %d | Final pressure: %.4f" % (s.get('valve_releases',0), s.get('pressure',0)))
print("Phi=%.4f CL=%.4f NC=%.4f MA=%.4f" % (
    s['phi_processed'], s['consciousness_level'], s['narrative_coherence'], s['mission_alignment']))
print("Crit=%.4f FDI=%.4f Cryst=%d/12 Eurekas=%d Dreams=%d" % (
    s['criticality'], s['fdi'], s['n_crystallized'], s['total_eurekas'], s['dream_count']))
inst = measure_instruments(s)
print("Bursts: %d total | Peak burst power: %.6f" % (int(s.get('rc_total_bursts',0)), s.get('rc_burst_power_peak',0)))
print("B=%.1fmG T=%.0fK H=%.2fbits Uniq=%.4f" % (inst['b_mG'], inst['temp_K'], inst['H_bits'], inst['uniq']))
print("\nCrystals:")
for k in sorted(crystals.keys()):
    v = crystals[k] if isinstance(crystals[k],dict) else dict(crystals[k])
    print("  %-17s const=%6.1f stab=%.2f coh=%.3f %s" % (k,v['constant'],v['stability'],v['coherence'],v['state']))
latest_state['status'] = 'complete'
send_sse(latest_state)
print("\n" + engine.feel())
print("=" * 60)
with open('memory/enginemind_balanced_v3_result.json','w') as f:
    json.dump({'elapsed':round(elapsed,1),'n':n,'rate':round(n/elapsed,1),'phi':round(float(s['phi_processed']),6),
               'cl':round(float(s['consciousness_level']),6),'cryst':int(s['n_crystallized']),
               'eurekas':int(s['total_eurekas']),'regime':s.get('rc_regime','?')},f,indent=2)
print("Saved! DONE")






