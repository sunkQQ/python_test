// 族谱记录系统前端交互脚本 (Bootstrap 5 版本)

// 当前模态框操作模式: 'add' 或 'edit'
let currentMode = 'add';
let editingMemberId = null;
let currentFamilyId = null; // 当前选中的家族ID（null 表示尚未选择任何家族）

// DOMContentLoaded 事件
document.addEventListener('DOMContentLoaded', function() {
    // 加载家族列表（内部会触发首次族谱/列表加载）
    loadFamilies();

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

    // 模态框隐藏时重置状态（修复"取消后按钮无法点击"问题）
    const memberModal = document.getElementById('memberModal');
    if (memberModal) {
        memberModal.addEventListener('hidden.bs.modal', function() {
            // 恢复保存按钮状态
            const saveBtn = document.getElementById('saveBtn');
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.textContent = '💾 保存';
            }
            // 重置表单
            resetForm();
        });
    }

    // 性别改变时更新配偶选项
    const genderSelect = document.getElementById('gender');
    if (genderSelect) {
        genderSelect.addEventListener('change', function() {
            updateSpouseOptions();
        });
    }
});

// 打开添加成员模态框
function openAddModal() {
    // 必须先选择家族，否则提示
    if (!currentFamilyId) {
        showToast('请先在顶部选择一个家族，再添加成员', 'error');
        return;
    }
    currentMode = 'add';
    editingMemberId = null;
    document.getElementById('modalTitle').textContent = '➕ 添加成员';
    resetForm();
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('memberModal'));
    modal.show();
    // 动态加载同家族的父/母/配偶候选
    updateParentOptions();
    updateSpouseOptions();
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
                // 切换到该成员所属的家族（避免跨家族编辑混乱）
                if (data.data.family_id && data.data.family_id !== currentFamilyId) {
                    currentFamilyId = data.data.family_id;
                    const sel = document.getElementById('familySelect');
                    if (sel) sel.value = String(currentFamilyId);
                }
                fillForm(data.data);
                // 加载同家族的父/母/配偶候选后再回填
                updateParentOptions().then(() => updateSpouseOptions());
                const modal = new bootstrap.Modal(document.getElementById('memberModal'));
                modal.show();
            } else {
                showToast('加载成员数据失败：' + data.message, 'error');
            }
        })
        .catch(err => {
            showToast('请求失败：' + err.message, 'error');
        });
}

// 更新父/母下拉选项（按当前家族过滤，父亲只显示男性，母亲只显示女性）
function updateParentOptions() {
    const fatherSelect = document.getElementById('father_id');
    const motherSelect = document.getElementById('mother_id');
    // 编辑时优先从 dataset 回填原值；否则保留当前已选值
    const initialFather = fatherSelect ? fatherSelect.dataset.initialValue : '';
    const initialMother = motherSelect ? motherSelect.dataset.initialValue : '';
    const targetFather = initialFather || (fatherSelect ? fatherSelect.value : '');
    const targetMother = initialMother || (motherSelect ? motherSelect.value : '');

    // 清空选项（保留默认）
    if (fatherSelect) fatherSelect.innerHTML = '<option value="">— 请选择 —</option>';
    if (motherSelect) motherSelect.innerHTML = '<option value="">— 请选择 —</option>';

    // 无家族则不加载候选
    if (!currentFamilyId) return Promise.resolve();

    return fetch('/api/members?family_id=' + currentFamilyId)
        .then(res => res.json())
        .then(data => {
            if (!data.success) return;
            data.members.forEach(m => {
                // 排除自己
                if (m.id === editingMemberId) return;
                if (m.gender === '男' && fatherSelect) {
                    const opt = document.createElement('option');
                    opt.value = m.id;
                    opt.textContent = `${m.name} (${m.birth_date || '未知出生'})`;
                    fatherSelect.appendChild(opt);
                } else if (m.gender === '女' && motherSelect) {
                    const opt = document.createElement('option');
                    opt.value = m.id;
                    opt.textContent = `${m.name} (${m.birth_date || '未知出生'})`;
                    motherSelect.appendChild(opt);
                }
            });
            // 回填原值（编辑场景）或保留当前选择
            if (targetFather && fatherSelect) fatherSelect.value = targetFather;
            if (targetMother && motherSelect) motherSelect.value = targetMother;
        })
        .catch(err => console.error('加载父/母候选失败:', err));
}

