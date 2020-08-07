# 中科大健康打卡平台自动打卡脚本

## 使用方法

安装所需要的包：

```shell
pip3 install requests lxml beautifulsoup4 argparse 
```

`data.json` 为 `post` 方法需要使用的数据（也就是之前需要手动提交的数据）文件的路径。

```shell
python3 Autoreport.py data.json
```

这里的 `data.json` 为一个示例。

脚本每 12 小时打卡一次。

## post 数据生成方法

使用 F12 开发者工具抓包之后得到数据，按照 json 格式写入 `data.json` 中。

1. 登录进入 `http://weixine.ustc.edu.cn/2020/`，打开开发者工具（Chrome 可以使用 F12 快捷键），选中 Network 窗口：

![](./imgs/1.png)

2. 点击确认上报，点击抓到的 `daliy_report` 请求，在 `Headers` 下面找到 `Form Data` 这就是每次上报提交的信息参数。

![](./imgs/2.png)

3. 将找到的 Data 除 `_token` （每次都会改变，所以不需要复制，脚本中会每次获取新的 token 并添加到要提交的数据中）外都复制下来，存放在 `data.json` 中，并参考示例文件转换为对应的格式。

4. 尝试运行脚本。

## 另外的接口

提供了 `send_mail` 接口，可以用于每次打卡提交之后向指定邮箱发送打卡结果，可以自己将接口做修改之后在 `report` 中调用。

`send_mail` 使用的是第三方的 `smtp` 服务，需要输入第三方邮件服务的授权码。

可以参考对应邮箱的教程（例如：[QQ邮箱](https://service.mail.qq.com/cgi-bin/help?subtype=1&no=166&id=28)）开启服务，并在脚本中添加对应的邮箱，尝试运行。
