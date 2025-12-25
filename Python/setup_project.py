# Content/Python/setup_project.py
import subprocess
import sys
import os
import unreal
from pathlib import Path
from setup import core, environment
import logging


def main():
    """项目设置主入口"""
    try:
        # 初始化日志
        log_path = Path(unreal.Paths.project_log_dir()) / "python_setup.log"
        core.init_logging(log_path)

        # 加载配置
        config = environment.load_config()
        # 设置环境路径
        environment.setup_environment_paths(config)

        # 设置环境变量
        environment.setup_environment_vars(config)

        # 设置Python路径
        environment.setup_python_path(config)

        # 确保PIP_TARGET_DIR存在
        target_dir = os.environ.get('PIP_TARGET_DIR')
        if not target_dir:
            # 处理环境变量未设置的情况
            raise EnvironmentError("PIP_TARGET_DIR environment variable is not set.")

        # 先更新pip
        result = subprocess.run(
            [core.executable(), "-m", "pip", "install", "--upgrade", "pip"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            logging.error(f"Failed to upgrade pip: {result.stderr}")
            raise result.stderr
        # 安装依赖
        requirements_file: Path = Path(config.get("DEPENDENCIES", "requirements_file", fallback="requirements.txt"))
        # 获取requirements.txt的完整路径
        if not requirements_file.is_absolute():
            requirements_file = core.get_content_dir() / "Python" / requirements_file
        if requirements_file.exists():
            subprocess.run(
                [core.executable(), "-m", "pip", "install","-t",os.environ['PIP_TARGET_DIR'],
                 '-r', requirements_file.as_posix(),
                 "--disable-pip-version-check",
                "--progress-bar", "off"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                logging.error(f"Failed to pip install : {result.stderr}")
                raise result.stderr

        logging.info("Project setup completed successfully!")
        return True
    except Exception as e:
        logging.error(f"Project setup failed: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    # 在UE编辑器内运行时
    if hasattr(unreal, "log"):
        main()
    else:
        # 独立运行时
        print("Running UE5 Python project setup...")
        success = main()
        sys.exit(0 if success else 1)
