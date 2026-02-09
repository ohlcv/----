#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF文本提取诊断工具
用于诊断PDF文本提取的问题
"""

import sys
import os
from pathlib import Path

# 默认文件路径
DEFAULT_FILE_PATH = r"c:\Users\GALAX\Projects\学习考试\学习资料\全国15043中国近现代史纲要规划卡.pdf"

def diagnose_pdf(pdf_path):
    """诊断PDF文件的文本提取"""
    print("=" * 80)
    print("PDF文本提取诊断工具")
    print("=" * 80)
    print(f"\n文件: {pdf_path}\n")
    
    if not os.path.exists(pdf_path):
        print("❌ 错误: 文件不存在")
        return False
    
    # 测试 pdfplumber
    print("【1】测试 pdfplumber...")
    try:
        import pdfplumber
        print("  ✓ pdfplumber 已安装")
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"  ✓ 总页数: {len(pdf.pages)}")
            
            # 提取第一页
            if pdf.pages:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                
                if text:
                    print(f"  ✓ 第一页文本长度: {len(text)} 字符")
                    print(f"  ✓ 第一页前500字符:")
                    print("  " + "-" * 76)
                    for line in text[:500].split('\n')[:10]:
                        print(f"  {line}")
                    print("  " + "-" * 76)
                    
                    # 检查是否包含知识点标记
                    if "知识点" in text:
                        print("  ✓ 包含 '知识点' 标记")
                    else:
                        print("  ⚠️  未找到 '知识点' 标记")
                else:
                    print("  ❌ 第一页未提取到文本")
        
        return True
                
    except ImportError:
        print("  ❌ pdfplumber 未安装")
        print("  💡 安装命令: pip install pdfplumber --break-system-packages")
    except Exception as e:
        print(f"  ❌ pdfplumber 提取失败: {e}")
    
    print()
    
    # 测试 pypdf
    print("【2】测试 pypdf...")
    try:
        from pypdf import PdfReader
        print("  ✓ pypdf 已安装")
        
        reader = PdfReader(pdf_path)
        print(f"  ✓ 总页数: {len(reader.pages)}")
        
        if reader.pages:
            first_page = reader.pages[0]
            text = first_page.extract_text()
            
            if text:
                print(f"  ✓ 第一页文本长度: {len(text)} 字符")
                print(f"  ✓ 第一页前500字符:")
                print("  " + "-" * 76)
                for line in text[:500].split('\n')[:10]:
                    print(f"  {line}")
                print("  " + "-" * 76)
                
                # 检查是否包含知识点标记
                if "知识点" in text:
                    print("  ✓ 包含 '知识点' 标记")
                else:
                    print("  ⚠️  未找到 '知识点' 标记")
            else:
                print("  ❌ 第一页未提取到文本")
        
        return True
            
    except ImportError:
        print("  ❌ pypdf 未安装")
        print("  💡 安装命令: pip install pypdf --break-system-packages")
    except Exception as e:
        print(f"  ❌ pypdf 提取失败: {e}")
    
    print()
    
    # 测试 PyPDF2
    print("【3】测试 PyPDF2...")
    try:
        from PyPDF2 import PdfReader
        print("  ✓ PyPDF2 已安装")
        
        reader = PdfReader(pdf_path)
        print(f"  ✓ 总页数: {len(reader.pages)}")
        
        if reader.pages:
            first_page = reader.pages[0]
            text = first_page.extract_text()
            
            if text:
                print(f"  ✓ 第一页文本长度: {len(text)} 字符")
                print(f"  ✓ 第一页前500字符:")
                print("  " + "-" * 76)
                for line in text[:500].split('\n')[:10]:
                    print(f"  {line}")
                print("  " + "-" * 76)
                
                # 检查是否包含知识点标记
                if "知识点" in text:
                    print("  ✓ 包含 '知识点' 标记")
                else:
                    print("  ⚠️  未找到 '知识点' 标记")
            else:
                print("  ❌ 第一页未提取到文本")
        
        return True
            
    except ImportError:
        print("  ❌ PyPDF2 未安装")
        print("  💡 安装命令: pip install PyPDF2 --break-system-packages")
    except Exception as e:
        print(f"  ❌ PyPDF2 提取失败: {e}")
    
    print()
    print("=" * 80)
    print("诊断建议:")
    print("  1. 推荐使用 pdfplumber，文本提取质量最好")
    print("  2. 如果PDF是扫描件，需要先进行OCR处理")
    print("  3. 检查PDF是否包含正确的文本层")
    print("=" * 80)
    
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"未提供文件路径，使用默认路径: {DEFAULT_FILE_PATH}")
        pdf_path = DEFAULT_FILE_PATH
    else:
        pdf_path = sys.argv[1]
    
    diagnose_pdf(pdf_path)
