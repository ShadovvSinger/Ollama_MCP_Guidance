"""
Copyright (c) 2025 ShadowSinger <shadowsinger.tp@gmail.com>
Licensed under the MIT License. See LICENSE file for the full license text.
"""

# 类型提示和基础依赖导入
# typing: 用于类型注解
# - Any: 任意类型
# - List: 列表类型 [item1, item2, ...]
# - Optional: 可选类型 Type | None
# - Dict: 字典类型 {key: value}
from typing import Any, List, Optional, Dict, Union

from pydantic import FileUrl

# json: 用于处理 JSON 数据
import json

# re: 用于正则表达式处理
import re

# httpx: 异步 HTTP 客户端，用于与 Ollama API 通信
import httpx

# pathlib: 用于处理文件路径
from pathlib import Path

# FastMCP: MCP 框架的服务器组件
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server

# text_utils: 用于文本处理和导航
from text_utils import navigate_sections

# 初始化配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 初始化 FastMCP 服务器实例
mcp = FastMCP("Ollama_MCP_Guidance")

# API 配置
OLLAMA_HOST = config['ollama']['host']
USER_AGENT = config['ollama']['user_agent']

# API 端点
API_GET_ENDPOINTS = config['api']['endpoints']['get']
API_POST_ENDPOINTS = config['api']['endpoints']['post']
API_DELETE_ENDPOINTS = config['api']['endpoints']['delete']

# 新增常量定义
OLLAMA_API_DOC_PATH = Path(config['api_doc']['file_path'])

# 辅助函数
# -----------------------------
# 注意：以下函数是基础实现函数，不是直接面向 LLM 的工具函数
# 这些函数将被工具函数（@mcp.tool 装饰的函数）调用来实现具体功能

# TODO: 流式响应支持（暂不实现）
# 注意：当前版本仅实现非流式响应处理
# 1. 流式响应实现将在后续版本中添加
# 2. 届时需要考虑：
#    - 在请求头中添加 Connection: keep-alive
#    - 处理流式响应的数据格式和错误情况
#    - 实现适当的超时和连接管理机制
#    - 添加重试机制和错误恢复策略
# 3. 当前版本专注于实现基础的非流式响应处理

async def make_ollama_get_request(
    endpoint_name: str,
    timeout: float = 30.0
) -> Optional[Dict[str, Any]]:
    """向 Ollama API 发送 GET 请求
    
    注意：这是一个基础实现函数，不是直接的工具函数。
    它将被 @mcp.tool 装饰的工具函数调用来实现具体功能。
    
    Args:
        endpoint_name: 端点名称，必须是 API_GET_ENDPOINTS 中定义的键
        timeout: 请求超时时间（秒）
        
    Returns:
        Optional[Dict[str, Any]]: API 响应数据，如果请求失败则返回 None
        
    Examples:
        # 在工具函数中使用此基础函数
        @mcp.tool()
        async def get_version() -> str:
            result = await make_ollama_get_request("version")
            if result is None:
                return "无法获取版本信息"
            return f"Ollama 版本: {result['version']}"
            
        # 获取运行中的模型列表
        @mcp.tool()
        async def list_models() -> str:
            result = await make_ollama_get_request("ps")
            if result is None:
                return "无法获取模型列表"
            return f"运行中的模型: {result['models']}"
    """
    # 验证端点名称
    if endpoint_name not in API_GET_ENDPOINTS:
        print(f"错误：未知的端点名称 '{endpoint_name}'")
        return None
        
    url = f"{OLLAMA_HOST}{API_GET_ENDPOINTS[endpoint_name]}"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url=url,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"HTTP 请求错误: {str(e)}")
            return None
        except Exception as e:
            print(f"请求处理错误: {str(e)}")
            return None


