"""
Automated GitHub Release Publisher for Las2Web.
Reads GitHub OAuth token from Windows Credential Manager,
creates or updates GitHub Release, and uploads Deliverables/Las2Web_win64.zip.
"""

import sys
import json
import ctypes
import urllib.request
import urllib.error
from pathlib import Path
from ctypes import wintypes

advapi32 = ctypes.windll.advapi32

class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ('Flags', wintypes.DWORD),
        ('Type', wintypes.DWORD),
        ('TargetName', wintypes.LPWSTR),
        ('Comment', wintypes.LPWSTR),
        ('LastWritten', wintypes.FILETIME),
        ('CredentialBlobSize', wintypes.DWORD),
        ('CredentialBlob', ctypes.POINTER(ctypes.c_byte)),
        ('Persist', wintypes.DWORD),
        ('AttributeCount', wintypes.DWORD),
        ('Attributes', ctypes.c_void_p),
        ('TargetAlias', wintypes.LPWSTR),
        ('UserName', wintypes.LPWSTR),
    ]

def get_github_token() -> str:
    pcred = ctypes.POINTER(CREDENTIAL)()
    res = advapi32.CredReadW('git:https://github.com', 1, 0, ctypes.byref(pcred))
    if not res:
        raise RuntimeError('Could not read GitHub credential from Windows Credential Manager')
    cred = pcred.contents
    blob = bytes(ctypes.string_at(cred.CredentialBlob, cred.CredentialBlobSize))
    try:
        token = blob.decode('utf-16-le')
    except Exception:
        token = blob.decode('utf-8', errors='ignore')
    advapi32.CredFree(pcred)
    return token.strip()


def publish_release(tag: str = 'v1.2611061940', repo: str = 'wwbim/Las2Web'):
    base_dir = Path(__file__).resolve().parent.parent
    zip_path = base_dir / 'Deliverables' / 'Las2Web_win64.zip'

    if not zip_path.is_file():
        print(f"Error: Release asset not found at {zip_path}", file=sys.stderr)
        sys.exit(1)

    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"Target asset: {zip_path.name} ({zip_size_mb:.2f} MB)")

    token = get_github_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'Las2Web-Publisher',
        'Accept': 'application/vnd.github+json',
    }

    # 1. Check or create release
    rel_url = f'https://api.github.com/repos/{repo}/releases/tags/{tag}'
    rel_data = None
    try:
        req = urllib.request.Request(rel_url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            rel_data = json.loads(resp.read().decode())
            print(f"Found existing release (ID: {rel_data['id']})")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("Release not found. Creating release...")
        else:
            raise

    if not rel_data:
        body_text = (
            "## Las2Web Standalone Point Cloud Converter ☁️\n\n"
            "### 🌟 核心特色 / Key Highlights\n"
            "- **即拖即转 / Instant Drag-and-Drop**: 直接拖入 `.las` 或 `.laz` 点云文件，松开鼠标立即在同级目录完成就地转换。\n"
            "- **Potree 2.x 规范输出**: 生成标准 `metadata.json`、`octree.bin`、`hierarchy.bin`，原生适配 `potree-core` 与 WebGL 流式渲染。\n"
            "- **客户机 100% 零依赖**: 绿色免安装，随包内置 Python 运行时、PyQt6 及完整 Visual C++ 2015-2022 运行库，任何全新 Windows 电脑解压即用。\n"
            "- **BIM-Scope 3D 查看器无缝对接**: 转换完成后提供微型本地 CORS & Range 静态服务，一键调起浏览器在 [BIM-Scope](https://wwbim.github.io/BIM-Scope/) 中查看 3D 点云。\n"
            "- **中英双语一键切换**: 顶部提供 `中 / EN` 按钮，界面文字与状态提示无需重启即时刷新。\n\n"
            "### 📦 运行说明 / Quick Start\n"
            "1. 下载下方 `Las2Web_win64.zip` 并解压到任意文件夹；\n"
            "2. 双击运行 `Las2Web.exe`（无需安装任何 Python 或 VC++ 运行库）；\n"
            "3. 直接拖入点云文件即可自动完成切片转换！"
        )
        payload = json.dumps({
            'tag_name': tag,
            'name': f'Las2Web {tag} - Standalone Portable (Win64)',
            'body': body_text,
            'draft': False,
            'prerelease': False,
        }).encode('utf-8')
        post_req = urllib.request.Request(
            f'https://api.github.com/repos/{repo}/releases',
            data=payload,
            headers={**headers, 'Content-Type': 'application/json'},
        )
        with urllib.request.urlopen(post_req) as resp:
            rel_data = json.loads(resp.read().decode())
            print(f"Created release (ID: {rel_data['id']})")

    # 2. Delete existing asset if needed
    for a in rel_data.get('assets', []):
        if a['name'] == 'Las2Web_win64.zip':
            print(f"Deleting older asset {a['name']}...")
            del_req = urllib.request.Request(a['url'], headers=headers, method='DELETE')
            with urllib.request.urlopen(del_req):
                print("Old asset removed.")

    # 3. Upload asset
    upload_base = rel_data['upload_url'].split('{')[0]
    upload_url = f'{upload_base}?name=Las2Web_win64.zip'

    print(f"Uploading {zip_path.name} ({zip_size_mb:.2f} MB)...")
    with open(zip_path, 'rb') as f:
        data = f.read()

    up_headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'Las2Web-Publisher',
        'Content-Type': 'application/zip',
        'Content-Length': str(len(data)),
    }
    up_req = urllib.request.Request(upload_url, data=data, headers=up_headers)
    with urllib.request.urlopen(up_req) as resp:
        asset_info = json.loads(resp.read().decode())
        print("Upload SUCCESS!")
        print("Download URL:", asset_info.get('browser_download_url'))
        print("Release URL: ", rel_data.get('html_url'))


if __name__ == '__main__':
    tag = sys.argv[1] if len(sys.argv) > 1 else 'v1.2611061940'
    publish_release(tag)
