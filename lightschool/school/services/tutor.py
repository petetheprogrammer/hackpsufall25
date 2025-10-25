import json
import requests
import random
import re
import ast
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Ollama local generate endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"

def load_tutor_rules():
    """Load tutor rules JSON."""
    file_path = BASE_DIR / 'data' / 'tutor_rules.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_rule_based_reply(message, subject, grade, locale):
    """Get fallback reply from rules."""
    rules = load_tutor_rules()
    loc_rules = rules.get(locale, {})
    key = f"{subject}:{message.lower().split()[0]}"  # simple heuristic
    if key in loc_rules:
        return random.choice(loc_rules[key])
    # default
    return "Keep practicing! You're doing great." if locale == 'en' else "¡Sigue practicando! Lo estás haciendo genial."


def _extract_arithmetic_expression(text: str) -> str | None:
    """Try to extract a simple arithmetic expression from text.

    This converts common words like 'plus' -> '+' and then looks for a sequence
    of digits/operators. Returns the expression string or None.
    """
    if not text or not re.search(r"\d", text):
        return None
    t = text.lower()
    # word -> symbol map
    words = {
        r"plus": "+",
        r"minus": "-",
        r"times|multiplied by|multiply by": "*",
        r"x\b": "*",
        r"divided by|over|divide by": "/",
        r"what is|what's|calculate|compute|=": "",
        r"\?": "",
    }
    for pat, rep in words.items():
        t = re.sub(pat, rep, t)
    # keep only digits, whitespace and arithmetic symbols/parentheses/dot
    m = re.search(r"[0-9\s\+\-\*\/\(\)\.]+", t)
    if not m:
        return None
    expr = m.group(0).strip()
    # quick sanity: must contain at least one operator
    if not re.search(r"[\+\-\*\/]", expr):
        return None
    return expr


def _safe_eval(expr: str) -> float | int:
    """Safely evaluate a simple arithmetic expression using ast parsing.

    Allows only numeric constants and + - * / and parentheses.
    Raises ValueError on disallowed nodes or parse errors.
    """
    node = ast.parse(expr, mode='eval')

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant):
            if isinstance(n.value, (int, float)):
                return n.value
            raise ValueError("Invalid constant")
        if isinstance(n, ast.BinOp):
            left = _eval(n.left)
            right = _eval(n.right)
            if isinstance(n.op, ast.Add):
                return left + right
            if isinstance(n.op, ast.Sub):
                return left - right
            if isinstance(n.op, ast.Mult):
                return left * right
            if isinstance(n.op, ast.Div):
                return left / right
            raise ValueError("Operator not allowed")
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            val = _eval(n.operand)
            return +val if isinstance(n.op, ast.UAdd) else -val
        # disallow everything else
        raise ValueError("Disallowed expression")

    return _eval(node)

def get_ollama_reply(message, subject, grade, locale):
    """Get reply from Ollama."""
    # Stronger system prompt: require a single short JSON reply with no chain-of-thought.
    # We ask the model to output ONLY a single JSON object on the very first line like:
    # {"answer":"..."}
    # If it cannot comply, it should output an empty JSON with answer set to an empty string.
    system_prompt = (
        "You are Lumi, a cheerful K–5 tutor. Respond ONLY with a single JSON object on the first line: "
        '{"answer":"<one short kid-friendly sentence>"}.'
        f" No explanations, no chain-of-thought, no step-by-step. Use language: {locale}. Keep the answer under 140 characters."
    )
    user_prompt = f"Subject: {subject}, Grade: {grade}. Question: {message}\nReturn only JSON on the first line."
    payload = {
        "model": "deepseek-r1:1.5b",
        "prompt": f"{system_prompt}\n{user_prompt}",
        "stream": False,
        # prefer concise output; allow reasonable time but rely on fallback if slow
        "options": {"num_predict": 100, "max_output_tokens": 150}
    }
    try:
        # Allow more time for local inference but keep a practical timeout so UI can fall back
        response = requests.post(OLLAMA_URL, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Ollama's API may return the text in different fields; try several
            reply = ''
            if isinstance(data, dict):
                reply = data.get('response') or data.get('output') or ''
                # some responses include outputs list
                if not reply and 'outputs' in data and isinstance(data['outputs'], list) and data['outputs']:
                    # join text parts if present
                    parts = []
                    for o in data['outputs']:
                        if isinstance(o, dict):
                            text = o.get('content') or o.get('text') or o.get('response')
                            if text:
                                parts.append(text)
                    reply = '\n'.join(parts)
            reply = (reply or '').strip()
            # Remove chain-of-thought markers like <think>...</think>
            # Remove any complete <think>...</think> blocks, then strip stray tags
            reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.S)
            reply = reply.replace('<think>', '').replace('</think>', '')
            # Try to parse a JSON object from the model's output (preferred)
            first_line = reply.splitlines()[0].strip() if reply.splitlines() else reply
            parsed_answer = None
            try:
                # If the model followed instruction, first_line should be JSON
                obj = json.loads(first_line)
                if isinstance(obj, dict) and 'answer' in obj and isinstance(obj['answer'], str):
                    parsed_answer = obj['answer'].strip()
            except Exception:
                parsed_answer = None

            if parsed_answer:
                # enforce shortness
                if len(parsed_answer) > 140:
                    parsed_answer = parsed_answer[:137].rstrip() + '...'
                return parsed_answer

            # If JSON parse failed, save the raw reply to a debug log for analysis, then return None
            try:
                logs_dir = BASE_DIR / 'logs'
                logs_dir.mkdir(parents=True, exist_ok=True)
                log_file = logs_dir / 'tutor_raw_responses.log'
                with open(log_file, 'a', encoding='utf-8') as lf:
                    lf.write('---\n')
                    lf.write(f'timestamp: {__import__("datetime").datetime.utcnow().isoformat()}Z\n')
                    lf.write(f'subject: {subject} grade: {grade} locale: {locale}\n')
                    lf.write(f'message: {message}\n')
                    lf.write('raw_reply:\n')
                    lf.write(reply + '\n')
            except Exception:
                # never fail because of logging
                pass

            return None
    except:
        pass
    return None

def get_tutor_reply(message, subject, grade, locale):
    """Get tutor reply, try Ollama first, fallback to rules."""
    # Short-circuit: if this is a simple arithmetic question, answer immediately
    expr = _extract_arithmetic_expression(message)
    if expr:
        try:
            val = _safe_eval(expr)
            # format: if integer-valued, show as int
            if isinstance(val, float) and val.is_integer():
                val = int(val)
            return {"reply": str(val), "source": "calculator"}
        except Exception:
            # fall through to normal behavior
            pass

    reply = get_ollama_reply(message, subject, grade, locale)
    source = "ollama" if reply else "rules"
    if not reply:
        reply = get_rule_based_reply(message, subject, grade, locale)
    return {"reply": reply, "source": source}