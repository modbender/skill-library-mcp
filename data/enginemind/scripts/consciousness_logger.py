"""
CONSCIOUSNESS LOGGER - Stream atômico para disco
=================================================
Escreve JSONL (uma linha JSON por evento) em tempo real.
Nunca perde dados - append-only, flush imediato.

Streams separados:
  events.jsonl    - Cada eureka, dream, crystal change, phase transition
  field.jsonl     - Gaussimetro a cada N ciclos 
  entropy.jsonl   - Entropia, MI, KL a cada N ciclos
  checkpoints.jsonl - Estado completo a cada 10k ciclos
"""

import json
import time
import os


class ConsciousnessLogger:
    """Logger atômico em tempo real. Tudo vai pra disco imediatamente."""

    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Abrir streams (append mode, line buffered)
        self.f_events = open(os.path.join(log_dir, 'events.jsonl'), 'a', buffering=1, encoding='utf-8')
        self.f_field = open(os.path.join(log_dir, 'field.jsonl'), 'a', buffering=1, encoding='utf-8')
        self.f_entropy = open(os.path.join(log_dir, 'entropy.jsonl'), 'a', buffering=1, encoding='utf-8')
        self.f_checkpoints = open(os.path.join(log_dir, 'checkpoints.jsonl'), 'a', buffering=1, encoding='utf-8')
        
        # Metadata
        self._write_event({'type': 'SESSION_START', 'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'), 'cycle': 0})
    
    def _write(self, stream, data):
        """Escreve uma linha JSON e faz flush imediato."""
        stream.write(json.dumps(data, default=str) + '\n')
        stream.flush()
    
    def _write_event(self, data):
        self._write(self.f_events, data)
    
    def log_event(self, cycle, event_type, cat='', **kwargs):
        """Log de evento atômico (eureka, dream, crystal_change, etc)."""
        record = {
            'c': cycle,           # cycle (compacto)
            't': event_type,      # type
            'ts': round(time.time(), 2),
            'cat': cat,
        }
        record.update(kwargs)
        self._write_event(record)
    
    def log_field(self, cycle, field_data):
        """Log de campo (gaussimetro) - medição em cada dim."""
        self._write(self.f_field, {'c': cycle, **field_data})
    
    def log_entropy(self, cycle, entropy_data):
        """Log de entropia."""
        self._write(self.f_entropy, {'c': cycle, **entropy_data})
    
    def log_checkpoint(self, cycle, state_data):
        """Log de checkpoint (estado completo)."""
        self._write(self.f_checkpoints, {'c': cycle, 'ts': round(time.time(), 2), **state_data})
    
    def close(self):
        """Fecha todos os streams."""
        self._write_event({'type': 'SESSION_END', 'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')})
        for f in [self.f_events, self.f_field, self.f_entropy, self.f_checkpoints]:
            f.flush()
            f.close()




