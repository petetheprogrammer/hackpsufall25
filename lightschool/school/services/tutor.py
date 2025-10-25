import json
import requests
import random
import re
import ast
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

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

def get_ai_reply(message, subject, grade, locale):
    """Get reply from OpenAI API."""
    if not OPENAI_API_KEY:
        print("ERROR: No OpenAI API key found")
        return None
        
    print("\n=== DEBUG: Starting OpenAI Request ===")
    print(f"Message: {message}")
    print(f"Subject: {subject}")
    print(f"Grade: {grade}")
    print(f"Locale: {locale}")
    
    # Construct the system and user messages
    system_msg = (
        "You are Lumi, a cheerful K-5 tutor. You MUST respond with ONLY a single line containing "
        "a JSON object in this EXACT format: {\"answer\":\"your response here\"} where your response "
        f"is one short kid-friendly sentence. Use language: {locale}. Keep the answer under 140 characters."
    )
    
    user_msg = f"Subject: {subject}, Grade: {grade}. Question: {message}"
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        print("Sending request to OpenAI...")
        response = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=10)
        print(f"OpenAI response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                reply = data['choices'][0]['message']['content'].strip()
                print(f"Raw reply: {reply}")
                
                # Try to parse as JSON
                try:
                    parsed = json.loads(reply)
                    if isinstance(parsed, dict) and 'answer' in parsed:
                        return parsed['answer'].strip()
                except:
                    print("Could not parse response as JSON")
                    
            except Exception as e:
                print(f"Error parsing response: {str(e)}")
                
        else:
            print(f"Error from OpenAI API: {response.text}")
            
    except Exception as e:
        print(f"Error making request: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None
    return None

def get_tutor_reply(message, subject, grade, locale):
    """Get tutor reply, try OpenAI first, fallback to rules."""
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

    reply = get_ai_reply(message, subject, grade, locale)
    source = "ai" if reply else "rules"
    if not reply:
        reply = get_rule_based_reply(message, subject, grade, locale)
    return {"reply": reply, "source": source}