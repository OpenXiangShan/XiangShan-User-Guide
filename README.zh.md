# 香山用户指南

## 翻译

我们正在使用 [Weblate](https://hosted.weblate.org/projects/openxiangshan/user-guide/) 将本项目文档翻译为英文及其他语言。欢迎大家参与翻译工作，帮助我们一起完善文档！

本项目文档的原始语言为中文，英文翻译正在进行中。

## 构建

我们使用 Pandoc 和 MkDocs 来构建此文档。

### Pandoc

Pandoc 用于构建 PDF 和单页 HTML 格式的文档。

```bash
# 安装依赖
bash ./utils/dependency.sh

# 构建 PDF
make pdf

# 构建用于打印的 PDF
make pdf TWOSIDE=1

# 构建 HTML（暂不可用）
make html

# 执行默认构建（PDF）
make
```

### MkDocs

MkDocs 用来构建部署于互联网的静态网站。

```bash
# 创建并激活 Python 虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 预览网站
mkdocs serve -f mkdocs-zh.yml

# 构建网站
mkdocs build -f mkdocs-zh.yml
```

## 许可协议

这份文档采用知识共享署名 4.0 协议授权。

版权所有 © 香山团队·北京开源芯片研究院
