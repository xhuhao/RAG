@echo off
REM =============================================
REM Skill安装脚本
REM 功能：安装skill到项目目录并创建符号链接
REM 用法：install-skill.bat <skill-package>
REM 示例：install-skill.bat mineru98/skills-store@powershell-utf8-fixer
REM =============================================

setlocal enabledelayedexpansion

REM 检查参数
if "%~1"=="" (
    echo 用法: install-skill.bat ^<skill-package^>
    echo 示例: install-skill.bat mineru98/skills-store@powershell-utf8-fixer
    exit /b 1
)

set SKILL_PACKAGE=%~1
set PROJECT_SKILLS_DIR=D:\项目\RAG-CC\RAG\skills
set AGENT_SKILLS_DIR=C:\Users\许昊\.agents\skills

REM 提取skill名称（取@后面的部分）
for /f "tokens=2 delims=@" %%a in ("%SKILL_PACKAGE%") do set SKILL_NAME=%%a
if "%SKILL_NAME%"=="" set SKILL_NAME=%SKILL_PACKAGE%

echo =============================================
echo 安装Skill: %SKILL_PACKAGE%
echo Skill名称: %SKILL_NAME%
echo 项目目录: %PROJECT_SKILLS_DIR%
echo =============================================

REM 1. 安装skill到默认位置
echo.
echo [1/4] 安装skill到默认位置...
npx skills add %SKILL_PACKAGE% -g -y
if errorlevel 1 (
    echo 安装失败！
    exit /b 1
)

REM 2. 检查是否安装成功
echo.
echo [2/4] 检查安装状态...
if not exist "%AGENT_SKILLS_DIR%\%SKILL_NAME%" (
    echo skill未安装到默认位置！
    exit /b 1
)
echo 安装成功！

REM 3. 移动到项目目录
echo.
echo [3/4] 移动到项目目录...
if exist "%PROJECT_SKILLS_DIR%\%SKILL_NAME%" (
    echo 项目目录已存在该skill，跳过移动
) else (
    move "%AGENT_SKILLS_DIR%\%SKILL_NAME%" "%PROJECT_SKILLS_DIR%\%SKILL_NAME%"
    if errorlevel 1 (
        echo 移动失败！
        exit /b 1
    )
    echo 移动成功！
)

REM 4. 创建符号链接（需要管理员权限）
echo.
echo [4/4] 创建符号链接...
if exist "%AGENT_SKILLS_DIR%\%SKILL_NAME%" (
    echo 符号链接已存在，跳过创建
) else (
    mklink /D "%AGENT_SKILLS_DIR%\%SKILL_NAME%" "%PROJECT_SKILLS_DIR%\%SKILL_NAME%"
    if errorlevel 1 (
        echo 创建符号链接失败！请以管理员身份运行此脚本。
        echo 或者手动创建符号链接：
        echo mklink /D "%AGENT_SKILLS_DIR%\%SKILL_NAME%" "%PROJECT_SKILLS_DIR%\%SKILL_NAME%"
        exit /b 1
    )
    echo 符号链接创建成功！
)

echo.
echo =============================================
echo 安装完成！
echo Skill位置: %PROJECT_SKILLS_DIR%\%SKILL_NAME%
echo 符号链接: %AGENT_SKILLS_DIR%\%SKILL_NAME%
echo =============================================

endlocal
