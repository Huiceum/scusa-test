from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# 你的前端 HTML 頁面，直接用 render_template_string 內嵌，方便示範
html = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>登入頁面</title>
<style>
  body {
    font-family: Arial, sans-serif;
    max-width: 400px;
    margin: 50px auto;
    padding: 1rem;
    border: 1px solid #ccc;
    border-radius: 8px;
  }
  label {
    display: block;
    margin-top: 1rem;
  }
  input[type=text], input[type=password] {
    width: 100%;
    padding: 0.5rem;
    margin-top: 0.3rem;
    box-sizing: border-box;
  }
  button {
    margin-top: 1.5rem;
    width: 100%;
    padding: 0.7rem;
    background-color: #0066cc;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
  }
  #message {
    margin-top: 1rem;
    font-weight: bold;
  }
</style>
</head>
<body>

<h2>登入系統</h2>

<form id="loginForm">
  <label for="userid">學號：</label>
  <input type="text" id="userid" name="userid" required />

  <label for="password">密碼：</label>
  <input type="password" id="password" name="password" required />

  <button type="submit">登入</button>
</form>

<div id="message"></div>

<script>
  const form = document.getElementById('loginForm');
  const messageDiv = document.getElementById('message');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    messageDiv.style.color = 'black';
    messageDiv.textContent = "登入中...";

    const userid = form.userid.value.trim();
    const password = form.password.value;

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ userid, password })
      });

      if (!response.ok) {
        throw new Error('網路錯誤，請稍後再試');
      }

      const data = await response.json();

      if(data.status === "success") {
        messageDiv.style.color = "green";
        messageDiv.textContent = "✅ 登入成功，類型：" + (data.message?.type || "未知");

        if(data.message?.type === "A") {
          setTimeout(() => window.location.href = "index.html", 1500);
        } else {
          setTimeout(() => window.location.href = "student.php", 1500);
        }
      } else {
        messageDiv.style.color = "red";
        messageDiv.textContent = "❌ 登入失敗，請檢查帳號或密碼";
      }

    } catch (error) {
      messageDiv.style.color = "red";
      messageDiv.textContent = "❌ 發生錯誤：" + error.message;
    }
  });
</script>

</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    userid = data.get('userid')
    password = data.get('password')

    url = "https://psv.scu.edu.tw/portal/jsonApi.php"
    payload = {
        "libName": "Login",
        "userid": userid,
        "password": password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": f"連線錯誤: {str(e)}"}), 500

    try:
        data = response.json()
    except Exception:
        return jsonify({"status": "error", "message": "回傳非 JSON 格式"}), 500

    return jsonify(data)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

