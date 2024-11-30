@echo off
:: 设置UTF-8编码，同时处理代码页错误
for /f "tokens=2 delims=:" %%a in ('chcp') do set "OLD_CP=%%a"
chcp 65001 >nul 2>nul || chcp 936 >nul 2>nul

setlocal EnableDelayedExpansion

:: 警告
echo 警告：一切都是建立在把 `fontforge.exe` 添加进 环境变量 后才能正常运行
echo 按任意键继续...
pause >nul

:: P1
echo 请把 FontCreator 中输出的P1源文件重命名为 `PlangothicP1-Regular_raw.ttf`
echo 按任意键继续...
pause >nul

fontforge -script merge_all_glyphs.py PlangothicP1-Regular_raw.ttf -s 0.5
echo.首先请在 FontCreator 中打开 `PlangothicP1-Regular_raw_merge_glyphs.ttf`
echo.然后`全选字形`，之后选择菜单栏"编辑(E)"^>"优化轮廓(Z)"
echo.最后输出电脑字体 ttf 并重命名为 `PlangothicP1-Regular_temp.ttf`
echo 按任意键继续...
pause >nul

fontforge -script convert-to-woff2.py PlangothicP1-Regular_temp.ttf -o PlangothicP1-Regular.ttf -f ttf
fontforge -script convert-to-woff2.py PlangothicP1-Regular.ttf -f otf
echo 处理完成...
pause >nul



:: P2
echo 请把 FontCreator 中输出的P2源文件重命名为 `PlangothicP2-Regular_raw.ttf`
echo 按任意键继续...
pause >nul

fontforge -script merge_all_glyphs.py PlangothicP2-Regular_raw.ttf -s 0.5
echo.首先请在 FontCreator 中打开 `PlangothicP2-Regular_raw_merge_glyphs.ttf`
echo.然后`全选字形`，之后选择菜单栏"编辑(E)"^>"优化轮廓(Z)"
echo.最后输出电脑字体 ttf 并重命名为 `PlangothicP2-Regular_temp.ttf`
echo 按任意键继续...
pause >nul

fontforge -script convert-to-woff2.py PlangothicP2-Regular_temp.ttf -o PlangothicP2-Regular.ttf -f ttf
fontforge -script convert-to-woff2.py PlangothicP2-Regular.ttf -f otf
echo 处理完成...
pause >nul