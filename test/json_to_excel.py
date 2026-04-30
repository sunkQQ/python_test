import json
import pandas as pd


def json_to_excel(json_data, output_file="output.xlsx"):
    """
    将JSON数据转换为Excel格式

    参数:
        json_data: JSON字符串或Python列表/字典
        output_file: 输出的Excel文件名
    """
    # 如果是字符串，解析为Python对象
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # 使用pandas创建DataFrame
    df = pd.DataFrame(data)

    # 导出到Excel文件
    df.to_excel(output_file, index=False, sheet_name="设备信息")
    print(f"成功导出到: {output_file}")


if __name__ == "__main__":
    # 从文件中读取JSON数据
    json_file = r"D:\新乡学院水控.txt"

    with open(json_file, "r", encoding="utf-8") as f:
        json_data = f.read()

    # 转换为Excel
    json_to_excel(json_data, "新乡学院水控设备信息.xlsx")