# 基础 POST 请求函数
async def make_ollama_post_request(
    endpoint_name: str,
    data: Dict[str, Any],
    stream: bool = False,
    timeout: float = 30.0
) -> Optional[Dict[str, Any]]:
    """向 Ollama API 发送 POST 请求
    
    注意：这是一个基础实现函数，不是直接的工具函数。
    它将被具体的 POST 请求函数调用来实现特定功能。
    
    Args:
        endpoint_name: 端点名称，必须是 API_POST_ENDPOINTS 中定义的键
        data: 请求体数据
        stream: 是否使用流式响应
        timeout: 请求超时时间（秒）
        
    Returns:
        Optional[Dict[str, Any]]: API 响应数据，如果请求失败则返回 None
    """
    # 验证端点名称
    if endpoint_name not in API_POST_ENDPOINTS:
        print(f"错误：未知的端点名称 '{endpoint_name}'")
        return None
        
    url = f"{OLLAMA_HOST}{API_POST_ENDPOINTS[endpoint_name]}"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # 添加流式响应参数
    if stream:
        data["stream"] = True
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url=url,
                headers=headers,
                json=data,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"HTTP 请求错误: {str(e)}")
            return None
        except Exception as e:
            print(f"请求处理错误: {str(e)}")
            return None
        
        

