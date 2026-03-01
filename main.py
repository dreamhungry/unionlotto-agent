import os
import sys
import json
from openai import OpenAI
from scraper import get_ssq_history

def load_config_file():
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"错误：配置文件 {config_path} 不存在。")
        sys.exit(1)
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"错误：配置文件 {config_path} 格式不正确，请检查 JSON 语法。")
        sys.exit(1)
    except Exception as e:
        print(f"错误：读取配置文件失败: {e}")
        sys.exit(1)

def get_config():
    config_data = load_config_file()
    
    llm_config = config_data.get("llm", {})
    scraper_config = config_data.get("scraper", {})
    prediction_config = config_data.get("prediction", {})
    
    api_key = llm_config.get("api_key")
    base_url = llm_config.get("base_url", "https://api.openai.com/v1")
    model = llm_config.get("model", "gpt-3.5-turbo")
    history_count = scraper_config.get("history_count", 30)
    prediction_count = prediction_config.get("count", 1)
    
    if not api_key or api_key == "your_api_key_here":
        print("错误：未设置 API Key。请在 config.json 文件中配置您的 llm.api_key。")
        sys.exit(1)
        
    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "history_count": int(history_count),
        "prediction_count": int(prediction_count)
    }

def format_history_data(history):
    formatted_data = []
    for item in history:
        red_balls_str = ", ".join(item['red_balls'])
        formatted_data.append(f"期号: {item['issue']} | 红球: {red_balls_str} | 蓝球: {item['blue_ball']}")
    return "\n".join(formatted_data)

def main():
    config = get_config()
    
    print(f"正在抓取最近 {config['history_count']} 期的双色球数据...")
    history = get_ssq_history(config['history_count'])
    
    if not history:
        print("未能获取到历史数据，程序退出。")
        return

    print(f"成功获取 {len(history)} 条数据。正在请求 LLM 进行预测...")
    
    history_text = format_history_data(history)
    print(f"历史数据是: \n{history_text}")
    prompt = f"""
你是一个专业的彩票分析师。以下是最近 {len(history)} 期的双色球开奖结果（时间倒序排列）：

{history_text}

请根据这些历史数据，分析红球和蓝球的走势（如冷热号、遗漏值、连号等），预测下一期的开奖号码。
双色球规则：红球从01-33中选6个，蓝球从01-16中选1个。

请直接输出 {config['prediction_count']} 组你认为最有可能中奖的号码，每组格式如下：
第 N 组：
红球：XX, XX, XX, XX, XX, XX
蓝球：XX

并简要说明你的分析理由（不超过200字）。
"""

    client = OpenAI(
        api_key=config['api_key'],
        base_url=config['base_url']
    )

    try:
        response = client.chat.completions.create(
            model=config['model'],
            messages=[
                {"role": "system", "content": "你是一个乐于助人的彩票分析助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        print("\n" + "="*30)
        print("LLM 预测结果：")
        print("="*30)
        print(content)
        print("="*30)
        
    except Exception as e:
        print(f"调用 LLM 失败: {e}")

if __name__ == "__main__":
    main()
