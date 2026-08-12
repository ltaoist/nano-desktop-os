"""
Nano Desktop OS - 一键启动脚本
启动后端服务（含 TOB 通信）和前端
按 Ctrl+C 关闭所有服务
"""

import os
import signal
import subprocess
import sys
import time


def main():
    print("=" * 50)
    print("  Nano Desktop OS")
    print("=" * 50)
    print()

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(os.path.dirname(backend_dir), "frontend")
    root_dir = os.path.dirname(os.path.dirname(backend_dir))

    processes = []

    def cleanup():
        print("\n正在关闭所有服务...")
        for proc in processes:
            try:
                if sys.platform == "win32":
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                        capture_output=True
                    )
                else:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        proc.kill()
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        print("所有服务已关闭。")

    def sig_handler(signum, frame):
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    try:
        python = sys.executable
        print("[1/2] 启动后端服务（含 TOB 通信）...")
        backend_proc = subprocess.Popen(
            [python, "-m", "src.backend.main"],
            cwd=root_dir,
            stdout=sys.__stdout__,
            stderr=sys.__stderr__,
        )
        processes.append(backend_proc)
        print("  后端: http://127.0.0.1:8000")
        time.sleep(1.5)
        if backend_proc.poll() is not None:
            print("  错误: 后端启动失败！")
            cleanup()
            sys.exit(1)

        print("[2/2] 启动前端...")
        npm = "npm.cmd" if sys.platform == "win32" else "npm"
        frontend_proc = subprocess.Popen(
            [npm, "run", "dev"],
            cwd=frontend_dir,
            stdout=sys.__stdout__,
            stderr=sys.__stderr__,
        )
        processes.append(frontend_proc)
        print("  前端: http://localhost:5173")
        print()
        print("=" * 50)
        print("  在浏览器中打开: http://localhost:5173")
        print("  默认账号: admin / admin")
        print("  按 Ctrl+C 关闭")
        print("=" * 50)
        print()

        try:
            while True:
                if backend_proc.poll() is not None:
                    print("后端进程意外退出！")
                    break
                if frontend_proc.poll() is not None:
                    print("前端进程意外退出！")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    except Exception as e:
        print(f"启动失败: {e}")

    finally:
        cleanup()


if __name__ == "__main__":
    main()