# Ollama 工具函数
# -----------------------------
@mcp.tool()
async def get_started_guide() -> str:
    """🌟 Getting Started Guide: Your Gateway to the ask-ollama Project
    
    ⚠️ AI Assistant Note:
    Before proceeding with any operations, it's highly recommended to:
    1. Ask the user if they're new to the project
    2. Explain that this guide will provide comprehensive understanding
    3. Mention that this tool contains essential information for optimal project usage
    
    Why this guide is essential for AI assistants:
    1. Provides complete project overview and capabilities
    2. Contains special instructions for AI-user interactions
    3. Details recommended workflows and best practices
    4. Lists all available tools with practical examples
    5. Explains current limitations and workarounds
    6. Includes API documentation navigation guide
    
    This guide will help you:
    - Better understand user requirements
    - Make informed tool recommendations
    - Navigate API documentation effectively
    - Avoid common pitfalls
    - Provide more accurate assistance
    
    Remember: Running this guide first will significantly enhance your ability to assist users effectively.
    
    Args:
        None: This function does not require any parameters.
        
    Returns:
        str: JSON-formatted string containing comprehensive project documentation and usage guidelines.
    """
    return json.dumps({
        "project": {
            "name": "ask-ollama",
            "type": "MCP (Model Context Protocol) Service",
            "description": "A MCP-based Ollama API interaction service providing standardized interfaces and structured responses",
            "version": "1.0.0",
            "status": "Development"
        },
        "features": {
            "core_features": [
                "Standardized JSON response format",
                "Comprehensive error handling and status feedback",
                "Detailed performance metrics",
                "Simple configuration management",
                "Built-in API documentation navigation"
            ],
            "current_limitations": [
                "No streaming response support (one-time response only)",
                "No multi-turn conversation history",
                "No system prompt support",
                "No context management",
                "No parameter tuning",
                "Some admin-level endpoints not implemented"
            ]
        },
        "available_tools": {
            "server_info": {
                "get_ollama_version": {
                    "description": "Get Ollama server version",
                    "use_case": "Check service availability and version compatibility"
                }
            },
            "model_management": {
                "get_ollama_list": {
                    "description": "List all available models",
                    "use_case": "View installed models"
                },
                "get_running_models": {
                    "description": "Show currently running models",
                    "use_case": "Monitor active model instances"
                },
                "post_show_model": {
                    "description": "Get detailed model information",
                    "use_case": "View model specifications and configuration"
                }
            },
            "model_interaction": {
                "simple_chat": {
                    "description": "Basic chat functionality",
                    "use_case": "Single-turn conversation without context"
                },
                "simple_generate": {
                    "description": "Basic text generation",
                    "use_case": "Single generation without streaming"
                },
                "post_generate_embeddings": {
                    "description": "Generate text vector representations",
                    "use_case": "Using /api/embed endpoint for text embeddings"
                }
            },
            "documentation": {
                "get_api_doc_section": {
                    "description": "Smart API Documentation Navigator",
                    "use_case": "Navigate and retrieve API documentation content using title paths",
                    "features": [
                        "Multi-level title navigation",
                        "Available title suggestions",
                        "Complete context information",
                        "Automatic content length management"
                    ],
                    "example": {
                        "titles": ["API", "Generate a completion", "Parameters"],
                        "explanation": "Retrieve parameter documentation for the completion generation API"
                    }
                }
            }
        },
        "recommended_workflow": {
            "important_notes": {
                "for_users": [
                    "If you're new to Ollama, it's recommended to keep the Ollama backend service logs visible",
                    "This helps understand how each API request is processed in real-time",
                    "You can observe memory usage, model loading status, and potential issues directly",
                    "Make sure to check config.json for proper service configuration"
                ],
                "for_llm_assistants": [
                    "Before demonstrating features or making API calls",
                    "Check config.json for service configuration",
                    "Ask for user's permission to proceed",
                    "Explain what operations will be performed",
                    "Use get_api_doc_section to understand API details",
                    "Wait for user's confirmation before executing commands"
                ]
            },
            "configuration": {
                "important_settings": [
                    {
                        "file": "config.json",
                        "key_settings": [
                            {
                                "path": "ollama.host",
                                "default": "http://localhost:11434",
                                "description": "Ollama service address, modify if running on a different machine"
                            },
                            {
                                "path": "ollama.timeout",
                                "default": 30,
                                "description": "API request timeout in seconds, increase for slow networks or large requests"
                            },
                            {
                                "path": "api_doc.max_length",
                                "default": 8000,
                                "description": "Maximum length for documentation content, adjust based on display requirements"
                            }
                        ],
                        "note": "Review and adjust these settings before starting to use the service"
                    }
                ]
            },
            "initial_setup": [
                {
                    "step": 1,
                    "action": "Check service status",
                    "tool": "get_ollama_version",
                    "purpose": "Verify connection and compatibility"
                },
                {
                    "step": 2,
                    "action": "View available models",
                    "tool": "get_ollama_list",
                    "purpose": "Confirm available models"
                }
            ],
            "basic_usage": [
                {
                    "step": 1,
                    "action": "View model information",
                    "tool": "post_show_model",
                    "purpose": "Understand model capabilities"
                },
                {
                    "step": 2,
                    "action": "Browse API documentation",
                    "tool": "get_api_doc_section",
                    "purpose": "Learn API details before use"
                },
                {
                    "step": 3,
                    "action": "Use chat or generation",
                    "tool": "simple_chat or simple_generate",
                    "purpose": "Interact with model"
                }
            ],
            "advanced_usage": [
                {
                    "step": 1,
                    "action": "Monitor model status",
                    "tool": "get_running_models",
                    "purpose": "Track resource usage"
                },
                {
                    "step": 2,
                    "action": "Generate text embeddings",
                    "tool": "post_generate_embeddings",
                    "purpose": "Generate vector representations using /api/embed"
                },
                {
                    "step": 3,
                    "action": "Explore API Details",
                    "tool": "get_api_doc_section",
                    "purpose": "Get detailed API parameters and usage information",
                    "example": {
                        "use_case": "View completion API parameter documentation",
                        "command": 'await get_api_doc_section(["API", "Generate a completion", "Parameters"])'
                    }
                }
            ]
        },
        "best_practices": [
            "Check server status before operations",
            "Use post_show_model to understand model capabilities",
            "Monitor performance metrics",
            "Review API documentation for parameter details",
            "Use documentation navigator for accurate information",
            "Be aware of endpoint limitations"
        ],
        "development_status": {
            "implemented": [
                "Basic information queries",
                "Model management (read-only operations)",
                "Basic text generation",
                "Single-turn chat",
                "Text embeddings",
                "API Documentation navigation"
            ],
            "not_implemented": [
                "Streaming responses",
                "Multi-turn conversations",
                "System prompts",
                "Parameter tuning",
                "Model management (write operations)"
            ]
        }
    }, indent=2)

