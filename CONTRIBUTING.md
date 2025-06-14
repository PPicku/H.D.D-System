# 贡献指南

## 部署开发环境

### 在本地部署 Python 环境

[Download Python](https://www.python.org/downloads/)

### 下载项目源码，并进入到项目根目录

```bash
git clone https://github.com/PPicku/H.D.D-System && cd H.D.D-System/
```

### 创建虚拟环境

```bash
python -m venv .venv
```

### 进入虚拟环境

在 Windows 环境下

```powershell
./.venv/Scripts/activate
```

在 Bash

```bash
source ./.venv/bin/activate
```

附：退出虚拟环境的指令

```bash
deactivate
```

### 安装项目所需库

```bash
pip install -r requirements.[windows 或者 macos].txt
```

### 运行项目代码

```bash
python .\Main.PY
```
