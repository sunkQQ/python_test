1、先安装打包工具（首次需要）
```bash
pip install pyinstaller
```

2、打包
```bash
pyinstaller -F -w notepad.py
```
-F 打包成单独一个 exe 文件
-w 运行不弹出黑色命令黑窗口

3、找到 exe
打包完成后，文件夹里多出一个 dist
打开 dist，里面就是 记事本.exe

4、beautifulsoup4 是一个解析 html 文档的库 （首次需要）
```bash
pip install requests beautifulsoup4
```

5、pandas 是一个数据处理库，openpyxl 是一个 Excel 操作库 （首次需要）
```bash
pip install pandas openpyxl
```