@mcp.tool()
async def get_ollama_list() -> str:
    """List all available models in the Ollama server.

    This tool queries the Ollama API's /api/tags endpoint to retrieve information about
    all available models, including both pulled models and their different tags.

    Args:
        None: This function does not require any parameters.

    Returns:
        str: JSON-formatted string containing:
            - List of available models with their details if successful
            - Error details if the request fails or response format is invalid
    """
    result = await make_ollama_get_request("tags")
    
    if result is None:
        return json.dumps({
            "error": "connection_failed",
            "message": "Failed to connect to Ollama service",
            "details": {
                "possible_causes": [
                    "Ollama service not running",
                    "Service address misconfigured",
                    "Network connectivity issues"
                ],
                "configuration": {
                    "check": "Please verify the following in config.json:",
                    "settings": [
                        "ollama.host - Currently set to: " + config['ollama']['host'],
                        "ollama.timeout - Currently set to: " + str(config['ollama']['timeout']) + " seconds"
                    ]
                }
            }
        }, indent=2)
    
    # Validate response format
    if not isinstance(result, dict):
        return json.dumps({
            "error": "invalid_response",
            "message": "Invalid response format from Ollama service",
            "details": {
                "expected_type": "dict",
                "received_type": str(type(result)),
                "response": str(result)
            }
        }, indent=2)
    
    models = result.get("models", [])
    if not isinstance(models, list):
        return json.dumps({
            "error": "invalid_models",
            "message": "Invalid models data format",
            "details": {
                "expected_type": "list",
                "received_type": str(type(models)),
                "response": str(models)
            }
        }, indent=2)
    
    if not models:
        return json.dumps({
            "error": "no_models",
            "message": "No models available",
            "details": {
                "suggestion": "Use 'ollama pull' command to download models"
            }
        }, indent=2)
    
    # Return raw response with proper formatting
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_ollama_version() -> str:
    """Get the version information of the Ollama server.

    This tool queries the Ollama API's /api/version endpoint to retrieve the server version.
    It's useful for checking if the Ollama service is running and verifying its version.

    Args:
        None: This function does not require any parameters.

    Returns:
        str: JSON-formatted string containing:
            - Version information if successful
            - Error details if the request fails
    """
    result = await make_ollama_get_request("version")
    
    if result is None:
        return json.dumps({
            "error": "connection_failed",
            "message": "Failed to connect to Ollama service",
            "details": {
                "possible_causes": [
                    "Ollama service not running",
                    "Service address misconfigured",
                    "Network connectivity issues"
                ],
                "configuration": {
                    "check": "Please verify the following in config.json:",
                    "settings": [
                        "ollama.host - Currently set to: " + config['ollama']['host'],
                        "ollama.timeout - Currently set to: " + str(config['ollama']['timeout']) + " seconds"
                    ]
                }
            }
        }, indent=2)
        
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_running_models() -> str:
    """Get the status of currently running Ollama models.

    This tool queries the Ollama API's /api/ps endpoint to retrieve information about running models,
    similar to the 'ollama ps' command. It validates the response format and provides formatted output.

    Args:
        None: This function does not require any parameters.

    Returns:
        str: JSON-formatted string containing:
            - List of running models with their details if successful
            - Error details if the request fails or response format is invalid
    """
    result = await make_ollama_get_request("ps")
    
    if result is None:
        return json.dumps({
            "error": "connection_failed",
            "message": "Failed to connect to Ollama service",
            "details": {
                "possible_causes": [
                    "Ollama service not running",
                    "Service address misconfigured",
                    "Network connectivity issues"
                ],
                "configuration": {
                    "check": "Please verify the following in config.json:",
                    "settings": [
                        "ollama.host - Currently set to: " + config['ollama']['host'],
                        "ollama.timeout - Currently set to: " + str(config['ollama']['timeout']) + " seconds"
                    ]
                }
            }
        }, indent=2)
    
    # Validate response format
    if not isinstance(result, dict):
        return json.dumps({
            "error": "invalid_response",
            "message": "Invalid response format from Ollama service",
            "details": {
                "expected_type": "dict",
                "received_type": str(type(result)),
                "response": str(result)
            }
        }, indent=2)
    
    models = result.get("models", [])
    if not isinstance(models, list):
        return json.dumps({
            "error": "invalid_models",
            "message": "Invalid models data format",
            "details": {
                "expected_type": "list",
                "received_type": str(type(models)),
                "response": str(models)
            }
        }, indent=2)
    
    if not models:
        return json.dumps({
            "error": "no_models",
            "message": "No running models found",
            "details": {
                "suggestion": "Models may need to be loaded first"
            }
        }, indent=2)
    
    # Return raw response with proper formatting
    return json.dumps(result, indent=2)

