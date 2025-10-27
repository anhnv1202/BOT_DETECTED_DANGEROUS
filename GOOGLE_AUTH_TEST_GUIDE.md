# 🔐 Hướng Dẫn Test Google Authentication

## 📋 Bước 1: Setup Google OAuth Credentials

### 1.1. Tạo Project trên Google Cloud Console

1. Vào [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Vào **APIs & Services** → **Library**
4. Enable **Google+ API** (hoặc Google Identity API)

### 1.2. Tạo OAuth 2.0 Credentials

1. Vào **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Nếu chưa có OAuth consent screen:
   - Chọn **Internal** (cho local testing)
   - Điền App name, User support email
   - Add scope: `email`, `profile`
   - Test users: thêm email của bạn
4. Application type: **Web application**
5. Name: `Dangerous Objects API`
6. **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/auth/google/callback
   ```
7. Click **Create**
8. **Copy Client ID và Client Secret**

### 1.3. Cấu Hình File .env

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Sửa file `.env` và thêm Google credentials:

```bash
GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:8000/api/auth/google/callback"
```

---

## 🧪 Bước 2: Chạy Server

```bash
python run.py --reload
```

Server chạy tại: `http://localhost:8000`

---

## 🚀 Bước 3: Test Google Auth

### Cách 1: Test Bằng Frontend (Khuyên Dùng)

#### Option A: Tạo HTML Test Page

Tạo file `test_google_auth.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Google Auth</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        pre { background: #f4f4f4; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>🔐 Test Google Authentication</h1>
    
    <button onclick="loginWithGoogle()">Sign in with Google</button>
    
    <div id="result"></div>
    
    <script>
        const API_BASE = 'http://localhost:8000';
        const GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID'; // Lấy từ .env
        
        async function loginWithGoogle() {
            try {
                // Step 1: Get authorization code from Google
                const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
                    `client_id=${GOOGLE_CLIENT_ID}&` +
                    `redirect_uri=http://localhost:8000/api/auth/google/callback&` +
                    `response_type=code&` +
                    `scope=email profile`;
                
                const popup = window.open(authUrl, 'Google Login', 'width=500,height=600');
                
                // Wait for popup to send code
                window.addEventListener('message', async (event) => {
                    if (event.origin !== API_BASE) return;
                    
                    const { code } = event.data;
                    if (code) {
                        // Step 2: Send code to backend
                        const response = await fetch(`${API_BASE}/api/auth/google`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ code })
                        });
                        
                        const data = await response.json();
                        
                        document.getElementById('result').innerHTML = 
                            `<h3>✅ Success!</h3><pre>${JSON.stringify(data, null, 2)}</pre>`;
                        
                        // Step 3: Test authenticated endpoint
                        testAuthenticatedAPI(data.access_token);
                    }
                });
                
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    `<h3>❌ Error</h3><pre>${error.message}</pre>`;
            }
        }
        
        async function testAuthenticatedAPI(token) {
            try {
                const response = await fetch(`${API_BASE}/api/auth/me`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const user = await response.json();
                
                document.getElementById('result').innerHTML += 
                    `<h4>👤 Current User:</h4><pre>${JSON.stringify(user, null, 2)}</pre>`;
            } catch (error) {
                console.error('Failed to get user info:', error);
            }
        }
    </script>
</body>
</html>
```

Mở file `test_google_auth.html` trong browser và click **Sign in with Google**.

#### Option B: Dùng Postman

1. Mở Postman
2. **GET**: `https://accounts.google.com/o/oauth2/v2/auth`
   - Params:
     - `client_id`: Your Google Client ID
     - `redirect_uri`: `http://localhost:8000/api/auth/google/callback`
     - `response_type`: `code`
     - `scope`: `email profile`
3. Click **Send** → Browser sẽ mở Google login
4. After login, URL redirect sẽ là: `http://localhost:8000/api/auth/google/callback?code=...`
5. Copy `code` từ URL
6. **POST**: `http://localhost:8000/api/auth/google`
   - Body (JSON):
     ```json
     {
       "code": "paste-code-here"
     }
     ```
7. Click **Send** → Sẽ nhận được `access_token`

---

### Cách 2: Test Bằng cURL (Manual)

#### 2.1. Lấy Authorization Code

Mở browser và truy cập URL này (thay `YOUR_CLIENT_ID`):

```
https://accounts.google.com/o/oauth2/v2/auth?client_id=569715235327-o7kefcrh934pelqg57akn4jnrq63rpi9.apps.googleusercontent.com&redirect_uri=http://localhost:8000/api/auth/google/callback&response_type=code&scope=email+profile
```

Sau khi login, browser sẽ redirect về:
```
http://localhost:8000/api/auth/google/callback?code=4/0AVHEtk4xY...
```

Copy `code` từ URL (sau `code=`).

#### 2.2. Gửi Code Về Backend

```bash
curl -X POST "http://localhost:8000/api/auth/google" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "paste-code-from-step-1-here"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 2.3. Test Authenticated Endpoint

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "email": "your-email@gmail.com",
  "name": "Your Name",
  "avatar": "https://lh3.googleusercontent.com/...",
  "credits": 1000000.0,
  "created_at": "2024-01-01T00:00:00"
}
```

---

## 🐛 Troubleshooting

### ❌ Error: "Google authentication failed"

**Nguyên nhân:**
- Client ID/Secret sai
- Redirect URI không khớp
- Code đã hết hạn

**Giải pháp:**
1. Kiểm tra file `.env` có đúng credentials không
2. Restart server: `python run.py --reload`
3. Lấy authorization code mới (chúng có hạn 10 phút)

### ❌ Error: "Invalid redirect_uri"

**Nguyên nhân:** Redirect URI trong Google Console không khớp với `.env`

**Giải pháp:**
1. Vào [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** → **Credentials** → Click vào OAuth client của bạn
3. Thêm đúng redirect URI: `http://localhost:8000/api/auth/google/callback`
4. Save và đợi 1-2 phút
5. Lấy code mới

### ❌ Error: "redirect_uri_mismatch"

**Nguyên nhân:** URL trong auth request không khớp Google Console

**Giải pháp:**
- Đảm bảo redirect URI trong request giống hệt trong Google Console
- Check trailing slash: nên là `/callback` không phải `/callback/`

### ❌ Error: "access_denied"

**Nguyên nhân:** User từ chối quyền hoặc chưa được add vào test users

**Giải pháp:**
1. Nếu dùng Internal consent screen, phải add email vào **Test users**
2. Vào **OAuth consent screen** → **Test users** → **Add Users**

---

## 📊 Test Flow Hoàn Chỉnh

### Scenario 1: New User

1. User chưa tồn tại trong database
2. Login bằng Google
3. Backend tự động tạo account mới với gói FREE
4. Trả về access_token

### Scenario 2: Existing User

1. User đã đăng ký bằng email/password
2. Login bằng Google (cùng email)
3. Backend tự động link Google account với user hiện tại
4. Update avatar nếu có
5. Trả về access_token

### Scenario 3: User Đã Link Google Trước

1. User đã login bằng Google trước đó
2. Login lại bằng Google
3. Backend tìm user bằng `google_id`
4. Trả về access_token

---

## 🔍 Kiểm Tra Database

```bash
# Xem users trong database
sqlite3 app.db "SELECT id, email, name, google_id FROM users;"

# Xem subscriptions
sqlite3 app.db "SELECT user_id, plan, monthly_quota FROM subscriptions;"
```

---

## 🧪 Automated Testing (Future)

```python
# test_google_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_google_auth():
    # Mock Google OAuth response
    # Test endpoint /api/auth/google
    pass
```

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề, check:

1. ✅ Server đang chạy: `curl http://localhost:8000/health`
2. ✅ Google credentials trong `.env` đúng
3. ✅ Redirect URI trong Google Console khớp
4. ✅ Logs server: check console output
5. ✅ Database có user mới được tạo

---

**License:** MIT

