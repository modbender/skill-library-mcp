#!/usr/bin/env python3
"""Embedding Service - Flask API for generating embeddings using e5-large-v2."""

import os
import logging
from flask import Flask, jsonify, request
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

MODEL_NAME = os.environ.get("EMBEDDING_MODEL", "intfloat/e5-large-v2")
EMBEDDING_PORT = int(os.environ.get("EMBEDDING_PORT", "8765"))

logger.info(f"Loading model: {MODEL_NAME}")
logger.info("NOTE: First run will download the model from HuggingFace (~1.3GB)")

model = SentenceTransformer(MODEL_NAME)
logger.info(f"Model loaded successfully. Embedding dimension: {model.get_sentence_embedding_dimension()}")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": MODEL_NAME,
        "embedding_dim": model.get_sentence_embedding_dimension()
    })


@app.route("/embed", methods=["POST"])
def embed():
    try:
        data = request.get_json()
        if not data or "texts" not in data:
            return jsonify({"error": "Missing 'texts' field"}), 400

        texts = data["texts"]
        if not isinstance(texts, list):
            return jsonify({"error": "'texts' must be a list"}), 400

        prefix = data.get("prefix", "passage: ")
        prefixed_texts = [f"{prefix}{text}" for text in texts]

        embeddings = model.encode(prefixed_texts, normalize_embeddings=True)

        return jsonify({
            "embeddings": embeddings.tolist(),
            "model": MODEL_NAME,
            "dimension": model.get_sentence_embedding_dimension()
        })

    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/embed_query", methods=["POST"])
def embed_query():
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' field"}), 400

        query = data["query"]
        prefixed_query = f"query: {query}"

        embedding = model.encode([prefixed_query], normalize_embeddings=True)

        return jsonify({
            "embedding": embedding[0].tolist(),
            "model": MODEL_NAME,
            "dimension": model.get_sentence_embedding_dimension()
        })

    except Exception as e:
        logger.error(f"Error generating query embedding: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logger.info(f"Starting embedding service on port {EMBEDDING_PORT}")
    app.run(host="127.0.0.1", port=EMBEDDING_PORT, debug=False)
