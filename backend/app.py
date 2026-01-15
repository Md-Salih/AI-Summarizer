"""Flask Web Application for Text Summarization."""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from inference import PretrainedInference
import os
import torch
import json
import time
from datetime import datetime
from typing import Any, Callable, cast

# Optional AI-generated text detector (aidetector)
_ai_detector_cache: dict[str, Any] = {
    "config": None,
    "model": None,
    "vocab": None,
    "tokenizer": None,
    "error": None,
}


def _get_ai_detector_config():
    model_file = os.getenv("AI_DETECTOR_MODEL_FILE", "./models/aidetector.model").strip()
    vocab_file = os.getenv("AI_DETECTOR_VOCAB_FILE", "./models/aidetector.vocab").strip()
    token_model = os.getenv("AI_DETECTOR_TOKEN_MODEL", "xx_ent_wiki_sm").strip()
    download = os.getenv("AI_DETECTOR_DOWNLOAD_SPACY", "false").strip().lower() in {"1", "true", "yes"}
    threshold_env = os.getenv("AI_DETECTOR_THRESHOLD", "0.5").strip()
    try:
        threshold_default = float(threshold_env)
    except Exception:
        threshold_default = 0.5
    return {
        "model_file": model_file,
        "vocab_file": vocab_file,
        "token_model": token_model,
        "download": download,
        "threshold_default": threshold_default,
    }


def _load_ai_detector():
    """Lazy-load aidetector artifacts. Returns (available: bool, reason: str|None)."""
    cfg = _get_ai_detector_config()
    cfg_key = (cfg["model_file"], cfg["vocab_file"], cfg["token_model"], cfg["download"])

    if _ai_detector_cache["config"] == cfg_key and (
        _ai_detector_cache["model"] is not None or _ai_detector_cache["error"] is not None
    ):
        return _ai_detector_cache["model"] is not None, _ai_detector_cache["error"]

    _ai_detector_cache.update({
        "config": cfg_key,
        "model": None,
        "vocab": None,
        "tokenizer": None,
        "error": None,
    })

    try:
        from aidetector.aidetectorclass import AiDetector  # type: ignore
        from aidetector.inference import load_vocab  # type: ignore
        from aidetector.tokenization import get_tokenizer  # type: ignore
    except Exception as e:
        _ai_detector_cache["error"] = f"aidetector not available: {e}"
        return False, _ai_detector_cache["error"]

    if not os.path.exists(cfg["model_file"]):
        _ai_detector_cache["error"] = (
            f"AI detector model file not found: {cfg['model_file']}. "
            "Train one with: aidetector train ..."
        )
        return False, _ai_detector_cache["error"]

    if not os.path.exists(cfg["vocab_file"]):
        _ai_detector_cache["error"] = (
            f"AI detector vocab file not found: {cfg['vocab_file']}. "
            "Train one with: aidetector train ..."
        )
        return False, _ai_detector_cache["error"]

    try:
        vocab = load_vocab(cfg["vocab_file"])
        tokenizer = get_tokenizer(tokenmodel=cfg["token_model"], download=cfg["download"])
        detector_model = AiDetector(len(vocab))
        state = torch.load(cfg["model_file"], map_location="cpu")
        detector_model.load_state_dict(state)
        detector_model.eval()

        _ai_detector_cache["model"] = detector_model
        _ai_detector_cache["vocab"] = vocab
        _ai_detector_cache["tokenizer"] = tokenizer
        return True, None
    except Exception as e:
        _ai_detector_cache["error"] = f"Failed to load AI detector: {e}"
        return False, _ai_detector_cache["error"]


def _aidetector_probability(text: str) -> float:
    detector_model = _ai_detector_cache["model"]
    vocab = _ai_detector_cache["vocab"]
    tokenizer = _ai_detector_cache["tokenizer"]
    if detector_model is None or vocab is None or tokenizer is None or not callable(tokenizer):
        raise RuntimeError("AI detector not loaded")

    vocab_map = cast(dict[str, int], vocab)
    tokenizer_fn = cast(Callable[[str], list[str]], tokenizer)
    tokens = [vocab_map.get(tok, 0) for tok in tokenizer_fn(text)]
    # Ensure minimum length for conv/pool layers
    min_len = 32
    max_len = 512
    if len(tokens) < min_len:
        tokens = tokens + [0] * (min_len - len(tokens))
    if len(tokens) > max_len:
        tokens = tokens[:max_len]

    sequence = torch.tensor([tokens], dtype=torch.long)
    with torch.no_grad():
        output = detector_model(sequence)[0]
        prob = torch.sigmoid(output).item()
    # Clamp to [0,1] just in case
    return float(max(0.0, min(1.0, prob)))

app = Flask(__name__)
CORS(app)  # Enable CORS for React Native app

# Initialize model (loaded once at startup)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Initializing model on {device}...")

preferred_model = os.getenv("SUMMARIZATION_MODEL", "google/flan-t5-base").strip()
fallback_models = [
    preferred_model,
    # FLAN-T5 family (recommended for instruction-following summarization)
    "google/flan-t5-base",
    # Fast, high-quality summarization fallback
    "sshleifer/distilbart-cnn-12-6",
    # Smallest fallback
    "t5-small",
]

model = None
last_error = None