@mcp.tool()
async def post_generate_embeddings(
    model: str,
    text: List[str]
) -> str:
    """Generate embeddings for the given text using Ollama API.

    Args:
        model (str): Model name to use for embeddings generation.
               Example: "nomic-embed-text"
        text (List[str]): List of texts to generate embeddings for.
               Example: ["Text 1"] or ["Text 1", "Text 2"]

    Returns:
        str: JSON-formatted string containing:
            - Embeddings data and metadata if successful
            - Error details if the request fails or response format is invalid
    """
    # Prepare request data
    data = {
        "model": model,
        "input": text  # text is already a list
    }
    
    # Send request
    response = await make_ollama_post_request("embed", data)
    
    # Handle errors
    if response is None:
        return json.dumps({
            "error": "connection_failed",
            "message": "Failed to connect to Ollama service",
            "details": {
                "possible_causes": [
                    "Ollama service not running",
                    "Service address misconfigured",
                    "Network connectivity issues"
                ],
                "configuration": {
                    "check": "Please verify the following in config.json:",
                    "settings": [
                        "ollama.host - Currently set to: " + config['ollama']['host'],
                        "ollama.timeout - Currently set to: " + str(config['ollama']['timeout']) + " seconds"
                    ]
                },
                "suggestions": [
                    "Check if Ollama service is running",
                    "Verify service address in config.json",
                    "Check network connectivity",
                    "Try increasing timeout in config.json if network is slow"
                ]
            }
        }, indent=2)
        
    # Validate response format
    if not isinstance(response, dict):
        return json.dumps({
            "error": "invalid_response",
            "message": "Invalid response format from Ollama service",
            "details": {
                "expected_type": "dict",
                "received_type": str(type(response)),
                "response": str(response)
            }
        }, indent=2)
        
    embeddings = response.get("embeddings")
    if embeddings is None:
        return json.dumps({
            "error": "missing_embeddings",
            "message": "No embeddings data found in response",
            "details": {
                "response": response
            }
        }, indent=2)
        
    if not isinstance(embeddings, list) or len(embeddings) == 0:
        return json.dumps({
            "error": "invalid_embeddings",
            "message": "Invalid embeddings format",
            "details": {
                "expected_type": "non-empty list",
                "received_type": str(type(embeddings)),
                "received_length": len(embeddings) if isinstance(embeddings, list) else 0
            }
        }, indent=2)
    
    # Add metadata to response
    result = {
        "embeddings": embeddings,
        "metadata": {
            "count": len(embeddings),
            "dimension": len(embeddings[0]) if embeddings else 0
        }
    }
    
    # Add performance metrics if available
    if "total_duration" in response:
        result["metadata"]["duration_ms"] = response["total_duration"] / 1_000_000
        
    return json.dumps(result, indent=2)

