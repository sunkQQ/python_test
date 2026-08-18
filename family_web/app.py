#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
族谱记录系统 - Flask 后端主程序

@author sunk
@since 2026-06-10
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g

app = Flask(__name__)
app.secret_key = "family_tree_secret_key_2026"

# 数据库文件路径（放在程序同目录下）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "family.db")


def get_db():
    """获取数据库连接（请求内缓存）"""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row  # 让查询结果支持通过列名访问
        # 自动检查表是否存在，如果不存在则创建
        g.db.execute(
            """
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT DEFAULT '未知',
                birth_date TEXT,
                death_date TEXT,
                is_alive INTEGER DEFAULT 1,
                father_id INTEGER,
                mother_id INTEGER,
                spouse_id INTEGER,
                note TEXT,
                created_at TEXT,
                FOREIGN KEY (father_id) REFERENCES members(id),
                FOREIGN KEY (mother_id) REFERENCES members(id),
                FOREIGN KEY (spouse_id) REFERENCES members(id)
            )
        """
        )
        g.db.commit()
    return g.db


@app.teardown_appcontext
def close_db(error):
    """请求结束后关闭数据库连接"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """初始化数据库表结构"""
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,                       -- 姓名
            gender TEXT DEFAULT '未知',               -- 性别：男/女/未知
            birth_date TEXT,                          -- 出生日期
            death_date TEXT,                          -- 去世日期（健在则留空）
            is_alive INTEGER DEFAULT 1,               -- 是否健在：1健在/0已故
            father_id INTEGER,                        -- 父亲ID
            mother_id INTEGER,                        -- 母亲ID
            spouse_id INTEGER,                        -- 配偶ID
            note TEXT,                                -- 备注（生平、职业等）
            created_at TEXT,                          -- 创建时间
            FOREIGN KEY (father_id) REFERENCES members(id),
            FOREIGN KEY (mother_id) REFERENCES members(id),
            FOREIGN KEY (spouse_id) REFERENCES members(id)
        )
    """
    )
    db.commit()
    db.close()


def get_all_members():
    """获取所有成员列表"""
    db = get_db()
    return db.execute("SELECT * FROM members ORDER BY id").fetchall()


def get_member(member_id):
    """获取单个成员信息"""
    db = get_db()
    return db.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()


def get_children(member_id):
    """获取某成员的子女列表"""
    db = get_db()
    return db.execute(
        "SELECT * FROM members WHERE father_id = ? OR mother_id = ? ORDER BY birth_date",
        (member_id, member_id),
    ).fetchall()


def format_member(row):
    """将数据库行转换为字典，便于前端使用"""
    if row is None:
        return None
    return {
        "id": row["id"],
        "name": row["name"],
        "gender": row["gender"],
        "birth_date": row["birth_date"] or "",
        "death_date": row["death_date"] or "",
        "is_alive": row["is_alive"],
        "father_id": row["father_id"],
        "mother_id": row["mother_id"],
        "spouse_id": row["spouse_id"],
        "note": row["note"] or "",
        "created_at": row["created_at"] or "",
    }


@app.route("/")
def index():
    """主页：展示所有成员"""
    members = [format_member(m) for m in get_all_members()]
    return render_template("index.html", members=members)


