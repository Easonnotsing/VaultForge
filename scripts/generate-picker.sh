#!/bin/bash
# generate-picker.sh
# 生成文件夹选择器的 HTML 页面

VAULT_PATH="$1"
OUTPUT_HTML="$2"
OUTPUT_DATA="$3"

# 生成文件夹树形数据
generate_tree() {
    local path="$1"
    local level="$2"

    ls -la "$path" 2>/dev/null | grep "^d" | tail -n +4 | while read -r line; do
        local name=$(echo "$line" | awk '{print $NF}')

        # 跳过隐藏文件夹
        if [[ "$name" == .* ]]; then
            continue
        fi

        local full_path="$path/$name"
        local subfolders=$(ls -la "$full_path" 2>/dev/null | grep "^d" | tail -n +4 | grep -v "^\." | wc -l)
        local files=$(find "$full_path" -maxdepth 1 -type f \( -name "*.md" -o -name "*.pdf" \) 2>/dev/null | wc -l)

        echo "{\"name\":\"$name\",\"path\":\"$full_path\",\"type\":\"folder\",\"subfolders\":$subfolders,\"files\":$files,\"level\":$level,\"expanded\":false}"

        # 只在第一层展开子文件夹
        if [ $level -eq 0 ] && [ $subfolders -gt 0 ]; then
            generate_tree "$full_path" 1
        fi
    done
}

# 生成文件数据
generate_files() {
    local path="$1"

    find "$path" -maxdepth 1 -type f \( -name "*.md" -o -name "*.pdf" \) 2>/dev/null | while read -r file; do
        local name=$(basename "$file")
        local ext="${name##*.}"
        local icon="📄"
        if [ "$ext" = "pdf" ] || [ "$ext" = "PDF" ]; then
            icon="📕"
        fi

        echo "{\"name\":\"$name\",\"path\":\"$file\",\"type\":\"file\",\"icon\":\"$icon\"}"
    done
}

# 生成 JSON 数据
{
    echo "{"
    echo "\"timestamp\": \"$(date -Iseconds)\","
    echo "\"vaultPath\": \"$VAULT_PATH\","

    echo "\"folders\": ["
    FIRST=true
    generate_tree "$VAULT_PATH" 0 | while read -r item; do
        if [ "$FIRST" = true ]; then
            FIRST=false
        else
            echo ","
        fi
        echo -n "$item"
    done
    echo ""
    echo "],"
    echo "\"files\": ["
    FIRST=true
    generate_files "$VAULT_PATH" | while read -r item; do
        if [ "$FIRST" = true ]; then
            FIRST=false
        else
            echo ","
        fi
        echo -n "$item"
    done
    echo ""
    echo "}"
} > "$OUTPUT_DATA"

echo "✅ 数据已生成：$OUTPUT_DATA"

# 生成 HTML
cat > "$OUTPUT_HTML" << 'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学习材料选择器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
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
        .header h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        .content {
            padding: 24px 32px;
            max-height: 55vh;
            overflow-y: auto;
        }
        .search-box {
            margin-bottom: 20px;
        }
        .search-input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 15px;
            transition: border-color 0.2s;
        }
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
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
        .folder-item:hover {
            background: #e9ecef;
            transform: translateX(4px);
        }
        .folder-item.selected {
            background: #e7f5ff;
            border-color: #339af0;
        }
        .folder-item.hidden {
            display: none;
        }
        .checkbox {
            width: 24px;
            height: 24px;
            border: 2px solid #ced4da;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            transition: all 0.2s;
            font-size: 14px;
        }
        .folder-item.selected .checkbox {
            background: #339af0;
            border-color: #339af0;
            color: white;
        }
        .folder-icon {
            font-size: 24px;
        }
        .folder-info {
            flex: 1;
        }
        .folder-name {
            font-size: 16px;
            font-weight: 500;
            color: #212529;
        }
        .folder-meta {
            font-size: 12px;
            color: #868e96;
            margin-top: 2px;
        }
        .footer {
            padding: 20px 32px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .selection-info {
            font-size: 14px;
            color: #495057;
        }
        .selection-count {
            font-weight: 600;
            color: #667eea;
        }
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
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .instructions {
            background: #fff3bf;
            border: 1px solid #ffd43b;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 20px;
            font-size: 13px;
            color: #856404;
        }
        .instructions strong {
            display: block;
            margin-bottom: 4px;
        }
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
            <div class="selection-info">
                已选择 <span class="selection-count" id="count">0</span> 个文件夹
            </div>
            <button class="btn btn-primary" id="confirmBtn" onclick="confirmSelection()" disabled>
                确认选择 →
            </button>
        </div>
    </div>

    <script>
        let selectedFolders = new Set();
        let allFolders = [];

        function loadData() {
            const dataScript = document.createElement('script');
            dataScript.src = 'data.json';
            dataScript.onload = function() {
                if (window.folderData) {
                    allFolders = window.folderData.folders || [];
                    renderFolders(allFolders);
                }
            };
            document.head.appendChild(dataScript);
        }

        function renderFolders(folders) {
            const container = document.getElementById('folderList');
            container.innerHTML = '';

            folders.forEach(folder => {
                const div = document.createElement('div');
                div.className = 'folder-item';
                div.dataset.id = folder.path;
                div.dataset.name = folder.name;

                div.innerHTML = `
                    <div class="checkbox"></div>
                    <span class="folder-icon">📂</span>
                    <div class="folder-info">
                        <div class="folder-name"></div>
                        <div class="folder-meta"></div>
                    </div>
                `;

                div.querySelector('.folder-name').textContent = folder.name;
                div.querySelector('.folder-meta').textContent =
                    `${folder.subfolders} 个子文件夹, ${folder.files} 个文件`;

                div.onclick = () => toggleFolder(folder.path, div);

                container.appendChild(div);
            });
        }

        function toggleFolder(path, element) {
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
            const items = document.querySelectorAll('.folder-item');
            items.forEach(item => {
                const name = item.dataset.name.toLowerCase();
                if (name.includes(query.toLowerCase()) || query === '') {
                    item.classList.remove('hidden');
                } else {
                    item.classList.add('hidden');
                }
            });
        }

        function confirmSelection() {
            const selections = [];
            selectedFolders.forEach(path => {
                const folder = allFolders.find(f => f.path === path);
                if (folder) {
                    selections.push({
                        type: 'folder',
                        path: folder.path,
                        name: folder.name
                    });
                }
            });

            const result = {
                timestamp: new Date().toISOString(),
                selections: selections
            };

            // 写入剪贴板
            navigator.clipboard.writeText(JSON.stringify(result, null, 2)).then(() => {
                alert('✅ 选择已确认！\n\n结果已复制到剪贴板。\n\n请返回 Claude 继续操作。');
            }).catch(() => {
                alert('选择结果：\n' + JSON.stringify(result, null, 2));
            });

            // 同时写入 localStorage
            localStorage.setItem('obsidian-learning-selections', JSON.stringify(result));
        }

        document.getElementById('searchInput').oninput = function(e) {
            filterFolders(e.target.value);
        };

        loadData();
    </script>
</body>
</html>
HTMLEOF

echo "✅ HTML 选择器已生成：$OUTPUT_HTML"
