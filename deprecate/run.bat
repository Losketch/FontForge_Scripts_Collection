@echo off
:: 设置UTF-8编码，同时处理代码页错误
for /f "tokens=2 delims=:" %%a in ('chcp') do set "OLD_CP=%%a"
chcp 65001 >nul 2>nul || chcp 936 >nul 2>nul

setlocal EnableDelayedExpansion

:: 设置标题
title 字体处理工具 - 请将字体文件拖拽到此窗口

:: 获取脚本目录，处理特殊字符
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:"=%"
:: 处理路径末尾的斜杠
if "%SCRIPT_DIR:~-1%" == "\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:MAIN_LOOP
cls
echo ============================================
echo.
echo 请将字体文件拖拽到此窗口，按回车确认
echo 或者输入 回车 退出程序
echo.
set "INPUT_FILE="
set /p "INPUT_FILE="

:: 检查是否退出
if /i "%INPUT_FILE%"=="exit" goto :END

:: 移除引号
set "INPUT_FILE=%INPUT_FILE:"=%"

:: 基本检查
if "%INPUT_FILE%"=="" (
    echo 错误：未提供输入文件
    goto :WAIT_AND_CONTINUE
)

:: 检查文件是否存在
if not exist "%INPUT_FILE%" (
    echo 错误：找不到文件：%INPUT_FILE%
    goto :WAIT_AND_CONTINUE
)

:: 检查必要组件
call :CHECK_REQUIREMENTS || goto :WAIT_AND_CONTINUE

:: 检查文件扩展名
for %%F in ("%INPUT_FILE%") do set "EXT=%%~xF"
set "EXT=%EXT:.=%"
if /i not "%EXT%"=="ttf" if /i not "%EXT%"=="otf" (
    echo 错误：不支持的文件格式 [%EXT%]，仅支持 TTF 或 OTF 格式。
    goto :WAIT_AND_CONTINUE
)

:: 处理文件路径中的特殊字符
set "PROCESSED_PATH=%INPUT_FILE: =^ %"
set "PROCESSED_PATH=%PROCESSED_PATH:&=^&%"
set "PROCESSED_PATH=%PROCESSED_PATH:(=^(%"
set "PROCESSED_PATH=%PROCESSED_PATH:)=^)%"

echo.
echo 正在处理：%~nx0
echo 源文件：%INPUT_FILE%
echo 请稍候...
echo.

:: 创建临时目录
set "TEMP_DIR=%TEMP%\FontProcess_%RANDOM%"
mkdir "%TEMP_DIR%" 2>nul

:: 切换到临时目录执行
pushd "%TEMP_DIR%"

:: 执行字体处理
call :PROCESS_FONT "%INPUT_FILE%" || (
    echo 处理失败！
    goto :CLEANUP
)

:CLEANUP
:: 清理并返回原目录
popd
rd /s /q "%TEMP_DIR%" 2>nul

:WAIT_AND_CONTINUE
echo.
echo 按任意键继续...
pause >nul
goto :MAIN_LOOP

:END
:: 恢复原始代码页
chcp %OLD_CP% >nul
endlocal
exit /b 0

:CHECK_REQUIREMENTS
if not exist "%SCRIPT_DIR%\bin\fontforge.exe" (
    echo 错误：找不到 FontForge
    echo 请确保 bin\fontforge.exe 存在于程序目录下
    exit /b 1
)
if not exist "%SCRIPT_DIR%\merge_all_glyphs.py" (
    echo 错误：找不到处理脚本
    echo 请确保 merge_all_glyphs.py 存在于程序目录下
    exit /b 1
)
exit /b 0

:PROCESS_FONT
set "FONT_PATH=%~1"
set "ERROR_LOG=%TEMP_DIR%\error.log"

:: 使用 try-catch 方式执行
(
    "%SCRIPT_DIR%\bin\fontforge.exe" -script "%SCRIPT_DIR%\merge_all_glyphs.py" "%FONT_PATH%" 2>"%ERROR_LOG%"
) && (
    echo 处理完成
    exit /b 0
) || (
    echo 处理失败！错误信息：
    type "%ERROR_LOG%"
    exit /b 1
)
