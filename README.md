# unionlotto-agent

AI-powered Union Lotto predictor with LLM analysis.

这是一个简单的双色球数据抓取和预测工具，它会自动抓取中彩网的历史开奖数据，并使用 OpenAI 兼容的 LLM API 进行分析和预测。

## Features

1.  **Auto Scraping**: Scrape recent N draws of Union Lotto results from zhcw.com.
2.  **Multi-Model Prediction**: Use multiple LLM models to predict independently, then a judge model selects the best result.
3.  **Single-Model Fallback**: If `predict_models` is not configured, falls back to direct prediction by the judge model.
4.  **Highly Configurable**: Custom API Key, models, API base URL, history count, and prediction count.

## 使用方法

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **配置环境**:
    复制 `config.example.json` 为 `config.json`，然后填入你的 OpenAI API Key 和其他配置：
    
    Windows:
    ```bash
    copy config.example.json config.json
    ```

    Linux/Mac:
    ```bash
    cp config.example.json config.json
    ```

    修改 `config.json`:
    ```json
    {
      "llm": {
        "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxx",
        "base_url": "https://api.openai.com/v1",
        "judge_model": "gpt-4o",
        "predict_models": ["gpt-4o-mini", "deepseek-chat", "claude-3-haiku-20240307"]
      },
      "prediction": {
        "count": 1
      },
      "scraper": {
        "history_count": 30
      }
    }
    ```

    **Configuration details:**
    - `llm.judge_model`: The model used for final judgment (required).
    - `llm.predict_models`: List of models for independent predictions (optional). If omitted or empty, the judge model directly predicts from history data.
    - `prediction.count`: Number of prediction groups to output.

3.  **运行程序**:
    ```bash
    python main.py
    ```

## 文件说明

- `main.py`: 主程序入口。
- `scraper.py`: 数据抓取模块。
- `config.json`: 配置文件（请参考 `config.example.json`）。
- `config.example.json`: 配置文件模板。
- `requirements.txt`: 项目依赖。

## 注意事项

- 本工具仅供娱乐和学习使用，彩票中奖纯属概率事件，请理性购彩。
- 抓取数据依赖于中彩网的页面结构，如果网站改版可能会失效。
