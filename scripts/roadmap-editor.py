#!/usr/bin/env python3
"""
roadmap-editor.py
生成学习路线图编辑网页，用 Playwright 打开，支持查看和修改路线图
"""

import json
import os
import sys
import subprocess
import re
from pathlib import Path

def parse_markdown_roadmap(md_content):
    """解析 Markdown 路线图，返回结构化数据"""
    sections = []

    # 匹配 H2 (##)
    h2_pattern = re.compile(r'^## (.+)$', re.MULTILINE)
    # 匹配 H3 (###)
    h3_pattern = re.compile(r'^### (.+)$', re.MULTILINE)

    # 分割内容
    parts = h2_pattern.split(md_content)

    # 处理前置内容（标题和元信息）
    header = parts[0].strip() if parts else ""

    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            h2_title = parts[i].strip()
            h2_content = parts[i+1]

            # 解析 H3
            h3_parts = h3_pattern.split(h2_content)
            h3_list = []

            for j in range(1, len(h3_parts), 2):
                if j+1 < len(h3_parts):
                    h3_title = h3_parts[j].strip()
                    h3_content = h3_parts[j+1].strip()
                    h3_list.append({
                        'title': h3_title,
                        'content': h3_content
                    })

            sections.append({
                'title': h2_title,
                'topics': h3_list
            })

    return {
        'header': header,
        'sections': sections
    }

def escape_js_string(s):
    """安全转义 JavaScript 字符串"""
    return s.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n')

def escape_html(s):
    """安全转义 HTML"""
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;'))

