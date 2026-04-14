"""
Multi-provider AI service for generating lessons and exercises.
Supports OpenAI-compatible APIs: OpenAI, Grok (xAI), Kimi (Moonshot), DeepSeek, etc.
Also supports Claude (Anthropic) native API.
"""
import json
import httpx
from models import get_db
from validators import validate_exercise, validate_animation_data

# ---- Provider configs (default base URLs) ----
PROVIDER_DEFAULTS = {
    "openai":   {"base_url": "https://api.openai.com/v1",          "model": "gpt-4o-mini"},
    "claude":   {"base_url": "https://api.anthropic.com",           "model": "claude-sonnet-4-20250514"},
    "grok":     {"base_url": "https://api.x.ai/v1",                "model": "grok-3-mini"},
    "kimi":     {"base_url": "https://api.moonshot.cn/v1",          "model": "moonshot-v1-8k"},
    "deepseek": {"base_url": "https://api.deepseek.com/v1",        "model": "deepseek-chat"},
    "custom":   {"base_url": "",                                    "model": ""},
}


async def get_ai_config() -> dict:
    db = await get_db()
    row = await db.execute("SELECT * FROM ai_config WHERE id=1")
    config = dict(await row.fetchone())
    await db.close()
    return config


async def update_ai_config(data: dict):
    db = await get_db()
    fields, values = [], []
    for k in ("provider", "api_key", "base_url", "model"):
        if k in data:
            fields.append(f"{k}=?")
            values.append(data[k])
    values.append(1)
    if fields:
        await db.execute(f"UPDATE ai_config SET {','.join(fields)} WHERE id=?", values)
        await db.commit()
    await db.close()
    return await get_ai_config()


async def _call_openai_compatible(config: dict, system_prompt: str, user_prompt: str) -> str:
    """Call any OpenAI-compatible API (OpenAI, Grok, Kimi, DeepSeek, etc.)."""
    url = f"{config['base_url'].rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}"
    }
    body = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _call_claude(config: dict, system_prompt: str, user_prompt: str) -> str:
    """Call Anthropic Claude API (non-OpenAI format)."""
    url = f"{config['base_url'].rstrip('/')}/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": config["api_key"],
        "anthropic-version": "2023-06-01"
    }
    body = {
        "model": config["model"],
        "max_tokens": 4000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}]
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]


async def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Route to the correct provider based on config."""
    config = await get_ai_config()
    if not config.get("api_key"):
        raise ValueError("AI API key not configured. Please set it in admin settings.")

    provider = config.get("provider", "openai")
    if provider == "claude":
        return await _call_claude(config, system_prompt, user_prompt)
    else:
        return await _call_openai_compatible(config, system_prompt, user_prompt)


def _parse_json_from_llm(text: str) -> dict:
    """Extract JSON from LLM response (handles markdown code blocks)."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # remove ```json
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)


# ====== Prompt Templates ======

LESSON_GENERATION_PROMPT = """你是一个儿童数学教育专家，专门为6-10岁的孩子设计数学教学内容。

请严格按照以下JSON格式生成教学动画数据，不要输出任何其他内容：
{
  "expression": "算式 = 答案",
  "methods": [
    {
      "type": "方法类型",
      "title": "方法名称",
      "steps": [
        {
          "action": "动作类型",
          "narration": "旁白文字（给孩子看的，要简单易懂）",
          ...其他参数
        }
      ]
    }
  ]
}

可用的方法类型(type):
- make_ten: 凑十法（适用于进位加法）
- break_ten: 破十法（适用于退位减法）
- number_line: 数轴法
- counting: 数数法/实物法
- step_by_step: 分步法

可用的动作类型(action):
- show_objects: 显示实物 (需要 left, right, shape 参数)
- split: 拆分数字 (需要 target, parts 参数)
- think_split: 思考拆分 (需要 target, need 参数)
- move_to_left: 移动凑十 (需要 count 参数)
- highlight_ten: 高亮十 (需要 value 参数)
- combine: 合并得到结果 (需要 values, result 参数)
- draw_line: 画数轴 (需要 from, to 参数)
- mark_start: 标记起点 (需要 position 参数)
- jump: 跳跃 (需要 count, direction 参数)
- jump_split: 分段跳跃 (需要 first_jump, second_jump, via 参数)
- mark_end: 标记终点 (需要 position 参数)
- count_on: 接着数 (需要 start, count 参数)
- count_all: 全部数 (需要 sequence 参数)
- show_result: 显示结果 (需要 result 参数)
- decompose: 分解数字 (需要 number, parts 参数)
- subtract_from_ten: 从十里减 (需要 minuend, subtrahend, result 参数)
- remove: 拿走 (需要 count 参数)

要求：
1. 每个算式至少提供2种解法
2. narration语言要童趣、简洁、鼓励性
3. 步骤要细致，适合动画逐步播放
4. 数学必须正确！"""


