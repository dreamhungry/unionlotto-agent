# unionlotto-agent

AI-powered Union Lotto predictor with LLM analysis.

这是一个简单的双色球数据抓取和预测工具，它会自动抓取中彩网的历史开奖数据，并使用 OpenAI 兼容的 LLM API 进行分析和预测。

## 功能

1.  **自动抓取数据**: 从中彩网抓取最近 N 期的双色球开奖结果。
2.  **LLM 分析**: 将历史数据发送给 LLM，让其分析走势并预测下一期号码。
3.  **高度可配置**: 支持自定义 API Key、模型、API 地址以及抓取的历史期数。

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
        "model": "gpt-3.5-turbo"
      },
      "scraper": {
        "history_count": 30
      }
    }
    ```

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
