## Loc新注册用户邀请人爬取脚本

运行前准备：

1. 安装依赖
```
pip install requests pymysql
```

2. 创建一个编码为`utf8mb4`的mysql数据库。
  - **推荐宝塔直接操作**

3. 修改脚本
  - 修改脚本`pymysql.connect`这一行的配置，为你刚才创建的数据库配置。

4. 运行：
```
python loc_reg.py
```