EXERCISE_GENERATION_PROMPT = """你是一个儿童数学出题专家。请根据要求生成练习题。

请严格按照以下JSON数组格式输出，不要输出任何其他内容：
[
  {
    "type": "fill_blank 或 choice",
    "question": "题目文字，如 8 + 5 = ?",
    "expression": "纯算式，如 8+5",
    "correct_answer": "正确答案数字",
    "options": ["选项1","选项2","选项3","选项4"],
    "solutions": [
      {"method": "方法名", "steps": ["步骤1", "步骤2"]}
    ],
    "hints": ["提示1", "提示2"],
    "difficulty": 1到3的整数
  }
]

注意：
- type为fill_blank时options可以为空数组
- type为choice时必须有4个选项且包含正确答案
- difficulty: 1=简单 2=中等 3=较难
- 数学必须100%正确
- hints要给思路引导，不要直接给答案"""


async def generate_lesson_content(topic: str, expression: str = None) -> dict:
    """Use LLM to generate lesson animation data."""
    user_prompt = f"请为以下主题生成教学动画数据：\n主题：{topic}"
    if expression:
        user_prompt += f"\n示例算式：{expression}"

    try:
        result_text = await call_llm(LESSON_GENERATION_PROMPT, user_prompt)
        data = _parse_json_from_llm(result_text)
        validation = validate_animation_data(data)
        if not validation["valid"]:
            return {"success": False, "errors": validation["errors"], "raw": data}
        return {"success": True, "data": data}
    except json.JSONDecodeError as e:
        return {"success": False, "errors": [f"JSON parse error: {str(e)}"], "raw": result_text}
    except Exception as e:
        return {"success": False, "errors": [str(e)]}


async def generate_exercises(topic: str, count: int = 5, difficulty: int = 1, max_value: int = 20) -> dict:
    """Use LLM to generate exercise questions."""
    user_prompt = f"""请生成 {count} 道练习题：
主题：{topic}
难度：{difficulty}（1=简单 2=中等 3=较难）
数值范围：{max_value}以内
要求：题目类型混合fill_blank和choice"""

    try:
        result_text = await call_llm(EXERCISE_GENERATION_PROMPT, user_prompt)
        exercises = _parse_json_from_llm(result_text)

        validated = []
        errors = []
        for i, ex in enumerate(exercises):
            v = validate_exercise(ex.get("expression", ""), str(ex.get("correct_answer", "")), max_value)
            if v["valid"]:
                validated.append(ex)
            else:
                errors.append(f"Exercise {i+1}: {v['errors']}")

        return {
            "success": len(validated) > 0,
            "exercises": validated,
            "errors": errors,
            "total_generated": len(exercises),
            "total_valid": len(validated),
        }
    except json.JSONDecodeError as e:
        return {"success": False, "errors": [f"JSON parse error: {str(e)}"], "exercises": []}
    except Exception as e:
        return {"success": False, "errors": [str(e)], "exercises": []}
