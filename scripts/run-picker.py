#!/usr/bin/env python3
"""
run-picker.py
生成文件夹选择器网页，用 Playwright 打开，获取用户选择结果
"""

import json
import os
import sys
import subprocess
from pathlib import Path

def scan_vault(vault_path):
    """扫描 vault，返回文件夹和文件树形数据"""
    items = []

    # 先收集所有顶层项
    top_level_folders = []
    top_level_files = []

    for item in sorted(Path(vault_path).iterdir()):
        if item.name.startswith('.'):
            continue
        if item.is_dir():
            top_level_folders.append(item)
        elif item.is_file() and item.suffix.lower() in ['.md', '.pdf']:
            top_level_files.append(item)

    # 如果有文件夹，扫描文件夹结构
    if top_level_folders:
        for item in top_level_folders:
            subfolders = sum(1 for _ in item.iterdir() if _.is_dir() and not _.name.startswith('.'))
            files = sum(1 for f in item.iterdir() if f.is_file() and f.suffix.lower() in ['.md', '.pdf'])

            items.append({
                'name': item.name,
                'path': str(item),
                'type': 'folder',
                'subfolders': subfolders,
                'files': files,
                'level': 0
            })

            # 只扫描顶层，第二层不展开
            for subitem in sorted(item.iterdir()):
                if subitem.is_dir() and not subitem.name.startswith('.'):
                    subsubfolders = sum(1 for _ in subitem.iterdir() if _.is_dir() and not _.name.startswith('.'))
                    subfiles = sum(1 for f in subitem.iterdir() if f.is_file() and f.suffix.lower() in ['.md', '.pdf'])

                    items.append({
                        'name': subitem.name,
                        'path': str(subitem),
                        'type': 'folder',
                        'subfolders': subsubfolders,
                        'files': subfiles,
                        'level': 1
                    })

    # 如果没有文件夹但有文件，显示文件列表
    if not top_level_folders and top_level_files:
        for item in top_level_files:
            ext = item.suffix.lower()
            items.append({
                'name': item.name,
                'path': str(item),
                'type': 'file',
                'ext': ext,
                'level': 0
            })

    return items

def escape_js_string(s):
    """安全转义 JavaScript 字符串"""
    return s.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n')

