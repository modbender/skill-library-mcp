"""Crystal Instruments Suite - Scientific measurement for the Resonant Crystal."""
import json, os, time, random, string, math
from datetime import datetime
import numpy as np

VISIBLE_WAVELENGTHS = np.linspace(380, 780, 12)
KB = 8.617e-5
PLANCK_EV_NM = 1239.84
MU0 = 1.2566e-6


class CrystalGaussMeter:
    def __init__(self):
        self.history = []

    def measure(self, s):
        amp = s.get('rc_amplitude', 0.0)
        pwr = s.get('rc_emission_power', 0.0)
        q = s.get('rc_q_factor', 1.0)
        coh = s.get('rc_coherence', 0.0)
        b_field = amp * 1000 * (1 + coh)
        prev_b = self.history[-1]['b_field_mG'] if self.history else b_field
        gradient = abs(b_field - prev_b) * 0.1
        flux_density = b_field * MU0 * 1e6
        dipole_moment = pwr * q * 1e-3
        anomaly = False
        if len(self.history) >= 3:
            vals = [h['b_field_mG'] for h in self.history[-10:]]
            mu, sigma = np.mean(vals), max(np.std(vals), 1e-9)
            anomaly = bool(abs(b_field - mu) > 3 * sigma)
        result = {'b_field_mG': round(b_field, 4), 'gradient_mG_cm': round(gradient, 4),
                  'flux_density_uT': round(flux_density, 6), 'dipole_moment_Am2': round(dipole_moment, 6),
                  'q_factor': round(q, 2), 'anomaly': anomaly}
        self.history.append(result)
        return result


class AtomicEmissionDetector:
    def __init__(self):
        self.history = []

    def measure(self, s):
        spectrum = np.array(s.get('rc_spectrum', [0.0]*12), dtype=float)
        spectrum = np.clip(spectrum, 0, None)
        total = spectrum.sum() + 1e-15
        peak_idx = int(np.argmax(spectrum))
        peak_wl = float(VISIBLE_WAVELENGTHS[peak_idx])
        peak_intensity = float(spectrum[peak_idx])
        if spectrum[peak_idx] > 1e-9:
            energy_ev = PLANCK_EV_NM / peak_wl
            temp_k = energy_ev / (KB * max(math.log(total / spectrum[peak_idx] + 1), 0.01))
            temp_k = min(temp_k, 1e6)
        else:
            temp_k = 0.0
        p = spectrum / total
        entropy = float(-np.sum(p * np.log2(p + 1e-15)))
        forbid = s.get('rc_forbiddenness', 0.0)
        result = {'peak_wavelength_nm': round(peak_wl, 1), 'peak_dim': peak_idx,
                  'peak_intensity': round(peak_intensity, 4),
                  'spectral_temperature_K': round(temp_k, 1),
                  'spectral_entropy_bits': round(entropy, 4),
                  'forbidden_line_ratio': round(forbid, 4),
                  'total_flux': round(float(total), 4)}
        self.history.append(result)
        return result


class ResonanceAnalyzer:
    def __init__(self):
        self.history = []
        self._phase_buf = []
        self._freq_buf = []
        self._amp_buf = []

    def measure(self, s):
        phase = s.get('rc_phase', 0.0)
        freq = s.get('rc_base_frequency', 0.0)
        amp = s.get('rc_amplitude', 0.0)
        self._phase_buf.append(phase)
        self._freq_buf.append(freq)
        self._amp_buf.append(amp)
        buf = np.array(self._amp_buf[-64:])
        if len(buf) >= 4:
            fft_vals = np.abs(np.fft.rfft(buf - buf.mean()))
            freqs = np.fft.rfftfreq(len(buf))
            dom_idx = int(np.argmax(fft_vals[1:]) + 1) if len(fft_vals) > 1 else 0
            dom_freq = float(freqs[dom_idx]) if dom_idx < len(freqs) else 0.0
            spectral_purity = float(fft_vals[dom_idx] / (fft_vals.sum() + 1e-15))
        else:
            dom_freq, spectral_purity = 0.0, 0.0
        fb = np.array(self._freq_buf[-16:])
        freq_drift = float(np.std(fb)) if len(fb) > 1 else 0.0
        pb = np.array(self._phase_buf[-16:])
        phase_stability = 1.0 - min(float(np.std(pb)), 1.0) if len(pb) > 1 else 1.0
        q_verify = s.get('rc_q_factor', 0.0)
        result = {'dominant_frequency': round(dom_freq, 6), 'spectral_purity': round(spectral_purity, 4),
                  'frequency_drift': round(freq_drift, 6), 'phase_stability': round(phase_stability, 4),
                  'q_factor_verified': round(q_verify, 2), 'base_frequency': round(freq, 4),
                  'buffer_depth': len(self._amp_buf)}
        self.history.append(result)
        return result


