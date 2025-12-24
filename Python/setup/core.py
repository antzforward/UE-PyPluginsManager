# Content/Python/setup/core.py
import os
import sys
import unreal
import logging

def init_logging(log_file):
    """初始化日志系统"""
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 同时输出到UE日志
    class UnrealLogHandler(logging.Handler):
        def emit(self, record):
            msg = self.format(record)
            if record.levelno >= logging.ERROR:
                unreal.log_error(msg)
            elif record.levelno >= logging.WARNING:
                unreal.log_warning(msg)
            else:
                unreal.log(msg)
    
    logging.getLogger().addHandler(UnrealLogHandler())
    logging.info("UE5 Python setup initialized")

def get_project_root():
    """获取项目根目录"""
    return unreal.Paths.project_dir()

def get_content_dir():
    """获取Content目录"""
    return unreal.Paths.project_content_dir()

def get_script_dir():
    """获取当前脚本目录"""
    return os.path.dirname(os.path.abspath(__file__))
    
def get_ue_python_interpreter():
    # 在UE5.0及以上版本，可以使用以下方法
    if hasattr(unreal, 'get_interpreter_executable_path'):
        return unreal.get_interpreter_executable_path()
    else:
        # 对于旧版本，我们尝试从sys.executable获取
        # 注意：在UE编辑器中运行Python时，sys.executable可能指向UE编辑器进程
        # 因此，我们需要检查路径中是否包含Python
        if "python" in sys.executable.lower():
            return sys.executable
        else:
            # 如果无法获取，我们尝试使用默认路径
            # Windows下UE内置Python的典型路径
            if sys.platform == "win32":
                engine_dir = unreal.Paths.engine_dir()
                return os.path.join(engine_dir, "Binaries", "ThirdParty", "Python3", "Win64", "python.exe")
            # Linux
            elif sys.platform == "linux":
                engine_dir = unreal.Paths.engine_dir()
                return os.path.join(engine_dir, "Binaries", "ThirdParty", "Python3", "Linux", "bin", "python3")
            # Mac
            elif sys.platform == "darwin":
                engine_dir = unreal.Paths.engine_dir()
                return os.path.join(engine_dir, "Binaries", "ThirdParty", "Python3", "Mac", "bin", "python3")
            else:
                raise OSError(f"Unsupported platform: {sys.platform}")