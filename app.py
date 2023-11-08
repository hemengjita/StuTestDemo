from flask import Flask, request, jsonify,render_template
import json
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
CORS(app)

# 假设这里使用一个字典来代替数据库，存储用户的作答信息
user_responses = {}

# 从文件加载用户数据
def load_user_data():
    with open('stu.json', 'r') as file:
        return json.load(file)

users = load_user_data()

@app.route("/login", methods=['GET', 'POST'])
@cross_origin()
def login():
    data = request.json
    print("当前登陆用户",data)
    user_id = data.get('ID')
    user_name = data.get('name')

    # 检查用户ID和姓名是否匹配
    for user in users:
        if user['ID'] == user_id and user['name'] == user_name:
            # 初始化用户作答信息
            user_responses[user_id] = {
                "name": user_name,
                "answers": []
            }
            return jsonify({"message": "登录成功"})
    return jsonify({"message": "抱歉，ID或者姓名不正确，请你再仔细检查一下哦！"}), 401

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    data = request.json
    user_id = data.get('ID')
    answer = data.get('answer')
    # 记录用户的作答信息
    if user_id in user_responses:
        user_responses[user_id]['answers'].append(answer)
        # print(f"User {user_id} ({user_responses[user_id]['name']}) submitted the answer: {answer}")
        return jsonify({"message": "作答已记录"})
    return jsonify({"message": "用户未登录"}), 401


@app.route('/save_answers/<user_id>', methods=['POST'])
def save_answers(user_id):
    # 确保有这个ID的用户目录存在
    user_dir = os.path.join(os.getcwd(), 'user_answers', user_id)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    # 文件路径
    answers_file_path = os.path.join(user_dir, 'answers.json')

    # 获取请求中的数据
    new_answers = request.json
    print("当前用户作答记录:",new_answers)

    # 如果已存在答案文件，则读取并更新答案
    if os.path.exists(answers_file_path):
        with open(answers_file_path, 'r', encoding='utf-8') as file:  # 确保读取时使用UTF-8编码
            existing_answers = json.load(file)
        existing_answers.update(new_answers)
        answers_data = existing_answers
    else:
        answers_data = new_answers

    # 保存数据到特定的文件中，保持中文等非ASCII字符的原样输出
    with open(answers_file_path, 'w', encoding='utf-8') as file:  # 确保写入时使用UTF-8编码
        json.dump(answers_data, file, ensure_ascii=False)  # 设置ensure_ascii为False

    return jsonify({'message': '作答记录保存成功'})

#启动test.html页面
@app.route('/')
def index():
    # 渲染 test.html 模板
    return render_template('test.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777,debug=True)

