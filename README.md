# Read first

- Constantly hitting a 429 error (rate limit) can get your GH Copilot subscription suspended. Knowing this is important to protect yourself. It isn't just for this project, people can get banned by using the LM API; see this [reddit thread](https://www.reddit.com/r/RooCode/s/3VXA5FUpA5).
- It seems you can hit error 429 quicker with the newer Claude 3.7 Sonnet models (they probably smaller quotas, and 3.7 runs faster than 3.5).
- Take advantage of the built-in token/rate limiter, to avoid excessive usage and possible termination.

If you want to know more about GH Copilot suspension risk, read this [GitHub issue comment](https://github.com/RooVetGit/Roo-Code/issues/1203#issuecomment-2692865792)

# Copilot More Continued

`Copilot More Continued` maximizes the value of your GitHub Copilot subscription by exposing models like Claude-3.7-Sonnet for use in agentic coding tools such as Cline, or any tool that supports bring-your-own-model setups. Unlike costly pay-as-you-go APIs, this approach lets you leverage these powerful models affordably.

## Ethical Use

- Respect the GitHub Copilot terms of service.
- Only use the API for coding tasks.
- Be mindful of the risk of being banned by GitHub Copilot for misuse.

## 🏃‍♂️ How to Run

1. Get the refresh token

   A refresh token is used to get the access token, and it contains various permissions to your account. You can get the refresh token by following the steps below:

    - Run the following command and note down the returned `device_code` and `user_code`:

    ```bash
    # 01ab8ac9400c4e429b23 is the client_id for the VS Code
    curl https://github.com/login/device/code -X POST -d 'client_id=01ab8ac9400c4e429b23&scope=user:email'
    ```

    - Open [GitHub Device Login](https://github.com/login/device/) and enter the `user_code`.

    - Replace `YOUR_DEVICE_CODE` with the `device_code` obtained earlier and run:

    ```bash
    curl https://github.com/login/oauth/access_token -X POST -d 'client_id=01ab8ac9400c4e429b23&scope=user:email&device_code=YOUR_DEVICE_CODE&grant_type=urn:ietf:params:oauth:grant-type:device_code'
    ```

    - Note down the `access_token` starting with `gho_`.

1. Install and run copilot more continued

   - Bare metal installation:

    ```bash
    git clone https://github.com/RobbyV2/copilot-more-continued.git
    cd copilot-more-continued
    # Install dependencies
    poetry install
    # Run the server
    poetry run uvicorn copilot_more_continued.server:app --host 0.0.0.0 --port 15432
    ```

   - Docker Compose installation:

    ```bash
    git clone https://github.com/RobbyV2/copilot-more-continued.git
    cd copilot-more-continued
    # Run the server
    docker-compose up --build
    ```

  Alternatively, use the `refresh-token.sh` script to automate the above.

## ⚙️ Configuration

The application allows you to customize behavior through environment variables or a `.env` file. Available configuration options:

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| GitHub Refresh Token | `REFRESH_TOKEN` | None (Required) | GitHub Copilot refresh token |
| Log Level | `LOGURU_LEVEL` | INFO | Sets the logging level for the application |
| Editor Version | `EDITOR_VERSION` | vscode/1.97.2 | Editor version for API requests |
| Max Tokens | `MAX_TOKENS` | 10240 | Maximum tokens in responses |
| Timeout | `TIMEOUT_SECONDS` | 300 | API request timeout in seconds |
| Record Traffic | `RECORD_TRAFFIC` | false | Whether to record API traffic |
| Sleep Between Calls | `SLEEP_BETWEEN_CALLS` | 0.0 | Sleep duration in seconds between API calls |
| API Keys | `API_KEYS` | None | Optional comma-delimited list of valid API keys |

See `.env.example` for a template configuration file. You can `cp .env.example .env` and modify the values as needed.

### Running Tests

Unit tests require no environment variables to run:

```bash
poetry install  # Install dependencies if not already done
poetry run pytest  # Run all tests
poetry run pytest -v  # Run with verbose output
poetry run pytest tests/test_server_auth.py  # Run specific test file
```

### API Key Validation

When `API_KEYS` is set, the server enforces API key validation on all requests. Keys should be provided in the Authorization header using the Bearer scheme:

```bash
curl http://localhost:15432/chat/completions \
  -H "Authorization: Bearer YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello"}]}'
```

If no API keys are configured, the server accepts any API key to maintain compatibility with existing clients.

Example API_KEYS configuration:

```env
API_KEYS=sk-xxx,key1,key2
```

### Rate Limiting Configuration

Rate limiting is optional and only applied to models that you explicitly configure. You can define rate limits for specific models using a `rate_limits.json` file in the project root directory:

```json
{
  "claude-3.7-sonnet": [
    {
      "window_minutes": 1,
      "total_tokens": 50000,
      "input_tokens": 50000,
      "output_tokens": 5000,
      "requests": 5,
      "behavior": "delay"
    },
    {
      "window_minutes": 60,
      "total_tokens": 500000,
      "input_tokens": 500000,
      "output_tokens": 50000,
      "requests": 100,
      "behavior": "error"
    }
  ]
}
```

Configuration options:

- `window_minutes`: Time window in minutes
- `total_tokens`: Max total tokens in window (optional)
- `input_tokens`: Max input tokens in window (optional)
- `output_tokens`: Max output tokens in window (optional)
- `requests`: Max requests in window (optional)
- `behavior`: What to do when limit is hit: "delay" or "error"

**⚠️ Warning:** The default `rate_limits.json` is just an example and not necessarily suitable for production use. You should adjust these limits based on your actual usage patterns.

Notes:

- Rate limits are only applied to models listed in the configuration file
- Models not listed in the file will have no rate limits
- You must specify at least one of: total_tokens, input_tokens, output_tokens, or requests
- Changes to rate limits require restarting the server to take effect

### Additional Rate Control

While rate limits help control usage within time windows, sometimes you may need finer control over request spacing. The `SLEEP_BETWEEN_CALLS` setting introduces a fixed delay between API calls, which can help prevent burst requests when the API responds very quickly. This is particularly useful when:

- You want to ensure a minimum time gap between requests regardless of response speed
- You need to prevent rapid successive requests that might trigger rate limits
- You want to maintain a more consistent, predictable request pattern

Example: Setting `SLEEP_BETWEEN_CALLS=1.0` ensures at least 1 second between each API call, even if the API responds faster.

## ✨ Magic Time

Now you can connect Cline or any other AI client to `http://localhost:15432` and start coding with the power of GPT-4o and Claude-3.5-Sonnet without worrying about the cost.

### 🚀 Cline Integration

1. Install Cline `code --install-extension saoudrizwan.claude-dev`
2. Open Cline and go to the settings
3. Set the following:
     - **API Provider**: `OpenAI Compatible`
     - **API URL**: `http://localhost:15432`
     - **API Key**: `anything`
     - **Model**: `gpt-4o`, `claude-3.7-sonnet`, `o1`, `o3-mini`

## 🔍 Debugging

For troubleshooting integration issues, you can enable traffic logging to inspect the API requests and responses.

### Traffic Logging

To enable logging, set the `RECORD_TRAFFIC` environment variable to `true`:

```bash
RECORD_TRAFFIC=true poetry run uvicorn copilot-more-continued.server:app --port 15432
```

Alternatively, you can add `RECORD_TRAFFIC=true` to your `.env` file.

All traffic will be logged to files in the current directory with the naming pattern: copilot_traffic_YYYYMMDD_HHMMSS.mitm

Attach this file when reporting issues. Please zip the original file that ends with the '.mitm' extension and upload to the GH issues.

Note: the Authorization header has been redacted, so the refresh token won't be leaked.

## 🤔 Limitations

Currently, images are not supported, although it may be possible as a few models (e.g. gpt-4o) now support images.