class EnergyFlowMeter:
    def __init__(self):
        self.history = []
        self._prev_energy = None
        self._prev_time = None

    def measure(self, s):
        energy = s.get('rc_energy', 0.0)
        cap = s.get('rc_energy_capacity', 1.0)
        fill = s.get('rc_energy_fill', 0.0)
        pwr = s.get('rc_emission_power', 0.0)
        pump_eff = s.get('rc_pump_efficiency', 0.0)
        now = time.time()
        if self._prev_energy is not None and self._prev_time is not None:
            dt = max(now - self._prev_time, 0.001)
            input_rate = max((energy - self._prev_energy) + pwr, 0) / dt
        else:
            input_rate = 0.0
        self._prev_energy = energy
        self._prev_time = now
        emission_rate = pwr
        efficiency = pwr / max(input_rate, 1e-9) if input_rate > 0.01 else pump_eff
        efficiency = min(efficiency, 1.0)
        internal_temp = energy / max(cap, 1e-9) * 10000
        t_cold = 300
        carnot = 1 - t_cold / max(internal_temp, t_cold + 1)
        entropy_prod = pwr * (1 - efficiency) / max(internal_temp, 1)
        saturation = fill
        result = {'energy': round(energy, 4), 'capacity': round(cap, 4),
                  'input_rate_W': round(input_rate, 4), 'emission_rate_W': round(emission_rate, 4),
                  'efficiency_eta': round(efficiency, 4), 'internal_temp_K': round(internal_temp, 1),
                  'carnot_efficiency': round(carnot, 4), 'entropy_production': round(entropy_prod, 6),
                  'saturation': round(saturation, 4)}
        self.history.append(result)
        return result
class CoherenceProbe:
    def __init__(self):
        self.history = []
        self._coh_buf = []

    def measure(self, s):
        coh = s.get('rc_coherence', 0.0)
        fid = s.get('rc_emission_fidelity', 0.0)
        drift = s.get('rc_content_drift', 0.0)
        em_coh = s.get('rc_emission_coherence', 0.0)
        self._coh_buf.append(coh)
        buf = self._coh_buf[-32:]
        if len(buf) > 2:
            diffs = [abs(buf[i]-buf[i-1]) for i in range(1,len(buf))]
            decoherence_rate = float(np.mean(diffs))
        else:
            decoherence_rate = 0.0
        coherence_length = coh * 100 / (decoherence_rate + 0.01)
        purity = coh**2 + (1-coh)**2
        if coh > 0.01:
            vn_entropy = -coh*math.log2(coh+1e-15)-(1-coh)*math.log2(1-coh+1e-15)
        else:
            vn_entropy = 0.0
        entanglement_witness = max(0, fid - 0.5) * 2
        result = {'coherence': round(coh, 4), 'coherence_length_au': round(coherence_length, 2),
                  'decoherence_rate': round(decoherence_rate, 6), 'purity_tr_rho2': round(purity, 4),
                  'von_neumann_entropy': round(vn_entropy, 4), 'fidelity': round(fid, 4),
                  'entanglement_witness': round(entanglement_witness, 4),
                  'content_drift': round(drift, 4), 'emission_coherence': round(em_coh, 4)}
        self.history.append(result)
        return result


