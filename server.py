# server.py
import os
import configparser
from flask import Flask, request, send_from_directory, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import random
import string
import re # <-- 新增：导入 re 模块

# --- 配置加载 ---
config = configparser.ConfigParser()
config_path = 'server_config.ini'

# 如果配置文件不存在，则创建默认配置并提示用户
if not os.path.exists(config_path):
    print(f"未找到 {config_path}，正在创建默认配置文件...")
    config['SERVER'] = {
        'HOST': '0.0.0.0',
        'PORT': '5000',
        'UPLOAD_FOLDER': 'uploads'
    }
    config['DOWNLOAD'] = {
        'DOWNLOAD_HOST_1': '127.0.0.1',
        'DOWNLOAD_PORT_1': '5000',
        'DOWNLOAD_HOST_2': '127.0.0.1',
        'DOWNLOAD_PORT_2': '5000'
    }
    config['FLASK_APP'] = {
        'SECRET_KEY': '请修改此密钥，生产环境请使用长且随机的字符串'
    }
    config['UPLOAD_SETTINGS'] = {
        'MAX_FILE_SIZE_MB': '100'
    }
    config['SECURITY'] = {
        'DELETE_PASSWORD': '请修改此密码'
    }
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)
    print(f"默认配置文件已创建在 {config_path}。")
    print("请务必编辑该文件，特别是 [FLASK_APP] 下的 SECRET_KEY，[DOWNLOAD] 下的 DOWNLOAD_HOST_1/PORT_1 和 DOWNLOAD_HOST_2/PORT_2，以及 [SECURITY] 下的 DELETE_PASSWORD。")
    # exit("请修改配置文件后重新启动服务器。")
else:
    config.read(config_path, encoding='utf-8')

# 从配置文件读取设置
SERVER_HOST = config['SERVER']['HOST']
SERVER_PORT = int(config['SERVER']['PORT'])
UPLOAD_FOLDER = config['SERVER']['UPLOAD_FOLDER']

DOWNLOAD_HOST_1 = config['DOWNLOAD']['DOWNLOAD_HOST_1']
DOWNLOAD_PORT_1 = int(config['DOWNLOAD']['DOWNLOAD_PORT_1'])
DOWNLOAD_HOST_2 = config['DOWNLOAD']['DOWNLOAD_HOST_2']
DOWNLOAD_PORT_2 = int(config['DOWNLOAD']['DOWNLOAD_PORT_2'])

FLASK_SECRET_KEY = config['FLASK_APP']['SECRET_KEY']
MAX_FILE_SIZE_MB = int(config['UPLOAD_SETTINGS']['MAX_FILE_SIZE_MB'])
DELETE_PASSWORD = config['SECURITY']['DELETE_PASSWORD']

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = FLASK_SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024 # MB to Bytes

# --- 辅助函数：生成随机文件名基础部分 ---
def generate_random_filename_base(length_min=6, length_max=8):
    """
    生成一个指定长度范围内的随机字母数字字符串作为文件名基础。
    """
    characters = string.ascii_letters + string.digits
    length = random.randint(length_min, length_max)
    return ''.join(random.choice(characters) for i in range(length))

# --- 新增辅助函数：针对包含非ASCII字符的文件名进行安全清理 ---
def sanitize_filename(filename, max_length=90):
    """
    清理文件名，允许非ASCII字符（如中文），同时移除或替换掉不安全或操作系统不允许的字符。
    防止路径遍历攻击 (如 '..')。
    """
    # 1. 移除首尾空白字符
    filename = filename.strip()

    # 2. 替换掉路径分隔符和Windows系统不允许的字符
    # 常见的非法字符: / \ : * ? " < > |
    # 另外，控制字符 (U+0000-U+001F) 也是不允许的
    # 使用下划线 '_' 替代这些非法字符
    invalid_chars_pattern = r'[\\/:*?"<>|\x00-\x1F]'
    filename = re.sub(invalid_chars_pattern, '_', filename)

    # 3. 移除任何路径遍历尝试 (例如 ".." 或 "./")
    filename = filename.replace('..', '').replace('./', '').replace('../', '')

    # 4. 移除文件名开头或结尾的无效字符（例如，点号，但保留扩展名中的点）
    # 这里我们只简单处理，确保文件名不是以点号开头（除非它是隐藏文件，但此处不考虑）
    # 如果处理后文件名为空，则返回一个默认安全名
    if not filename:
        return "untitled_file"

    # 5. 限制文件名长度，为扩展名留出空间
    if len(filename) > max_length:
        filename = filename[:max_length]

    return filename


# --- 辅助函数：检查文件是否允许上传/显示 (仅用于上传和列表显示过滤) ---
ALLOWED_EXTENSIONS = {'mp3'}

