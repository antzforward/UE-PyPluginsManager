# Content/Python/setup_project.py
import sys
import os
import unreal
from setup import core, dependencies, environment

def main():
    """项目设置主入口"""
    try:
        # 初始化日志
        log_path = os.path.join(unreal.Paths.project_log_dir(), "python_setup.log")
        core.init_logging(log_path)
        
        # 加载配置
        config = environment.load_config()
        
        # 设置环境变量
        environment.setup_environment_vars(config)
        
        # 设置Python路径
        environment.setup_python_path(config)
        
        # 安装依赖
        requirements_file = config.get("DEPENDENCIES", "requirements_file", fallback="requirements.txt")
        dependencies.install_project_dependencies(requirements_file)
        
        # 验证安装
        dependencies.validate_installation()
        
        unreal.log("Project setup completed successfully!")
        return True
    except Exception as e:
        unreal.log_error(f"Project setup failed: {str(e)}")
        import traceback
        unreal.log_error(traceback.format_exc())
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