@app.route("/member/add", methods=["GET", "POST"])
def add_member():
    """添加成员"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("姓名不能为空", "error")
            return redirect(url_for("add_member"))

        # 收集表单数据
        gender = request.form.get("gender", "未知")
        birth_date = request.form.get("birth_date", "").strip() or None
        death_date = request.form.get("death_date", "").strip() or None
        is_alive = 1 if request.form.get("is_alive") == "on" else 0
        father_id = request.form.get("father_id") or None
        mother_id = request.form.get("mother_id") or None
        spouse_id = request.form.get("spouse_id") or None
        note = request.form.get("note", "").strip()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 父亲ID不能是自己
        father_id = int(father_id) if father_id else None
        mother_id = int(mother_id) if mother_id else None
        spouse_id = int(spouse_id) if spouse_id else None

        db = get_db()
        # 后端校验：父亲必须是男性，母亲必须是女性（防止前端绕过）
        if father_id:
            father_row = db.execute(
                "SELECT gender FROM members WHERE id = ?", (father_id,)
            ).fetchone()
            if not father_row or father_row["gender"] != "男":
                flash("父亲必须选择男性成员", "error")
                members = [format_member(m) for m in get_all_members()]
                return render_template(
                    "member_form.html", member=None, members=members, action="add"
                )
        if mother_id:
            mother_row = db.execute(
                "SELECT gender FROM members WHERE id = ?", (mother_id,)
            ).fetchone()
            if not mother_row or mother_row["gender"] != "女":
                flash("母亲必须选择女性成员", "error")
                members = [format_member(m) for m in get_all_members()]
                return render_template(
                    "member_form.html", member=None, members=members, action="add"
                )

        db.execute(
            """INSERT INTO members 
               (name, gender, birth_date, death_date, is_alive, 
                father_id, mother_id, spouse_id, note, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name,
                gender,
                birth_date,
                death_date,
                is_alive,
                father_id,
                mother_id,
                spouse_id,
                note,
                created_at,
            ),
        )
        db.commit()
        flash(f"成员「{name}」添加成功！", "success")
        return redirect(url_for("index"))

    # GET 请求：展示添加表单
    members = [format_member(m) for m in get_all_members()]
    return render_template(
        "member_form.html", member=None, members=members, action="add"
    )


