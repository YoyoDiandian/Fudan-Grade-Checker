# Fudan-Grade-Checker

Fudan-Grade-Checker 是一个自动监控复旦大学教务系统成绩变动并通过 PushPlus 微信推送通知的脚本。

## 功能简介
- 自动登录复旦大学教务系统
- 定时检查成绩更新
- 成绩变动时通过 PushPlus 微信推送通知
- 支持自定义检查间隔

## 使用方法

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/FDU-Grade-Checker.git
cd FDU-Grade-Checker
```

### 2. 安装依赖

建议使用 Python 3.7 及以上版本。

```bash
pip install -r requirements.txt
```

如未提供 `requirements.txt`，可手动安装：

```bash
pip install requests beautifulsoup4 python-dotenv
```

### 3. 配置环境变量

在项目根目录下修改 `.env` 文件，内容如示例：

```
USERNAME=2230xxx0abc
PASSWORD=123456
PUSHPLUS_TOKEN=aaaaaaaaaaaaaa
CHECK_INTERVAL=300
```

- `USERNAME`：复旦大学统一身份认证学号
- `PASSWORD`：统一身份认证密码
- `PUSHPLUS_TOKEN`：PushPlus 推送 token（[获取方法](https://www.pushplus.plus/)）
- `CHECK_INTERVAL`：成绩检查间隔，单位为秒，默认为 300 秒（5 分钟）

### 4. 运行脚本

```bash
python fudan_grade_monitor.py
```

脚本会自动定时检查成绩并推送通知。

## 注意事项
- 请勿将 `.env` 文件上传到公共仓库，避免泄露个人信息。
- 本项目仅供学习交流使用，请遵守相关法律法规和学校规定。

## License

MIT License