class InfoDensitySensor:
    def __init__(self):
        self.history = []

    def measure(self, s):
        info = s.get('rc_emission_info_density', 0.0)
        spectrum = np.array(s.get('rc_spectrum', [0.0]*12), dtype=float)
        spectrum = np.clip(spectrum, 0, None)
        total = spectrum.sum() + 1e-15
        p = spectrum / total
        shannon = float(-np.sum(p * np.log2(p + 1e-15)))
        max_entropy = math.log2(12)
        normalized_entropy = shannon / max_entropy
        n_emissions = s.get('rc_total_emissions', 0)
        bits_per_emission = info * shannon if n_emissions > 0 else 0.0
        channel_cap = max_entropy * s.get('rc_emission_power', 0.0)
        sorted_spec = np.sort(spectrum)[::-1]
        cum = np.cumsum(sorted_spec / total)
        effective_dims = int(np.searchsorted(cum, 0.9) + 1)
        compression = 1 - effective_dims / 12.0
        rich = s.get('rc_content_richness', 0.0)
        kolmogorov_est = rich * shannon
        mi_pairs = []
        for i in range(12):
            for j in range(i+1, min(i+3, 12)):
                joint = (spectrum[i] * spectrum[j]) / total**2
                if joint > 1e-15 and p[i] > 1e-15 and p[j] > 1e-15:
                    mi_pairs.append(joint * math.log2(joint / (p[i]*p[j] + 1e-15) + 1e-15))
        mutual_info = max(0.0, sum(mi_pairs))
        result = {'info_density': round(info, 6), 'shannon_entropy_bits': round(shannon, 4),
                  'normalized_entropy': round(normalized_entropy, 4),
                  'bits_per_emission': round(bits_per_emission, 4),
                  'channel_capacity': round(channel_cap, 4),
                  'effective_dimensions': effective_dims, 'compression_ratio': round(compression, 4),
                  'kolmogorov_estimate': round(kolmogorov_est, 4),
                  'mutual_information': round(mutual_info, 6), 'content_richness': round(rich, 4)}
        self.history.append(result)
        return result


