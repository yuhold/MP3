# 🚀 MP3 快捷上传与直链分享工具

一个轻量级的 Flask 应用，提供 MP3 文件的快速上传、自定义文件名、多直链下载选择，并支持密码保护的文件删除功能。

**GitHub 仓库**: [yuhold/MP3](https://github.com/yuhold/MP3)

## ✨ 主要功能

*   **MP3 文件上传**: 简单易用的网页界面，快速上传您的 MP3 文件。
*   **自定义文件名**: 上传时可选择自定义文件名，支持中文字符，方便管理。
*   **随机文件名生成**: 如果不提供自定义文件名，系统会自动生成一个随机且唯一的短文件名。
*   **上传进度显示**: 前端提供上传进度条，实时显示上传状态。
*   **双直链下载选择**: 支持在配置文件中设置两个不同的下载地址（例如，不同的域名或IP），方便用户选择下载源。
*   **文件列表展示**: 清晰列出所有已上传的 MP3 文件及其对应的下载直链。
*   **密码保护的文件删除**: 通过简单的密码验证，安全删除不再需要的文件。
*   **INI 配置文件**: 所有关键设置（如主机、端口、上传目录、下载地址、密钥、密码等）均通过 `server_config.ini` 文件统一管理。

## 📦 快速开始

### 前提条件

在开始之前，请确保您的系统已安装以下软件：

*   **Python 3.6+**
*   **pip** (Python 包管理器)

### 安装步骤

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/yuhold/MP3.git
    cd MP3
    ```

2.  **创建虚拟环境 (推荐)**:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **安装依赖**:
    ```bash
    pip install Flask
    ```
    *(本项目主要依赖 Flask，Werkzeug、configparser 等是 Python 内置或 Flask 依赖项)*

## ⚙️ 配置说明

首次运行 `server.py` 时，如果 `server_config.ini` 文件不存在，系统会自动在项目根目录生成一个默认配置。**请务必根据您的实际需求修改这些配置项，特别是安全相关的密钥和密码！**

以下是 `server_config.ini` 文件的示例内容及说明：

```ini
# server_config.ini

[SERVER]
HOST = 0.0.0.0
# 服务器监听的IP地址。
# 0.0.0.0 表示监听所有可用的网络接口，允许外部访问。
# 127.0.0.1 表示只监听本地回环地址，仅限本机访问。
PORT = 5000
# 服务器监听的端口号。
UPLOAD_FOLDER = uploads
# 上传文件存放的目录名。该目录会在服务器启动时自动创建（如果不存在）。

[DOWNLOAD]
DOWNLOAD_HOST_1 = 127.0.0.1
# 第一个下载地址的主机名或IP。
# 例如：'gc2.yuholt.cn' 或 '192.168.1.100'。
# 此地址是用户在浏览器中访问文件时看到的地址。
DOWNLOAD_PORT_1 = 5000
# 第一个下载地址的端口。如果使用默认HTTP端口80或HTTPS端口443，则可省略。
DOWNLOAD_HOST_2 = 127.0.0.1
# 第二个下载地址的主机名或IP。提供备用下载链接。
DOWNLOAD_PORT_2 = 5000
# 第二个下载地址的端口。

[FLASK_APP]
SECRET_KEY = 请修改此密钥，生产环境请使用长且随机的字符串
# Flask 应用的秘密密钥，用于会话管理和消息签名。
# 务必修改为一个长、复杂、随机的字符串，不要使用默认值！
# 可以使用 Python 生成一个：import os; os.urandom(24).hex()

[UPLOAD_SETTINGS]
MAX_FILE_SIZE_MB = 100
# 允许上传的最大文件大小，单位为MB。
# 默认为100MB。

[SECURITY]
DELETE_PASSWORD = 请修改此密码
# 用于删除文件的密码。
# 务必修改为一个强密码，不要使用默认值！
```

## 🚀 使用方法

1.  **启动服务器**:
    在项目根目录下，运行：
    ```bash
    python server.py
    ```
    您将看到类似以下的输出：
    ```
    未找到 server_config.ini，正在创建默认配置文件...
    默认配置文件已创建在 server_config.ini。
    请务必编辑该文件，特别是 [FLASK_APP] 下的 SECRET_KEY，[DOWNLOAD] 下的 DOWNLOAD_HOST_1/PORT_1 和 DOWNLOAD_HOST_2/PORT_2，以及 [SECURITY] 下的 DELETE_PASSWORD。
    服务器正在启动，监听地址：http://0.0.0.0:5000
    文件将保存到目录：uploads
    下载直链1将使用域名/IP：127.0.0.1:5000
    下载直链2将使用域名/IP：127.0.0.1:5000
    单个文件最大上传大小：100MB
    文件删除需要密码鉴权。
     * Debug mode: on
    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
     * Running on all addresses (0.0.0.0)
     * Running on http://127.0.0.1:5000
    Press CTRL+C to quit
    ```

2.  **访问网页界面**:
    在您的浏览器中打开 `http://<您的服务器IP或域名>:<端口>` (例如：`http://localhost:5000` 或 `http://您的公网IP:5000`)。

3.  **上传文件**:
    *   点击 "选择文件" 按钮，选择一个 MP3 文件。
    *   在 "（可选）自定义文件名" 文本框中输入您想要的文件名（支持中文）。
    *   点击 "上传文件" 按钮。
    *   上传成功后，页面上方会显示上传成功的提示和两个可供下载的直链。

4.  **下载文件**:
    在 "已上传的 MP3 文件" 列表中，点击文件名或右侧的直链即可下载。每个文件都会显示两个来自您配置的下载地址的链接。

5.  **删除文件**:
    在文件列表中的每个文件旁边，有一个删除表单。输入您在 `server_config.ini` 中设置的 `DELETE_PASSWORD`，然后点击 "删除" 按钮。确认后文件将被删除。

## ⚠️ 安全注意事项

*   **`SECRET_KEY`**: 这是一个非常重要的密钥，用于保护 Flask 应用的安全。请**务必**将其更改为一个长、复杂、随机的字符串，并且不要泄露。在生产环境中，此密钥应通过环境变量或其他安全方式管理，而不是直接硬编码在配置文件中。
*   **`DELETE_PASSWORD`**: 这是删除文件的密码。请**务必**将其更改为一个强密码，以防止未经授权的文件删除。
*   **文件上传**: 尽管前端和后端都对文件类型和大小进行了限制，但任何文件上传功能都存在潜在风险。此工具仅允许上传 MP3 文件，并且对自定义文件名进行了安全清理，但仍不建议在高度敏感的环境中直接对外暴露。
*   **生产部署**: 本项目默认使用 Flask 内置的开发服务器 (`app.run(debug=True)`)。**这不适用于生产环境！** 在生产环境中，您应该使用专业的 WSGI 服务器 (如 Gunicorn, uWSGI) 配合反向代理 (如 Nginx, Apache) 来部署您的应用，并考虑启用 HTTPS。
*   **文件系统权限**: 确保 `uploads` 目录具有服务器进程写入的权限，但同时限制其他不必要的权限，以提高安全性。

## 🤝 贡献

欢迎任何形式的贡献，包括但不限于：

*   提交 Bug 报告
*   提出新功能建议
*   改进代码
*   完善文档

如果您有任何问题或建议，请随时通过 [GitHub Issues](https://github.com/yuhold/MP3/issues) 提出。

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](https://github.com/yuhold/MP3/blob/main/LICENSE) 文件。