# ⚡ Quick Test Guide - MoMo Payment

## 🎯 Tình Huống Của Bạn

Bạn có:
- ✅ Partner Code: `MOMORLHW20251010`
- ✅ Environment: Test (Sandbox)

## 📱 Bước 1: Cài App MoMo Test

### Android:
```
Link: [Từ developers.momo.vn]
Search: "MoMo Test" trên Play Store
```

⚠️ **Gỡ app MoMo chính nếu có!**

### iOS:
```
Search: "MoMo Test" trên App Store
```

## 📝 Bước 2: Đăng Ký Ví Test

1. Mở app MoMo Test
2. Nhập số điện thoại test:
   ```
   Số điện thoại: 0912345678
   ```
3. Nhập OTP:
   ```
   OTP: 0000
   ```
4. Tạo mật khẩu:
   ```
   Mật khẩu: 000000
   ```
5. Điền thông tin:
   - Họ tên: `Nguyen Van A`
   - Email: `test@example.com`
   - Quốc gia: **Việt Nam**

## 💰 Bước 3: Nạp Tiền Test

### Liên Kết Ngân Hàng Test

1. Vào **"Ví của tôi"** → **"Liên kết tài khoản"**
2. Chọn ngân hàng: **Agribank**
3. Nhập thông tin:

```
Số thẻ ATM: 9704123456789012
Họ tên: Nguyen Van A
Ngày phát hành: [Chọn bất kỳ]
```

**Lưu ý:** Số thẻ phải bắt đầu bằng `9704` + 12 số bất kỳ

### Nạp Tiền

1. Vào **"Nạp tiền"**
2. Nhập số tiền: `1,000,000 VNĐ` (test)
3. Nhập mật khẩu: `000000`
4. OTP (nếu có): `0000`

✅ Bạn có 1,000,000 VNĐ trong ví test

## 🧪 Bước 4: Test Thanh Toán

### 4.1. Tạo Payment Request

```bash
POST https://bot-detected.cersc.site/api/payment/topup
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "amount": 10000
}
```

**Response:**
```json
{
  "pay_url": "https://test-payment.momo.vn/v2/gateway/pay?t=...",
  "request_id": "REQ_..."
}
```

### 4.2. Thanh Toán

**Cách 1: Quét QR (Màn hình desktop)**
1. Mở app MoMo Test
2. Chọn **"Quét mã QR"**
3. Chụp QR code từ màn hình
4. Xác nhận thanh toán

**Cách 2: Mở URL (Mobile)**
1. Copy `pay_url` và mở trên điện thoại
2. Chọn **"Mở bằng MoMo Test"**
3. Xác nhận thanh toán

### 4.3. Verify Credits

```bash
GET https://bot-detected.cersc.site/api/subscription/current
Authorization: Bearer YOUR_TOKEN
```

✅ Credits đã được cộng vào!

## ✅ Checklist

- [ ] Có app MoMo Test
- [ ] Đã đăng ký ví với SĐT: 0912345678
- [ ] Đã nạp tiền test vào ví
- [ ] Có `pay_url` từ API
- [ ] Đã quét QR / mở link
- [ ] Đã thanh toán thành công
- [ ] Credits được cộng vào

## 🎉 Success!

Nếu đến đây mà credits đã tăng → Payment flow hoạt động đúng! 🚀

## 📞 Troubleshooting

### "Không tìm thấy ứng dụng MoMo"
→ Cần cài **MoMo Test** (không phải app chính)

### "OTP không đúng"
→ OTP luôn là: `0000` hoặc `000000`

### "Số dư không đủ"
→ Nạp tiền test vào ví

### "resultCode 13"
→ Check credentials trong `.env`

### Không nhận được credits
→ Check IPN URL và logs server

