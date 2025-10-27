# 🧪 Hướng Dẫn Test Payment MoMo

## 🎯 Tình Huống: Bạn đã có trang thanh toán hiển thị QR Code

### Bước 1: Mở trên Điện Thoại (Khuyên dùng)

1. **Copy URL** từ trang thanh toán
2. **Gửi vào điện thoại** (email, chat, note,...)
3. **Mở trên mobile browser**
4. Sẽ hiển thị trang thanh toán
5. **Chọn "Mở bằng MoMo Test"**
6. Thanh toán

### Bước 2: Quét QR Code

1. **Mở app MoMo Test**
2. **Chọn "Quét mã QR"**
3. **Chụp QR code** từ màn hình desktop (hoặc scan trực tiếp nếu đang ở mobile)
4. **Xác nhận** 10.000₫
5. **Nhập mật khẩu**
6. **Hoàn tất** thanh toán

### Bước 3: Kiểm Tra Kết Quả

Sau khi thanh toán thành công:

```bash
# Kiểm tra credits của user
GET /api/subscription/current
Authorization: Bearer YOUR_TOKEN
```

Response sẽ có:
```json
{
  "plan": "free",
  "credits": 10000,  // ✅ Tiền đã được cộng vào
  "monthly_quota": 100
}
```

## ⚠️ Troubleshooting

### "Không tìm thấy ứng dụng MoMo"
→ Cần cài **MoMo Test** (KHÔNG phải app MoMo chính)

### "OTP không đúng"
→ OTP test luôn là: `0000`

### "Số dư không đủ"
→ Nạp tiền vào ví test:
- Liên kết thẻ test: `9704XXXXXXXXXXXX`
- Nạp tiền test (không phải tiền thật)

### Không nhận được credits sau thanh toán
→ Check:
1. IPN URL có accessible không
2. Logs server có nhận callback không
3. Verify IPN signature

## 📝 Checklist Test

- [ ] Có app MoMo Test
- [ ] Có tài khoản test
- [ ] Đã nạp tiền vào ví test
- [ ] Có trang thanh toán với QR code
- [ ] Đã quét QR code
- [ ] Đã thanh toán thành công
- [ ] Kiểm tra credits được cộng vào

## 🎉 Success!

Nếu credits đã được cộng vào → Payment flow hoạt động đúng! ✅

