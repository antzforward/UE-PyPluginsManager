# Content/Python/setup/dependencies.py
import sys
import os
import subprocess
import re
import unreal
from . import core
import logging

def parse_requirements(file_path):
    """
    解析requirements.txt文件，支持-r引用其他文件
    返回依赖项列表
    """
    requirements = []
    base_dir = os.path.dirname(file_path)
    
    if not os.path.exists(file_path):
        logging.error(f"Requirements file not found: {file_path}")
        return []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith("#"):
                    continue
                
                # 处理文件引用
                if line.startswith("-r "):
                    include_file = line.split(" ", 1)[1].strip()
                    include_path = os.path.join(base_dir, include_file)
                    requirements.extend(parse_requirements(include_path))
                else:
                    requirements.append(line)
                    logging.info(f"Parsed {line} dependencies from {file_path}")
        
        logging.info(f"Parsed {len(requirements)} dependencies from {file_path}")
        return requirements
    except Exception as e:
        logging.error(f"Error parsing requirements file {file_path}: {str(e)}")
        return requirements

def is_package_installed(package_spec):
    """检查包是否已安装（简化版本检查）"""
    # 提取包名（忽略版本说明符）
    package_name = re.split(r"[<>!=~]", package_spec)[0].strip()
    
    python_exe = core.get_ue_python_interpreter()
    try:
        result = subprocess.run(
            [python_exe, "-m", "pip", "show", package_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        logging.warning(f"Error checking package {package_name}: {str(e)}")
        return False

def install_package(package_spec):
    """安装单个Python包"""
    if is_package_installed(package_spec):
        logging.info(f"Package already installed: {package_spec}")
        return True
    
    logging.info(f"Installing package: {package_spec}")
    python_exe = core.get_ue_python_interpreter()
    
    try:
        result = subprocess.run(
            [python_exe, "-m", "pip", "install", package_spec],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            return True
        else:
            logging.error(f"Failed to install {package_spec}: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error installing {package_spec}: {str(e)}")
        return False

def install_project_dependencies(requirements_file="requirements.txt"):
    """安装项目所有依赖"""
    # 获取requirements.txt的完整路径
    if not os.path.isabs(requirements_file):
        requirements_file = os.path.join(core.get_content_dir(), "Python", requirements_file)
    
    dependencies = parse_requirements(requirements_file)
    if not dependencies:
        logging.warning("No dependencies found to install")
        return True
    
    logging.info(f"Found {len(dependencies)} dependencies to install")
    
    # 先确保pip是最新版本,让UE来自己保证
    python_exe = core.get_ue_python_interpreter()

    try:
        result = subprocess.run(
            [python_exe, "-m", "pip", "install","--upgrade","pip" ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return True
        else:
            logging.error(f"Failed to install {package_spec}: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error installing {package_spec}: {str(e)}")
        return False

    success_count = 0
    failure_count = 0
    
    for dep in dependencies:
        if install_package(dep):
            success_count += 1
        else:
            failure_count += 1
    
    logging.info(f"Dependency installation summary: {success_count} successful, {failure_count} failed")
    return failure_count == 0

def validate_installation():
    """验证关键包是否安装成功"""
    critical_packages = ["numpy", "pandas", "requests"]
    missing = []
    
    for package in critical_packages:
        if not is_package_installed(package):
            missing.append(package)
    
    if missing:
        logging.warning(f"Critical packages missing: {', '.join(missing)}")
        return False
    
    logging.info("All critical packages are installed")
    return True