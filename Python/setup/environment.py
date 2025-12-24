# Content/Python/setup/environment.py
import os
import sys
import configparser
import unreal
import logging
from . import core

def load_config(config_file="setup_config.ini"):
    """加载配置文件"""
    # 确定配置文件路径
    if not os.path.isabs(config_file):
        config_file = os.path.join(core.get_content_dir(), "Python", config_file)
    
    config = configparser.ConfigParser()
    
    # 默认配置
    default_config = {
        "ENVIRONMENT": {
            "python_path": core.get_ue_python_interpreter(),
            "project_root": core.get_project_root(),
            "content_dir": core.get_content_dir()
        },
        "DEPENDENCIES": {
            "requirements_file": "requirements.txt"
        },
        "PATHS": {
            "python_paths": "Content/Python/Scripts;Content/Python/Libs"
        },
        "VARIABLES": {
            "UE_PROJECT": core.get_project_root(),
            "PYTHON_DEBUG": "1"
        }
    }
    
    # 应用默认配置
    config.read_dict(default_config)
    
    # 加载用户配置（如果存在）
    if os.path.exists(config_file):
        try:
            config.read(config_file)
            logging.info(f"Loaded config from {config_file}")
        except Exception as e:
            logging.error(f"Error loading config file: {str(e)}")
    
    return config

def setup_environment_vars(config):
    """设置环境变量"""
    if "VARIABLES" not in config:
        return
    
    logging.info("Setting environment variables...")
    
    for key, value in config["VARIABLES"].items():
        # 替换路径中的占位符
        value = value.replace("${PROJECT_ROOT}", core.get_project_root())
        value = value.replace("${CONTENT_DIR}", core.get_content_dir())
        
        # 设置环境变量
        os.environ[key] = value
        logging.info(f"  {key} = {value}")

def setup_python_path(config):
    """设置Python路径"""
    if "PATHS" not in config or "python_paths" not in config["PATHS"]:
        return
    
    path_str = config["PATHS"]["python_paths"]
    paths = path_str.split(";")
    
    added_paths = []
    for path in paths:
        # 替换路径中的占位符
        path = path.replace("${PROJECT_ROOT}", core.get_project_root())
        path = path.replace("${CONTENT_DIR}", core.get_content_dir())
        
        # 转换为绝对路径
        abs_path = os.path.join(core.get_project_root(), path)
        
        if os.path.exists(abs_path):
            if abs_path not in sys.path:
                sys.path.append(abs_path)
                added_paths.append(abs_path)
        else:
            logging.warning(f"Python path does not exist: {abs_path}")
    
    if added_paths:
        logging.info(f"Added to Python path: {', '.join(added_paths)}")