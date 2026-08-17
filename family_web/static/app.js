// 族谱记录系统前端交互脚本

// 标签页切换
document.addEventListener('DOMContentLoaded', function() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            // 切换按钮状态
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            // 切换内容显示
            tabContents.forEach(c => c.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            // 如果切换到树视图，则加载树
            if (tabId === 'tree') {
                loadTree();
            }
        });
    });

    // 默认加载族谱树
    loadTree();

    // 全部展开/收起
    document.getElementById('expandAll').addEventListener('click', function() {
        document.querySelectorAll('.tree-children').forEach(el => el.style.display = 'flex');
    });

    document.getElementById('collapseAll').addEventListener('click', function() {
        document.querySelectorAll('.tree-children').forEach(el => el.style.display = 'none');
    });
});

// 从后端获取树形数据并渲染
function loadTree() {
    const container = document.getElementById('treeContainer');
    fetch('/api/tree')
        .then(res => res.json())
        .then(data => {
            if (!data || data.length === 0) {
                container.innerHTML = `
                    <div class="empty-tree">
                        <p>🌳 暂无族谱数据</p>
                        <a href="/member/add" class="btn btn-primary">添加第一位成员</a>
                    </div>`;
                return;
            }
            container.innerHTML = '';
            data.forEach(root => {
                container.appendChild(renderNode(root));
            });
        })
        .catch(err => {
            container.innerHTML = `<p class="loading">加载失败：${err.message}</p>`;
        });
}

// 递归渲染树节点
function renderNode(node) {
    const nodeEl = document.createElement('div');
    nodeEl.className = 'tree-node node-gender-' + (node.gender || '未知');

    // 节点卡片（包含本人和配偶）
    const cardWrap = document.createElement('div');
    cardWrap.style.display = 'flex';
    cardWrap.style.alignItems = 'center';
    cardWrap.style.gap = '6px';

    // 本人卡片
    const card = document.createElement('div');
    card.className = 'node-card';
    card.innerHTML = `
        <div class="node-avatar">${escapeHtml(node.name || '?').charAt(0)}</div>
        <div class="node-info">
            <div class="node-name">${escapeHtml(node.name)}</div>
            <div class="node-dates">${formatDates(node)}</div>
        </div>
    `;
    card.addEventListener('click', () => {
        window.location.href = '/member/view/' + node.id;
    });
    cardWrap.appendChild(card);

    // 配偶
    if (node.spouse_id && node.spouse_name) {
        const spouseEl = document.createElement('div');
        spouseEl.className = 'node-spouse';
        spouseEl.textContent = node.spouse_name;
        spouseEl.title = '配偶：' + node.spouse_name;
        spouseEl.addEventListener('click', (e) => {
            e.stopPropagation();
            window.location.href = '/member/view/' + node.spouse_id;
        });
        cardWrap.appendChild(spouseEl);
    }

    nodeEl.appendChild(cardWrap);

    // 子女节点
    if (node.children && node.children.length > 0) {
        const childrenWrap = document.createElement('div');
        childrenWrap.className = 'tree-children';
        node.children.forEach(child => {
            childrenWrap.appendChild(renderNode(child));
        });
        nodeEl.appendChild(childrenWrap);
    }

    return nodeEl;
}

// 格式化日期显示
function formatDates(node) {
    let dates = [];
    if (node.birth_date) {
        dates.push(node.birth_date);
    }
    if (!node.is_alive && node.death_date) {
        dates.push(node.death_date);
    }
    if (dates.length === 2) {
        return dates[0] + ' ~ ' + dates[1];
    } else if (dates.length === 1) {
        return dates[0] + (node.is_alive ? ' 至今' : '');
    }
    return '';
}

// HTML 转义，防止 XSS
function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