def generate_picker_html(vault_path, output_dir):
    """生成选择器 HTML 文件"""

    # 扫描文件夹
    folders = scan_vault(vault_path)

    # 生成文件夹的 JS 数组
    folders_js = []
    for folder in folders:
        item_str = (
            'name:"' + escape_js_string(folder["name"]) + '",' +
            'path:"' + escape_js_string(folder["path"]) + '",' +
            'type:"' + folder["type"] + '",' +
            'level:' + str(folder["level"])
        )
        if folder["type"] == 'folder':
            item_str += ',subfolders:' + str(folder["subfolders"]) + ',files:' + str(folder["files"])
        else:
            item_str += ',ext:"' + folder.get("ext", "") + '"'
        folders_js.append('{' + item_str + '}')
    folders_data = '{folders:[' + ','.join(folders_js) + ']}'

    # HTML 模板
    html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学习材料选择器</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 700px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px 32px;
        }
        .header h1 { font-size: 24px; font-weight: 600; margin-bottom: 8px; }
        .header p { font-size: 14px; opacity: 0.9; }
        .content { padding: 24px 32px; max-height: 55vh; overflow-y: auto; }
        .instructions {
            background: #fff3bf;
            border: 1px solid #ffd43b;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 20px;
            font-size: 13px;
            color: #856404;
        }
        .instructions strong { display: block; margin-bottom: 4px; }
        .search-box { margin-bottom: 20px; }
        .search-input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 15px;
            transition: border-color 0.2s;
        }
        .search-input:focus { outline: none; border-color: #667eea; }
        .folder-item {
            padding: 14px 16px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 12px;
            border: 2px solid transparent;
        }
        .folder-item:hover { background: #e9ecef; transform: translateX(4px); }
        .folder-item.selected { background: #e7f5ff; border-color: #339af0; }
        .folder-item.hidden { display: none; }
        .folder-item.level-1 { margin-left: 32px; }
        .checkbox {
            width: 24px; height: 24px;
            border: 2px solid #ced4da;
            border-radius: 6px;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
            transition: all 0.2s;
        }
        .folder-item.selected .checkbox { background: #339af0; border-color: #339af0; color: white; }
        .checkmark { display: none; font-size: 14px; }
        .folder-item.selected .checkmark { display: block; }
        .folder-icon { font-size: 24px; }
        .folder-info { flex: 1; }
        .folder-name { font-size: 16px; font-weight: 500; color: #212529; }
        .folder-meta { font-size: 12px; color: #868e96; margin-top: 2px; }
        .footer {
            padding: 20px 32px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .selection-info { font-size: 14px; color: #495057; }
        .selection-count { font-weight: 600; color: #667eea; }
        .btn {
            padding: 12px 32px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102,126,234,0.4); }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 学习材料选择器</h1>
            <p>选择要处理的学习文件夹</p>
        </div>
        <div class="content">
            <div class="instructions">
                <strong>💡 使用说明</strong>
                点击文件夹选择或取消选择，然后点击"确认选择"继续。
            </div>
            <div class="search-box">
                <input type="text" class="search-input" id="searchInput" placeholder="🔍 搜索文件夹...">
            </div>
            <div id="folderList"></div>
        </div>
        <div class="footer">
            <div class="selection-info">已选择 <span class="selection-count" id="count">0</span> 个项目</div>
            <button class="btn btn-primary" id="confirmBtn" onclick="confirmSelection()" disabled>确认选择 →</button>
        </div>
    </div>

    <script>
        var selectedFolders = new Set();
        var allFolders = [];
        var folderData = __FOLDER_DATA__;

        function init() {
            var container = document.getElementById('folderList');
            for (var i = 0; i < folderData.folders.length; i++) {
                var folder = folderData.folders[i];
                allFolders.push(folder);
                var div = document.createElement('div');
                div.className = 'folder-item' + (folder.level === 1 ? ' level-1' : '');
                div.dataset.path = folder.path;
                div.dataset.name = folder.name;

                var checkbox = document.createElement('div');
                checkbox.className = 'checkbox';
                var checkmark = document.createElement('span');
                checkmark.className = 'checkmark';
                checkmark.textContent = '✓';
                checkbox.appendChild(checkmark);

                var icon = document.createElement('span');
                icon.className = 'folder-icon';
                icon.textContent = '📁';

                var info = document.createElement('div');
                info.className = 'folder-info';

                var name = document.createElement('div');
                name.className = 'folder-name';
                name.textContent = folder.name;

                var meta = document.createElement('div');
                meta.className = 'folder-meta';
                meta.textContent = folder.subfolders + ' 個子文件夹, ' + folder.files + ' 個文件';

                info.appendChild(name);
                info.appendChild(meta);

                div.appendChild(checkbox);
                div.appendChild(icon);
                div.appendChild(info);

                div.onclick = (function(p, el) { return function() { toggleItem(p, el); }; })(folder.path, div);
                container.appendChild(div);
            }
        }

        function toggleItem(path, element) {
            if (selectedFolders.has(path)) {
                selectedFolders.delete(path);
                element.classList.remove('selected');
            } else {
                selectedFolders.add(path);
                element.classList.add('selected');
            }
            updateUI();
        }

        function updateUI() {
            document.getElementById('count').textContent = selectedFolders.size;
            document.getElementById('confirmBtn').disabled = selectedFolders.size === 0;
        }

        function filterFolders(query) {
            var items = document.querySelectorAll('.folder-item');
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                var name = item.dataset.name.toLowerCase();
                item.classList.toggle('hidden', name.indexOf(query.toLowerCase()) === -1);
            }
        }

        function confirmSelection() {
            var selections = [];
            selectedFolders.forEach(function(path) {
                for (var i = 0; i < allFolders.length; i++) {
                    if (allFolders[i].path === path) {
                        selections.push({ type: allFolders[i].type, path: allFolders[i].path, name: allFolders[i].name });
                        break;
                    }
                }
            });

            var result = { timestamp: new Date().toISOString(), selections: selections };

            localStorage.setItem('obsidian-learning-selections', JSON.stringify(result));

            var resultText = JSON.stringify(result, null, 2);
            navigator.clipboard.writeText(resultText).then(function() {
                alert('✅ 选择已确认！\\n\\n结果已复制到剪贴板。\\n\\n请返回 Claude 继续操作。');
            }).catch(function() {
                alert('选择结果：\\n' + resultText);
            });
        }

        document.getElementById('searchInput').oninput = function(e) {
            filterFolders(e.target.value);
        };

        window.onload = init;
    </script>
</body>
</html>'''

    # 替换数据占位符
    html_content = html_template.replace('__FOLDER_DATA__', folders_data)

    # 写入文件
    picker_path = os.path.join(output_dir, 'picker.html')
    with open(picker_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return picker_path

def run_with_playwright(picker_path):
    """使用 Playwright 打开选择器并获取用户选择"""

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed, installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], check=True)
        subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=True)
        from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('file://' + picker_path)

        print("Browser picker opened. Please select folders in the browser window...")
        print("When you've made your selection and clicked '确认选择', the result will be saved.")

        # 等待用户点击确认 (最多等待 120 秒)
        try:
            page.wait_for_function("localStorage.getItem('obsidian-learning-selections') !== null", timeout=120000)
        except Exception as e:
            print(f"Timeout or error waiting for selection: {e}")
            browser.close()
            return None

        # 获取选择结果
        result = page.evaluate("localStorage.getItem('obsidian-learning-selections')")
        browser.close()

        if result:
            return json.loads(result)
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run-picker.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]
    output_dir = os.path.join(vault_path, '.obsidian-learning-picker')

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成选择器
    picker_path = generate_picker_html(vault_path, output_dir)
    print("Picker generated: " + picker_path)

    # 用 Playwright 打开
    print("Opening browser picker...")
    result = run_with_playwright(picker_path)

    print("\nSelection result:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 保存选择结果
    selections_path = os.path.join(output_dir, 'selections.json')
    with open(selections_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\nSelection saved to: " + selections_path)

    return result

if __name__ == '__main__':
    main()
