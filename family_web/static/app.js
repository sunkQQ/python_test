// 族谱记录系统前端交互脚本 (Bootstrap 5 版本)

// 当前模态框操作模式: 'add' 或 'edit'
let currentMode = 'add';
let editingMemberId = null;

// DOMContentLoaded 事件
document.addEventListener('DOMContentLoaded', function() {
    // 默认加载族谱树
    loadTree();

    // 全部展开/收起
    document.getElementById('expandAll').addEventListener('click', function() {
        document.querySelectorAll('.tree-children').forEach(el => el.style.display = 'flex');
    });

    document.getElementById('collapseAll').addEventListener('click', function() {
        document.querySelectorAll('.tree-children').forEach(el => el.style.display = 'none');
    });

    // 表单健在状态切换
    const isAliveCheck = document.getElementById('is_alive');
    if (isAliveCheck) {
        isAliveCheck.addEventListener('change', function() {
            toggleDeathDate(this);
        });
    }
});

// 打开添加成员模态框
function openAddModal() {
    currentMode = 'add';
    editingMemberId = null;
    document.getElementById('modalTitle').textContent = '➕ 添加成员';
    resetForm();
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('memberModal'));
    modal.show();
}

// 打开编辑成员模态框
function openEditModal(memberId) {
    currentMode = 'edit';
    editingMemberId = memberId;
    document.getElementById('modalTitle').textContent = '✏️ 编辑成员 #' + memberId;
    
    // 从后端获取成员数据
    fetch('/api/member/' + memberId)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                fillForm(data.data);
                const modal = new bootstrap.Modal(document.getElementById('memberModal'));
                modal.show();
            } else {
                alert('加载成员数据失败：' + data.message);
            }
        })
        .catch(err => {
            alert('请求失败：' + err.message);
        });
}

// 重置表单
function resetForm() {
    document.getElementById('memberForm').reset();
    document.getElementById('memberId').value = '';
    document.getElementById('is_alive').checked = true;
    document.getElementById('death_date').disabled = true;
}

// 用数据填充表单
function fillForm(member) {
    document.getElementById('memberId').value = member.id;
    document.getElementById('name').value = member.name || '';
    document.getElementById('gender').value = member.gender || '未知';
    document.getElementById('birth_date').value = member.birth_date || '';
    document.getElementById('death_date').value = member.death_date || '';
    document.getElementById('is_alive').checked = member.is_alive === 1;
    document.getElementById('father_id').value = member.father_id || '';
    document.getElementById('mother_id').value = member.mother_id || '';
    document.getElementById('spouse_id').value = member.spouse_id || '';
    document.getElementById('note').value = member.note || '';
    toggleDeathDate(document.getElementById('is_alive'));
}

// 健在状态切换
function toggleDeathDate(checkbox) {
    const deathInput = document.getElementById('death_date');
    if (!deathInput) return;
    if (checkbox.checked) {
        deathInput.disabled = true;
        deathInput.value = '';
    } else {
        deathInput.disabled = false;
    }
}

// 保存成员（添加或编辑）
function saveMember() {
    const form = document.getElementById('memberForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // 处理 is_alive 复选框
    data.is_alive = document.getElementById('is_alive').checked ? 'on' : 'off';
    
    // 处理ID
    data.father_id = data.father_id || null;
    data.mother_id = data.mother_id || null;
    data.spouse_id = data.spouse_id || null;

    if (!data.name || !data.name.trim()) {
        showToast('请输入姓名', 'error');
        return;
    }

    const url = currentMode === 'add' 
        ? '/api/member/add' 
        : '/api/member/edit/' + editingMemberId;
    
    const method = 'POST';

    // 显示保存中
    const saveBtn = document.getElementById('saveBtn');
    saveBtn.disabled = true;
    saveBtn.textContent = '保存中...';

    fetch(url, {
        method: method,
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        saveBtn.disabled = false;
        saveBtn.textContent = '💾 保存';
        
        if (data.success) {
            showToast(data.message, 'success');
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('memberModal'));
            if (modal) modal.hide();
            // 刷新数据
            if (currentMode === 'add') {
                loadTree();
                refreshList();
            } else {
                loadTree();
                refreshList();
            }
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(err => {
        saveBtn.disabled = false;
        saveBtn.textContent = '💾 保存';
        showToast('请求失败：' + err.message, 'error');
    });
}

// 删除成员
function deleteMember(memberId, memberName) {
    if (!confirm(`确定删除成员「${memberName}」吗？\n\n此操作会解除该成员与其他成员的关系（但不会影响其他成员的信息）。`)) {
        return;
    }
    
    fetch('/api/member/delete/' + memberId, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            loadTree();
            refreshList();
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(err => {
        showToast('请求失败：' + err.message, 'error');
    });
}

// 刷新成员列表（简单方式：重新加载页面，或调用后端渲染）
// 这里简单刷新列表部分，通过获取新页面HTML
function refreshList() {
    // 简单做法：重新加载页面（因为列表是后端渲染的）
    // 为了更好的体验，我们可以使用 AJAX 获取新的列表数据
    // 但为了简单和稳定性，这里使用 location.reload()
    // 更好的做法是添加一个 API 返回渲染好的列表HTML
    location.reload();
}

// 提示消息（Toast）
function showToast(message, type = 'success') {
    const toastContainer = document.createElement('div');
    toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '9999';
    
    const bgClass = type === 'success' ? 'bg-success' : 'bg-danger';
    const icon = type === 'success' ? '✅' : '❌';
    
    toastContainer.innerHTML = `
        <div class="toast show border-0 ${bgClass} text-white" role="alert">
            <div class="toast-body">
                <strong>${icon} ${message}</strong>
            </div>
        </div>
    `;
    
    document.body.appendChild(toastContainer);
    
    // 3秒后自动消失
    setTimeout(() => {
        toastContainer.querySelector('.toast').classList.remove('show');
        setTimeout(() => toastContainer.remove(), 300);
    }, 3000);
}

// 从后端获取树形数据并渲染
function loadTree() {
    const container = document.getElementById('treeContainer');
    fetch('/api/tree')
        .then(res => res.json())
        .then(data => {
            if (!data || data.length === 0) {
                container.innerHTML = `
                    <div class="empty-tree text-center py-5">
                        <div style="font-size: 4rem;">🌳</div>
                        <h5 class="mt-3 text-muted">暂无族谱数据</h5>
                        <p class="mb-3 text-muted">添加第一位成员开始构建您的家族族谱</p>
                        <button class="btn btn-primary btn-lg" data-bs-toggle="modal" data-bs-target="#memberModal" onclick="openAddModal()">
                            ➕ 添加成员
                        </button>
                    </div>`;
                return;
            }
            container.innerHTML = '';
            data.forEach(root => {
                container.appendChild(renderNode(root));
            });
        })
        .catch(err => {
            container.innerHTML = `<div class="alert alert-danger">加载族谱失败：${err.message}</div>`;
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
    cardWrap.style.gap = '8px';

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
        // 点击节点直接打开编辑模态框
        openEditModal(node.id);
    });
    cardWrap.appendChild(card);

    // 配偶
    if (node.spouse_id && node.spouse_name) {
        const spouseEl = document.createElement('div');
        spouseEl.className = 'node-spouse';
        spouseEl.textContent = node.spouse_name;
        spouseEl.title = '配偶：' + node.spouse_name + '（点击编辑）';
        spouseEl.addEventListener('click', (e) => {
            e.stopPropagation();
            openEditModal(node.spouse_id);
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