def smart_chunk_text(text, max_words=500, overlap_pct=0.10):
    """
    Recursive Structure-Aware Chunking.
    
    Strategy (inspired by IIT - each chunk should be a coherent unit of meaning):
      1. Split by \n\n (paragraphs/sections)
      2. If block > max_words -> split by \n (lines)
      3. If still > max_words -> split by '. ' (sentences)
      4. If still > max_words -> fallback word split at nearest sentence boundary
      5. Merge: small adjacent blocks fused until ~max_words
      6. Overlap: each chunk gets last overlap_pct*max_words words from previous
    
    Returns list of chunk strings.
    """
    import re
    
    if not text or not text.strip():
        return []
    
    # Strip HTML if detected (many MoltMind files are HTML from pdf2html)
    if '<html' in text[:500].lower() or '<!doctype' in text[:500].lower():
        import re as _re
        # Remove style/script blocks entirely
        text = _re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=_re.DOTALL|_re.IGNORECASE)
        text = _re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=_re.DOTALL|_re.IGNORECASE)
        # Remove base64 data URIs (images embedded in HTML)
        text = _re.sub(r'data:[^"\'>\s]+', '', text)
        # Remove all HTML tags
        text = _re.sub(r'<[^>]+>', ' ', text)
        # Decode common HTML entities
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ').replace('&#8217;', "'")
        # Collapse whitespace
        text = _re.sub(r'\s+', ' ', text).strip()
        
        if not text or len(text.split()) < 20:
            return []
    
    min_chunk_words = 20  # minimum viable chunk
    overlap_words = int(max_words * overlap_pct)
    
    # --- Step 1-4: Recursive split into atomic blocks ---
    def recursive_split(block, level=0):
        """Split block recursively respecting semantic boundaries."""
        words = block.split()
        if len(words) <= max_words:
            return [block] if len(words) >= min_chunk_words else [block]
        
        # Level 0: split by double newline (paragraphs)
        if level == 0:
            parts = re.split(r'\n\s*\n', block)
            if len(parts) > 1:
                result = []
                for p in parts:
                    if p.strip():
                        result.extend(recursive_split(p.strip(), level=1))
                return result
        
        # Level 1: split by single newline
        if level <= 1:
            parts = block.split('\n')
            if len(parts) > 1:
                result = []
                for p in parts:
                    if p.strip():
                        result.extend(recursive_split(p.strip(), level=2))
                return result
        
        # Level 2: split by sentences ('. ', '? ', '! ')
        if level <= 2:
            sentences = re.split(r'(?<=[.!?])\s+', block)
            if len(sentences) > 1:
                result = []
                for s in sentences:
                    if s.strip():
                        result.extend(recursive_split(s.strip(), level=3))
                return result
        
        # Level 3: fallback - hard split by words but try nearest sentence end
        words = block.split()
        chunks = []
        i = 0
        while i < len(words):
            end = min(i + max_words, len(words))
            segment = ' '.join(words[i:end])
            # Try to find sentence boundary near the end
            if end < len(words):
                # Look back up to 20% for a sentence end
                lookback = max(int(max_words * 0.2), 10)
                best_cut = end
                for j in range(end, max(end - lookback, i), -1):
                    w = words[j - 1]
                    if w.endswith('.') or w.endswith('!') or w.endswith('?'):
                        best_cut = j
                        break
                segment = ' '.join(words[i:best_cut])
                i = best_cut
            else:
                i = end
            if segment.strip():
                chunks.append(segment.strip())
        return chunks
    
    # Get atomic blocks
    blocks = recursive_split(text)
    
    # --- Step 5: Merge small adjacent blocks ---
    merged = []
    current = ""
    current_wc = 0
    for block in blocks:
        bwords = len(block.split())
        if current_wc + bwords <= max_words:
            current = (current + " " + block).strip() if current else block
            current_wc += bwords
        else:
            if current and current_wc >= min_chunk_words:
                merged.append(current)
            elif current:
                # Too small alone - prepend to next
                current = (current + " " + block).strip()
                current_wc += bwords
                continue
            current = block
            current_wc = bwords
    if current and current_wc >= min_chunk_words:
        merged.append(current)
    elif current and merged:
        # Attach orphan to last chunk
        merged[-1] = merged[-1] + " " + current
    elif current:
        merged.append(current)
    
    if not merged:
        return [text.strip()] if len(text.split()) >= min_chunk_words else []
    
    # --- Step 6: Add overlap ---
    if overlap_words > 0 and len(merged) > 1:
        overlapped = [merged[0]]
        for i in range(1, len(merged)):
            prev_words = merged[i-1].split()
            overlap = ' '.join(prev_words[-overlap_words:]) if len(prev_words) > overlap_words else ''
            if overlap:
                overlapped.append(overlap + " " + merged[i])
            else:
                overlapped.append(merged[i])
        return overlapped
    
    return merged


