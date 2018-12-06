## tumblr多线程下载脚本。

### feature：
1. 支持下载多个用户视频
2. 多线程下载
3. 自动去重已失效视频

### 兼容性
 - 兼容Python2.7以上版本
 - windows下的兼容性未测试

### 使用教程
- 安装依赖包：
```pip install requests```

- 修改脚本最后的tumblr用户名列表。
示例：
names=['username1','username2']

- 运行脚本
```python tumblr.py```
