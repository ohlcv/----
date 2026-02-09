#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF解析脚本
用于解析考纲规划目录中的PDF文件，提取文本内容并保存为文本文件
"""

import os
import PyPDF2
from pathlib import Path

def parse_pdf(pdf_path, output_dir):
    """
    解析单个PDF文件并保存为文本文件
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
    """
    try:
        # 打开PDF文件
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # 提取文件名（不含扩展名）
            pdf_name = os.path.basename(pdf_path)
            name_without_ext = os.path.splitext(pdf_name)[0]
            
            # 构建输出文件路径
            output_path = os.path.join(output_dir, f"{name_without_ext}.txt")
            
            # 提取文本内容
            text_content = []
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_content.append(f"=== 第 {page_num + 1} 页 ===\n{text}\n")
            
            # 保存文本内容
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write('\n'.join(text_content))
            
            print(f"✓ 成功解析: {pdf_name}")
            print(f"  保存为: {output_path}")
            return True
            
    except Exception as e:
        print(f"✗ 解析失败: {pdf_path}")
        print(f"  错误信息: {str(e)}")
        return False

def main():
    """
    主函数：遍历考纲规划目录中的所有PDF文件并解析
    """
    # 定义目录路径
    base_dir = Path("c:\\Users\\GALAX\\Projects\\专升本")
    pdf_dir = base_dir / "考纲规划"
    output_dir = base_dir / "考纲规划" / "解析结果"
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    print("=== PDF解析脚本 ===")
    print(f"PDF目录: {pdf_dir}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 遍历PDF文件
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("⚠️  未找到PDF文件")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    print()
    
    # 解析每个PDF文件
    print("开始解析...")
    print("=" * 50)
    
    success_count = 0
    for pdf_file in pdf_files:
        if parse_pdf(pdf_file, output_dir):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"解析完成: 成功 {success_count} 个, 失败 {len(pdf_files) - success_count} 个")
    print(f"解析结果保存在: {output_dir}")

if __name__ == "__main__":
    main()
