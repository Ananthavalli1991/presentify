from typing import Dict, Any, List
import json

def _openai_outline(prompt: str, api_key: str, model: str = "gpt-4o-mini") -> List[Dict[str, Any]]:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    sys = "You are a slide architect. Return only valid JSON that matches the schema."
    schema = {
        "type":"object",
        "properties":{
            "slides":{
                "type":"array",
                "items":{
                    "type":"object",
                    "properties":{
                        "title":{"type":"string"},
                        "bullets":{"type":"array","items":{"type":"string"}},
                        "notes":{"type":"string"}
                    },
                    "required":["title","bullets"]
                }
            }
        },
        "required":["slides"]
    }
    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role":"system","content":sys},
            {"role":"user","content":prompt}
        ],
        response_format={"type":"json_schema","json_schema":{"name":"slides","schema":schema}}
    )
    data = resp.choices[0].message.content
    return json.loads(data)["slides"]

def _anthropic_outline(prompt: str, api_key: str, model: str = "claude-3-5-sonnet-20240620") -> List[Dict[str, Any]]:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    sys = "You are a slide architect. Return only JSON per the schema."
    schema = {
        "name":"slides",
        "schema":{
            "type":"object",
            "properties":{
                "slides":{
                    "type":"array",
                    "items":{
                        "type":"object",
                        "properties":{
                            "title":{"type":"string"},
                            "bullets":{"type":"array","items":{"type":"string"}},
                            "notes":{"type":"string"}
                        },
                        "required":["title","bullets"]
                    }
                }
            },
            "required":["slides"]
        }
    }
    msg = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=0.2,
        system=sys,
        messages=[{"role":"user","content":prompt}],
        response_format={"type":"json_schema","json_schema":schema}
    )
    import json
    return json.loads(msg.content[0].text)["slides"]

def _gemini_outline(prompt: str, api_key: str, model: str = "gemini-1.5-flash") -> List[Dict[str, Any]]:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    m = genai.GenerativeModel(model)
    resp = m.generate_content(f"""Return strictly JSON with key "slides" as described:
{{
  "slides":[
    {{"title": "...", "bullets": ["...","..."], "notes":"... (optional)"}}
  ]
}}
---
{prompt}
""")
    import json, re
    txt = resp.text.strip()
    mobj = re.search(r'\{[\s\S]*\}\s*$', txt)
    if not mobj:
        raise ValueError("Gemini response did not contain JSON.")
    return json.loads(mobj.group(0))["slides"]

def build_outline(text: str, guidance: str, provider: str, api_key: str) -> List[Dict[str, Any]]:
    guide = guidance.strip() if guidance else ""
    prompt = f"""You will convert the following text into a slide deck outline.
- Choose a reasonable number of slides (5–20 typically) based on density.
- Prefer concise, scannable bullets (<=8 per slide, <=120 chars each).
- If guidance is provided, tailor tone/structure accordingly.
- Optional: include a "notes" field for speaker notes.

Guidance: {guide or "none"}

SOURCE TEXT (may include markdown):
{text}
"""
    p = (provider or "").lower()
    if p in ("openai","gpt","oai"):
        return _openai_outline(prompt, api_key)
    if p in ("anthropic","claude"):
        return _anthropic_outline(prompt, api_key)
    if p in ("gemini","google"):
        return _gemini_outline(prompt, api_key)
    raise ValueError("Unsupported provider. Use one of: openai, anthropic, gemini.")