// 更新配偶选项（根据当前性别过滤，只显示异性，且只限同家族）
function updateSpouseOptions() {
    const gender = document.getElementById('gender').value;
    const spouseSelect = document.getElementById('spouse_id');
    // 编辑时优先从 dataset 回填原值；否则保留当前已选值
    const initialSpouse = spouseSelect ? spouseSelect.dataset.initialValue : '';
    const targetSpouse = initialSpouse || (spouseSelect ? spouseSelect.value : '');

    // 清空选项（保留默认）
    spouseSelect.innerHTML = '<option value="">— 请选择 —</option>';

    // 无家族则不加载
    if (!currentFamilyId) return;

    fetch('/api/members?family_id=' + currentFamilyId)
        .then(res => res.json())
        .then(data => {
            if (!data.success) return;
            data.members.forEach(m => {
                // 排除自己
                if (m.id === editingMemberId) return;
                // 配偶必须是异性
                if (gender === '男' && m.gender === '女') {
                    const opt = document.createElement('option');
                    opt.value = m.id;
                    opt.textContent = `${m.name} (${m.gender})`;
                    spouseSelect.appendChild(opt);
                } else if (gender === '女' && m.gender === '男') {
                    const opt = document.createElement('option');
                    opt.value = m.id;
                    opt.textContent = `${m.name} (${m.gender})`;
                    spouseSelect.appendChild(opt);
                }
                // 性别为"未知"时不显示候选（避免误选同性）
            });
            // 回填原值（编辑场景）或保留当前选择
            if (targetSpouse) spouseSelect.value = targetSpouse;
        })
        .catch(err => console.error('加载成员列表失败:', err));
}

// 加载家族列表
function loadFamilies() {
    fetch('/api/families')
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                loadTree();
                loadMemberList();
                return;
            }
            const familySelect = document.getElementById('familySelect');
            familySelect.innerHTML = '';

            if (data.families.length === 0) {
                // 没有任何家族时显示提示
                const opt = document.createElement('option');
                opt.value = '';
                opt.textContent = '请先创建家族';
                familySelect.appendChild(opt);
                loadTree();
                loadMemberList();
                return;
            }

            // 不再提供"全部家族"选项，强制用户选择具体家族
            data.families.forEach(f => {
                const opt = document.createElement('option');
                opt.value = f.id;
                opt.textContent = f.name;
                familySelect.appendChild(opt);
            });

            // 默认选中第一个家族
            if (!currentFamilyId) {
                currentFamilyId = data.families[0].id;
            }
            familySelect.value = String(currentFamilyId);

            // 加载该家族的族谱树和成员列表
            loadTree();
            loadMemberList();
        })
        .catch(err => {
            console.error('加载家族列表失败:', err);
            loadTree();
            loadMemberList();
        });
}

// 切换家族
function switchFamily(familyId) {
    currentFamilyId = familyId ? parseInt(familyId) : null;
    loadTree();
    loadMemberList();
}

