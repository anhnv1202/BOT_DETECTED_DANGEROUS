# 🧪 Hướng Dẫn Test Thanh Toán MoMo

## 📱 Bước 1: Tải Ứng Dụng MoMo Test

### Android:
- Tải file APK từ: [developers.momo.vn](https://developers.momo.vn/)
- Hoặc search "MoMo Test" trên Play Store

### iOS:
- Search "MoMo Test" trên App Store
- Hoặc xin link từ MoMo support

**⚠️ Lưu ý:** Nếu đã cài MoMo bản chính thức, phải gỡ trước khi cài bản Test!

## 📝 Bước 2: Tạo Tài Khoản Test

1. **Mở app MoMo Test**
2. **Nhập số điện thoại:** 
   - Dùng số điện thoại bất kỳ (10 chữ số)
   - VD: `0912345678`
3. **Nhập OTP:** 
   - Mã mặc định: `0000` hoặc `000000`
4. **Tạo mật khẩu:** 
   - 6 chữ số bất kỳ
5. **Nhập thông tin:**
   - Họ và tên (có khoảng trắng): `Nguyen Van A`
   - Email: `test@example.com`
   - Giới tính: Chọn bất kỳ
   - Quốc gia: **Việt Nam**

✅ Bạn đã có tài khoản test!

## 💳 Bước 3: Nạp Tiền Vào Ví Test

### 3.1. Liên Kết Ngân Hàng Test

1. **Vào Menu:** "Ví của tôi" → "Liên kết tài khoản"
2. **Chọn ngân hàng:** VD: Agribank
3. **Nhập thông tin thẻ ATM:**
   - **Số thẻ:** `9704XXXXXXXXXXXX` (16 chữ số)
     - 9704 là prefix bắt buộc
     - 12 chữ số còn lại: bất kỳ
     - VD: `9704123456789012`
   - **Họ tên chủ thẻ:** Tên bất kỳ
   - **Ngày phát hành:** Chọn bất kỳ

### 3.2. Nạp Tiền

1. **Tại màn hình chính:** Chọn "Nạp tiền"
2. **Nhập số tiền:** VD: 1,000,000 VNĐ
3. **Nhập mật khẩu:** Mật khẩu đã tạo
4. **Nhập OTP (nếu có):** `0000`
5. **Hoàn tất:** Tiền sẽ có trong ví test

⚠️ **Lưu ý:** 
- Trong 24h đầu có thể bị hạn chế số dư
- Nếu lỗi, đóng app và mở lại
- Tiền test KHÔNG phải tiền thật!

## 🎯 Bước 4: Test Thanh Toán Từ API

### 4.1. Tạo Request Topup

**API:** `POST /api/payment/topup`

```bash
curl -X POST "https://bot-detected.cersc.site/api/payment/topup" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":10000}'
```

**Response:**
```json
{
  "pay_url": "https://test-payment.momo.vn/v2/gateway/pay?t=...",
  "request_id": "REQ_...",
  "qr_code_url": null
}
```

### 4.2. Thanh Toán Bằng MoMo Test

**Cách 1: Mở URL trên Mobile**
1. Copy `pay_url` từ response
2. Mở trên điện thoại (có app MoMo Test)
3. Chọn **"Mở bằng MoMo"**
4. Xác nhận thanh toán

**Cách 2: Quét QR Code** (nếu có)
1. Mở `qr_code_url`
2. Chụp ảnh QR code
3. Mở bằng MoMo Test
4. Xác nhận thanh toán

### 4.3. Kiểm Tra Kết Quả

Sau khi thanh toán thành công:

1. **MoMo sẽ gọi IPN:** 
   - URL: `https://bot-detected.cersc.site/api/payment/momo/ipn`
   - Server xử lý callback

2. **User được redirect:** 
   - URL: `https://bot-detected.cersc.site/payment/success`
   - (Nếu có frontend)

3. **Tiền được cộng vào ví credits:**
   - Check: `GET /api/subscription/current`
   - Số tiền trong `credits` sẽ tăng

## 🔍 Bước 5: Verify IPN Callback

### Kiểm Tra Transaction

```bash
# Check transaction history (cần implement endpoint này)
curl -X GET "https://bot-detected.cersc.site/api/transactions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Kiểm Tra Credits

```bash
curl -X GET "https://bot-detected.cersc.site/api/subscription/current" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## ⚠️ Troubleshooting

### Lỗi "Không tìm thấy ứng dụng MoMo"
- ✅ Cần cài app MoMo Test (KHÔNG phải app chính)
- ✅ Uninstall app MoMo chính nếu có
- ✅ Reinstall MoMo Test

### Lỗi "OTP không đúng"
- ✅ OTP test luôn là: `0000` hoặc `000000`
- ✅ Nhập lại nếu sai

### Không nhận được tiền sau thanh toán
- ✅ Check ngrok đang chạy (`ngrok http 8000`)
- ✅ Check IPN URL trong `.env` đúng với ngrok URL hiện tại
- ✅ Xem ngrok web interface: `http://127.0.0.1:4040` để kiểm tra requests
- ✅ Check logs server xem có nhận callback
- ✅ Verify signature của IPN

### "Xác thực doanh nghiệp thất bại" (resultCode 13)
- ✅ Đã sửa trong code
- ✅ Check credentials trong `.env`

## 📚 Tài Liệu Tham Khảo

- [Ngrok Setup Guide](NGROK_SETUP_GUIDE.md) - Hướng dẫn chi tiết setup ngrok
- [MoMo Developers Portal](https://developers.momo.vn/)
- [Test Instructions](https://developers.momo.vn/v3/vi/docs/payment/onboarding/test-instructions/)
- [API Documentation](https://developers.momo.vn/v3/vi/docs/payment/api/wallet/onetime)

## 🎉 Kết Luận

Với tài khoản MoMo test, bạn có thể:
- ✅ Test toàn bộ luồng thanh toán
- ✅ Test IPN callback
- ✅ Verify credits được cộng vào ví
- ✅ Test các tính năng khác mà không cần tiền thật

**Lưu ý:** MoMo Test chỉ hoạt động trong môi trường test (`test-payment.momo.vn`), không thể thanh toán thật!

