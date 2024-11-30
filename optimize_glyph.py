#!/usr/bin/env python3
"""
optimize_glyph.py - Font Glyph Optimization Tool
字体字形轮廓优化工具

This script optimizes font glyphs by:
- Converting compound glyphs to actual outlines
- Simplifying and cleaning up contours
- Standardizing control points and curves
- Optimizing line endpoints
- Adding hints for better rendering

Usage:
    fontforge -script optimize_glyph.py "font_file_path"
    fontforge -script optimize_glyph.py "font_file_path" -s simplify_value

Arguments:
    font_file_path: Path to the input font file
    simplify_value: Optional parameter to control outline simplification (default: 0.5)
                   - 0.5-1.0: Conservative mode, preserves more details
                   - 1.0-2.0: Balanced mode, moderate optimization
                   - 2.0-3.0: Aggressive mode, maximum simplification

Output:
    Creates a new optimized font file with "_merge_glyphs" suffix
"""

import sys
import os
import io
import time
import contextlib

os.system('color')

try:
    import fontforge
except ModuleNotFoundError:
    print("\n\033[31m警告：当前没有使用 `fontforge` 运行，功能无法使用\033[0m")
    pass

def format_time(seconds):
    """将秒数转换为人类可读的时间格式"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"

def get_glyph_info(glyph):
    """获取字形的可读信息"""
    try:
        if glyph.unicode != -1:  # 如果有 Unicode 值
            char = chr(glyph.unicode)
            return f"U+{glyph.unicode:04X}"
        else:  # 如果没有 Unicode 值，只返回字形名
            return f"{glyph.glyphname}"
    except (ValueError, AttributeError):
        return f"{glyph.glyphname}"

def process_compound_glyph(glyph):
    """处理复合字形，将引用转换为实际轮廓"""
    try:
        if len(glyph.references) > 0:
            try:
                glyph.unlinkReferences()
            except (AttributeError, TypeError):
                glyph.unlink()
    except (AttributeError, TypeError):
        pass

def process_line_endpoints(glyph):
    """处理直线段端点，确保直线段的端点是方形控点"""
    contours = glyph.foreground
    for contour in contours:
        prev_point = None
        for point in contour:
            if prev_point is not None:
                # 如果两点构成水平或垂直线
                if (abs(point.x - prev_point.x) < 0.1 or 
                    abs(point.y - prev_point.y) < 0.1):
                    point.type = fontforge.splineCorner
                    prev_point.type = fontforge.splineCorner
            prev_point = point

def processing_optimization_glyph_extension(glyph):
    """处理优化字形扩展"""
    glyph.simplify(0.5, ('mergelines', 'smoothcurves', 'choosehv', 'removesingletonpoints' ), 0.3, 0, 0.5)
    glyph.addExtrema()
    glyph.width = int(round(glyph.width / 10.0) * 10)
    glyph.balance()  # 平衡贝塞尔控制点
    glyph.autoHint()

def process_font(input_file, simplify_value=0.5):
    """主函数"""
    try:
        font = fontforge.open(input_file)
    except OSError as e:
        print(f"\033[31m错误：无法打开字体文件 - {e}\033[0m")
        return
    glyphs = list(font.glyphs())
    total_glyphs = len(glyphs)

    # 验证字形数量
    if total_glyphs == 0:
        print("警告：没有找到可处理的字形")
        return

    start_time = time.time()
    last_update_time = start_time

    print(f"开始处理字体，共 {total_glyphs} 个字形...")
    print("进度", end="")

    for index, glyph in enumerate(glyphs):
        # 进度计算
        current_time = time.time()
        elapsed_time = current_time - start_time
        progress = (index + 1) / total_glyphs if total_glyphs > 0 else 0

        # 预估剩余时间
        if index > 0 and elapsed_time > 0:  # 添加 elapsed_time 检查
            glyphs_per_second = (index + 1) / elapsed_time
            remaining_glyphs = total_glyphs - (index + 1)
            estimated_remaining_time = remaining_glyphs / glyphs_per_second
        else:
            estimated_remaining_time = 0

        glyph_info = get_glyph_info(glyph)

        # 更新进度条（每n秒更新一次）
        if current_time - last_update_time >= 0.2:
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = "#" * filled_length + "-" * (bar_length - filled_length)

            print(f"\r\033[34m进度({index + 1}/{total_glyphs})\033[32m: [{bar}] "
                f"\033[35m({progress:.1%})\033[0m "
                f"\033[33m⏱️ {format_time(elapsed_time)} "
                f"\033[36m⏳ {format_time(estimated_remaining_time)} "
                f"\033[0m⚡ 当前处理: {glyph_info}",
                end="", flush=True
            )
            last_update_time = current_time

        # 处理复合字形
        process_compound_glyph(glyph)

        # 第一轮优化：初步清理和简化
        glyph.simplify(0.1, ('mergelines', 'choosehv'), 0.1, 0.1, 0)
        glyph.round(1)
        glyph.simplify(0, ('forcelines',))  # 强制将接近直线的段转换为直线

        # 处理直线段端点
        process_line_endpoints(glyph)
        glyph.simplify(simplify_value, ('mergelines', 'smoothcurves', 'removesingletonpoints'), 0.3, 0, 0.5)

        # 第二轮优化：添加必要的控制点和标准化
        glyph.addExtrema()            # 在曲线的极值处添加控制点，提高编辑精度
        glyph.canonicalContours()     # 确保轮廓按标准顺序排列
        glyph.canonicalStart()        # 设置标准起始点，有助于后续处理

        # 第三轮优化：最终清理
        glyph.round()                 # 将控制点坐标取整
        glyph.simplify()              # 再次简化轮廓，去除冗余点

        # 第四轮优化：轮廓处理和微调
        glyph.removeOverlap()         # 合并所有重叠的路径
        glyph.correctDirection()      # 确保外轮廓为顺时针，内轮廓为逆时针
        glyph.simplify(simplify_value, ('mergelines', 'smoothcurves'), 0.3, 0, 0.5)
        glyph.round()                 # 最终的坐标取整
        glyph.autoHint()              # 添加自动提示信息，改善小尺寸显示效果

        # 处理优化字形扩展（可选）
        # processing_optimization_glyph_extension(glyph)

    # 完成处理
    total_time = time.time() - start_time
    bar = "=" * 30
    print(f"\n\033[34m进度({total_glyphs}/{total_glyphs})\033[32m: [{bar}] "
        f"\033[35m(100%)\033[0m "
        f"\033[33m⏱️ 总用时: {format_time(total_time)}\033[0m"
    )
    print(f"\n新字体保存中...")

    # 保存新字体
    file_name, file_extension = os.path.splitext(input_file)
    output_file = f"{file_name}_merge_glyphs{file_extension}"
    font.generate(output_file, flags=('opentype', 'round', 'dummy-dsig', 'apple'))
    print(f"\n新字体已保存为: {output_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='字体轮廓优化工具')
    parser.add_argument('font_file', nargs='?', help='字体文件路径')
    parser.add_argument(
        '-s', '--simplify',
        type=float, default=0.5,
        help='simplify 参数值 (默认: 0.5)'
    )

    args = parser.parse_args()

    if not args.font_file:
        print("\033[32m\n ============================= 使用说明 ==============================")
        print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
        print("┃　1. 打开命令行(cmd)　　　　　　　　　　　　　　　　　　 　　　　　 ┃")
        print("┃　2. 基本命令：　　　　　　　　　　　　　　　　　　 　　　　　　　  ┃")
        print('┃　 　fontforge -script optimize_glyph.py "你的字体文件路径"　　　　 ┃')
        print("┃　3. 高级命令（自定义 simplify 参数）：　　　　　　　　　　　　　   ┃")
        print('┃　 　fontforge -script optimize_glyph.py "字体路径" -s 2.0　　　 　 ┃')
        print("┃　　　　　　　　　　　　　　　　　　 　　　　　　　　　　　　　　　 ┃")
        print("┃　例如：　　　　　　　　　　　　　　　　　　　　　 　　　　　　　　 ┃")
        print('┃　 　fontforge -script optimize_glyph.py "C:\\字体\\测试字体.ttf"　　 ┃')
        print('┃　 　fontforge -script optimize_glyph.py "测试字体.ttf" -s 2.5　　　┃')
        print(r'┃　 或者把 `fontforge` 换成 ".\bin\fontforge.exe" 　　　　　　　　　 ┃')
        print("┃　　　　　　　　　　　　　　　　　　 　　　　　　　　　　　　　　　 ┃")
        print("┃　注意：路径中如果有空格，需要用引号括起来　　　　　　　　　　　　  ┃")
        print("┃　　　　　　　　　　　　　　　　　　 　　　　　　　　　　　　　　　 ┃")
        print("┃　关于 simplify 参数：　　　　　　　　　　　　　　　　　　　　　　　┃")
        print("┃　·作用：控制字体轮廓的简化程度　　　　　　　　　　　　　　　　　　┃")
        print("┃　·默认值：0.5（保守模式）　　　　　　　　　　　　　　　　　　　　 ┃")
        print("┃　·参考值范围：　　　　　　　　　　　　　　　　　　　　　　　　　　┃")
        print("┃　　- 0.5-1.0：保守模式，保留更多细节，文件更大　　　　　　　　　　 ┃")
        print("┃　　- 1.0-2.0：平衡模式，适中的优化效果　　　　　　　　　　　　　　 ┃")
        print("┃　　- 2.0-3.0：激进模式，更大程度简化，文件更小　　　　　　　　　　 ┃")
        print("┃　·建议：　　　　　　　　　　　　　　　　　　　　　　　　　　　　　┃")
        print("┃　　- 细节丰富的美术字体建议使用较小值（0.5-1.0）　　　　　　　　　 ┃")
        print("┃　　- 常规字体推荐使用默认值（1.5）　　　　　　　　　　　　　　　　 ┃")
        print("┃　　- 笔画简单的字体可以尝试较大值（2.0-3.0）　　　　　　　　　　　 ┃")
        print("┃　　　　　　　　　　　　　　　　　　 　　　　　　　　　　　　　　　 ┃")
        print('┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛')
        input("\033[0m按回车键退出...")
        sys.exit(1)

    try:
        print(f"\n使用 simplify 参数值: {args.simplify}")
        process_font(args.font_file, args.simplify)
        print("处理完成！")
    except Exception as e:
        print(f"\n\033[31m发生严重错误：{str(e)}\033[0m")
        input("按回车键退出...")
