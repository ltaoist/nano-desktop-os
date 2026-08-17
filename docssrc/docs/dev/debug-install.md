# 安装与分发

将应用目录（`.App` 或 `.py`）复制到 `Data/AppData/` 下即完成安装，重启服务或刷新页面后应用出现在启动器中。`Data/AppData/` 目录下可同时放置多个应用：

```
Data/
└── AppData/
    ├── calc.App/
    │   ├── main.py
    │   ├── index.html
    │   └── static/
    ├── snake.App/
    │   ├── main.py
    │   ├── index.html
    │   └── static/
    ├── myscript.py/
    │   └── myscript.py
    └── ...
```

也可以通过界面上的安装器（📦）上传 ZIP 包，安装器自动解压到 `Data/AppData/`。卸载即删除对应目录，清空应用数据即删除 `Data/AppDataStore/` 下对应数据目录。

分发应用时将应用目录打包为 ZIP 文件即可，ZIP 内根目录为应用目录名（`.App` 或 `.py` 目录）：

```
myapp.App.zip
└── myapp.App/
    ├── main.py
    ├── index.html
    └── static/
        └── ...
```

```
myscript.py.zip
└── myscript.py/
    └── myscript.py
```

---

- [TOB 编程](../tob/) — 前后端互操作的完整 API 参考
- [calc.App 例程](../calc/) · [snake.App 例程](../snake/) — 通过代码学习
