#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《中国近现代史纲要》综合分析脚本
功能：全面分析规划卡文档的结构、知识点、测试题等信息
版本：2.0（合并优化版）
支持：TXT文件、PDF文件
"""

import re
import os
import argparse
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from pathlib import Path
import tempfile

# 尝试导入PDF处理库
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# 默认文件路径
DEFAULT_FILE_PATH = r"c:\Users\GALAX\Projects\学习考试\学习资料\解析结果\全国15043中国近现代史纲要规划卡.txt"

# 章节配置
CHAPTERS = ["导言", "第一章", "第二章", "第三章", "第四章", "第五章", 
            "第六章", "第七章", "第八章", "第九章", "第十章"]

CHAPTER_NAMES = {
    "导言": "导言",
    "第一章": "进入近代后中华民族的磨难与抗争",
    "第二章": "不同社会力量对国家出路的早期探索",
    "第三章": "辛亥革命与君主专制制度的终结",
    "第四章": "中国共产党成立和中国革命新局面",
    "第五章": "中国革命的新道路",
    "第六章": "中华民族的抗日战争",
    "第七章": "为建立新中国而奋斗",
    "第八章": "中华人民共和国的成立与中国社会主义建设道路的探索",
    "第九章": "改革开放与中国特色社会主义的开创和发展",
    "第十章": "中国特色社会主义进入新时代"
}


class HistoryOutlineAnalyzer:
    """中国近现代史纲要分析器"""
    
    def __init__(self, file_path: str):
        """初始化分析器"""
        self.file_path = file_path
        self.content = ""
        self.lines = []
        self.knowledge_points = []
        self.stats = {}
        
    def load_file(self) -> bool:
        """加载文件内容（支持TXT和PDF）"""
        try:
            if not os.path.exists(self.file_path):
                print(f"错误: 文件不存在 - {self.file_path}")
                return False
            
            if not os.access(self.file_path, os.R_OK):
                print(f"错误: 无法读取文件 - {self.file_path}")
                return False
            
            # 判断文件类型
            file_ext = Path(self.file_path).suffix.lower()
            
            if file_ext == '.pdf':
                # 处理PDF文件
                self.content = self._extract_pdf_text()
                if not self.content:
                    return False
            else:
                # 处理文本文件
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.content = f.read()
            
            if not self.content:
                print("错误: 文件内容为空")
                return False
            
            self.lines = self.content.split('\n')
            return True
            
        except UnicodeDecodeError as e:
            print(f"错误: 文件编码错误 - {e}")
            return False
        except Exception as e:
            print(f"错误: 读取文件失败 - {e}")
            return False
    
    def _extract_pdf_text(self) -> str:
        """从PDF文件中提取文本"""
        # 优先使用pdfplumber（文本提取质量更好）
        try:
            import pdfplumber
            print("  使用 pdfplumber 提取文本...")
            
            with pdfplumber.open(self.file_path) as pdf:
                text_content = []
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        text_content.append(f"=== 第 {i + 1} 页 ===\n{text}\n")
                
                return '\n'.join(text_content)
        
        except ImportError:
            print("  pdfplumber 未安装，尝试使用 pypdf...")
        except Exception as e:
            print(f"  pdfplumber 提取失败: {e}")
            print("  尝试使用 pypdf...")
        
        # 备用方案：使用pypdf
        try:
            try:
                from pypdf import PdfReader
            except ImportError:
                try:
                    from PyPDF2 import PdfReader
                except ImportError:
                    print("错误: 需要安装 pdfplumber、pypdf 或 PyPDF2 库来处理PDF文件")
                    print("推荐安装: pip install pdfplumber --break-system-packages")
                    print("或者安装: pip install pypdf --break-system-packages")
                    return ""
            
            print("  使用 pypdf 提取文本...")
            reader = PdfReader(self.file_path)
            text_content = []
            
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_content.append(f"=== 第 {page_num + 1} 页 ===\n{text}\n")
            
            return '\n'.join(text_content)
            
        except Exception as e:
            print(f"错误: PDF解析失败 - {e}")
            return ""
    
    def analyze_basic_info(self) -> Dict[str, Any]:
        """分析文档基本信息"""
        # 字符统计
        total_chars = len(self.content)
        total_chars_no_space = len(re.sub(r'\s+', '', self.content))
        
        # 页数统计
        page_matches = re.findall(r'=== 第 (\d+) 页 ===', self.content)
        pages = sorted(list(set(int(p) for p in page_matches if p.isdigit())))
        
        return {
            "total_chars": total_chars,
            "total_chars_no_space": total_chars_no_space,
            "pages": pages,
            "page_count": len(pages)
        }
    
    def analyze_structure(self) -> Dict[str, Any]:
        """分析文档结构"""
        # 统计小节
        sections = re.findall(r'第\d+页第[一二三四五]节', self.content)
        sections_count = len(sections)
        
        # 按章节统计小节
        chapter_sections = {ch: 0 for ch in CHAPTERS}
        section_matches = [(m.group(1), m.start()) 
                          for m in re.finditer(r'第\d+页(第[一二三四五]节)', self.content)]
        
        # 找到章节位置
        chapter_positions = []
        for chapter in CHAPTERS:
            for match in re.finditer(chapter, self.content):
                line_start = self.content.rfind('\n', 0, match.start()) + 1
                line_end = self.content.find('\n', match.start())
                if line_end == -1:
                    line_end = len(self.content)
                line = self.content[line_start:line_end]
                if re.search(r'第\d+页|===.*===', line):
                    chapter_positions.append((chapter, match.start()))
        
        chapter_positions.sort(key=lambda x: x[1])
        
        # 为每个小节确定所属章节
        for section_name, section_pos in section_matches:
            closest_chapter = None
            closest_distance = float('inf')
            
            for chapter, ch_pos in chapter_positions:
                if ch_pos < section_pos and (section_pos - ch_pos) < closest_distance:
                    closest_chapter = chapter
                    closest_distance = section_pos - ch_pos
            
            if closest_chapter:
                chapter_sections[closest_chapter] += 1
        
        return {
            "total_sections": sections_count,
            "chapter_sections": chapter_sections
        }
    
    def extract_knowledge_points(self) -> List[Dict[str, Any]]:
        """提取所有知识点"""
        knowledge_points = []
        current_chapter = None
        current_knowledge = None
        
        for i, line in enumerate(self.lines):
            # 检测章节
            for chapter in CHAPTERS:
                if chapter in line and re.search(r'第\d+页|===.*===', line):
                    current_chapter = chapter
                    break
            
            # 检测知识点标题
            if "知识点" in line and re.search(r'知识点\d+', line):
                # 保存上一个知识点
                if current_knowledge:
                    knowledge_points.append(current_knowledge)
                
                # 提取知识点编号
                knowledge_match = re.search(r'知识点(\d+)', line)
                knowledge_id = knowledge_match.group(1) if knowledge_match else "0"
                
                # 提取标题（去除知识点编号后的内容）
                knowledge_title = re.sub(r'知识点\d+', '', line).strip()
                # 清理标题中的各种标记
                knowledge_title = re.sub(r'\[.*?\]', '', knowledge_title).strip()
                knowledge_title = re.sub(r'【.*?】', '', knowledge_title).strip()
                knowledge_title = re.sub(r'★+', '', knowledge_title).strip()
                
                # 提取重要程度（可能在同一行）
                importance_match = re.search(r'(★★★|★★|★)', line)
                importance = importance_match.group(1) if importance_match else None
                
                # 提取考核要求
                exam_requirements = []
                if "【单选】" in line:
                    exam_requirements.append("单选")
                if "【简答】" in line:
                    exam_requirements.append("简答")
                if "【论述】" in line:
                    exam_requirements.append("论述")
                
                # 创建知识点对象
                current_knowledge = {
                    "id": knowledge_id,
                    "title": knowledge_title,
                    "chapter": current_chapter,
                    "chapter_name": CHAPTER_NAMES.get(current_chapter, ""),
                    "importance": importance,
                    "exam_requirements": exam_requirements,
                    "content": [],
                    "start_line": i,
                    "content_lines": []  # 记录内容行用于后续查找重要程度
                }
            
            # 收集知识点内容
            elif current_knowledge and i > current_knowledge["start_line"]:
                next_knowledge = re.search(r'知识点\d+', line)
                next_chapter = any(ch in line and re.search(r'第\d+页|===.*===', line) 
                                  for ch in CHAPTERS)
                
                if next_knowledge or next_chapter:
                    knowledge_points.append(current_knowledge)
                    current_knowledge = None
                elif line.strip() and not re.search(r'^\s*$', line):
                    current_knowledge["content"].append(line.strip())
                    current_knowledge["content_lines"].append(line)
                    
                    # 如果还没有找到重要程度，继续在内容中查找
                    if not current_knowledge["importance"]:
                        importance_match = re.search(r'(★★★|★★|★)', line)
                        if importance_match:
                            current_knowledge["importance"] = importance_match.group(1)
        
        # 保存最后一个知识点
        if current_knowledge:
            knowledge_points.append(current_knowledge)
        
        # 清理临时字段
        for kp in knowledge_points:
            if "content_lines" in kp:
                del kp["content_lines"]
        
        self.knowledge_points = knowledge_points
        return knowledge_points
    
    def analyze_knowledge_distribution(self) -> Dict[str, Any]:
        """分析知识点分布"""
        # 二次扫描：确保所有知识点都有重要程度标记
        # 有些文档格式中，星号可能在知识点后续的几行内
        for kp in self.knowledge_points:
            if not kp["importance"]:
                # 在内容中查找星号
                for content_line in kp["content"][:5]:  # 只查看前5行内容
                    match = re.search(r'(★★★|★★|★)', content_line)
                    if match:
                        kp["importance"] = match.group(1)
                        break
        
        # 按章节统计
        chapter_counts = {ch: 0 for ch in CHAPTERS}
        for kp in self.knowledge_points:
            if kp["chapter"] in chapter_counts:
                chapter_counts[kp["chapter"]] += 1
        
        # 按重要程度统计
        importance_counts = {"★★★": 0, "★★": 0, "★": 0, "未标注": 0}
        for kp in self.knowledge_points:
            imp = kp["importance"]
            if imp in importance_counts:
                importance_counts[imp] += 1
            else:
                importance_counts["未标注"] += 1
        
        # 按考核要求统计
        exam_counts = {"单选": 0, "简答": 0, "论述": 0, "综合": 0, "未标注": 0}
        for kp in self.knowledge_points:
            reqs = kp["exam_requirements"]
            if len(reqs) == 0:
                exam_counts["未标注"] += 1
            elif len(reqs) > 1:
                exam_counts["综合"] += 1
            else:
                for req in reqs:
                    if req in exam_counts:
                        exam_counts[req] += 1
        
        # 各章节详细分布
        chapter_details = {}
        for chapter in CHAPTERS:
            chapter_kps = [kp for kp in self.knowledge_points if kp["chapter"] == chapter]
            
            # 重要程度分布
            imp_dist = {"★★★": 0, "★★": 0, "★": 0}
            for kp in chapter_kps:
                if kp["importance"] in imp_dist:
                    imp_dist[kp["importance"]] += 1
            
            # 考核要求分布
            exam_dist = {"单选": 0, "简答": 0, "论述": 0}
            for kp in chapter_kps:
                for req in kp["exam_requirements"]:
                    if req in exam_dist:
                        exam_dist[req] += 1
            
            chapter_details[chapter] = {
                "total": len(chapter_kps),
                "importance": imp_dist,
                "exam_requirements": exam_dist
            }
        
        return {
            "total": len(self.knowledge_points),
            "by_chapter": chapter_counts,
            "by_importance": importance_counts,
            "by_exam": exam_counts,
            "chapter_details": chapter_details
        }
    
    def analyze_questions(self) -> Dict[str, Any]:
        """分析测试题"""
        # 统计题目类型
        real_questions = re.findall(r'【真题·', self.content)
        mock_questions = re.findall(r'【模拟·', self.content)
        
        # 统计答案和解析
        answers = re.findall(r'【答案】', self.content)
        explanations = re.findall(r'【解析】', self.content)
        
        # 按章节统计题目
        chapter_questions = {ch: 0 for ch in CHAPTERS}
        current_chapter = None
        
        for line in self.lines:
            # 检测章节
            for chapter in CHAPTERS:
                if chapter in line and re.search(r'第\d+页|===.*===', line):
                    current_chapter = chapter
                    break
            
            # 统计题目
            if current_chapter:
                question_count = len(re.findall(r'【真题·|【模拟·', line))
                chapter_questions[current_chapter] += question_count
        
        return {
            "total": len(real_questions) + len(mock_questions),
            "real": len(real_questions),
            "mock": len(mock_questions),
            "answers": len(answers),
            "explanations": len(explanations),
            "by_chapter": chapter_questions
        }
    
    def analyze_content_features(self) -> Dict[str, Any]:
        """分析内容特征"""
        # 知识点平均长度
        total_length = sum(len(' '.join(kp["content"])) for kp in self.knowledge_points)
        avg_length = total_length / len(self.knowledge_points) if self.knowledge_points else 0
        
        # 内容类型分析
        content_types = {
            "历史事件": 0,
            "人物思想": 0,
            "理论政策": 0,
            "历史意义": 0,
            "其他": 0
        }
        
        for kp in self.knowledge_points:
            content = ' '.join(kp["content"])
            if "意义" in content or "影响" in content or "作用" in content:
                content_types["历史意义"] += 1
            elif "政策" in content or "方针" in content or "路线" in content:
                content_types["理论政策"] += 1
            elif re.search(r'(毛泽东|孙中山|邓小平|江泽民|胡锦涛|习近平)', content):
                content_types["人物思想"] += 1
            elif re.search(r'(战争|运动|革命|起义|事变)', content):
                content_types["历史事件"] += 1
            else:
                content_types["其他"] += 1
        
        # 核心知识点
        core_knowledge = [kp for kp in self.knowledge_points if kp["importance"] == "★★★"]
        
        return {
            "avg_length": avg_length,
            "content_types": content_types,
            "core_knowledge_count": len(core_knowledge),
            "core_knowledge_list": [(kp["chapter"], kp["title"]) for kp in core_knowledge[:100]]
        }
    
    def run_analysis(self) -> bool:
        """执行完整分析"""
        print("正在加载文件...")
        if not self.load_file():
            return False
        
        print("正在分析文档结构...")
        self.stats["basic_info"] = self.analyze_basic_info()
        self.stats["structure"] = self.analyze_structure()
        
        print("正在提取知识点...")
        self.extract_knowledge_points()
        
        print("正在分析知识点分布...")
        self.stats["knowledge"] = self.analyze_knowledge_distribution()
        
        print("正在分析测试题...")
        self.stats["questions"] = self.analyze_questions()
        
        print("正在分析内容特征...")
        self.stats["content"] = self.analyze_content_features()
        
        return True
    
    def print_report(self, verbose: bool = False, debug: bool = False):
        """打印分析报告"""
        if debug:
            self._print_debug_info()
        
        self._print_header()
        self._print_basic_info()
        self._print_structure_info()
        self._print_knowledge_summary()
        self._print_chapter_details()
        self._print_question_summary()
        self._print_content_features()
        
        # 调试模式或详细模式都显示知识点列表
        if verbose or debug:
            self._print_knowledge_list()
        
        self._print_footer()
    
    def _print_debug_info(self):
        """打印调试信息"""
        print("\n" + "=" * 80)
        print("调试信息：前200个知识点的详细解析")
        print("=" * 80)
        
        # 先显示提取的文本样本
        print("\n【文本提取样本】（前2000字符）")
        print("-" * 80)
        print(self.content[:2000])
        print("-" * 80)
        print(f"\n总字符数: {len(self.content)}")
        print(f"总行数: {len(self.lines)}")
        print()
        
        display_count = min(200, len(self.knowledge_points))
        
        if display_count == 0:
            print("\n⚠️  未提取到任何知识点！")
            print("请检查:")
            print("  1. 文本格式是否正确")
            print("  2. 是否包含 '知识点1', '知识点2' 等标记")
            print("  3. 使用 --save-text 参数保存提取的文本查看详情")
            print()
        else:
            for i, kp in enumerate(self.knowledge_points[:display_count], 1):
                print(f"\n知识点 {i}:")
                print(f"  ID: {kp['id']}")
                print(f"  标题: {kp['title']}")
                print(f"  章节: {kp['chapter']}")
                print(f"  重要程度: {kp['importance'] if kp['importance'] else '未找到'}")
                print(f"  考核要求: {', '.join(kp['exam_requirements']) if kp['exam_requirements'] else '无'}")
                print(f"  内容行数: {len(kp['content'])}")
                if kp['content']:
                    print(f"  首行内容: {kp['content'][0][:80]}...")
            
            if len(self.knowledge_points) > 200:
                print(f"\n... 还有 {len(self.knowledge_points) - 200} 个知识点未显示")
        
        print("\n" + "=" * 80)
        print()
    
    def _print_header(self):
        """打印报告头部"""
        print("\n" + "=" * 80)
        print("《中国近现代史纲要》规划卡综合分析报告")
        print("=" * 80)
        print()
    
    def _print_basic_info(self):
        """打印基本信息"""
        info = self.stats["basic_info"]
        print("【一、文档基本信息】")
        print(f"  总字符数: {info['total_chars']:,} 字符")
        print(f"  有效字数: 约 {info['total_chars_no_space']:,} 字")
        if info['pages']:
            print(f"  文档页数: {info['page_count']} 页 (第1页 - 第{info['pages'][-1]}页)")
        print()
    
    def _print_structure_info(self):
        """打印结构信息"""
        structure = self.stats["structure"]
        print("【二、文档结构层次】")
        print(f"  章节总数: {len(CHAPTERS)} 章")
        print(f"    ├─ 导言: 1 章")
        print(f"    └─ 正文: 10 章")
        print(f"  小节总数: {structure['total_sections']} 节")
        print(f"  知识点数: {self.stats['knowledge']['total']} 个")
        print()
    
    def _print_knowledge_summary(self):
        """打印知识点概况"""
        knowledge = self.stats["knowledge"]
        print("【三、知识点分布概况】")
        print(f"  总计: {knowledge['total']} 个知识点")
        print()
        
        print("  重要程度分布:")
        for level, count in knowledge["by_importance"].items():
            if count > 0:
                percentage = (count / knowledge['total']) * 100
                level_desc = {
                    "★★★": "核心考点",
                    "★★": "重要考点",
                    "★": "一般考点",
                    "未标注": "未标注"
                }.get(level, level)
                print(f"    {level:6s} ({level_desc:8s}): {count:3d} 个 ({percentage:5.1f}%)")
        print()
        
        print("  考核要求分布:")
        for req, count in knowledge["by_exam"].items():
            if count > 0:
                percentage = (count / knowledge['total']) * 100
                print(f"    {req:6s}: {count:3d} 个 ({percentage:5.1f}%)")
        print()
    
    def _print_chapter_details(self):
        """打印各章详细信息"""
        knowledge = self.stats["knowledge"]
        structure = self.stats["structure"]
        questions = self.stats["questions"]
        
        print("【四、各章节详细分析】")
        for chapter in CHAPTERS:
            name = CHAPTER_NAMES[chapter]
            details = knowledge["chapter_details"][chapter]
            sections = structure["chapter_sections"][chapter]
            qs = questions["by_chapter"][chapter]
            
            print(f"\n  {chapter} {name}")
            print(f"  {'─' * 76}")
            print(f"    知识点: {details['total']} 个  |  小节: {sections} 节  |  测试题: {qs} 道")
            
            # 重要程度
            imp = details["importance"]
            print(f"    重要程度: ★★★ {imp['★★★']:2d}个  ★★ {imp['★★']:2d}个  ★ {imp['★']:2d}个")
            
            # 考核要求
            exam = details["exam_requirements"]
            print(f"    考核要求: 单选 {exam['单选']:2d}个  简答 {exam['简答']:2d}个  论述 {exam['论述']:2d}个")
        print()
    
    def _print_question_summary(self):
        """打印测试题概况"""
        questions = self.stats["questions"]
        print("【五、测试题统计】")
        print(f"  题目总数: {questions['total']} 道")
        print(f"    ├─ 真题: {questions['real']} 道 ({questions['real']/questions['total']*100:.1f}%)")
        print(f"    └─ 模拟题: {questions['mock']} 道 ({questions['mock']/questions['total']*100:.1f}%)")
        print(f"  配套答案: {questions['answers']} 个")
        print(f"  配套解析: {questions['explanations']} 个")
        print(f"  题型: 以单选题为主")
        print()
    
    def _print_content_features(self):
        """打印内容特征"""
        content = self.stats["content"]
        print("【六、内容特征分析】")
        print(f"  知识点平均长度: {content['avg_length']:.0f} 字符")
        print()
        print("  内容类型分布:")
        total = sum(content["content_types"].values())
        for ctype, count in content["content_types"].items():
            if count > 0:
                percentage = (count / total) * 100
                print(f"    {ctype:8s}: {count:3d} 个 ({percentage:5.1f}%)")
        print()
        
        print("  文档特点:")
        print("    ✓ 每个知识点标注考核要求（单选/简答/论述）")
        print("    ✓ 每个知识点标注重要程度（★ ~ ★★★）")
        print("    ✓ 每章配有知识体系导图说明")
        print("    ✓ 每章附有考点练习（真题+模拟题）")
        print("    ✓ 包含【识记】【领会】【应用】三级能力要求")
        print()
    
    def _print_knowledge_list(self):
        """打印知识点列表（包含所有级别）"""
        # 按重要程度分组知识点
        knowledge_by_importance = {
            "★★★": [],
            "★★": [],
            "★": []
        }
        
        for kp in self.knowledge_points:
            importance = kp["importance"]
            if importance in knowledge_by_importance:
                knowledge_by_importance[importance].append((kp["chapter"], kp["title"]))
        
        print("【七、知识点列表】")
        
        # 显示★★★级别知识点
        core_list = knowledge_by_importance["★★★"]
        print(f"  （★★★ 级别）共 {len(core_list)} 个核心知识点")
        
        if core_list:
            # 按章节分组显示，默认显示前50个
            current_chapter = None
            for i, (chapter, title) in enumerate(core_list, 1):
                if i <= 50:
                    if chapter != current_chapter:
                        if current_chapter is not None:
                            print()
                        print(f"    ▸ {chapter} {CHAPTER_NAMES.get(chapter, '')}")
                        current_chapter = chapter
                    print(f"      {i:2d}. {title}")
            
            if len(core_list) > 50:
                print(f"\n      ... 还有 {len(core_list) - 50} 个★★★级别知识点")
        else:
            print("    （未找到★★★级别知识点）")
        
        print()
        
        # 显示★★级别知识点
        important_list = knowledge_by_importance["★★"]
        print(f"  （★★ 级别）共 {len(important_list)} 个重要知识点")
        
        if important_list:
            # 按章节分组显示，默认显示前50个
            current_chapter = None
            for i, (chapter, title) in enumerate(important_list, 1):
                if i <= 50:
                    if chapter != current_chapter:
                        if current_chapter is not None:
                            print()
                        print(f"    ▸ {chapter} {CHAPTER_NAMES.get(chapter, '')}")
                        current_chapter = chapter
                    print(f"      {i:2d}. {title}")
            
            if len(important_list) > 50:
                print(f"\n      ... 还有 {len(important_list) - 50} 个★★级别知识点")
        else:
            print("    （未找到★★级别知识点）")
        
        print()
        
        # 显示★级别知识点
        general_list = knowledge_by_importance["★"]
        print(f"  （★ 级别）共 {len(general_list)} 个一般知识点")
        
        if general_list:
            # 按章节分组显示，默认显示前50个
            current_chapter = None
            for i, (chapter, title) in enumerate(general_list, 1):
                if i <= 50:
                    if chapter != current_chapter:
                        if current_chapter is not None:
                            print()
                        print(f"    ▸ {chapter} {CHAPTER_NAMES.get(chapter, '')}")
                        current_chapter = chapter
                    print(f"      {i:2d}. {title}")
            
            if len(general_list) > 50:
                print(f"\n      ... 还有 {len(general_list) - 50} 个★级别知识点")
        else:
            print("    （未找到★级别知识点）")
        
        print()
    
    def _print_footer(self):
        """打印报告尾部"""
        print("=" * 80)
        print("分析完成！")
        print("=" * 80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='《中国近现代史纲要》规划卡综合分析工具（支持TXT和PDF）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                          # 使用默认路径
  %(prog)s -f /path/to/file.txt     # 分析TXT文件
  %(prog)s -f /path/to/file.pdf     # 分析PDF文件
  %(prog)s -v                       # 显示详细信息（核心知识点列表）
  %(prog)s -d                       # 调试模式（显示前200个知识点详情+核心知识点列表）
  %(prog)s -f file.pdf -v           # 指定PDF文件并显示详细信息

说明:
  - 核心知识点: 重要程度为 ★★★ 的知识点
  - -v 模式: 显示前100个核心知识点
  - -d 模式: 显示前200个知识点的详细解析 + 前100个核心知识点
        """
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        default=DEFAULT_FILE_PATH,
        help=f'输入文件路径（支持.txt和.pdf） (默认: {DEFAULT_FILE_PATH})'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示核心知识点列表（前100个 ★★★ 级别知识点）'
    )
    
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='调试模式：显示前200个知识点的详细解析 + 核心知识点列表'
    )
    
    parser.add_argument(
        '--save-text',
        type=str,
        metavar='FILE',
        help='保存提取的文本到指定文件（用于调试PDF提取）'
    )
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = HistoryOutlineAnalyzer(args.file)
    
    # 检测文件类型
    file_ext = Path(args.file).suffix.lower()
    file_type = "PDF文件" if file_ext == '.pdf' else "文本文件"
    
    # 执行分析
    print(f"\n开始分析《中国近现代史纲要》规划卡...")
    print(f"文件路径: {args.file}")
    print(f"文件类型: {file_type}\n")
    
    if analyzer.run_analysis():
        # 如果指定了保存文本选项
        if args.save_text:
            try:
                with open(args.save_text, 'w', encoding='utf-8') as f:
                    f.write(analyzer.content)
                print(f"\n提取的文本已保存到: {args.save_text}\n")
            except Exception as e:
                print(f"\n保存文本失败: {e}\n")
        
        analyzer.print_report(verbose=args.verbose, debug=args.debug)
    else:
        print("\n分析失败！请检查文件路径和文件格式。")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())