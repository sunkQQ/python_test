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
    """提供族谱树形数据（JSON），供前端渲染树形结构"""
    members = [format_member(m) for m in get_all_members()]
    # 找出所有根节点（没有父亲的成员，作为树的起点）
    root_ids = [m["id"] for m in members if not m["father_id"] and not m["mother_id"]]
    member_map = {m["id"]: m for m in members}

    def build_node(member_id):
        """递归构建子节点"""
        m = member_map.get(member_id)
        if not m:
            return None
        children = [
            build_node(c["id"])
            for c in members
            if c["father_id"] == member_id or c["mother_id"] == member_id
        ]
        # 过滤None
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
