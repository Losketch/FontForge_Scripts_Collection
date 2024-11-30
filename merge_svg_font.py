#!/usr/bin/env python3
"""
merge_svg_font.py - Merge multiple SVG files into a single SVG font
将多个SVG文件合并为单个SVG字体文件

Usage:
    fontforge -script merge_svg_font.py [input_dir] [output_font] [font_name]
"""

import fontforge
import os
import sys
from datetime import datetime

def create_svg_font(input_dir="input_dir", output_font="output_font.svg", font_name="CustomFont"):
    """
    Create SVG font from individual SVG files
    从单个SVG文件创建SVG字体
    """
    try:
        # 验证输入目录是否存在
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Input directory '{input_dir}' not found")

        # 创建新字体
        font = fontforge.font()
        
        # 设置字体基本信息
        font.fontname = font_name
        font.familyname = font_name
        font.fullname = font_name
        font.copyright = f"Created by merge_svg_font.py at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 计数器
        processed = 0
        errors = 0

        # 遍历目录中的所有SVG文件
        for filename in sorted(os.listdir(input_dir)):
            if not filename.endswith(".svg"):
                continue
                
            try:
                # 提取文件名中的Unicode码位
                unicode_str = filename.replace("u", "").replace(".svg", "")
                unicode_val = int(unicode_str, 16)
                
                # 创建新字形
                glyph = font.createChar(unicode_val)
                
                # 导入SVG轮廓
                svg_path = os.path.join(input_dir, filename)
                glyph.importOutlines(svg_path)
                
                # 优化字形（可选）
                glyph.removeOverlap()
                glyph.simplify()
                glyph.round()
                
                processed += 1
                
            except ValueError as e:
                print(f"Error processing {filename}: Invalid Unicode value")
                errors += 1
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                errors += 1

        # 设置字体参数
        font.ascent = 800
        font.descent = 200
        font.em = 1000
        
        # 保存字体
        font.generate(output_font)
        
        print(f"\nFont generation complete:")
        print(f"- Output file: {output_font}")
        print(f"- Processed glyphs: {processed}")
        print(f"- Errors: {errors}")
        
    except Exception as e:
        print(f"Error creating font: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # 处理命令行参数
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "input_dir"
    output_font = sys.argv[2] if len(sys.argv) > 2 else "output_font.svg"
    font_name = sys.argv[3] if len(sys.argv) > 3 else "CustomFont"
    
    create_svg_font(input_dir, output_font, font_name)