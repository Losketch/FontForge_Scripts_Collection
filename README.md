# FontForge Scripts Collection

一组用于字体处理的 FontForge Python 脚本集合，提供字体优化、格式转换和 SVG 字体生成等功能。

## 功能特性

- 🔧 字形优化和轮廓合并
  - 简化和标准化字形轮廓
  - 合并重叠路径
  - 添加渲染提示
- 🔄 字体格式转换
  - 支持主流字体格式互转
  - 自动优化参数配置
- 🎨 SVG 字体生成
  - 批量 SVG 文件合并
  - 生成字体元数据

## 脚本说明

### 1. optimize_glyph.py
字形优化和轮廓合并脚本，提供全面的字形清理和优化功能。

```bash
fontforge -script optimize_glyph.py input.ttf [options]
    -s, --simplify FLOAT  轮廓简化程度 (默认0.5)
    -h, --help           显示帮助信息
```

功能特性：
- 将复合字形转换为实际轮廓
- 简化和清理冗余节点
- 标准化控制点和曲线
- 优化线条端点
- 自动添加渲染提示
- 修复轮廓方向
- 去除重叠路径

### 2. convert_font.py
字体格式转换脚本，支持主流字体格式的互相转换。

```bash
fontforge -script convert_font.py input_font [options]
    -o, --output OUTPUT    输出字体文件名称（可选）
    -f, --format FORMAT   输出格式 (ttf/otf/woff/woff2/eot/svg)，默认：woff2
```

支持格式：
- TrueType (.ttf)
- OpenType (.otf)
- WOFF (.woff)
- WOFF2 (.woff2)
- Embedded OpenType (.eot)
- SVG (.svg)

### 3. merge_svg_font.py
将多个 SVG 文件合并生成 SVG 字体。

```bash
fontforge -script merge_svg_font.py input_folder [output_font] [font_name]
    output_font    输出 SVG 字体文件
    font_name       字体名称
```

功能特性：
- 将目录下符合文件名（uxxxx.svg）的 SVG 文件批量导入 SVG 字体
- 分配 Unicode 码位
- 生成字体元数据
- 支持自定义字体信息

## 安装要求

### Linux
```bash
sudo apt update && sudo apt install fontforge python3-fontforge
```

### macOS
```bash
brew install fontforge
```

### Windows
从 [FontForge 仓库](https://github.com/fontforge/fontforge/releases/latest) 下载安装包

## 使用示例

### 字形优化
```bash
# 基础优化
fontforge -script optimize_glyph.py input.ttf

# 设置简化程度
fontforge -script optimize_glyph.py input.ttf -s 1.5
```

### 格式转换
```bash
# TTF 转 WOFF2
fontforge -script convert_font.py input.ttf -o output.woff2 -f woff2
```

### SVG 字体生成
```bash
# 基础用法
fontforge -script merge_svg_font.py ./svg_folder output_font.svg "MyFont"
```

## 注意事项

- 使用前请确保安装了最新版本的 FontForge
- 建议在处理前备份原始字体文件
- SVG 文件命名必须使用 Unicode 码位（如：`u4E00.svg`）
- 优化参数可能需要根据具体字体调整
- 部分字体可能包含授权限制，请确认许可证

## 许可证

本项目采用 [Apache-2.0 许可证](LICENSE)

## 致谢

- [FontForge](https://fontforge.org/) 项目及其社区
- 所有贡献者和测试者

## 问题反馈

如果你发现任何问题或有改进建议，欢迎：
1. 提交 [Issue](../../issues)
2. 发起 [Pull Request](../../pulls)