def allowed_file(filename):
    """
    检查文件名是否具有允许的扩展名。主要用于上传过滤和文件列表显示。
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 路由：主页 (显示上传表单和文件列表) ---
@app.route('/', methods=['GET'])
def index():
    """
    渲染主页，包含文件上传表单和已上传文件列表。
    Flash messages 会自动显示。
    """
    all_files = os.listdir(app.config['UPLOAD_FOLDER'])
    mp3_files = sorted([f for f in all_files if allowed_file(f)])

    return render_template('index.html',
                            files=mp3_files,
                            download_host_1=DOWNLOAD_HOST_1,
                            download_port_1=DOWNLOAD_PORT_1,
                            download_host_2=DOWNLOAD_HOST_2,
                            download_port_2=DOWNLOAD_PORT_2,
                            max_file_size_mb=MAX_FILE_SIZE_MB)

# --- 路由：文件上传处理 ---
@app.route('/upload', methods=['POST'])
def upload_file():
    """
    处理文件上传请求。
    - 检查文件是否存在于请求中。
    - 检查文件名是否为空。
    - 检查文件类型是否允许 (MP3)。
    - 处理自定义文件名或生成随机文件名，并安全保存文件。
    - 生成下载直链并使用 flash 消息显示。
    - 重定向回主页。
    """
    if 'file' not in request.files:
        flash('请求中缺少文件部分', 'error')
        return redirect(url_for('index'))

    file = request.files['file']
    custom_filename_input = request.form.get('custom_filename', '').strip() # 获取自定义文件名输入

    if file.filename == '':
        flash('未选择文件', 'error')
        return redirect(url_for('index'))

    original_filename_ext = ''
    if '.' in file.filename:
        original_filename_ext = '.' + file.filename.rsplit('.', 1)[1].lower()
    else:
        flash('文件没有扩展名，或不是允许的类型。', 'error')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('文件类型不允许，只允许MP3文件', 'error')
        return redirect(url_for('index'))

    filename_base = "" # 存储最终的文件名基础部分（不含扩展名）

    # 优先使用自定义文件名，并进行安全过滤 (使用新的 sanitize_filename 函数)
    if custom_filename_input:
        processed_filename_base = sanitize_filename(custom_filename_input, max_length=90) # 留出空间给扩展名
        
        # 确保自定义文件名被安全过滤后不为空
        if not processed_filename_base:
            flash('自定义文件名无效或被安全过滤为空，请尝试其他名称。', 'error')
            return redirect(url_for('index'))
            
        filename_base = processed_filename_base
    else:
        # 如果没有自定义文件名，则生成随机文件名
        filename_base = generate_random_filename_base()

    # 拼接最终文件名 (基础部分 + 原始扩展名)
    filename = filename_base + original_filename_ext

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # 检查文件是否已存在（无论是自定义名还是随机名）
    if os.path.exists(filepath):
        flash(f'文件 "{filename}" 已存在，请尝试更改文件名或重新选择文件。', 'error')
        return redirect(url_for('index'))

    try:
        file.save(filepath)
        download_url_1 = url_for('uploaded_file', filename=filename, _external=True, _scheme='http', _host=DOWNLOAD_HOST_1, _port=DOWNLOAD_PORT_1)
        download_url_2 = url_for('uploaded_file', filename=filename, _external=True, _scheme='http', _host=DOWNLOAD_HOST_2, _port=DOWNLOAD_PORT_2)

        print(f"文件 '{filename}' 上传成功，保存至 '{filepath}'。直链1：{download_url_1}，直链2：{download_url_2}")

        flash_message_content = f"""
        文件上传成功！<br>
        直链1: <a href="{download_url_1}" target="_blank">{download_url_1}</a><br>
        直链2: <a href="{download_url_2}" target="_blank">{download_url_2}</a>
        """
        flash(flash_message_content, 'success')

        return redirect(url_for('index'))
    except Exception as e:
        if "RequestEntityTooLarge" in str(e):
            flash(f'文件大小超过限制 ({MAX_FILE_SIZE_MB}MB)。', 'error')
        else:
            print(f"保存文件 '{filename}' 时发生错误: {e}")
            flash(f'文件保存失败: {str(e)}', 'error')
        return redirect(url_for('index'))

# --- 路由：文件下载 (提供静态文件服务) ---
@app.route('/<filename>')
def uploaded_file(filename):
    """
    提供已上传文件的下载服务。
    为了安全，这里仍然使用 werkzeug.utils.secure_filename 来处理传入的 URL 文件名，
    以防止用户在 URL 中构造恶意路径。
    """
    s_filename = secure_filename(filename) # 对于从URL中获取的文件名，仍使用 secure_filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], s_filename)

    if not os.path.exists(filepath):
        return "请求的文件不存在。", 404

    return send_from_directory(app.config['UPLOAD_FOLDER'], s_filename)

# --- 路由：文件删除 (需要密码鉴权) ---
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """
    处理文件删除请求，需要密码鉴权。
    """
    provided_password = request.form.get('delete_password')
    if provided_password != DELETE_PASSWORD:
        flash('删除密码不正确！', 'error')
        return redirect(url_for('index'))

    s_filename = secure_filename(filename) # 对于从URL中获取的文件名，仍使用 secure_filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], s_filename)

    if os.path.exists(filepath) and allowed_file(s_filename):
        try:
            os.remove(filepath)
            print(f"文件 '{s_filename}' 已成功删除。")
            flash(f"文件 '{s_filename}' 已成功删除。", 'success')
        except Exception as e:
            print(f"删除文件 '{s_filename}' 失败: {e}")
            flash(f"删除文件 '{s_filename}' 失败: {str(e)}", 'error')
    else:
        flash(f"文件 '{s_filename}' 不存在或不允许删除。", 'error')
    
    return redirect(url_for('index'))

# --- 启动服务器 ---
if __name__ == '__main__':
    print(f"服务器正在启动，监听地址：http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"文件将保存到目录：{UPLOAD_FOLDER}")
    print(f"下载直链1将使用域名/IP：{DOWNLOAD_HOST_1}:{DOWNLOAD_PORT_1}")
    print(f"下载直链2将使用域名/IP：{DOWNLOAD_HOST_2}:{DOWNLOAD_PORT_2}")
    print(f"单个文件最大上传大小：{MAX_FILE_SIZE_MB}MB")
    print(f"文件删除需要密码鉴权。")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)

