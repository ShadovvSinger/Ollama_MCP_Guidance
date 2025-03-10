"""
Copyright (c) 2025 ShadowSinger <shadowsinger.tp@gmail.com>
Licensed under the MIT License. See LICENSE file for the full license text.

图像处理工具模块，提供图像格式转换和验证功能。
"""

import base64
import imghdr
import mimetypes
import re
from pathlib import Path
from typing import Optional
import requests


class ImageProcessError(Exception):
    """图像处理相关的错误"""
    pass


def validate_and_convert_to_base64(
    image_source: str,
    max_size_mb: float = 10.0,
    timeout: int = 10
) -> str:
    """
    验证并将图像转换为base64格式。
    
    Args:
        image_source: 图像来源（本地路径、URL或base64字符串）
        max_size_mb: 最大允许的文件大小（MB）
        timeout: URL请求超时时间（秒）
        
    Returns:
        str: base64编码的图像字符串（包含mime type前缀）
        
    Raises:
        ImageProcessError: 当图像处理过程中出现错误
    """
    try:
        # 已经是base64格式
        if re.match(r'^data:image/.+;base64,', image_source):
            # 验证base64字符串的大小
            base64_size = len(image_source) * 3 / 4 / 1024 / 1024  # 估算大小（MB）
            if base64_size > max_size_mb:
                raise ImageProcessError(f"Base64 image too large: {base64_size:.1f}MB > {max_size_mb}MB")
            return image_source
            
        # URL格式
        if image_source.startswith(('http://', 'https://')):
            try:
                response = requests.get(image_source, timeout=timeout)
                response.raise_for_status()
                image_data = response.content
                mime_type = response.headers.get('content-type', '')
                
                # 验证是否为图像
                if not mime_type.startswith('image/'):
                    raise ImageProcessError(f"Invalid image type from URL: {mime_type}")
                    
            except requests.exceptions.RequestException as e:
                raise ImageProcessError(f"Failed to fetch image from URL: {str(e)}")
                
        # 本地文件
        else:
            path = Path(image_source)
            if not path.exists():
                raise ImageProcessError(f"Image file not found: {image_source}")
                
            # 检查文件大小
            file_size_mb = path.stat().st_size / 1024 / 1024
            if file_size_mb > max_size_mb:
                raise ImageProcessError(f"Image file too large: {file_size_mb:.1f}MB > {max_size_mb}MB")
                
            # 读取文件
            with open(path, 'rb') as f:
                image_data = f.read()
                
            # 验证图像格式
            image_format = imghdr.what(None, h=image_data)
            if not image_format:
                raise ImageProcessError(f"Invalid or unsupported image format: {path}")
                
            mime_type = f'image/{image_format}'
            
        # 验证图像数据大小
        data_size_mb = len(image_data) / 1024 / 1024
        if data_size_mb > max_size_mb:
            raise ImageProcessError(f"Image data too large: {data_size_mb:.1f}MB > {max_size_mb}MB")
            
        # 转换为base64
        base64_data = base64.b64encode(image_data).decode('utf-8')
        return f"data:{mime_type};base64,{base64_data}"
        
    except Exception as e:
        if not isinstance(e, ImageProcessError):
            raise ImageProcessError(f"Failed to process image: {str(e)}")
        raise


def is_valid_image_source(source: str) -> bool:
    """
    检查给定的图像来源是否有效。
    
    Args:
        source: 图像来源（本地路径、URL或base64字符串）
        
    Returns:
        bool: 如果图像来源格式有效返回True，否则返回False
    """
    # 检查是否为base64格式
    if re.match(r'^data:image/.+;base64,', source):
        return True
        
    # 检查是否为URL
    if source.startswith(('http://', 'https://')):
        return True
        
    # 检查是否为本地文件
    path = Path(source)
    if path.exists() and path.is_file():
        # 检查文件扩展名
        return path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
    return False


def get_supported_formats() -> list[str]:
    """
    获取支持的图像格式列表。
    
    Returns:
        list[str]: 支持的图像格式列表
    """
    return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'] 


if __name__ == '__main__':
    import sys
    import json
    from datetime import datetime

    def test_image_source(source: str) -> None:
        """测试图像处理功能"""
        print(f"\n测试图像来源: {source}")
        print("-" * 50)
        
        # 测试图像来源是否有效
        print(f"1. 验证图像来源格式")
        is_valid = is_valid_image_source(source)
        print(f"   结果: {'有效' if is_valid else '无效'}")
        
        if not is_valid:
            print("   跳过后续测试（无效的图像来源）")
            return
            
        # 测试转换为base64
        print(f"\n2. 转换为Base64")
        try:
            start_time = datetime.now()
            base64_data = validate_and_convert_to_base64(source)
            duration = (datetime.now() - start_time).total_seconds()
            
            # 显示结果摘要
            print(f"   转换成功!")
            print(f"   处理时间: {duration:.2f} 秒")
            print(f"   Base64长度: {len(base64_data)} 字符")
            print(f"   前50个字符: {base64_data[:50]}...")
            
        except ImageProcessError as e:
            print(f"   转换失败: {str(e)}")
            
    def main():
        """主函数：展示模块功能"""
        print("图像处理工具测试程序")
        print("=" * 50)
        
        # 显示支持的格式
        print(f"支持的图像格式: {', '.join(get_supported_formats())}")
        print("=" * 50)
        
        # 测试用例
        test_cases = []
        
        # 如果提供了命令行参数，使用它们作为测试用例
        if len(sys.argv) > 1:
            test_cases = sys.argv[1:]
        else:
            # 默认测试用例
            test_cases = [
                "https://upload.wikimedia.org/wikipedia/commons/6/6a/PNG_Test.png",
                "http://images.cocodataset.org/val2017/000000397133.jpg",
                "https://www.learningcontainer.com/wp-content/uploads/2020/08/Small-Sample-png-Image-File-Download.jpg",
                "/Users/lgl/Desktop/screen-shot-of-a-paper.png",  # 本地文件（可能不存在）
                "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",  # base64
                "invalid_image.xyz",  # 无效格式
                "https://example.com/nonexistent.jpg",  # 无效URL
            ]
            
            # 测试用例解读
            test_cases_interpretation = [
                '合理的png图片url，应当成功转换',
                '合理的jpg图片url，应当成功转换',
                '合理的jpg图片url，应当成功转换',
                '合理的本地png图片文件，应当成功转换',
                '已经是base64的图片，应当成功转换',
                '无效格式的图片路径，应当抛出异常',
                '无效的图片url，应当抛出异常',
            ]
            
        # 运行测试
        for source, interpretation in zip(test_cases, test_cases_interpretation):
            print(f"\n测试用例: {interpretation}")
            test_image_source(source)
            
        print("\n测试完成!")
        
    main()