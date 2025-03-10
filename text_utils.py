"""
Copyright (c) 2025 ShadowSinger <shadowsinger.tp@gmail.com>
Licensed under the MIT License. See LICENSE file for the full license text.
"""

from typing import Optional, Dict, Any, List
import re

def get_titles_at_level(content: str, heading_level: int) -> List[str]:
    """获取指定等级的所有标题
    
    Args:
        content (str): 文档内容
        heading_level (int): 标题等级
        
    Returns:
        List[str]: 该等级下的所有标题（不含 # 符号）
    """
    heading_mark = '#' * heading_level
    pattern = f"^{heading_mark}\\s+(.+?)\\s*$"
    
    titles = []
    for line in content.split('\n'):
        match = re.match(pattern, line)
        if match:
            titles.append(match.group(1).strip())
    
    return titles

def find_section_by_title(
    content: str,
    target_title: str,
    heading_level: int
) -> Dict[str, Any]:
    """在文档中查找指定等级的标题及其内容
    
    Args:
        content: 文档内容
        target_title: 要查找的标题（不含#符号）
        heading_level: 标题等级（1=一级标题#，2=二级标题##）
    
    Returns:
        Dict[str, Any]: {
            success: bool,     # 是否找到目标章节
            content: str,      # 找到的内容（成功时）
            title: str,       # 完整标题（成功时）
            message: str,     # 状态信息
            error: str,       # 错误类型（失败时）
            available_titles: List[str]  # 当前等级的所有可用标题（总是返回）
        }
    """
    try:
        # 获取当前等级的所有可用标题
        available_titles = get_titles_at_level(content, heading_level)
        
        if heading_level < 1:
            return {
                "success": False,
                "error": "invalid_level",
                "message": "Heading level must be positive",
                "available_titles": available_titles
            }
        
        heading_mark = '#' * heading_level
        heading_pattern = f"^{heading_mark}\\s+(.+?)\\s*$"
        lines = content.split('\n')
        result_lines = []
        
        # 查找目标标题和同级标题的位置
        target_idx = -1
        next_same_idx = -1
        same_level_indices = []
        
        for i, line in enumerate(lines):
            if line.startswith(heading_mark + ' '):
                same_level_indices.append(i)
                if re.match(heading_pattern, line).group(1).strip() == target_title:
                    target_idx = i
                elif target_idx >= 0:
                    next_same_idx = i
                    break
        
        if target_idx == -1:
            return {
                "success": False,
                "error": "title_not_found",
                "message": f"Title '{target_title}' not found at level {heading_level}",
                "available_titles": available_titles
            }
        
        # 收集内容：高层标题 + 目标章节
        for i in range(same_level_indices[0]):
            line = lines[i]
            if any(line.startswith('#' * l + ' ') for l in range(1, heading_level)) or \
               not any(line.startswith('#' * l + ' ') for l in range(1, heading_level + 1)):
                result_lines.append(line)
        
        end_idx = next_same_idx if next_same_idx >= 0 else len(lines)
        result_lines.extend(lines[target_idx:end_idx])
        
        return {
            "success": True,
            "content": '\n'.join(line for line in result_lines if line.strip()),
            "title": f"{heading_mark} {target_title}",
            "message": f"Found section: {target_title}",
            "available_titles": available_titles
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": "processing_error",
            "message": str(e),
            "available_titles": []  # 发生异常时返回空列表
        }