def generate_editor_html(roadmap_data, output_path):
    """生成编辑器 HTML 文件"""

    # 生成 JS 数据 - 使用对象格式，sections 作为属性
    sections_json = json.dumps({'sections': roadmap_data['sections']}, ensure_ascii=False)

    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学习路线图编辑器</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
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
        .toolbar {
            background: #f8f9fa;
            padding: 16px 32px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .toolbar-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-preview { background: #e7f5ff; color: #1971c2; }
        .btn-preview:hover { background: #d0ebff; }
        .btn-edit { background: #fff3bf; color: #f08c00; }
        .btn-edit:hover { background: #ffec99; }
        .btn-save {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-save:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102,126,234,0.4); }
        .content {
            padding: 24px 32px;
            max-height: 65vh;
            overflow-y: auto;
        }
        .roadmap-display { line-height: 1.8; }
        .roadmap-display h2 {
            color: #495057;
            font-size: 20px;
            margin: 32px 0 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #667eea;
        }
        .roadmap-display h3 {
            color: #343a40;
            font-size: 16px;
            margin: 24px 0 12px;
            padding-left: 12px;
            border-left: 4px solid #339af0;
        }
        .roadmap-display p { margin: 8px 0; color: #495057; }
        .roadmap-display ul { margin: 8px 0; padding-left: 24px; }
        .roadmap-display li { margin: 4px 0; color: #495057; }
        .roadmap-display pre {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
            margin: 12px 0;
        }
        .roadmap-display blockquote {
            border-left: 4px solid #ffd43b;
            padding-left: 16px;
            color: #856404;
            margin: 12px 0;
        }
        .roadmap-display table {
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            font-size: 14px;
        }
        .roadmap-display th, .roadmap-display td {
            border: 1px solid #dee2e6;
            padding: 8px 12px;
            text-align: left;
        }
        .roadmap-display th { background: #f8f9fa; }
        .roadmap-display code {
            background: #f1f3f5;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 13px;
        }
        .edit-panel { display: none; background: #fff; }
        .edit-panel.active { display: block; }
        .edit-section {
            margin-bottom: 24px;
            padding: 16px;
            background: #f8f9fa;
            border-radius: 12px;
        }
        .edit-section-title {
            font-size: 16px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .edit-section-title .num {
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .edit-topics { margin-left: 24px; }
        .edit-topic {
            background: white;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 8px;
            border: 1px solid #e9ecef;
        }
        .edit-topic-title { font-weight: 500; margin-bottom: 8px; color: #212529; }
        .edit-topic-content {
            width: 100%;
            min-height: 100px;
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-family: inherit;
            font-size: 13px;
            resize: vertical;
        }
        .edit-topic-content:focus { outline: none; border-color: #667eea; }
        .footer {
            padding: 20px 32px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status { font-size: 14px; color: #495057; }
        .status-modified { color: #f08c00; font-weight: 500; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 学习路线图编辑器</h1>
            <p>查看、编辑和修改学习路线图内容</p>
        </div>
        <div class="toolbar">
            <button class="toolbar-btn btn-preview" id="btnPreview" onclick="showPreview()">👁️ 预览模式</button>
            <button class="toolbar-btn btn-edit" id="btnEdit" onclick="showEdit()">✏️ 编辑模式</button>
            <button class="toolbar-btn btn-save" onclick="saveChanges()">💾 保存修改</button>
        </div>
        <div class="content">
            <div id="previewPanel" class="roadmap-display">
                <div id="previewContent"></div>
            </div>
            <div id="editPanel" class="edit-panel">
                <div id="editContent"></div>
            </div>
        </div>
        <div class="footer">
            <div class="status" id="status">就绪</div>
            <button class="toolbar-btn btn-save" onclick="saveChanges()">💾 保存到文件</button>
        </div>
    </div>

    <script>
        var roadmapData = __SECTIONS_DATA__;
        var isModified = false;

        function htmlEscape(text) {
            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        }

        function renderPreview() {
            var html = '';

            // 渲染各阶段
            roadmapData.sections.forEach(function(section, sIdx) {
                html += '<h2>' + htmlEscape(section.title) + '</h2>';

                section.topics.forEach(function(topic, tIdx) {
                    html += '<h3>' + htmlEscape(topic.title) + '</h3>';

                    // 渲染内容
                    var content = topic.content;
                    // 移除代码块并单独处理
                    content = content.replace(/```([\s\S]*?)```/g, '<pre><code>' + htmlEscape('$1') + '</code></pre>');
                    // 处理列表
                    content = content.replace(/^- (.+)$/gm, '<li>' + htmlEscape('$1') + '</li>');
                    content = content.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
                    // 处理加粗
                    content = content.replace(/\*\*(.+?)\*\*/g, '<strong>' + htmlEscape('$1') + '</strong>');
                    // 处理行内代码
                    content = content.replace(/`([^`]+)`/g, '<code>' + htmlEscape('$1') + '</code>');
                    // 处理换行
                    content = content.replace(/\\n/g, '<br>');

                    html += '<div>' + content + '</div>';
                });
            });

            document.getElementById('previewContent').innerHTML = html;
        }

        function renderEdit() {
            var html = '';

            roadmapData.sections.forEach(function(section, sIdx) {
                html += '<div class="edit-section">';
                html += '<div class="edit-section-title"><span class="num">' + (sIdx + 1) + '</span> ' + htmlEscape(section.title) + '</div>';
                html += '<div class="edit-topics">';

                section.topics.forEach(function(topic, tIdx) {
                    html += '<div class="edit-topic">';
                    html += '<div class="edit-topic-title">' + htmlEscape(topic.title) + '</div>';
                    html += '<textarea class="edit-topic-content" data-s="' + sIdx + '" data-t="' + tIdx + '" oninput="onContentChange()">' + htmlEscape(topic.content) + '</textarea>';
                    html += '</div>';
                });

                html += '</div></div>';
            });

            document.getElementById('editContent').innerHTML = html;
        }

        function onContentChange() {
            isModified = true;
            document.getElementById('status').textContent = '已修改（未保存）';
            document.getElementById('status').className = 'status status-modified';

            // 更新数据结构
            var textareas = document.querySelectorAll('.edit-topic-content');
            textareas.forEach(function(ta) {
                var sIdx = parseInt(ta.dataset.s);
                var tIdx = parseInt(ta.dataset.t);
                roadmapData.sections[sIdx].topics[tIdx].content = ta.value;
            });
        }

        function showPreview() {
            document.getElementById('previewPanel').style.display = 'block';
            document.getElementById('editPanel').classList.remove('active');
            renderPreview();
        }

        function showEdit() {
            document.getElementById('previewPanel').style.display = 'none';
            document.getElementById('editPanel').classList.add('active');
            renderEdit();
        }

        function saveChanges() {
            var result = {
                timestamp: new Date().toISOString(),
                sections: roadmapData.sections
            };

            localStorage.setItem('roadmap-editor-result', JSON.stringify(result));

            // 复制到剪贴板
            var text = JSON.stringify(result, null, 2);
            navigator.clipboard.writeText(text).then(function() {
                alert('✅ 路线图已保存！\\n\\n结果已复制到剪贴板。\\n请返回 Claude 继续操作。');
            }).catch(function() {
                alert('✅ 路线图已保存到本地存储！\\n\\n请返回 Claude 继续操作。');
            });

            isModified = false;
            document.getElementById('status').textContent = '已保存';
            document.getElementById('status').className = 'status';
        }

        // 初始化
        document.getElementById('previewContent').innerHTML = '<p>加载中...</p>';
        showPreview();
    </script>
</body>
</html>'''

    # 替换数据占位符
    html_content = html_content.replace('__SECTIONS_DATA__', sections_json)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path

def run_with_playwright(editor_path):
    """使用 Playwright 打开编辑器"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Installing Playwright...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], check=True)
        from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('file://' + editor_path)

        print("Editor opened. You can preview and edit the roadmap in the browser...")
        print("When you've saved changes and clicked 'OK', the result will be saved.")

        # 等待用户保存
        try:
            page.wait_for_function("localStorage.getItem('roadmap-editor-result') !== null", timeout=300000)
        except:
            print("Timeout waiting for save...")
            browser.close()
            return None

        # 获取结果
        result = page.evaluate("localStorage.getItem('roadmap-editor-result')")
        browser.close()

        return json.loads(result) if result else None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 roadmap-editor.py <roadmap_file>")
        sys.exit(1)

    roadmap_file = sys.argv[1]

    if not os.path.exists(roadmap_file):
        print(f"Error: File not found: {roadmap_file}")
        sys.exit(1)

    # 读取路线图
    with open(roadmap_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 解析
    roadmap_data = parse_markdown_roadmap(md_content)
    print(f"Parsed {len(roadmap_data['sections'])} sections")

    # 生成编辑器 HTML
    output_dir = os.path.dirname(roadmap_file)
    editor_path = os.path.join(output_dir, '.roadmap-editor', 'editor.html')
    os.makedirs(os.path.dirname(editor_path), exist_ok=True)

    generate_editor_html(roadmap_data, editor_path)
    print(f"Editor generated: {editor_path}")

    # 打开编辑器
    print("Opening editor in browser...")
    result = run_with_playwright(editor_path)

    if result:
        print("\nEdit result received!")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return result

if __name__ == '__main__':
    main()
