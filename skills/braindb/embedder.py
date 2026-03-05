#!/usr/bin/env python3
"""BrainDB Embedding Service — sentence-transformers all-mpnet-base-v2."""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from sentence_transformers import SentenceTransformer
import numpy as np
import time

# Load model once at startup — all-mpnet-base-v2 is the best sentence-transformers model (420MB)
MODEL_NAME = 'all-mpnet-base-v2'
print(f"🧠 Loading embedding model ({MODEL_NAME})...", flush=True)
start = time.time()
model = SentenceTransformer(MODEL_NAME)
print(f"✅ Model loaded in {time.time()-start:.1f}s — dim={model.get_sentence_embedding_dimension()}", flush=True)


def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class EmbeddingHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress request logging

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(content_length))

        if self.path == '/embed':
            # Embed one or more texts
            texts = body.get('texts', [body.get('text', '')])
            if isinstance(texts, str):
                texts = [texts]
            
            embeddings = model.encode(texts, normalize_embeddings=True)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'embeddings': [e.tolist() for e in embeddings],
                'dim': len(embeddings[0]),
                'count': len(embeddings),
            }).encode())

        elif self.path == '/similarity':
            # Compare a query against multiple candidates
            query = body['query']
            candidates = body['candidates']  # list of {id, text}
            
            query_emb = model.encode([query], normalize_embeddings=True)[0]
            candidate_texts = [c['text'] for c in candidates]
            candidate_embs = model.encode(candidate_texts, normalize_embeddings=True)
            
            results = []
            for i, (cand, emb) in enumerate(zip(candidates, candidate_embs)):
                sim = cosine_similarity(query_emb, emb)
                results.append({
                    'id': cand['id'],
                    'text': cand['text'][:100],
                    'similarity': round(sim, 4),
                })
            
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'results': results,
            }).encode())

        elif self.path == '/batch_similarity':
            # Query against pre-computed embeddings (faster for repeated searches)
            query = body['query']
            stored = body['stored']  # list of {id, embedding}
            
            query_emb = model.encode([query], normalize_embeddings=True)[0]
            
            results = []
            for item in stored:
                emb = np.array(item['embedding'])
                sim = cosine_similarity(query_emb, emb)
                results.append({
                    'id': item['id'],
                    'similarity': round(sim, 4),
                })
            
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'results': results[:body.get('maxResults', 10)],
            }).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'model': MODEL_NAME,
                'dim': model.get_sentence_embedding_dimension(),
                'device': 'mps' if hasattr(model, '_target_device') else 'cpu',
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3334
    server = HTTPServer(('0.0.0.0', port), EmbeddingHandler)
    print(f"🔮 Embedding service listening on port {port}", flush=True)
    server.serve_forever()