def navigate_sections(
    content: str,
    title_path: List[str],
    max_length: Optional[int] = None
) -> Dict[str, Any]:
    """按标题路径逐层导航文档内容
    
    Args:
        content: 文档内容
        title_path: 标题路径列表，如 ["Main Title", "Section 2"]
        max_length: 返回内容的最大长度（可选）
    
    Returns:
        Dict[str, Any]: {
            success: bool,         # 是否成功找到完整路径
            content: str,          # 当前内容（可能被截断）
            content_length: int,   # 原始内容长度
            current_level: int,    # 当前层级（从1开始）
            failed_level: int,     # 失败的层级（失败时）
            message: str,          # 状态信息
            status_list: List[int],  # 每层查询状态(1=成功,0=失败,-1=未查询)
            query_path: List[str],  # 查询的标题路径
            available_titles: List[str],  # 当前层级的可用标题列表
            next_level_titles: List[str]  # 下一层级的可用标题列表（仅当前层成功时）
        }
    """
    current_content = content
    current_level = 0
    status_list = []
    last_result = None
    
    try:
        for title in title_path:
            current_level += 1
            last_result = find_section_by_title(current_content, title, current_level)
            
            if not last_result["success"]:
                status_list.append(0)
                status_list.extend([-1] * (len(title_path) - len(status_list)))
                
                # 获取当前层的可用标题
                available_titles = last_result["available_titles"]
                
                content_length = len(current_content)
                if max_length is not None and content_length > max_length:
                    current_content = current_content[:max_length-len("\n... (content truncated)")] + "\n... (content truncated)"
                
                return {
                    "success": False,
                    "content": current_content,
                    "content_length": content_length,
                    "current_level": current_level,
                    "failed_level": current_level,
                    "message": f"Failed at level {current_level}: {last_result['message']}",
                    "status_list": status_list,
                    "query_path": title_path,
                    "available_titles": available_titles,
                    "next_level_titles": []  # 失败时返回空列表
                }
            
            current_content = last_result["content"]
            status_list.append(1)
        
        # 获取当前层的可用标题
        available_titles = last_result["available_titles"]
        
        # 获取下一层的可用标题
        next_level_titles = get_titles_at_level(current_content, current_level + 1)
        
        content_length = len(current_content)
        if max_length is not None and content_length > max_length:
            current_content = current_content[:max_length-len("\n... (content truncated)")] + "\n... (content truncated)"
        
        return {
            "success": True,
            "content": current_content,
            "content_length": content_length,
            "current_level": current_level,
            "message": f"Found: {' > '.join(title_path)}",
            "status_list": status_list,
            "query_path": title_path,
            "available_titles": available_titles,
            "next_level_titles": next_level_titles
        }
        
    except Exception as e:
        if len(status_list) < len(title_path):
            status_list.append(0)
            status_list.extend([-1] * (len(title_path) - len(status_list)))
        
        content_length = len(current_content)
        if max_length is not None and content_length > max_length:
            current_content = current_content[:max_length] + "\n... (content truncated)"
            
        return {
            "success": False,
            "content": current_content,
            "content_length": content_length,
            "current_level": current_level,
            "failed_level": current_level,
            "message": f"Error at level {current_level}: {str(e)}",
            "status_list": status_list,
            "query_path": title_path,
            "available_titles": last_result["available_titles"] if last_result else [],
            "next_level_titles": []  # 错误时返回空列表
        }

# 测试代码
if __name__ == "__main__":
    test_content = """# Main Title
Some introduction text

## Section 1
Content of section 1

## Section 2
Content of section 2

### Subsection 2.1
Content of subsection 2.1
#### Deep Section
Very deep content

### Subsection 2.2
Content of subsection 2.2

## Section 3
Content of section 3
"""
    
    def print_result(case_name: str, result: Dict[str, Any]) -> None:
        """打印测试结果的辅助函数"""
        print(f"\n{case_name}")
        print(f"Success: {result['success']}")
        if not result['success']:
            print(f"Failed at level: {result['failed_level']}")
        
        print("\nQuery Status:")
        for title, status in zip(result["query_path"], result["status_list"]):
            print(f"- {title}: {status}")
        
        print("\nAvailable titles at current level:")
        for title in result["available_titles"]:
            print(f"- {title}")
        
        print(f"\nContent length: {result['content_length']}")
        print("Content:")
        print("---")
        print(result["content"])
        print("="*50)
    
    # 测试用例
    cases = [
        ("Successful deep navigation (no length limit)", 
         ["Main Title", "Section 2", "Subsection 2.1", "Deep Section"],
         None),
        ("Successful deep navigation (length limit: 50)", 
         ["Main Title", "Section 2", "Subsection 2.1", "Deep Section"],
         50),
        ("Navigation to non-existent section (length limit: 30)",
         ["Main Title", "Section 2", "Wrong Section"],
         30),
        ("Navigation fails at first level (no length limit)",
         ["Wrong Title", "Section 2", "Subsection 2.1"],
         None)
    ]
    
    for case_name, path, max_len in cases:
        print_result(case_name, navigate_sections(test_content, path, max_len)) 