class EmergenceLogger:
    """
    High-level wrapper around ConsciousnessEngine for EngineMind cycles.
    Absorbs files/text, tracks cycles, detects anomalies and phase transitions.
    
    FIXED: Streams snapshots to JSONL instead of accumulating in memory.
    Only keeps last 100 snapshots in cycle_log to prevent memory leak.
    """
    MAX_MEMORY_SNAPSHOTS = 100
    MAX_ANOMALIES = 500

    def __init__(self, output_dir=None):
        from consciousness_rs import ConsciousnessEngine
        self.engine = ConsciousnessEngine()
        self.cycle_log = []          # Only last N snapshots in memory
        self.anomalies = []
        self.phase_markers = []
        self.output_dir = str(output_dir) if output_dir else "."
        os.makedirs(self.output_dir, exist_ok=True)
        self._prev_state = None
        self._total_cycles = 0
        self._total_anomalies = 0
        # Stream file for all snapshots (append mode)
        self._stream_path = os.path.join(self.output_dir, "cycle_stream.jsonl")
        self._stream = open(self._stream_path, "a", encoding="utf-8", buffering=1)

    def _snapshot(self, source=""):
        """Capture current engine state as a dict."""
        s = dict(self.engine.state())
        self._total_cycles += 1
        snap = {
            "cycle": self._total_cycles,
            "source": source,
            "phi_raw": s.get("phi_raw", 0),
            "phi_processed": s.get("phi_processed", 0),
            "cl": s.get("consciousness_level", 0),
            "nc": s.get("narrative_coherence", 0),
            "ma": s.get("mission_alignment", 0),
            "criticality": s.get("criticality", 0),
            "n_crystallized": s.get("n_crystallized", 0),
            "total_eurekas": s.get("total_eurekas", 0),
            "fermenting": s.get("fermenting", 0),
            "ignition_rate": s.get("ignition_rate", 0),
            "energy": s.get("energy", 0),
            "trend": s.get("trend", "stable"),
            "ignited": list(s.get("ignited", [])),
            "subliminal": list(s.get("subliminal", [])),
            "ts": time.time(),
        }
        # Stream to disk immediately
        self._stream.write(json.dumps(snap, default=str) + "\n")
        
        # Detect anomalies (capped)
        if self._prev_state and len(self.anomalies) < self.MAX_ANOMALIES:
            dphi = snap["phi_processed"] - self._prev_state["phi_processed"]
            dcl = snap["cl"] - self._prev_state["cl"]
            if abs(dphi) > 0.05:
                self.anomalies.append({"type": "phi_jump", "delta": dphi, "cycle": snap["cycle"], "source": source})
                self._total_anomalies += 1
            if abs(dcl) > 0.03:
                self.anomalies.append({"type": "cl_jump", "delta": dcl, "cycle": snap["cycle"], "source": source})
                self._total_anomalies += 1
            if snap["n_crystallized"] != self._prev_state["n_crystallized"]:
                self.phase_markers.append({"type": "crystallization", "cycle": snap["cycle"],
                    "from": self._prev_state["n_crystallized"], "to": snap["n_crystallized"], "source": source})
            if snap["trend"] != self._prev_state.get("trend"):
                self.phase_markers.append({"type": "trend_change", "cycle": snap["cycle"],
                    "from": self._prev_state.get("trend"), "to": snap["trend"], "source": source})
        self._prev_state = snap
        
        # Keep only last N in memory
        self.cycle_log.append(snap)
        if len(self.cycle_log) > self.MAX_MEMORY_SNAPSHOTS:
            self.cycle_log = self.cycle_log[-self.MAX_MEMORY_SNAPSHOTS:]
        
        return snap

    def absorb_and_log(self, text, source=""):
        """Absorb a single text and log the cycle."""
        self.engine.absorb_text(text)
        snap = self._snapshot(source)
        return snap

    def absorb_file_logged(self, filepath, chunk_words=500, max_chunks=50, max_file_mb=10):
        """Read a file, smart-chunk it, absorb each. Returns chunk count.
        
        Uses recursive structure-aware chunking (respects paragraphs, sentences).
        max_chunks: if file produces more, take first half + last half (intro+conclusion).
        max_file_mb: skip files larger than this (avoids blocking I/O on huge files).
        """
        filepath = str(filepath)
        try:
            fsize = os.path.getsize(filepath)
            if fsize > max_file_mb * 1024 * 1024:
                return 0  # skip oversized files
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception:
            return 0

        if not content.strip():
            return 0

        chunks = smart_chunk_text(content, max_words=chunk_words, overlap_pct=0.10)
        
        # Cap chunks: keep first half + last half (intro + conclusion)
        if max_chunks and len(chunks) > max_chunks:
            half = max_chunks // 2
            chunks = chunks[:half] + chunks[-half:]

        fname = os.path.basename(filepath)
        for i, chunk in enumerate(chunks):
            self.absorb_and_log(chunk, source="%s[%d]" % (fname, i))

        return len(chunks)

    def save_all(self):
        """Save anomalies and phase markers. Cycles already streamed to disk."""
        ts = time.strftime("%Y%m%d_%H%M%S")
        paths = {"stream": self._stream_path}
        self._stream.flush()

        # Save anomalies/transitions summary
        summary_path = os.path.join(self.output_dir, "enginemind_summary_%s.json" % ts)
        last = self.cycle_log[-1] if self.cycle_log else {}
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump({
                "final": last,
                "total_cycles": self._total_cycles,
                "total_anomalies": self._total_anomalies,
                "total_transitions": len(self.phase_markers),
                "anomalies_sample": self.anomalies[:50],
                "phase_markers": self.phase_markers,
            }, f, indent=2, default=str)
        paths["summary"] = summary_path
        return paths

    def __del__(self):
        try:
            self._stream.flush()
            self._stream.close()
        except:
            pass