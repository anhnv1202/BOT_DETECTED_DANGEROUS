#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script chạy server FastAPI
Sử dụng: python run.py [options]
"""
import os
import sys
import argparse
import uvicorn
from pathlib import Path

# Fix encoding cho Windows terminal
if sys.platform == "win32":
    import locale
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')


def check_environment():
    """Kiểm tra môi trường trước khi chạy"""
    print("=" * 60)
    print("DANGEROUS OBJECTS AI API")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8+ required!")
        sys.exit(1)
    print(f"[OK] Python version: {sys.version.split()[0]}")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("[WARNING] File .env không tồn tại!")
        print("   Copy .env.example sang .env và điền thông tin:")
        print("   cp .env.example .env")
        
        # Hỏi user có muốn tạo .env mẫu không
        response = input("\n[?] Tạo file .env mẫu? (y/n): ").lower()
        if response == 'y':
            if Path(".env.example").exists():
                import shutil
                shutil.copy(".env.example", ".env")
                print("[OK] Đã tạo file .env từ .env.example")
                print("[WARNING] Hãy sửa các giá trị trong .env trước khi chạy!")
                sys.exit(0)
            else:
                print("[ERROR] Không tìm thấy .env.example")
                sys.exit(1)
    else:
        print("[OK] File .env tồn tại")
    
    # Check model file
    model_file = Path("mobilenetv2_dangerous_objects.pth")
    if not model_file.exists():
        print(f"[ERROR] Model file không tìm thấy: {model_file}")
        print("   Đặt file model weights vào thư mục gốc!")
        sys.exit(1)
    else:
        size_mb = model_file.stat().st_size / (1024 * 1024)
        print(f"[OK] Model file: {model_file} ({size_mb:.1f} MB)")
    
    # Check database
    db_file = Path("app.db")
    if db_file.exists():
        print(f"[OK] Database: {db_file}")
    else:
        print("[INFO]  Database sẽ được tạo tự động lần đầu chạy")
    
    print("=" * 60)
    print()


def init_database():
    """Khởi tạo database nếu chưa có"""
    from app.database import init_db
    print("[SETUP] Khởi tạo database...")
    try:
        init_db()
        print("[OK] Database đã sẵn sàng")
    except Exception as e:
        print(f"[ERROR] Lỗi khởi tạo database: {e}")
        sys.exit(1)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Chạy Dangerous Objects AI API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python run.py                    # Chạy với cấu hình mặc định
  python run.py --port 3000        # Chạy trên port 3000
  python run.py --reload           # Chạy với auto-reload (dev mode)
  python run.py --host 0.0.0.0     # Cho phép truy cập từ bên ngoài
  python run.py --workers 4        # Chạy với 4 workers (production)
        """
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host để bind server (mặc định: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port để chạy server (mặc định: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Bật auto-reload khi code thay đổi (dev mode)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Số lượng worker processes (production mode)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Log level (mặc định: info)"
    )
    
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Bỏ qua kiểm tra môi trường"
    )
    
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Chỉ khởi tạo database rồi thoát"
    )
    
    args = parser.parse_args()
    
    # Kiểm tra môi trường
    if not args.skip_checks:
        check_environment()
    
    # Khởi tạo database nếu cần
    if args.init_db:
        init_database()
        print("\n[OK] Xong! Database đã được khởi tạo.")
        return
    
    # Cấu hình uvicorn
    config = {
        "app": "app.main:app",
        "host": args.host,
        "port": args.port,
        "log_level": args.log_level,
    }
    
    # Dev mode (single worker với reload)
    if args.reload:
        print("[SETUP] Chạy ở chế độ DEVELOPMENT (auto-reload)")
        print(f"[SERVER] Server: http://{args.host}:{args.port}")
        print(f"[DOCS] Docs: http://{args.host}:{args.port}/docs")
        print("\n[TIP] Nhấn Ctrl+C để dừng server\n")
        config["reload"] = True
        config["reload_dirs"] = ["app"]
    
    # Production mode (multiple workers, no reload)
    elif args.workers > 1:
        print(f"[START] Chạy ở chế độ PRODUCTION ({args.workers} workers)")
        print(f"[SERVER] Server: http://{args.host}:{args.port}")
        print(f"[DOCS] Docs: http://{args.host}:{args.port}/docs")
        print("\n[TIP] Nhấn Ctrl+C để dừng server\n")
        config["workers"] = args.workers
    
    # Single worker mode
    else:
        print("[START] Chạy server...")
        print(f"[SERVER] Server: http://{args.host}:{args.port}")
        print(f"[DOCS] Docs: http://{args.host}:{args.port}/docs")
        print("\n[TIP] Nhấn Ctrl+C để dừng server\n")
    
    # Chạy server
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n\n👋 Server đã dừng. Tạm biệt!")
    except Exception as e:
        print(f"\n[ERROR] Lỗi khi chạy server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