for model_name in fallback_models:
    if not model_name:
        continue
    try:
        print(f"Loading summarization model: {model_name}...")
        model = PretrainedInference(model_name, device=device)
        print("✓ Model loaded successfully")
        break
    except Exception as e:
        last_error = e
        print(f"Warning: Could not load model '{model_name}': {e}")

if model is None:
    print("Error: Could not load any model.")
    print(f"Last error: {last_error}")
    print("Try: pip install transformers torch sentencepiece protobuf")


@app.route('/')
def index():
    """Backend info (frontend runs separately on Vite)."""
    return jsonify({
        "name": "Transformer Summarization API",
        "status": "ok",
        "model_loaded": model is not None,
        "device": device,
        "endpoints": {
            "health": "/api/health",
            "summarize": "/api/summarize",
            "summarize_stream": "/api/summarize/stream",
            "ai_detect": "/api/ai-detect",
        },
        "frontend_hint": "Open the React app (Vite) at http://localhost:3000",
    })


@app.route('/api/ai-detect', methods=['POST'])
def ai_detect():
    """Optional AI-generated text detection via `aidetector`.

    This endpoint is intentionally fail-safe: if `aidetector` or its artifacts are
    not configured, it returns `available: false` (HTTP 200) so the frontend can
    fallback to the existing heuristic without breaking the app.
    """
    data = request.json or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({
            'available': False,
            'reason': 'No text provided',
        }), 400

    cfg = _get_ai_detector_config()
    try:
        threshold = float(data.get('threshold', cfg['threshold_default']))
    except Exception:
        threshold = cfg['threshold_default']

    available, reason = _load_ai_detector()
    if not available:
        return jsonify({
            'available': False,
            'reason': reason or 'AI detector unavailable',
            'hint': 'Configure AI_DETECTOR_MODEL_FILE and AI_DETECTOR_VOCAB_FILE after training.',
        })

    try:
        prob = _aidetector_probability(text)
        return jsonify({
            'available': True,
            'ai_probability': round(prob, 4),
            'ai_percent': int(round(prob * 100)),
            'is_ai': prob >= threshold,
            'threshold': threshold,
            'engine': 'aidetector',
        })
    except Exception as e:
        return jsonify({
            'available': False,
            'reason': f'AI detector inference failed: {e}',
        })


@app.route('/api/summarize', methods=['POST'])
def summarize():
    """
    Generate summary (standard non-streaming endpoint) with optimized parameters.
    """
    try:
        data = request.json
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) < 10:
            return jsonify({'error': 'Text too short (minimum 10 characters)'}), 400
        
        if len(text) > 5000:
            return jsonify({'error': 'Text too long (maximum 5000 characters)'}), 400
        
        # Optimized generation parameters for accuracy
        max_length = data.get('max_length', 150)
        min_length = data.get('min_length', 40)
        num_beams = data.get('num_beams', 8)
        
        if model is None:
            return jsonify({'error': 'Model not loaded. Please install: pip install transformers torch'}), 500
        
        # Generate summary with optimized settings
        start_time = time.time()
        summary = model.summarize(
            text,
            max_length=max_length,
            min_length=min_length,
            num_beams=num_beams,
            length_penalty=2.0,
            no_repeat_ngram_size=3
        )
        elapsed = time.time() - start_time
        
        return jsonify({
            'summary': summary,
            'input_length': len(text),
            'summary_length': len(summary),
            'compression_ratio': round((1 - len(summary) / len(text)) * 100, 1),
            'generation_time': round(elapsed, 2),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in summarize: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/summarize/stream', methods=['POST'])
def summarize_stream():
    """
    Generate summary with token-by-token streaming.
    This powers the animated UI with optimized parameters!
    """
    try:
        data = request.json
        text = data.get('text', '').strip()
        max_length = data.get('max_length', 150)
        
        # Calculate proportional min_length to preserve important details
        # Higher max_length = more detailed summary with better coverage
        # Improved formula: ensures summaries reach target length more consistently
        min_length = max(40, int(max_length * 0.4))
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        def generate():
            """Generator function for Server-Sent Events."""
            try:
                start_time = time.time()
                token_count = 0
                
                # Stream tokens in real-time with improved parameters
                for token_info in model.summarize_streaming(
                    text, 
                    max_length=max_length,
                    min_length=min_length,
                    num_beams=6,
                    length_penalty=2.0,
                    no_repeat_ngram_size=3,
                    repetition_penalty=1.2,
                    early_stopping=True
                ):  # type: ignore
                    token_count += 1
                    total = token_info.get('total', max_length)
                    progress = min(100, int((token_count / total) * 100))
                    
                    event_data = {
                        'token': token_info.get('token', ''),
                        'step': token_count,
                        'progress': progress,
                        'done': False
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                    time.sleep(0.03)  # Smooth animation delay
                
                # Send completion
                elapsed = time.time() - start_time
                completion_data = {
                    'done': True,
                    'progress': 100,
                    'time': round(elapsed, 2)
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                
            except Exception as e:
                print(f"Streaming error: {e}")
                error_data = {'error': str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return Response(generate(), mimetype='text/event-stream',
                       headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'device': device,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("TRANSFORMER SUMMARIZATION - WEB APPLICATION")
    print("=" * 70)
    print(f"\nDevice: {device}")
    print(f"Model loaded: {model is not None}")
    print("\nStarting server...")
    print("Open http://localhost:5000 in your browser")
    print("=" * 70 + "\n")
    
    # Disable auto-reloader to prevent threading issues
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
