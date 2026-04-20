from tools import get_weather
from google import genai
import json, re

def extract_tool_call(text):
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(text[i:])
            if isinstance(obj, dict) and "tool" in obj:
                return obj
        except json.JSONDecodeError:
            pass
    return None

def main():
    client = genai.Client()
    # Describe the tool to the model (or pass a proper tool spec if your SDK supports it)
    tool_desc = {
        "name": "get_weather",
        "description": "Returns current temperature (C) for a city. Args: {\"city\": \"City name\"}"
    }
    system_prompt = (
        "You are an assistant. Available tool:\n"
        f"{json.dumps(tool_desc)}\n\n"
        "If you need to call the tool, reply with a JSON object exactly like:\n"
        '{"tool":"get_weather","args":{"city":"City name"}}\n'
        "Otherwise, answer directly."
    )

    user_query = "Explain the weather in New York City today."
    # First turn: ask the model
    resp = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=system_prompt + "\nUser: " + user_query
    )
    text = resp.text


    tool_call = extract_tool_call(text)
    if tool_call and tool_call.get("tool") == "get_weather":
        city = tool_call.get("args", {}).get("city")
        if not city:
            print("Tool call missing 'city' arg.")
            return
        # Execute your real function
        temp_c = get_weather(city)
        tool_result = {"temperature_c": temp_c}

        # Send tool result back and ask for final answer
        followup = (
            "Tool result (JSON):\n"
            + json.dumps({"tool": tool_call["tool"], "result": tool_result})
            + "\nPlease produce the final user-facing answer using that result. Use anime tone"
        )
        final = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=followup
        )
        print(final.text)
    else:
        print(text)

if __name__ == "__main__":
    main()