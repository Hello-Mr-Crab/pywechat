# Quick Start

欢迎使用**pywechat！Windows微信桌面版自动化开源RPA工具库。

!['微信安装包'](/pics/wechat.png "微信")

## 开始前必看

[微信4.1+自动化说明](/Weixin4.0.md)

源代码共包含两个核心Package：
***`pywechat`**：适配 **微信3.9.x**版本。
***`pyweixin`**：适配 **微信4.x版本**（具有Skill及MCP扩展,具体可见Skill,Mcp）

## 环境要求

| 依赖项 | 版本要求 |
| :--- | :--- |
| **操作系统** | Windows 10 / 11 (**64位**) |
| **Python** | Python >= 3.10（支持TypeHint） |
| **微信** | 3.9.x 或 4.x (根据使用的包决定) |

## 项目结构

```block
src/
│   ├── pywechat/
│   │   ├── WeChatAuto.py
│   │   └── ...
│   └── pyweixin/
│       ├── WeChatAuto.py
│       └── ...
├── setup.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 安装与使用(Python Package)

最新版pywechat已同步发布于PYPI,版本为1.9.8

### 全局使用

```bash
pip install pywechat127
```

### 本地开发模式安装

```bash
cd src
pip install -e .
```

### 如果需要快速本地开发与测试，还可以在当前目录下相对导入使用

```block
workspace/
│   ├── pywechat/
│   │   ├── WeChatAuto.py
│   │   └── ...
│   └── pyweixin/
│   │   ├── WeChatAuto.py
│   │   └── ...
│   │
│   └── test.py
```

不过需要先安装依赖(如果没有的话):

```bash
pip install -r requirements.txt
```

## 安装与使用(Skill)

**`OpenClaw`**

最新版本1.0.4

```bash
openclaw skills install pyweixin-rpa
```

### 其他平台(cmd命令)

下边几个平台亦可使用github链接导入(后续会发布一个新repo)

**`codex`**

```bash
cd %USERPROFILE%
cd .codex\skills
robocopy "D:\autowechat\Skill\OtherPlatforms\pyweixin-rpa" pyweixin-rpa /E
```

**`cursor`**  

```bash
cd %USERPROFILE%
cd .cursor\skills
robocopy "D:\autowechat\Skill\OtherPlatforms\pyweixin-rpa" pyweixin-rpa /E
```

注意将"D:\autowechat\Skill\OtherPlatforms\pyweixin-rpa"替换为实际路径，如果上述命令失败亦可手动复制到对应目录然后重启codex,cursor

**`claude`**

Customize内点击Create Skill，选择Upload a Skill

!['Claude导入'](/pics/claude导入自定义skill.png "Claude")

选择pyweixin-rpa.skill文件上传

<p align="center">
  <img src="/pics/claude选择skill.png" alt="claude选择skill">
</p>

上传后便可以使用了

!['Claude接入skill'](/pics/claude接入pyweixin-rpa.png "Claude")

### Have fun in WechatAutomation (＾＿－)
