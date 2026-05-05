#!/usr/bin/env python3
"""
检查GitHub Actions构建状态
"""

import time
import json
import subprocess
import sys

def get_workflow_status():
    """获取工作流状态"""
    try:
        # 获取所有工作流运行
        cmd = "curl -s 'https://api.github.com/repos/xx8888888-xh/clock2/actions/runs?branch=main&per_page=5'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ 获取工作流状态失败")
            return None
        
        data = json.loads(result.stdout)
        
        print("=== GitHub Actions 构建状态 ===")
        
        for run in data["workflow_runs"]:
            print(f"ID: {run['id']}")
            print(f"提交SHA: {run['head_sha']}")
            print(f"状态: {run['status']}")
            print(f"结果: {run['conclusion'] or '正在运行'}")
            print(f"创建时间: {run['created_at']}")
            print(f"URL: {run['html_url']}")
            print("---")
        
        # 查看最新运行
        latest_run = data["workflow_runs"][0]
        if latest_run["status"] == "completed" and latest_run["conclusion"] == "success":
            print(f"✅ 最新构建已成功: {latest_run['id']}")
            return latest_run["id"]
        elif latest_run["status"] == "in_progress":
            print(f"⏳ 最新构建正在运行: {latest_run['id']}")
            return None
        else:
            print(f"❌ 最新构建失败或取消: {latest_run['conclusion']}")
            return None
            
    except Exception as e:
        print(f"❌ 获取状态失败: {e}")
        return None

def get_apk_download_url(run_id):
    """获取APK下载URL"""
    try:
        cmd = f"curl -s 'https://api.github.com/repos/xx8888888-xh/clock2/actions/runs/{run_id}/artifacts'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ 获取Artifacts失败")
            return None
        
        data = json.loads(result.stdout)
        
        if data["total_count"] == 0:
            print("❌ 没有Artifacts")
            return None
        
        for artifact in data["artifacts"]:
            if artifact["name"] == "clock2-apk":
                download_url = artifact["archive_download_url"]
                print(f"✅ APK下载URL: {download_url}")
                return download_url
        
        print("❌ 没有找到clock2-apk Artifact")
        return None
        
    except Exception as e:
        print(f"❌ 获取下载URL失败: {e}")
        return None

def check_commit_messages():
    """检查提交消息"""
    try:
        cmd = "cd /root/.openclaw/workspace/clock2/clock2 && git log --oneline -5"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ 获取提交历史失败")
            return
        
        print("=== 最近提交 ===")
        print(result.stdout)
        
    except Exception as e:
        print(f"❌ 检查提交失败: {e}")

def main():
    """主函数"""
    print("监控GitHub Actions构建状态...")
    
    # 检查提交
    check_commit_messages()
    
    # 获取状态
    print("\n检查构建状态...")
    
    # 等待5分钟检查
    wait_time = 5 * 60
    print(f"等待{wait_time}秒让构建完成...")
    time.sleep(wait_time)
    
    # 再次检查状态
    print("\n再次检查构建状态...")
    run_id = get_workflow_status()
    
    if run_id:
        # 获取下载URL
        download_url = get_apk_download_url(run_id)
        
        if download_url:
            print("\n可以尝试下载APK")
            print("URL:", download_url)
            print("注意：下载需要GitHub身份验证")
        else:
            print("\n暂时无法下载APK，请稍后再试")
    else:
        print("\n构建仍在进行中或失败")

if __name__ == "__main__":
    main()