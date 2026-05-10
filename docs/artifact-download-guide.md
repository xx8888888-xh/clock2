# GitHub Actions Artifact 下载经验

## 问题背景

从 GitHub Actions 下载 Artifact（如构建产物 APK）时，常遇到以下问题：

1. **403 认证失败**：GitHub API 返回 302 重定向到 Azure Blob Storage，如果将 `Authorization` header 带到 Azure 请求中，会导致 403
2. **下载极慢/中断**：`curl`、`wget` 单线程下载，在网络不稳定时容易超时或文件损坏
3. **URL 过期**：Azure 的下载链接有效期仅约 10 分钟，过期后返回 403

---

## 最快最稳定的下载方法

### 方法一：Python requests（推荐）

```python
import requests

TOKEN = "your_github_token"
REPO = "owner/repo"
ARTIFACT_ID = "1234567890"

# Step 1: 获取重定向 URL（带 auth，不跟随重定向）
resp = requests.get(
    f"https://api.github.com/repos/{REPO}/actions/artifacts/{ARTIFACT_ID}/zip",
    headers={"Authorization": f"token {TOKEN}"},
    allow_redirects=False
)
redirect_url = resp.headers["Location"]

# Step 2: 从 Azure 下载（不带 auth header）
with requests.get(redirect_url, stream=True, timeout=300) as r:
    r.raise_for_status()
    with open("output.zip", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
```

### 方法二：curl 两步法

```bash
# Step 1: 获取重定向 URL（只打印 header，不下载）
REDIRECT_URL=$(curl -s -D - -H "Authorization: token YOUR_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/actions/artifacts/ARTIFACT_ID/zip" \
  | grep -i "^location:" | head -1 | tr -d '\r' | cut -d' ' -f2-)

# Step 2: 用新 URL 下载（不带 Authorization header）
curl -L "$REDIRECT_URL" -o output.zip
```

### 方法三：aria2c 多线程下载（大文件推荐）

```bash
# 先获取 URL（同方法二 Step 1）
# 然后用 aria2c 多线程下载
aria2c -x 16 -s 16 -k 1M -o output.zip "$REDIRECT_URL"
```

---

## 常见错误与解决

| 错误 | 原因 | 解决 |
|------|------|------|
| `403 Server failed to authenticate` | Authorization header 被带到 Azure | 用 `allow_redirects=False` 分两步请求 |
| 文件损坏 / ZIP 无法解压 | 下载中断，文件不完整 | 使用 `stream=True` 流式下载，或用 aria2c 断点续传 |
| URL 过期 | Azure 链接有效期约 10 分钟 | 每次下载前重新获取 URL |
| 下载极慢 | 单线程 + 网络不稳定 | 使用 aria2c 多线程或 Python requests 流式下载 |

---

## 获取 Artifact ID 的方法

```bash
# 列出最近的成功构建
curl -s -H "Authorization: token YOUR_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/actions/runs?per_page=5&status=success" \
  | python3 -c "
import sys,json
for run in json.load(sys.stdin)['workflow_runs']:
    print(f'ID: {run[\"id\"]}  Status: {run[\"conclusion\"]}  Created: {run[\"created_at\"]}')
"

# 列出某次构建的 artifacts
curl -s -H "Authorization: token YOUR_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID/artifacts" \
  | python3 -c "
import sys,json
for a in json.load(sys.stdin)['artifacts']:
    print(f'Name: {a[\"name\"]}  ID: {a[\"id\"]}  Size: {a[\"size_in_bytes\"]} bytes')
"
```

---

## 关键原则

1. **永远不要把 GitHub Authorization header 带到 Azure Blob Storage 请求中**
2. **每次下载前获取新的重定向 URL**，避免 URL 过期
3. **大文件优先用流式下载或多线程**，避免单线程超时
4. **下载后验证文件完整性**（检查文件大小、ZIP 格式）