// 添加家族
function addFamily() {
    const name = prompt('请输入家族名称：');
    if (!name || !name.trim()) return;

    fetch('/api/family/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim() })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast('家族「' + name + '」添加成功！', 'success');
                // 切换到新家族
                currentFamilyId = data.id;
                loadFamilies();
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(err => showToast('请求失败：' + err.message, 'error'));
}

// 重置表单
function resetForm() {
    document.getElementById('memberForm').reset();
    document.getElementById('memberId').value = '';
    document.getElementById('is_alive').checked = true;
    document.getElementById('death_date').disabled = true;
    // 清空下拉的动态选项和 dataset（避免编辑后添加时复用上次的初始值）
    const fatherSelect = document.getElementById('father_id');
    const motherSelect = document.getElementById('mother_id');
    const spouseSelect = document.getElementById('spouse_id');
    [fatherSelect, motherSelect, spouseSelect].forEach(sel => {
        if (sel) {
            sel.innerHTML = '<option value="">— 请选择 —</option>';
            delete sel.dataset.initialValue;
        }
    });
}

// 用数据填充表单
function fillForm(member) {
    document.getElementById('memberId').value = member.id;
    document.getElementById('name').value = member.name || '';
    document.getElementById('gender').value = member.gender || '未知';
    document.getElementById('birth_date').value = member.birth_date || '';
    document.getElementById('death_date').value = member.death_date || '';
    document.getElementById('is_alive').checked = member.is_alive === 1;
    // 父/母/配偶值先记下，等 updateParentOptions/updateSpouseOptions 加载完候选后由 value 回填
    document.getElementById('father_id').dataset.initialValue = member.father_id || '';
    document.getElementById('mother_id').dataset.initialValue = member.mother_id || '';
    document.getElementById('spouse_id').dataset.initialValue = member.spouse_id || '';
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

    // 处理 is_alive（FormData 中未勾选时不存在该字段）
    formData.set('is_alive', document.getElementById('is_alive').checked ? 'on' : 'off');

    // 关键：把当前家族ID 传给后端，让成员归属到正确家族
    if (currentMode === 'add') {
        if (!currentFamilyId) {
            showToast('请先选择家族', 'error');
            return;
        }
        formData.set('family_id', String(currentFamilyId));
    } else if (editingMemberId) {
        // 编辑模式：保留原家族（后端 UPDATE 不改 family_id），不传也没关系
    }

    if (!formData.get('name') || !formData.get('name').trim()) {
        showToast('请输入姓名', 'error');
        return;
    }

    const url = currentMode === 'add'
        ? '/api/member/add'
        : '/api/member/edit/' + editingMemberId;

    // 显示保存中
    const saveBtn = document.getElementById('saveBtn');
    saveBtn.disabled = true;
    saveBtn.textContent = '保存中...';

    fetch(url, {
        method: 'POST',
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
                // 刷新数据（不再用 location.reload，避免丢失家族选择）
                loadTree();
                loadMemberList();
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

    fetch('/api/member/delete/' + memberId, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                loadTree();
                loadMemberList();
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(err => showToast('请求失败：' + err.message, 'error'));
}

// 加载成员列表（AJAX 渲染表格，按当前家族过滤）
function loadMemberList() {
    const listContainer = document.getElementById('listContainer');
    if (!listContainer) return;

    if (!currentFamilyId) {
        listContainer.innerHTML = `
            <div class="card-body text-center py-5">
                <div style="font-size: 4rem;">🌳</div>
                <h4 class="text-muted mb-3">请先选择一个家族</h4>
                <p class="text-muted">在顶部下拉框中选择或创建家族后，即可查看该家族的成员</p>
            </div>`;
        return;
    }

    fetch('/api/members?family_id=' + currentFamilyId)
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                listContainer.innerHTML = `<div class="alert alert-danger m-3">${data.message}</div>`;
                return;
            }
            renderMemberList(data.members);
            // 同步更新页脚的成员计数
            const counter = document.getElementById('memberCount');
            if (counter) counter.textContent = String(data.members.length);
        })
        .catch(err => {
            listContainer.innerHTML = `<div class="alert alert-danger m-3">加载失败：${err.message}</div>`;
        });
}

// 渲染成员列表表格
function renderMemberList(members) {
    const listContainer = document.getElementById('listContainer');
    if (!members || members.length === 0) {
        listContainer.innerHTML = `
            <div class="card-body text-center py-5">
                <div style="font-size: 4rem;">🌳</div>
                <h4 class="text-muted mb-3">该家族暂无成员</h4>
                <button class="btn btn-primary btn-lg" onclick="openAddModal()">
                    ➕ 添加第一位成员
                </button>
            </div>`;
        return;
    }

    // 构建 id -> name 映射，用于显示配偶名
    const nameMap = {};
    members.forEach(m => { nameMap[m.id] = m.name; });

    let rowsHtml = '';
    members.forEach(m => {
        const genderBadge = m.gender === '男'
            ? '<span class="badge bg-primary">♂ 男</span>'
            : (m.gender === '女' ? '<span class="badge bg-danger">♀ 女</span>'
                : `<span class="badge bg-secondary">${escapeHtml(m.gender)}</span>`);
        const statusBadge = m.is_alive
            ? '<span class="badge bg-success">健在</span>'
            : '<span class="badge bg-dark">已故</span>';
        const spouseName = m.spouse_id ? (nameMap[m.spouse_id] || '—') : '—';

        rowsHtml += `
            <tr>
                <td class="text-muted">#${m.id}</td>
                <td><strong>${escapeHtml(m.name)}</strong></td>
                <td>${genderBadge}</td>
                <td>${escapeHtml(m.birth_date) || '—'}</td>
                <td>${statusBadge}</td>
                <td>${escapeHtml(spouseName)}</td>
                <td class="text-center">
                    <div class="btn-group btn-group-sm">
                        <button type="button" class="btn btn-outline-warning" onclick="openEditModal(${m.id})">编辑</button>
                        <button type="button" class="btn btn-outline-danger" onclick="deleteMember(${m.id}, '${escapeHtml(m.name)}')">删除</button>
                    </div>
                </td>
            </tr>`;
    });

    listContainer.innerHTML = `
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>ID</th>
                            <th>姓名</th>
                            <th>性别</th>
                            <th>出生日期</th>
                            <th>状态</th>
                            <th>配偶</th>
                            <th class="text-center">操作</th>
                        </tr>
                    </thead>
                    <tbody>${rowsHtml}</tbody>
                </table>
            </div>
        </div>`;
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
                <strong>${icon} ${escapeHtml(message)}</strong>
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
    if (!container) return;

    if (!currentFamilyId) {
        container.innerHTML = `
            <div class="empty-tree text-center py-5">
                <div style="font-size: 4rem;">🌳</div>
                <h5 class="mt-3 text-muted">请先选择一个家族</h5>
                <p class="mb-3 text-muted">在顶部下拉框中选择或创建家族后，即可查看族谱</p>
            </div>`;
        return;
    }

    const url = '/api/tree?family_id=' + currentFamilyId;
    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (!data || data.length === 0) {
                container.innerHTML = `
                    <div class="empty-tree text-center py-5">
                        <div style="font-size: 4rem;">🌳</div>
                        <h5 class="mt-3 text-muted">该家族暂无族谱数据</h5>
                        <p class="mb-3 text-muted">添加第一位成员开始构建家族族谱</p>
                        <button class="btn btn-primary btn-lg" onclick="openAddModal()">
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
    card.addEventListener('click', () => openEditModal(node.id));
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
    if (node.birth_date) dates.push(node.birth_date);
    if (!node.is_alive && node.death_date) dates.push(node.death_date);
    if (dates.length === 2) return dates[0] + ' ~ ' + dates[1];
    if (dates.length === 1) return dates[0] + (node.is_alive ? ' 至今' : '');
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
