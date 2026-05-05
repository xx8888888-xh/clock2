#!/usr/bin/env python3
"""
监控GitHub Actions构建进度
"""

import time
import json
import subprocess
import os

def check_build_status():
    """检查构建状态"""
    
    print("监控GitHub Actions构建进度...")
    
    # 检查当前运行状态
    run_id = "25296806257"
    
    for i in range(60):  # 最多等待60分钟
        # 获取构建状态
        cmd = f"curl -s 'https://api.github.com/repos/xx8888888-xh/clock2/actions/runs/{run_id}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ 获取状态失败，等待5秒后重试...")
            time.sleep(5)
            continue
        
        data = json.loads(result.stdout)
        
        status = data.get("status", "")
        conclusion = data.get("conclusion", "")
        
        print(f"检查时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"构建状态: {status}")
        print(f"构建结果: {conclusion if conclusion else '尚未完成'}")
        print(f"构建ID: {run_id}")
        print(f"构建URL: {data.get('html_url', '')}")
        
        if status == "completed":
            if conclusion == "success":
                print("✅ 构建成功！")
                
                # 获取Artifacts
                cmd2 = f"curl -s 'https://api.github.com/repos/xx8888888-xh/clock2/actions/runs/{run_id}/artifacts'"
                result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
                
                if result2.returncode == 0:
                    artifacts = json.loads(result2.stdout)
                    total_count = artifacts.get("total_count", 0)
                    print(f"📦 Artifacts数量: {total_count}")
                    
                    for artifact in artifacts.get("artifacts", []):
                        name = artifact.get("name", "")
                        size_bytes = artifact.get("size_in_bytes", 0)
                        size_mb = size_bytes / 1024 / 1024
                        
                        print(f"📦 Artifact: {name} ({size_mb:.2f} MB)")
                        if name == "clock2-apk":
                            download_url = artifact.get("archive_download_url", "")
                            print(f"🔗 APK下载URL: {download_url}")
                            return True, download_url
                
                return True, None
            else:
                print(f"❌ 构建失败: {conclusion}")
                return False, None
        
        # 检查构建步骤进度
        cmd3 = f"curl -s 'https://api.github.com/repos/xx8888888-xh/clock2/actions/runs/{run_id}/jobs'"
        result3 = subprocess.run(cmd3, shell=True, capture_output=True, text=True)
        
        if result3.returncode == 0:
            jobs_data = json.loads(result3.stdout)
            if jobs_data.get("jobs"):
                steps = jobs_data["jobs"][0].get("steps", [])
                
                for step in steps:
                    if step.get("status") == "in_progress":
                        print(f"📈 当前正在执行的步骤: {step.get('name')}")
                        break
                    elif step.get("status") == "completed":
                        continue
        
        print(f"⏳ 构建仍在进行中，等待5分钟...")
        time.sleep(300)  # 等待5分钟
    
    print("❌ 等待超时")
    return False, None

def update_memory_file():
    """更新记忆文件"""
    
    memory_file = "/root/.openclaw/workspace/memory/2025-05-04.md"
    
    # 读取当前内存
    if os.path.exists(memory_file):
        with open(memory_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 更新构建状态
        new_content = content.replace(
            "🔄 GitHub Actions构建\n🔄 等待APK下载测试",
            "✅ GitHub Actions构建完成\n🔄 APK下载测试"
        )
        
        with open(memory_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print("📝 记忆文件已更新")

if __name__ == "__main__":
    print("开始监控GitHub Actions构建进度")
    success, download_url = check_build_status()
    
    if success:
        print("🎉 构建完成！")
        update_memory_file()
        
        if download_url:
            print("下载APK方法:")
            print(f"1. 直接从GitHub Actions页面下载: {download_url}")
            print("2. GitHub身份验证可能需要")
            print("3. Release页面也会提供下载")
        else:
            print("📋 APK位置:")
            print("- GitHub Actions → Artifacts → clock2-apk")
            print("- GitHub Releases → Downloads")
            print("- GitHub仓库 → bin目录")
    else:
        print("❌ 构建可能失败或仍在进行中")