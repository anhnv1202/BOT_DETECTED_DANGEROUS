# 🔧 Fix Lỗi Ngrok - Cần Authtoken

## ❌ Lỗi Bạn Đang Gặp:

```
ERROR: authentication failed: Usage of ngrok requires a verified account and authtoken.
ERROR: Sign up for an account: https://dashboard.ngrok.com/signup
```

**Nguyên nhân:** Ngrok cần đăng ký tài khoản và authtoken để sử dụng (miễn phí).

## ✅ Cách Fix (5 Phút):

### Bước 1: Đăng Ký Ngrok (MIỄN PHÍ)

1. Mở trình duyệt
2. Truy cập: **https://dashboard.ngrok.com/signup**
3. Đăng ký bằng email
4. Xác thực email

### Bước 2: Lấy Authtoken

1. Đăng nhập vào: **https://dashboard.ngrok.com/get-started/your-authtoken**
2. Copy authtoken của bạn (chuỗi dài như: `2abc123xyz...`)

### Bước 3: Cấu Hình Authtoken

Mở terminal/PowerShell và chạy:

```bash
# Thay YOUR_AUTHTOKEN bằng authtoken bạn vừa copy
ngrok config add-authtoken YOUR_AUTHTOKEN
```

**Ví dụ:**
```bash
ngrok config add-authtoken 2abc123xyz456def789ghi012jkl345mno678
```

✅ Nếu thành công, bạn sẽ thấy: `Authtoken saved to configuration file`

### Bước 4: Test Ngrok

```bash
# Chạy thử
ngrok http 8000
```

Nếu không còn lỗi, bạn sẽ thấy output:
```
ngrok

Session Status                online
...
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000
```

## 🚀 Sau Khi Fix Xong:

### 1. Chạy Server của bạn

```bash
# Terminal/PowerShell 1
python run.py --reload
```

### 2. Chạy Ngrok

```bash
# Terminal/PowerShell 2
ngrok http 8000
```

Copy URL hiển thị (ví dụ: `https://abc123.ngrok-free.app`)

### 3. Cập Nhật File `.env`

Mở file `.env` và cập nhật:

```bash
# Thay abc123.ngrok-free.app bằng URL ngrok của bạn
MOMO_IPN_URL="https://abc123.ngrok-free.app/api/payment/momo/ipn"
MOMO_REDIRECT_URL="https://abc123.ngrok-free.app/api/payment/success"
```

### 4. Restart Server

```bash
# Stop server (Ctrl+C) và chạy lại
python run.py --reload
```

### 5. Test IPN Endpoint

Mở trình duyệt: **http://127.0.0.1:4040**

Đây là ngrok dashboard để xem tất cả requests.

## 💡 Tips

### Ngrok Authtoken Chỉ Cần Cấu Hình 1 Lần

Sau khi chạy `ngrok config add-authtoken`, bạn không cần làm lại. Cứ chạy `ngrok http 8000` là được.

### URL Ngrok Thay Đổi Mỗi Lần Chạy

- ⚠️ Mỗi lần chạy ngrok, URL sẽ khác
- ✅ Giữ ngrok chạy liên tục khi test thanh toán
- ✅ Update `.env` mỗi khi restart ngrok

### Ngrok Free Limitations

- ✅ Miễn phí
- ✅ Không giới hạn thời gian
- ⚠️ URL thay đổi mỗi lần
- ⚠️ Có thể chậm hơn (free tier)

## 🆘 Vẫn Còn Lỗi?

1. **Check ngrok đã cài chưa:**
   ```bash
   ngrok version
   ```

2. **Check authtoken đã cấu hình chưa:**
   ```bash
   ngrok config check
   ```

3. **Xem logs:**
   - Ngrok terminal output
   - Ngrok dashboard: http://127.0.0.1:4040

4. **Liên hệ support:**
   - Ngrok docs: https://ngrok.com/docs
   - Ngrok status: https://status.ngrok.com/

## 📚 Tài Liệu Thêm

- [NGROK_SETUP_GUIDE.md](NGROK_SETUP_GUIDE.md) - Hướng dẫn đầy đủ
- [Ngrok Getting Started](https://dashboard.ngrok.com/get-started/setup)

