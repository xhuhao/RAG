"""
文件：default.py
功能：默认配置
说明：所有环境通用的配置项
"""

class Config:
    """默认配置类"""

    # Flask配置
    SECRET_KEY = 'guangxi-rag-2025'
    DEBUG = False

    # MySQL数据库配置
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3308
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '123456'
    MYSQL_DB = 'db_enterprise_ga'

    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Chroma向量数据库配置
    CHROMA_HOST = 'localhost'
    CHROMA_PORT = 8000

    # Ollama嵌入模型配置
    OLLAMA_HOST = 'localhost'
    OLLAMA_PORT = 11434
    OLLAMA_MODEL = 'qwen3-embedding:4b'

    # Deepseek LLM配置
    DEEPSEEK_API_KEY = 'sk-7711c3d839284441b33737da4256e6f0'
    DEEPSEEK_MODEL = 'deepseek-v4-pro'
    DEEPSEEK_TEMPERATURE = 0.2
    DEEPSEEK_MAX_TOKENS = 1024
    DEEPSEEK_TOP_P = 0.9

    # 多轮对话配置
    MAX_HISTORY_TURNS = 20

    # 文件上传配置
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER = 'uploads'

    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'
    LOG_ERROR_FILE = 'logs/error.log'
