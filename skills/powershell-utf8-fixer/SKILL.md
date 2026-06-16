---
name: powershell-utf8-fixer
description: 解决PowerShell中文乱码问题
version: 1.0.0
---

# PowerShell UTF-8 编码修复工具

解决Windows PowerShell中文乱码显示问题。

## 问题描述

在Windows PowerShell中执行Python脚本时，中文输出显示为乱码：
```
�����е��ĵ�����: 405  ← 乱码
集合中的文档数量: 405  ← 正确
```

## 解决方案

### 方案1：临时设置（当前会话有效）

在PowerShell中执行：
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
```

### 方案2：永久设置（推荐）

#### 步骤1：创建PowerShell配置文件
```powershell
# 检查配置文件是否存在
if (!(Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}

# 添加UTF-8设置到配置文件
Add-Content -Path $PROFILE -Value "
# UTF-8编码设置
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
`$env:PYTHONIOENCODING = 'utf-8'
"
```

#### 步骤2：重新加载配置文件
```powershell
. $PROFILE
```

#### 步骤3：验证设置
```powershell
python -c "print('中文测试：成功！')"
```

### 方案3：Windows系统设置（最彻底）

1. 打开 **控制面板**
2. 点击 **区域**
3. 点击 **管理** 选项卡
4. 点击 **更改系统区域设置**
5. 勾选 **Beta版: 使用Unicode UTF-8提供全球语言支持**
6. 点击 **确定**
7. **重启电脑**

## 验证方法

执行以下命令验证是否生效：
```powershell
python -c "print('测试中文：OK')"
```

如果显示 `测试中文：OK` 而不是乱码，说明设置成功。

## 注意事项

- 方案1只对当前PowerShell会话有效
- 方案2对当前用户的所有PowerShell会话有效
- 方案3对整个系统有效，但需要重启电脑