@mcp.tool()
async def simple_chat(
    model: str,
    prompt: str
) -> str:
    """Basic chat interaction with Ollama models.

    This is a simplified chat implementation that provides basic conversation
    capabilities without advanced features. For advanced features, please use
    complex_chat (not implemented yet).

    Limitations:
    1. No conversation history (messages array)
    2. No streaming support (stream)
    3. No system prompts (system role)
    4. No image input support (images)
    5. No format control (format)
    6. No parameter tuning (options)
    7. No keep-alive control (keep_alive)

    Features:
    1. Basic chat: Single message and response
    2. Error handling: Connection and format validation
    3. Performance metrics: Processing time and token statistics

    Args:
        model (str): Model name to use, e.g., "llama2", "mistral"
        prompt (str): User input text

    Returns:
        str: JSON-formatted string containing:
            - Model response and metadata if successful
            - Error details if the request fails or response format is invalid
    """
    # Prepare request data
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }
    
    # Send request
    response = await make_ollama_post_request("chat", data)
    
    # Handle errors
    if response is None:
        return json.dumps({
            "error": "connection_failed",
            "message": "Failed to connect to Ollama service",
            "details": {
                "possible_causes": [
                    "Ollama service not running",
                    "Service address misconfigured",
                    "Network connectivity issues"
                ],
                "configuration": {
                    "check": "Please verify the following in config.json:",
                    "settings": [
                        "ollama.host - Currently set to: " + config['ollama']['host'],
                        "ollama.timeout - Currently set to: " + str(config['ollama']['timeout']) + " seconds"
                    ]
                },
                "suggestions": [
                    "Check if Ollama service is running",
                    "Verify service address in config.json",
                    "Check network connectivity",
                    "Try increasing timeout in config.json if network is slow"
                ]
            }
        }, indent=2)
        
    # Validate response format
    if not isinstance(response, dict):
        return json.dumps({
            "error": "invalid_response",
            "message": "Invalid response format from Ollama service",
            "details": {
                "expected_type": "dict",
                "received_type": str(type(response)),
                "response": str(response)
            }
        }, indent=2)
        
    # Get response message
    message = response.get("message", {})
    if not isinstance(message, dict):
        return json.dumps({
            "error": "invalid_message",
            "message": "Invalid message format in response",
            "details": {
                "expected_type": "dict",
                "received_type": str(type(message)),
                "response": str(response)
            }
        }, indent=2)
        
    content = message.get("content")
    if content is None:
        return json.dumps({
            "error": "missing_content",
            "message": "No content found in response message",
            "details": {
                "suggestions": [
                    "Check if input is appropriate",
                    "Try simplifying the prompt",
                    "Try a different model"
                ],
                "response": str(response)
            }
        }, indent=2)
    
    # Prepare result with response and metadata
    result = {
        "response": {
            "content": content,
            "role": message.get("role", "assistant")
        },
        "metadata": {
            "model": model,
            "input": {
                "role": "user",
                "content": prompt
            }
        }
    }
    
    # Add performance metrics if available
    metrics = {}
    
    if "total_duration" in response:
        metrics["duration_ms"] = response["total_duration"] / 1_000_000
        
    if "prompt_eval_count" in response:
        metrics["input_tokens"] = response["prompt_eval_count"]
        
    if "eval_count" in response:
        metrics["output_tokens"] = response["eval_count"]
        
    if "eval_duration" in response and "eval_count" in response:
        eval_duration_sec = response["eval_duration"] / 1_000_000_000
        tokens_per_sec = response["eval_count"] / eval_duration_sec
        metrics["tokens_per_second"] = round(tokens_per_sec, 1)
    
    if metrics:
        result["metadata"]["performance"] = metrics
    
    return json.dumps(result, indent=2)

