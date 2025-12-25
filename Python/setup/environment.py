# Content/Python/setup/environment.py
import os
import sys
import configparser
import unreal
import logging
from pathlib import Path
from . import core


def load_config(config_path="setup_config.ini"):
    """加载配置文件"""
    config = configparser.ConfigParser()

    # 默认配置
    default_config = {
        "ENVIRONMENT": {
            "PIP_TARGET_DIR":f"{core.get_project_root().as_posix()}/Intermediate/PipInstall/Lib/site-packages"
        },
        "DEPENDENCIES": {
            "requirements_file": "requirements.txt"
        },
        "PATHS": {
            "python_paths": "Content/Python/Scripts;Content/Python/Libs",
        },
        "VARIABLES": {
            "PYTHON_DEBUG": "0",
        }
    }

    # 应用默认配置
    config.read_dict(default_config)

    config_file = Path(config_path)
    # 确定配置文件路径
    if not config_file.is_absolute():
        config_file = core.get_content_dir() / "Python" / config_path

    # 加载用户配置（如果存在）
    if config_file.exists():
        try:
            config.read(config_file)
            logging.info(f"Loaded config from {config_file}")
        except Exception as e:
            logging.error(f"Error loading config file: {str(e)}")

    return config

def setup_environment_paths(config):
    """
    设置系统Path，并添加到环境变量中
    """
    if "ENVIRONMENT" not in config:
        return
    logging.info("Setting environment paths...")
    for key,path in config["ENVIRONMENT"].items():
        # 替换路径中的占位符
        path = path.replace("${PROJECT_ROOT}", core.get_project_root().as_posix())
        path = path.replace("${CONTENT_DIR}", core.get_content_dir().as_posix())
        path = Path(path)
        # 转换为绝对路径
        if not path.is_absolute():
            path = core.get_project_root() / path
        if not path.exists():
            path.mkdir(exist_ok=True)
        path_str = path.as_posix()
        if path_str not in sys.path:
            sys.path.insert(0,path_str)
        os.environ[key] = path_str

def setup_environment_vars(config):
    """设置环境变量
    """
    if "VARIABLES" not in config:
        return

    logging.info("Setting environment variables...")

    for key, value in config["VARIABLES"].items():
        # 替换路径中的占位符
        value = value.replace("${PROJECT_ROOT}", core.get_project_root().as_posix())
        value = value.replace("${CONTENT_DIR}", core.get_content_dir().as_posix())

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
        path = path.replace("${PROJECT_ROOT}", core.get_project_root().as_posix())
        path = path.replace("${CONTENT_DIR}", core.get_content_dir().as_posix())

        path = Path(path)
        # 转换为绝对路径
        if not path.is_absolute():
            path = core.get_project_root() / path

        if path.exists():
            path_str = path.as_posix()
            if path_str not in sys.path:
                sys.path.insert(0, path_str)
                added_paths.append(path_str)
        else:
            logging.warning(f"Python path does not exist: {path}")

    if added_paths:
        logging.info(f"Added to Python path: {', '.join(added_paths)}")
