# Nano Desktop OS

![](docssrc\assets\login.png)
![](docssrc\assets\pane.png)
![](docssrc\assets\calc.png)
![](docssrc\assets\snake.png)


## 启动

```
python src\background\launch.py
```

访问 `http://localhost:5173` 。

登陆凭证：账户密码都是 `admin` 。

## app 开发

参考 [Data\AppData\calc.App](Data\AppData\calc.App) 和 [Data\AppData\snake.App](Data\AppData\snake.App)

## 核心观念

* 通过python实现后端，通过JavaScript实现前端，通过线程对象代理（Thread Objects Broker）实现对象的互操作。
* 支持弹性的对象的注册、命名、发现、调用、遗忘等。
* 通过封装web socket提供互操作性。
* 基于不同环境的对象的互操作而不是消息传递/事件驱动。

## 更多资料

参考 [资料.md](资料.md) 。

也可以使用AI对代码进行分析。