@app.route("/member/edit/<int:member_id>", methods=["GET", "POST"])
def edit_member(member_id):
    """编辑成员"""
    member = get_member(member_id)
    if member is None:
        flash("成员不存在", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("姓名不能为空", "error")
            return redirect(url_for("edit_member", member_id=member_id))

        gender = request.form.get("gender", "未知")
        birth_date = request.form.get("birth_date", "").strip() or None
        death_date = request.form.get("death_date", "").strip() or None
        is_alive = 1 if request.form.get("is_alive") == "on" else 0
        father_id = request.form.get("father_id") or None
        mother_id = request.form.get("mother_id") or None
        spouse_id = request.form.get("spouse_id") or None
        note = request.form.get("note", "").strip()

        father_id = int(father_id) if father_id else None
        mother_id = int(mother_id) if mother_id else None
        spouse_id = int(spouse_id) if spouse_id else None

        # 防止把本人设为自己的父/母/配偶
        father_id = None if father_id == member_id else father_id
        mother_id = None if mother_id == member_id else mother_id
        spouse_id = None if spouse_id == member_id else spouse_id

        db = get_db()
        # 后端校验：父亲必须是男性，母亲必须是女性
        if father_id:
            father_row = db.execute(
                "SELECT gender FROM members WHERE id = ?", (father_id,)
            ).fetchone()
            if not father_row or father_row["gender"] != "男":
                flash("父亲必须选择男性成员", "error")
                members = [format_member(m) for m in get_all_members()]
                return render_template(
                    "member_form.html",
                    member=format_member(member),
                    members=members,
                    action="edit",
                )
        if mother_id:
            mother_row = db.execute(
                "SELECT gender FROM members WHERE id = ?", (mother_id,)
            ).fetchone()
            if not mother_row or mother_row["gender"] != "女":
                flash("母亲必须选择女性成员", "error")
                members = [format_member(m) for m in get_all_members()]
                return render_template(
                    "member_form.html",
                    member=format_member(member),
                    members=members,
                    action="edit",
                )

        db.execute(
            """UPDATE members SET
               name = ?, gender = ?, birth_date = ?, death_date = ?, is_alive = ?,
               father_id = ?, mother_id = ?, spouse_id = ?, note = ?
               WHERE id = ?""",
            (
                name,
                gender,
                birth_date,
                death_date,
                is_alive,
                father_id,
                mother_id,
                spouse_id,
                note,
                member_id,
            ),
        )
        db.commit()
        flash(f"成员「{name}」更新成功！", "success")
        return redirect(url_for("index"))

    members = [format_member(m) for m in get_all_members()]
    return render_template(
        "member_form.html", member=format_member(member), members=members, action="edit"
    )


@app.route("/member/delete/<int:member_id>", methods=["POST"])
def delete_member(member_id):
    """删除成员"""
    member = get_member(member_id)
    if member is None:
        flash("成员不存在", "error")
        return redirect(url_for("index"))

    name = member["name"]
    db = get_db()
    # 删除前，把其他成员指向该成员的外键置空（避免破坏关系）
    db.execute("UPDATE members SET father_id = NULL WHERE father_id = ?", (member_id,))
    db.execute("UPDATE members SET mother_id = NULL WHERE mother_id = ?", (member_id,))
    db.execute("UPDATE members SET spouse_id = NULL WHERE spouse_id = ?", (member_id,))
    db.execute("DELETE FROM members WHERE id = ?", (member_id,))
    db.commit()
    flash(f"成员「{name}」已删除", "success")
    return redirect(url_for("index"))


@app.route("/member/view/<int:member_id>")
def view_member(member_id):
    """查看成员详情"""
    member = get_member(member_id)
    if member is None:
        flash("成员不存在", "error")
        return redirect(url_for("index"))

    member = format_member(member)
    db = get_db()

    # 获取关联成员信息
    father = (
        format_member(
            db.execute(
                "SELECT * FROM members WHERE id = ?", (member["father_id"],)
            ).fetchone()
        )
        if member["father_id"]
        else None
    )
    mother = (
        format_member(
            db.execute(
                "SELECT * FROM members WHERE id = ?", (member["mother_id"],)
            ).fetchone()
        )
        if member["mother_id"]
        else None
    )
    spouse = (
        format_member(
            db.execute(
                "SELECT * FROM members WHERE id = ?", (member["spouse_id"],)
            ).fetchone()
        )
        if member["spouse_id"]
        else None
    )
    children = [format_member(c) for c in get_children(member_id)]

    return render_template(
        "member_detail.html",
        member=member,
        father=father,
        mother=mother,
        spouse=spouse,
        children=children,
    )


@app.route("/api/tree")
def api_tree():
    """提供族谱树形数据（JSON），供前端渲染树形结构。
    修复了同一成员在树中出现多次的问题：一个成员只能作为其父亲的子女（若父亲为空则作为母亲的子女）。
    同时确保配偶不会作为独立的根节点出现。
    """
    members = [format_member(m) for m in get_all_members()]
    member_map = {m["id"]: m for m in members}

    # 找出所有根节点：没有父亲的成员
    # 但如果一个成员已经是另一个根节点的配偶，就不要把它也作为根节点
    root_ids = []
    excluded_ids = set()  # 被排除的根节点ID（因为它们是其他根节点的配偶）

    # 第一遍：收集所有没有父亲的成员
    candidates = []
    for m in members:
        if not m["father_id"]:
            candidates.append(m["id"])

    # 第二遍：如果候选成员是另一个候选成员的配偶，就排除它
    for cid in candidates:
        m = member_map.get(cid)
        if m and m["spouse_id"] and m["spouse_id"] in candidates:
            # 比较ID大小，选择较小的作为根节点（确保一致性）
            if m["spouse_id"] < cid:
                excluded_ids.add(cid)

    # 构建最终的根节点列表
    root_ids = [cid for cid in candidates if cid not in excluded_ids]

    # 维护已访问的集合，防止节点重复渲染
    visited = set()

    def build_node(member_id):
        """递归构建子节点，确保每个节点只出现一次"""
        if member_id in visited:
            return None
        visited.add(member_id)

        m = member_map.get(member_id)
        if not m:
            return None

        # 查找子女：优先查找 father_id 匹配的成员
        children_ids = []
        for c in members:
            # 如果该成员的父亲是当前成员，或者（没有父亲且母亲是当前成员）
            if c["father_id"] == member_id or (
                not c["father_id"] and c["mother_id"] == member_id
            ):
                if c["id"] not in visited:
                    children_ids.append(c["id"])

        children = [build_node(cid) for cid in children_ids]
        children = [c for c in children if c]

        return {
            "id": m["id"],
            "name": m["name"],
            "gender": m["gender"],
            "birth_date": m["birth_date"],
            "death_date": m["death_date"],
            "is_alive": m["is_alive"],
            "spouse_id": m["spouse_id"],
            "spouse_name": (
                member_map[m["spouse_id"]]["name"]
                if m["spouse_id"] and m["spouse_id"] in member_map
                else ""
            ),
            "note": m["note"],
            "children": children,
        }

    tree = [build_node(rid) for rid in root_ids]
    tree = [t for t in tree if t]
    return jsonify(tree)


# === AJAX API 接口 ===


@app.route("/api/member/add", methods=["POST"])
def api_add_member():
    """AJAX 添加成员接口"""
    try:
        # 优先尝试获取 JSON 数据，如果失败则获取表单数据
        try:
            data = request.get_json(force=True)
        except Exception:
            data = request.form.to_dict(flat=False)

        # 处理 FormData 返回的列表值
        if isinstance(data, dict):
            for key, val in data.items():
                if isinstance(val, list):
                    data[key] = val[0] if val else None

        name = data.get("name", "").strip() if data.get("name") else ""
        if not name:
            return jsonify(success=False, message="姓名不能为空"), 400

        gender = data.get("gender", "未知")
        birth_date = data.get("birth_date", "").strip() or None
        death_date = data.get("death_date", "").strip() or None
        is_alive = 1 if data.get("is_alive") == "on" else 0
        father_id = data.get("father_id") or None
        mother_id = data.get("mother_id") or None
        spouse_id = data.get("spouse_id") or None
        note = data.get("note", "").strip()

        father_id = int(father_id) if father_id else None
        mother_id = int(mother_id) if mother_id else None
        spouse_id = int(spouse_id) if spouse_id else None

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db = get_db()
        # 后端性别校验
        if father_id:
            father_row = db.execute(
                "SELECT gender FROM members WHERE id = ?", (father_id,)
            ).fetchone()
            if not father_row or father_row["gender"] != "男":
                return jsonify(success=False, message="父亲必须选择男性成员"), 400
        if mother_id:
            mother_row = db.execute(
                "SELECT gender FROM members WHERE id = ?", (mother_id,)
            ).fetchone()
            if not mother_row or mother_row["gender"] != "女":
                return jsonify(success=False, message="母亲必须选择女性成员"), 400

        cursor = db.execute(
            """INSERT INTO members 
               (name, gender, birth_date, death_date, is_alive, 
                father_id, mother_id, spouse_id, note, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name,
                gender,
                birth_date,
                death_date,
                is_alive,
                father_id,
                mother_id,
                spouse_id,
                note,
                created_at,
            ),
        )
        new_id = cursor.lastrowid

        # 如果指定了配偶，反向更新配偶的 spouse_id
        if spouse_id:
            db.execute(
                "UPDATE members SET spouse_id = ? WHERE id = ?", (new_id, spouse_id)
            )

        db.commit()
        return jsonify(success=True, message=f"成员「{name}」添加成功！", id=new_id)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route("/api/member/edit/<int:member_id>", methods=["POST"])
def api_edit_member(member_id):
    """AJAX 编辑成员接口"""
    try:
        member = get_member(member_id)
        if member is None:
            return jsonify(success=False, message="成员不存在"), 404

        # 优先尝试获取 JSON 数据，如果失败则获取表单数据
        try:
            data = request.get_json(force=True)
        except Exception:
            data = request.form.to_dict(flat=False)

        # 处理 FormData 返回的列表值
        if isinstance(data, dict):
            for key, val in data.items():
                if isinstance(val, list):
                    data[key] = val[0] if val else None

        name = data.get("name", "").strip() if data.get("name") else ""
        if not name:
            return jsonify(success=False, message="姓名不能为空"), 400

        gender = data.get("gender", "未知")
        birth_date = data.get("birth_date", "").strip() or None
        death_date = data.get("death_date", "").strip() or None
        is_alive = 1 if data.get("is_alive") == "on" else 0
        father_id = data.get("father_id") or None
        mother_id = data.get("mother_id") or None
        spouse_id = data.get("spouse_id") or None
        note = data.get("note", "").strip()

        father_id = int(father_id) if father_id else None
        mother_id = int(mother_id) if mother_id else None
        spouse_id = int(spouse_id) if spouse_id else None

        # 防止把本人设为自己的父/母/配偶
        father_id = None if father_id == member_id else father_id
        mother_id = None if mother_id == member_id else mother_id
        spouse_id = None if spouse_id == member_id else spouse_id

        db = get_db()
        # 后端性别校验
        if father_id:
            father_row = db.execute(
                "SELECT gender FROM members WHERE id = ?", (father_id,)
            ).fetchone()
            if not father_row or father_row["gender"] != "男":
                return jsonify(success=False, message="父亲必须选择男性成员"), 400
        if mother_id:
            mother_row = db.execute(
                "SELECT gender FROM members WHERE id = ?", (mother_id,)
            ).fetchone()
            if not mother_row or mother_row["gender"] != "女":
                return jsonify(success=False, message="母亲必须选择女性成员"), 400

        db.execute(
            """UPDATE members SET
               name = ?, gender = ?, birth_date = ?, death_date = ?, is_alive = ?,
               father_id = ?, mother_id = ?, spouse_id = ?, note = ?
               WHERE id = ?""",
            (
                name,
                gender,
                birth_date,
                death_date,
                is_alive,
                father_id,
                mother_id,
                spouse_id,
                note,
                member_id,
            ),
        )

        # 处理配偶关系的双向更新
        old_spouse_id = member["spouse_id"]
        if spouse_id != old_spouse_id:
            # 如果有新配偶，更新新配偶的 spouse_id
            if spouse_id:
                db.execute(
                    "UPDATE members SET spouse_id = ? WHERE id = ?",
                    (member_id, spouse_id),
                )
            # 如果有旧配偶，清除旧配偶的 spouse_id（除非旧配偶已经是其他人的配偶）
            if old_spouse_id:
                old_spouse = get_member(old_spouse_id)
                if old_spouse and old_spouse["spouse_id"] == member_id:
                    db.execute(
                        "UPDATE members SET spouse_id = NULL WHERE id = ?",
                        (old_spouse_id,),
                    )

        db.commit()
        return jsonify(success=True, message=f"成员「{name}」更新成功！")
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route("/api/member/delete/<int:member_id>", methods=["POST"])
def api_delete_member(member_id):
    """AJAX 删除成员接口"""
    try:
        member = get_member(member_id)
        if member is None:
            return jsonify(success=False, message="成员不存在"), 404

        name = member["name"]
        db = get_db()
        db.execute(
            "UPDATE members SET father_id = NULL WHERE father_id = ?", (member_id,)
        )
        db.execute(
            "UPDATE members SET mother_id = NULL WHERE mother_id = ?", (member_id,)
        )
        db.execute(
            "UPDATE members SET spouse_id = NULL WHERE spouse_id = ?", (member_id,)
        )
        db.execute("DELETE FROM members WHERE id = ?", (member_id,))
        db.commit()
        return jsonify(success=True, message=f"成员「{name}」已删除")
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route("/api/member/<int:member_id>")
def api_get_member(member_id):
    """获取单个成员信息（用于表单回填）"""
    member = get_member(member_id)
    if member is None:
        return jsonify(success=False, message="成员不存在"), 404
    return jsonify(success=True, data=format_member(member))


@app.route("/search")
def search():
    """搜索成员"""
    keyword = request.args.get("q", "").strip()
    if not keyword:
        return redirect(url_for("index"))
    db = get_db()
    results = db.execute(
        "SELECT * FROM members WHERE name LIKE ? OR note LIKE ? ORDER BY id",
        (f"%{keyword}%", f"%{keyword}%"),
    ).fetchall()
    members = [format_member(m) for m in get_all_members()]
    results = [format_member(r) for r in results]
    return render_template(
        "index.html", members=members, search_results=results, keyword=keyword
    )


if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("族谱记录系统已启动")
    print("访问地址: http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    app.run(debug=True, host="127.0.0.1", port=5000)