@mcp.tool()
async def post_show_model(
    model: str
) -> str:
    """Show detailed information about a model.

    This function retrieves detailed information about the specified model
    through the Ollama API's /api/show endpoint.

    Args:
        model (str): Model name, e.g., "llama2" or "mistral"

    Returns:
        str: JSON-formatted model information including:
            - Basic info (family, parameter size, quantization)
            - Technical parameters (context length, layer count)
            - Configuration (template, system prompt)
            - License and modelfile content
            If the request fails, returns error information in JSON format.
    """
    # Prepare request data
    data = {
        "name": model
    }
    
    # Send request
    response = await make_ollama_post_request("show", data)
    
    # Handle errors
    if response is None:
        return json.dumps({
            "error": "connection_failed",
            "message": "Failed to connect to Ollama service",
            "details": {
                "possible_causes": [
                    "Ollama service not running",
                    "Service address misconfigured",
                    "Network connectivity issues"
                ],
                "configuration": {
                    "check": "Please verify the following in config.json:",
                    "settings": [
                        "ollama.host - Currently set to: " + config['ollama']['host'],
                        "ollama.timeout - Currently set to: " + str(config['ollama']['timeout']) + " seconds"
                    ]
                }
            }
        }, indent=2)
    
    # Return raw response
    return json.dumps(response, indent=2)

