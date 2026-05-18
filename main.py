import os
import sys
import json
from openai import OpenAI
from scraper import get_ssq_history


def load_config_file():
    """Load and parse the config.json file."""
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
    """Extract and validate configuration values."""
    config_data = load_config_file()

    llm_config = config_data.get("llm", {})
    scraper_config = config_data.get("scraper", {})
    prediction_config = config_data.get("prediction", {})

    api_key = llm_config.get("api_key")
    base_url = llm_config.get("base_url", "https://api.openai.com/v1")
    # Support both "judge_model" (new) and "model" (legacy) keys
    judge_model = llm_config.get("judge_model") or llm_config.get("model", "gpt-3.5-turbo")
    predict_models = llm_config.get("predict_models", [])
    history_count = scraper_config.get("history_count", 30)
    prediction_count = prediction_config.get("count", 1)

    if not api_key or api_key.lower() == "your_api_key_here":
        print("错误：未设置 API Key。请在 config.json 文件中配置您的 llm.api_key。")
        sys.exit(1)

    return {
        "api_key": api_key,
        "base_url": base_url,
        "judge_model": judge_model,
        "predict_models": predict_models,
        "history_count": int(history_count),
        "prediction_count": int(prediction_count),
    }


def format_history_data(history):
    """Format history data into a readable text block."""
    formatted_data = []
    for item in history:
        red_balls_str = ", ".join(item['red_balls'])
        formatted_data.append(f"期号: {item['issue']} | 红球: {red_balls_str} | 蓝球: {item['blue_ball']}")
    return "\n".join(formatted_data)


def build_predict_prompt(history_text, history_count, prediction_count):
    """Build the prediction prompt for individual predict models."""
    return f"""你是一个专业的彩票分析师。以下是最近 {history_count} 期的双色球开奖结果（时间倒序排列）：

{history_text}

请根据这些历史数据，分析红球和蓝球的走势（如冷热号、遗漏值、连号等），预测下一期的开奖号码。
双色球规则：红球从01-33中选6个，蓝球从01-16中选1个。

请直接输出 {prediction_count} 组你认为最有可能中奖的号码，每组格式如下：
第 N 组：
红球：XX, XX, XX, XX, XX, XX
蓝球：XX

并简要说明你的分析理由（不超过200字）。"""


def build_judge_prompt(history_text, history_count, predictions, prediction_count):
    """Build the judge prompt that includes history data and all model predictions."""
    predictions_text = ""
    for i, (model_name, prediction) in enumerate(predictions, 1):
        predictions_text += f"\n--- 模型 {i}: {model_name} ---\n{prediction}\n"

    return f"""你是一个资深的彩票分析专家和裁判。你的任务是从多个AI模型的预测结果中，综合分析并选出最终的预测号码。

以下是最近 {history_count} 期的双色球开奖结果（时间倒序排列）：

{history_text}

以下是各个AI模型基于上述历史数据给出的预测结果：
{predictions_text}

请你综合以上历史数据和各模型的预测，运用你的专业判断（考虑冷热号分布、遗漏值、号码间距、连号趋势等因素），从这些预测中选择或组合出你认为最优的结果。

双色球规则：红球从01-33中选6个，蓝球从01-16中选1个。

请直接输出 {prediction_count} 组你认为最有可能中奖的号码，每组格式如下：
第 N 组：
红球：XX, XX, XX, XX, XX, XX
蓝球：XX

并简要说明你的综合判断理由（不超过300字），包括你为什么选择/偏向某些模型的结果。"""


def call_llm(client, model, system_prompt, user_prompt):
    """Call LLM API with the given model and prompts."""
    # Models that only support default temperature (1)
    no_temperature_models = ["gpt-5.5"]

    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    if model not in no_temperature_models:
        kwargs["temperature"] = 0.7

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def run_predict_models(client, predict_models, history_text, history_count, prediction_count):
    """Run prediction with each model in predict_models list."""
    predictions = []
    prompt = build_predict_prompt(history_text, history_count, prediction_count)

    for model_name in predict_models:
        print(f"\n正在使用模型 [{model_name}] 进行预测...")
        try:
            result = call_llm(
                client,
                model_name,
                "你是一个乐于助人的彩票分析助手。",
                prompt,
            )
            predictions.append((model_name, result))
            print(f"模型 [{model_name}] 预测完成。")
        except Exception as e:
            print(f"模型 [{model_name}] 调用失败: {e}")

    return predictions


def main():
    config = get_config()

    print(f"正在抓取最近 {config['history_count']} 期的双色球数据...")
    history = get_ssq_history(config['history_count'])

    if not history:
        print("未能获取到历史数据，程序退出。")
        return

    print(f"成功获取 {len(history)} 条数据。")

    history_text = format_history_data(history)
    print(f"历史数据是: \n{history_text}")

    client = OpenAI(
        api_key=config['api_key'],
        base_url=config['base_url'],
    )

    predict_models = config['predict_models']

    if predict_models:
        # Multi-model prediction + judge workflow
        print(f"\n配置了 {len(predict_models)} 个预测模型，启动多模型预测模式...")
        predictions = run_predict_models(
            client, predict_models, history_text,
            config['history_count'], config['prediction_count'],
        )

        if not predictions:
            print("所有预测模型均调用失败，程序退出。")
            return

        # Show individual predictions
        print("\n" + "=" * 50)
        print("各模型预测结果汇总：")
        print("=" * 50)
        for model_name, prediction in predictions:
            print(f"\n--- [{model_name}] ---")
            print(prediction)

        # Judge model makes final decision
        print(f"\n正在使用裁判模型 [{config['judge_model']}] 进行最终裁决...")
        judge_prompt = build_judge_prompt(
            history_text, config['history_count'],
            predictions, config['prediction_count'],
        )

        try:
            final_result = call_llm(
                client,
                config['judge_model'],
                "你是一个资深的彩票分析专家，擅长综合多方分析给出最优判断。",
                judge_prompt,
            )
            print("\n" + "=" * 50)
            print(f"裁判模型 [{config['judge_model']}] 最终预测结果：")
            print("=" * 50)
            print(final_result)
            print("=" * 50)
        except Exception as e:
            print(f"调用裁判模型失败: {e}")
    else:
        # Legacy single-model workflow (no predict_models configured)
        print(f"正在请求 LLM [{config['judge_model']}] 进行预测...")
        prompt = build_predict_prompt(
            history_text, config['history_count'], config['prediction_count'],
        )

        try:
            content = call_llm(
                client,
                config['judge_model'],
                "你是一个乐于助人的彩票分析助手。",
                prompt,
            )
            print("\n" + "=" * 30)
            print("LLM 预测结果：")
            print("=" * 30)
            print(content)
            print("=" * 30)
        except Exception as e:
            print(f"调用 LLM 失败: {e}")


if __name__ == "__main__":
    main()

