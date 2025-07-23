import argparse
import os
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.pens.recordingPen import RecordingPen

def get_unicode_codepoints(font: TTFont) -> set[int]:
    """
    从已加载的字体文件中提取所有Unicode码位。
    """
    codepoints = set()
    if 'cmap' not in font:
        print(f"警告: 字体文件不包含 'cmap' 表。")
        return codepoints

    for table in font['cmap'].tables:
        if isinstance(table, CmapSubtable):
            codepoints.update(table.cmap.keys())
    return codepoints

def format_codepoints(codepoint_set: set[int]) -> str:
    """将码位集合格式化为易读的字符串。"""
    if not codepoint_set:
        return "无"
    sorted_codepoints = sorted(list(codepoint_set))
    # 显示前10个和后10个
    if len(sorted_codepoints) > 20:
        return ", ".join([f"U+{cp:04X}" for cp in sorted_codepoints[:10]]) + \
               f", ... ({len(sorted_codepoints) - 20}更多), " + \
               ", ".join([f"U+{cp:04X}" for cp in sorted_codepoints[-10:]])
    else:
        return ", ".join([f"U+{cp:04X}" for cp in sorted_codepoints])

def compare_fonts(old_font_path: str, new_font_path: str):
    """
    比较两个字体文件，找出cmap表中的新增/减少码位，并检测字形轮廓和度量改动。
    """
    print("\n" + "="*60)
    print(f"正在比较字体文件:")
    print(f"  旧字体: {old_font_path}")
    print(f"  新字体: {new_font_path}")
    print("="*60 + "\n")

    if not os.path.exists(old_font_path):
        print(f"错误: 旧字体文件 '{old_font_path}' 不存在。")
        return
    if not os.path.exists(new_font_path):
        print(f"错误: 新字体文件 '{new_font_path}' 不存在。")
        return

    try:
        old_font = TTFont(old_font_path)
        new_font = TTFont(new_font_path)
    except Exception as e:
        print(f"错误: 无法加载字体文件。请检查文件是否损坏或路径是否正确。详细信息: {e}")
        return

    print("正在提取旧字体中的Unicode码位...")
    old_codepoints = get_unicode_codepoints(old_font)
    print(f"旧字体包含 {len(old_codepoints)} 个Unicode码位。\n")

    print("正在提取新字体中的Unicode码位...")
    new_codepoints = get_unicode_codepoints(new_font)
    print(f"新字体包含 {len(new_codepoints)} 个Unicode码位。\n")

    print("-" * 60)
    print("正在分析码位差异 (cmap 表)...")
    print("-" * 60 + "\n")

    added_codepoints = new_codepoints - old_codepoints
    removed_codepoints = old_codepoints - new_codepoints

    print("✨ 新增的Unicode码位字形:")
    print(f"  数量: {len(added_codepoints)}")
    print(f"  列表: {format_codepoints(added_codepoints)}\n")

    print("🗑️ 减少的Unicode码位字形:")
    print(f"  数量: {len(removed_codepoints)}")
    print(f"  列表: {format_codepoints(removed_codepoints)}\n")

    # --- 字形轮廓和度量改动检测 ---
    print("\n" + "="*60)
    print("正在分析字形轮廓和度量改动...")
    print("="*60 + "\n")

    common_codepoints = old_codepoints.intersection(new_codepoints)

    changed_outlines = set()
    changed_metrics = set()

    old_cmap_map = old_font.getBestCmap()
    new_cmap_map = new_font.getBestCmap()

    old_glyph_set = old_font.getGlyphSet()
    new_glyph_set = new_font.getGlyphSet()

    old_hmtx = old_font['hmtx'] if 'hmtx' in old_font else None
    new_hmtx = new_font['hmtx'] if 'hmtx' in new_font else None

    old_has_outlines = 'glyf' in old_font or 'CFF ' in old_font
    new_has_outlines = 'glyf' in new_font or 'CFF ' in new_font

    if not old_has_outlines or not new_has_outlines:
        print("警告: 至少有一个字体文件不包含轮廓数据 (glyf 或 CFF 表)，跳过轮廓比较。")
    else:
        for codepoint in sorted(list(common_codepoints)):
            old_glyph_name = old_cmap_map.get(codepoint)
            new_glyph_name = new_cmap_map.get(codepoint)

            if old_glyph_name is None or new_glyph_name is None:
                continue

            old_pen = RecordingPen()
            new_pen = RecordingPen()

            try:
                old_glyph_set[old_glyph_name].draw(old_pen)
                new_glyph_set[new_glyph_name].draw(new_pen)

                if old_pen.value != new_pen.value:
                    changed_outlines.add(codepoint)
            except KeyError as ke:
                print(f"警告: 无法获取码位 U+{codepoint:04X} 对应的字形 '{ke}' 的轮廓数据。跳过轮廓比较。")
            except Exception as e:
                print(f"警告: 比较码位 U+{codepoint:04X} 的字形轮廓时发生错误: {e}. 跳过轮廓比较。")

    if not old_hmtx or not new_hmtx:
        print("警告: 至少有一个字体文件不包含水平度量数据 (hmtx 表)，跳过度量比较。")
    else:
        for codepoint in sorted(list(common_codepoints)):
            old_glyph_name = old_cmap_map.get(codepoint)
            new_glyph_name = new_cmap_map.get(codepoint)

            if old_glyph_name is None or new_glyph_name is None:
                continue

            try:
                old_width, old_lsb = old_hmtx[old_glyph_name]
                new_width, new_lsb = new_hmtx[new_glyph_name]

                if old_width != new_width or old_lsb != new_lsb:
                    changed_metrics.add(codepoint)
            except KeyError as ke:
                print(f"警告: 无法获取码位 U+{codepoint:04X} 对应的字形 '{ke}' 的度量数据。跳过度量比较。")
            except Exception as e:
                print(f"警告: 比较码位 U+{codepoint:04X} 的度量时发生错误: {e}. 跳过度量比较。")

    print("✏️ 发生字形轮廓改动的Unicode码位:")
    print(f"  数量: {len(changed_outlines)}")
    print(f"  列表: {format_codepoints(changed_outlines)}\n")

    print("📏 发生字形度量改动的Unicode码位 (如宽度、左侧边距):")
    print(f"  数量: {len(changed_metrics)}")
    print(f"  列表: {format_codepoints(changed_metrics)}\n")

    print("="*60)
    if not added_codepoints and not removed_codepoints and not changed_outlines and not changed_metrics:
        print("🎉 两个字体文件完全一致，没有发现任何码位或字形改动。")
    else:
        print("✅ 码位和字形改动分析完成。")
    print("="*60 + "\n")

    old_font.close()
    new_font.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="比较两个字体文件（新旧版本）的cmap表，找出新增和减少的Unicode码位字形，并检测字形轮廓和度量改动。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("old_font", help="旧字体文件的路径，例如: old_font.ttf")
    parser.add_argument("new_font", help="新字体文件的路径，例如: new_font.ttf")

    args = parser.parse_args()

    compare_fonts(args.old_font, args.new_font)
