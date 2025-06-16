import requests
from bs4 import BeautifulSoup
import hashlib
import time
from dotenv import load_dotenv
import os

load_dotenv()
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
LOGIN_URL = "https://uis.fudan.edu.cn/authserver/login?service=http%3A%2F%2Fjwfw.fudan.edu.cn%2Feams%2Fhome.action"
GRADE_URL = "https://jwfw.fudan.edu.cn/eams/teach/grade/course/person!search.action?semesterId=487&projectType=&projectId="
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))
PUSHPLUS_TOKEN = os.getenv('PUSHPLUS_TOKEN')


def send_message(title, content):
    url = "https://www.pushplus.plus/send/"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "txt",
        "channel": "wechat"
    }

    try:
        resp = requests.post(url, json=data, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"PushPlus消息发送失败: {e}")

def login_and_get_grades():
    session = requests.Session()
    # 1. 先GET登录页，获取隐藏字段
    login_page = session.get(LOGIN_URL)
    if login_page.status_code != 200:
        raise Exception('无法访问登录页')
    soup = BeautifulSoup(login_page.text, 'html.parser')
    lt = soup.find('input', {'name': 'lt'})['value']
    dllt = soup.find('input', {'name': 'dllt'})['value']
    execution = soup.find('input', {'name': 'execution'})['value']
    _eventId = soup.find('input', {'name': '_eventId'})['value']
    rmShown = soup.find('input', {'name': 'rmShown'})['value']
    # 2. 构造登录表单
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'lt': lt,
        'dllt': dllt,
        'execution': execution,
        '_eventId': _eventId,
        'rmShown': rmShown
    }
    # 3. POST登录
    resp = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    if resp.status_code != 200 or '统一身份认证' in resp.text:
        raise Exception('登录失败')
    # 4. 获取成绩页面
    resp = session.get(GRADE_URL)
    if resp.status_code != 200:
        raise Exception('获取成绩页面失败')
    return resp.text

def extract_grades(html):
    soup = BeautifulSoup(html, 'html.parser')
    # 查找 class 为 gridtable 的表格
    grades_table = soup.find('table', {'class': 'gridtable'})
    if not grades_table:
        return ''
    # 提取表格文本内容
    return grades_table.get_text()

def get_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def parse_grades(grades_text):
    # 按行分割并去除空行
    lines = [line.strip() for line in grades_text.split('\n') if line.strip()]
    # 跳过表头，按每8列为一门课
    courses = []
    i = 8  # 跳过表头
    while i + 7 < len(lines):
        course = {
            '学年学期': lines[i],
            '课程代码': lines[i+1],
            '课程序号': lines[i+2],
            '课程名称': lines[i+3],
            '课程类别': lines[i+4],
            '学分': lines[i+5],
            '最终': lines[i+6],
            '绩点': lines[i+7]
        }
        courses.append(course)
        i += 8
    return courses

def check_and_notify(new_courses, old_courses):
    # 只对新增课程做判断
    old_set = set((c['课程代码'], c['课程序号']) for c in old_courses)
    for c in new_courses:
        key = (c['课程代码'], c['课程序号'])
        if key not in old_set:
            grade = c['最终'].strip()
            gp = c['绩点'].strip()
            if grade in ['A', 'A-', 'A+']:
                send_message('Good News', f"课程 {c['课程名称']} 成绩为 {grade} / 绩点 {gp}")
            elif grade == 'B+':
                send_message('Bad News', f"课程 {c['课程名称']} 成绩为 {grade} / 绩点 {gp}")
            elif grade in ['B', 'B-', 'C+', 'C', 'C-', 'D+', 'D-', 'F']:
                send_message('terrible news', f"课程 {c['课程名称']} 成绩为 {grade} / 绩点 {gp}")

def main():
    last_hash = None
    old_courses = []
    while True:
        try:
            html = login_and_get_grades()
            grades_text = extract_grades(html)
            current_hash = get_hash(grades_text)
            new_courses = parse_grades(grades_text)
            if last_hash and current_hash != last_hash:
                check_and_notify(new_courses, old_courses)
            old_courses = new_courses
            last_hash = current_hash
        except Exception as e:
            send_message('成绩监控异常', f'发生异常: {e}')
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()