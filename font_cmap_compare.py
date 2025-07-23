import argparse
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
import os

def get_unicode_codepoints(font_path: str) -> set[int]:
    """
    从字体文件中提取所有Unicode码位。
    """
    codepoints = set()
    try:
        font = TTFont(font_path)
        if 'cmap' not in font:
            print(f"警告: 字体文件 '{font_path}' 不包含 'cmap' 表。")
            return codepoints

        for table in font['cmap'].tables:
            if isinstance(table, CmapSubtable):
                codepoints.update(table.cmap.keys())
        font.close()
    except Exception as e:
        print(f"错误: 无法处理字体文件 '{font_path}': {e}")
    return codepoints

def compare_fonts_cmap(old_font_path: str, new_font_path: str):
    """
    比较两个字体文件的cmap表，找出新增和减少的Unicode码位。
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

    print("正在提取旧字体中的Unicode码位...")
    old_codepoints = get_unicode_codepoints(old_font_path)
    print(f"旧字体包含 {len(old_codepoints)} 个Unicode码位。\n")

    print("正在提取新字体中的Unicode码位...")
    new_codepoints = get_unicode_codepoints(new_font_path)
    print(f"新字体包含 {len(new_codepoints)} 个Unicode码位。\n")

    print("-" * 60)
    print("正在分析码位差异...")
    print("-" * 60 + "\n")

    added_codepoints = new_codepoints - old_codepoints
    removed_codepoints = old_codepoints - new_codepoints

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

    print("✨ 新增的Unicode码位字形:")
    print(f"  数量: {len(added_codepoints)}")
    print(f"  列表: {format_codepoints(added_codepoints)}\n")

    print("🗑️ 减少的Unicode码位字形:")
    print(f"  数量: {len(removed_codepoints)}")
    print(f"  列表: {format_codepoints(removed_codepoints)}\n")

    print("="*60)
    if not added_codepoints and not removed_codepoints:
        print("🎉 两个字体的 'cmap' 表完全一致，没有发现码位差异。")
    else:
        print("✅ 码位差异分析完成。")
    print("="*60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="比较两个字体文件（新旧版本）的cmap表，找出新增和减少的Unicode码位字形。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("old_font", help="旧字体文件的路径，例如: old_font.ttf")
    parser.add_argument("new_font", help="新字体文件的路径，例如: new_font.ttf")

    args = parser.parse_args()

    compare_fonts_cmap(args.old_font, args.new_font)