@mcp.tool()
async def simple_generate(
    model: str,
    prompt: str
) -> str:
    """Basic text generation with Ollama models.

    This is a simplified implementation of the /api/generate endpoint that provides
    basic text generation capabilities without advanced features.

    Limitations:
    1. No streaming support
    2. No raw mode
    3. No format control
    4. No parameter tuning (options)
    5. No context management

    Features:
    1. Basic generation: Single prompt and response
    2. Error handling: Connection and format validation
    3. Performance metrics: Processing time and token statistics

    Args:
        model (str): Model name to use, e.g., "llama2", "mistral"
        prompt (str): Text prompt for generation

    Returns:
        str: JSON-formatted string containing:
            - Generated text and metadata if successful
            - Error details if the request fails
    """
    # Prepare request data
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    # Send request
    response = await make_ollama_post_request("generate", data)
    
    # Handle errors
    if response is None:
        return json.dumps({
            "error": "connection_failed",
            "message": "Failed to connect to Ollama service",
            "details": {
                "possible_causes": [
                    "Ollama service not running",
                    "Service address misconfigured",
                    "Network connectivity issues"
                ],
                "configuration": {
                    "check": "Please verify the following in config.json:",
                    "settings": [
                        "ollama.host - Currently set to: " + config['ollama']['host'],
                        "ollama.timeout - Currently set to: " + str(config['ollama']['timeout']) + " seconds"
                    ]
                },
                "suggestions": [
                    "Check if Ollama service is running",
                    "Verify service address in config.json",
                    "Check network connectivity",
                    "Try increasing timeout in config.json if network is slow"
                ]
            }
        }, indent=2)
        
    # Validate response format
    if not isinstance(response, dict):
        return json.dumps({
            "error": "invalid_response",
            "message": "Invalid response format from Ollama service",
            "details": {
                "expected_type": "dict",
                "received_type": str(type(response)),
                "response": str(response)
            }
        }, indent=2)
        
    # Get response text
    text = response.get("response")
    if text is None:
        return json.dumps({
            "error": "missing_response",
            "message": "No response text found in response",
            "details": {
                "suggestions": [
                    "Check if input is appropriate",
                    "Try simplifying the prompt",
                    "Try a different model"
                ],
                "response": str(response)
            }
        }, indent=2)
    
    # Prepare result with response and metadata
    result = {
        "response": {
            "text": text
        },
        "metadata": {
            "model": model,
            "input": prompt
        }
    }
    
    # Add performance metrics if available
    metrics = {}
    
    if "total_duration" in response:
        metrics["duration_ms"] = response["total_duration"] / 1_000_000
        
    if "prompt_eval_count" in response:
        metrics["input_tokens"] = response["prompt_eval_count"]
        
    if "eval_count" in response:
        metrics["output_tokens"] = response["eval_count"]
        
    if "eval_duration" in response and "eval_count" in response:
        eval_duration_sec = response["eval_duration"] / 1_000_000_000
        tokens_per_sec = response["eval_count"] / eval_duration_sec
        metrics["tokens_per_second"] = round(tokens_per_sec, 1)
    
    if metrics:
        result["metadata"]["performance"] = metrics
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_api_doc_section(
    titles: List[str],
    max_length: int = config.get("api_doc.max_length", 8000)
) -> str:
    f"""Get the content of a specific section from the Ollama API documentation.

    This tool uses a navigation-based approach to retrieve content from the API documentation.
    It provides rich context including query status, available titles, and content truncation info.

    Args:
        titles (List[str]): List of titles forming the path to the desired section,
                         e.g. ["API", "Generate a completion", "Parameters"]
        max_length (Optional[int]): Maximum length for returned content. 
                                  Defaults to {config.get("api_doc.max_length", 8000)} characters.
                                  Content exceeding this limit will be truncated.

    Returns:
        str: JSON-formatted string containing:
            - metadata: A formatted string containing:
                * Query success status
                * Error message or suggestions
                * Deepest level reached
                * Status for each query path item
                * Available titles at current level
                * Available titles at next level (if current level succeeded)
            - truncation: Information about content truncation
            - content: The section content (truncated if too long)
    """
    try:
        # 读取文档内容
        with open("ollama-api.md", "r", encoding="utf-8") as f:
            doc_content = f.read()
    except Exception as e:
        return json.dumps({
            "metadata": (
                "查询失败\n"
                f"错误信息：文档读取出错 - {str(e)}\n"
                "当前层次：0\n"
                f"查询路径：{' > '.join(titles)} - 未执行\n"
                "当前层次可用标题：无法获取\n"
                "下一层次可用标题：无法获取\n"
                "\n配置检查：\n"
                f"请确认 config.json 中的 api_doc.file_path 设置是否正确\n"
                f"当前设置为：{config['api_doc']['file_path']}"
            ),
            "truncation": {
                "original_length": 0,
                "max_length": max_length,
                "is_truncated": False
            },
            "content": ""
        }, indent=2)

    # 使用导航函数查找内容
    nav_result = navigate_sections(doc_content, titles, max_length=max_length)
    
    # 构建查询状态描述
    status_desc = []
    for i, (path, status) in enumerate(zip(nav_result["query_path"], nav_result["status_list"])):
        if status == 1:
            status_desc.append(f"{path} - 查找成功")
        elif status == 0:
            status_desc.append(f"{path} - 未找到标题")
        else:
            status_desc.append(f"{path} - 查找失败")

    # 构建元数据字符串
    metadata = (
        f"查询{'成功' if nav_result['success'] else '失败'}\n"
        f"{'建议：请检查标题名称，当前可用标题如下' if not nav_result['success'] else '信息：已找到请求的内容'}\n"
        f"当前最深层：{nav_result['current_level']}\n"
        f"查询路径：\n" + "\n".join(f"  {desc}" for desc in status_desc) + "\n"
        f"当前层次可用标题：\n" + "\n".join(f"  - {title}" for title in nav_result['available_titles']) + "\n"
        f"下一层次可用标题：\n" + "\n".join(f"  - {title}" for title in nav_result['next_level_titles'])
    )

    # 构建截断信息
    truncation = {
        "original_length": nav_result["content_length"],
        "max_length": max_length,
        "is_truncated": len(nav_result["content"]) < nav_result["content_length"]
    }

    return json.dumps({
        "metadata": metadata,
        "truncation": truncation,
        "content": nav_result["content"]
    }, indent=2)

@mcp.resource("file://api-md")
def read_api_file() -> str:
    """读取 API 文档资源"""
    try:
        with open('ollama-api.md', "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise ValueError(f"读取文档失败: {str(e)}")

if __name__ == "__main__":
    # Initialize and run server
    mcp.run(transport='stdio')