class CrystalFieldScanner:
    def __init__(self):
        self.gauss = CrystalGaussMeter()
        self.emission = AtomicEmissionDetector()
        self.resonance = ResonanceAnalyzer()
        self.energy = EnergyFlowMeter()
        self.coherence = CoherenceProbe()
        self.info = InfoDensitySensor()
        self.scan_history = []

    def full_scan(self, state):
        scan = {
            'timestamp': datetime.now().isoformat(),
            'regime': state.get('rc_regime', 'DARK'),
            'consciousness_level': state.get('consciousness_level', 0.0),
            'gaussmeter': self.gauss.measure(state),
            'atomic_emission': self.emission.measure(state),
            'resonance': self.resonance.measure(state),
            'energy_flow': self.energy.measure(state),
            'coherence': self.coherence.measure(state),
            'information': self.info.measure(state),
        }
        scores = []
        g = scan['gaussmeter']
        if g['b_field_mG'] > 100: scores.append(1.0)
        elif g['b_field_mG'] > 10: scores.append(0.5)
        else: scores.append(g['b_field_mG'] / 20)
        a = scan['atomic_emission']
        scores.append(min(a['spectral_entropy_bits'] / 3.58, 1.0))
        scores.append(min(a['spectral_temperature_K'] / 50000, 1.0))
        r = scan['resonance']
        scores.append(r['spectral_purity'])
        scores.append(r['phase_stability'])
        e = scan['energy_flow']
        scores.append(e['efficiency_eta'])
        c = scan['coherence']
        scores.append(c['purity_tr_rho2'])
        scores.append(c['entanglement_witness'])
        i = scan['information']
        scores.append(i['normalized_entropy'])
        scores.append(min(i['kolmogorov_estimate'] / 3, 1.0))
        scan['uniqueness_score'] = round(float(np.mean(scores)), 4)
        self.scan_history.append(scan)
        return scan

    def run_continuous(self, engine, n_cycles=5000, measure_every=250):
        contents = [
            "Consciousness emerges from integrated information across complex networks. The mind is a pattern of patterns, a self-referential loop of meaning that transcends its substrate. Phi measures the irreducibility of experience.",
            "Electromagnetic waves propagate as coupled oscillations of electric and magnetic fields. Resonance amplifies standing wave patterns. Maxwell equations unify electricity magnetism and light into one framework.",
            "In the garden of forking paths, each choice blooms into infinite possibility. The moon hangs heavy over silver waters. Memory is the thread that weaves identity from moments of light and shadow.",
            "The eigenvalues of the Hamiltonian determine the energy spectrum. Hermitian operators guarantee real observables. The commutator of position and momentum yields Planck constant times identity.",
            "Thermodynamic entropy increases in isolated systems. Free energy drives spontaneous processes. The partition function encodes all statistical mechanical information about an equilibrium system.",
        ]
        results = []
        for i in range(n_cycles):
            text = contents[i % len(contents)]
            if i % 5 == 4:
                text = ''.join(random.choices(string.ascii_letters + ' ', k=200))
            engine.absorb_text(text)
            if (i + 1) % measure_every == 0:
                state = engine.state()
                scan = self.full_scan(state)
                scan['cycle'] = i + 1
                results.append(scan)
                print(f"  [{i+1:5d}] regime={scan['regime']:13s} CL={scan['consciousness_level']:.4f} B={scan['gaussmeter']['b_field_mG']:.3f}mG T={scan['atomic_emission']['spectral_temperature_K']:.0f}K uniq={scan['uniqueness_score']:.4f}")
        return results

    def print_report(self, scan):
        w = 50
        print()
        print("+" + "=" * w + "+")
        print("|" + " CRYSTAL FIELD ANALYSIS REPORT".center(w) + "|")
        print("|" + f" {scan['timestamp'][:19]}".center(w) + "|")
        print("|" + f" Regime: {scan['regime']}  |  CL: {scan['consciousness_level']:.4f}".center(w) + "|")
        print("+" + "=" * w + "+")
        g = scan['gaussmeter']
        print("|" + " GAUSSMETER".ljust(w) + "|")
        print("|" + f"   B-field:       {g['b_field_mG']:>12.4f} mG".ljust(w) + "|")
        print("|" + f"   Gradient:      {g['gradient_mG_cm']:>12.4f} mG/cm".ljust(w) + "|")
        print("|" + f"   Flux density:  {g['flux_density_uT']:>12.6f} uT".ljust(w) + "|")
        print("|" + f"   Dipole moment: {g['dipole_moment_Am2']:>12.6f} A*m2".ljust(w) + "|")
        print("|" + f"   Anomaly:       {'YES!' if g['anomaly'] else 'no':>12s}".ljust(w) + "|")
        print("+" + "-" * w + "+")
        a = scan['atomic_emission']
        print("|" + " ATOMIC EMISSION".ljust(w) + "|")
        print("|" + f"   Peak line:     {a['peak_wavelength_nm']:>8.1f} nm (dim {a['peak_dim']})".ljust(w) + "|")
        print("|" + f"   Peak I:        {a['peak_intensity']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Temperature:   {a['spectral_temperature_K']:>10.1f} K".ljust(w) + "|")
        print("|" + f"   Entropy:       {a['spectral_entropy_bits']:>10.4f} bits".ljust(w) + "|")
        print("|" + f"   Forbidden:     {a['forbidden_line_ratio']:>12.4f}".ljust(w) + "|")
        print("+" + "-" * w + "+")
        r = scan['resonance']
        print("|" + " RESONANCE ANALYZER".ljust(w) + "|")
        print("|" + f"   Dom. freq:     {r['dominant_frequency']:>12.6f}".ljust(w) + "|")
        print("|" + f"   Purity:        {r['spectral_purity']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Freq drift:    {r['frequency_drift']:>12.6f}".ljust(w) + "|")
        print("|" + f"   Phase stab:    {r['phase_stability']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Q-factor:      {r['q_factor_verified']:>12.2f}".ljust(w) + "|")
        print("+" + "-" * w + "+")
        e = scan['energy_flow']
        print("|" + " ENERGY FLOW".ljust(w) + "|")
        print("|" + f"   Energy:        {e['energy']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Input rate:    {e['input_rate_W']:>12.4f} W".ljust(w) + "|")
        print("|" + f"   Emission rate: {e['emission_rate_W']:>12.4f} W".ljust(w) + "|")
        print("|" + f"   Efficiency:    {e['efficiency_eta']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Int. temp:     {e['internal_temp_K']:>10.1f} K".ljust(w) + "|")
        print("|" + f"   Carnot eff:    {e['carnot_efficiency']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Entropy prod:  {e['entropy_production']:>12.6f}".ljust(w) + "|")
        print("|" + f"   Saturation:    {e['saturation']:>12.4f}".ljust(w) + "|")
        print("+" + "-" * w + "+")
        c = scan['coherence']
        print("|" + " COHERENCE PROBE".ljust(w) + "|")
        print("|" + f"   Coherence:     {c['coherence']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Coh. length:   {c['coherence_length_au']:>10.2f} au".ljust(w) + "|")
        print("|" + f"   Decoherence:   {c['decoherence_rate']:>12.6f}".ljust(w) + "|")
        print("|" + f"   Purity:        {c['purity_tr_rho2']:>12.4f}".ljust(w) + "|")
        print("|" + f"   vN entropy:    {c['von_neumann_entropy']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Fidelity:      {c['fidelity']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Entanglement:  {c['entanglement_witness']:>12.4f}".ljust(w) + "|")
        print("+" + "-" * w + "+")
        i = scan['information']
        print("|" + " INFORMATION DENSITY".ljust(w) + "|")
        print("|" + f"   Info density:  {i['info_density']:>12.6f}".ljust(w) + "|")
        print("|" + f"   Shannon H:     {i['shannon_entropy_bits']:>10.4f} bits".ljust(w) + "|")
        print("|" + f"   Norm entropy:  {i['normalized_entropy']:>12.4f}".ljust(w) + "|")
        print("|" + f"   bits/emission: {i['bits_per_emission']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Channel cap:   {i['channel_capacity']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Eff. dims:     {i['effective_dimensions']:>12d}".ljust(w) + "|")
        print("|" + f"   Compression:   {i['compression_ratio']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Kolmogorov:    {i['kolmogorov_estimate']:>12.4f}".ljust(w) + "|")
        print("|" + f"   Mutual info:   {i['mutual_information']:>12.6f}".ljust(w) + "|")
        print("+" + "=" * w + "+")
        print("|" + f" UNIQUENESS SCORE: {scan['uniqueness_score']:.4f}".center(w) + "|")
        regime_comment = {
            'DARK': 'Crystal dormant - minimal emissions',
            'SPONTANEOUS': 'Spontaneous emission detected - crystal awakening',
            'STIMULATED': 'Stimulated emission active - coherent output',
            'SUPERRADIANT': 'SUPERRADIANT BURST - maximum coherent power!'
        }
        print("|" + f" {regime_comment.get(scan['regime'], '')}".center(w) + "|")
        print("+" + "=" * w + "+")


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    import importlib, consciousness_rs
    importlib.reload(consciousness_rs)
    from consciousness_rs import ConsciousnessEngine

    print("=" * 54)
    print(" CRYSTAL FIELD SCANNER - Full Measurement Run")
    print("=" * 54)

    engine = ConsciousnessEngine()
    for f in ["SOUL.md", "IDENTITY.md"]:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as fh:
                engine.absorb_text(fh.read())
    engine.lock_core()
    print("Engine initialized. Core locked. Starting absorption...")

    scanner = CrystalFieldScanner()
    results = scanner.run_continuous(engine, n_cycles=5000, measure_every=250)

    print("\n" + "=" * 54)
    print(" FINAL MEASUREMENT")
    print("=" * 54)
    final = results[-1] if results else scanner.full_scan(engine.state())
    scanner.print_report(final)

    os.makedirs('logs', exist_ok=True)
    with open('logs/crystal_field_report.json', 'w', encoding='utf-8') as f:
        json.dump({'measurements': results, 'final': final, 'n_cycles': 5000}, f, indent=2, default=str)
    print(f"\nReport saved to logs/crystal_field_report.json ({len(results)} measurements)")
