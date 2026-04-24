# 输出打印
# print("hello world")

# 多内容输出
# print("名字", "年龄", 20)

# 变量+运算
"""a = 10
b = 20
print("相加结算", a + b)
flag = True
if flag:
    print("是")
else:
    print("否")
name = "张三"
print("姓名", name)
"""

# 运算
""" print("加", a + b)
print("减", a - b)
print("乘", a * b)
print("除", a / b)
print("余", a % b) """

# 字符串
# s1 = "单引号"
# s2 = "双引号"
# s3 = """多行
# 字符串"""
# print(s3)
# print(s1)
# print(s2)
# # 拼接
# print("你好" + "python")

# 输入
# age = input("请输入年龄")
# print("年龄", age)

# 条件判断
""" age = 23
if age >= 18:
    print("成年人")
elif age >= 12:
    print("未成年人")
else:
    print("儿童") """

# for循环
""" for i in range(5):
    print("当前循环次数", i) """

# while循环
""" i = 0
while i < 5:
    print(i)
    i = i + 1 """

# 列表list
""" lit = [1, 2, 3, "dsdfs", 5]
for i in lit:
    print(i)

# 字典dict 键值对
dic = {"name": "小明", "age": 20}
print(dic["name"]) """


# 函数加
""" def add(a, b):
    return a + b """


# 单行注释
"""
多行注释
"""

# 打印1-10之间的偶数
"""for i in range(10):
if i % 2 == 0:
    print(i)"""

# 打印乘法口诀表
""" for i in range(10):
    if i == 0:
        continue
    for j in range(10):
        if j == 0 or i == 0 or i < j:
            continue
        print(j, "*", i, "=", i * j, end="   ")
    print() """

# 字符串反转
""" str = input("请输入一个字符串")
str = str[::-1]
print(str)
 """

# 字典遍历
""" student = {"name": "张三", "age": 20, "gender": "男", "score": 90}
for key in student:
    print(key, student[key]) """


def calc_bmi(height, weight):
    bmi = weight / (height * height)
    return bmi


height = int(input("请输入身高："))
weight = int(input("请输入体重："))
bmi = calc_bmi(height, weight)
print("bmi", bmi)
