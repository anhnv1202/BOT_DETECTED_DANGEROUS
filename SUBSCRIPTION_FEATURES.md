# 📱 Tính Năng Subscription - Cơ Chế Mới

## ✅ Các Tính Năng Mới

### 1. Prevent Purchasing Same Plan
**Không cho mua lại gói đang dùng (kể cả khi đã CANCELLED)**

- ✅ Nếu đang dùng PLUS → Không cho purchase PLUS
- ✅ Nếu đang dùng PRO → Không cho purchase PRO
- ✅ Nếu đã CANCELLED nhưng vẫn còn hạn → Không cho purchase lại
- ✅ User phải chờ hết hạn hoặc upgrade lên gói cao hơn

**Error Messages:**

Khi đang ACTIVE:
```json
{
  "detail": "You are already on the PLUS plan. No need to purchase again."
}
```

Khi đã CANCELLED nhưng còn hạn:
```json
{
  "detail": "You cancelled your PRO subscription, but you can still use it until it expires. No need to purchase again."
}
```

### 2. Prevent Downgrade
**Không cho down về gói thấp hơn**

- ❌ Không cho từ PRO → PLUS
- ❌ Không cho từ PRO → FREE
- ❌ Không cho từ PLUS → FREE
- ✅ Chỉ cho upgrade: FREE → PLUS → PRO
- ✅ Chỉ có Cancel để về FREE

**Error Message:**
```json
{
  "detail": "Cannot downgrade from PRO to PLUS. You can only upgrade or cancel your current subscription."
}
```

### 3. Cancel Subscription Endpoint
**Hủy gói - User vẫn dùng đến hết hạn**

**Endpoint:** `POST /api/subscription/cancel`

**Request:**
```bash
curl -X POST "https://api.example.com/api/subscription/cancel" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (Same subscription, status = CANCELLED):**
```json
{
  "id": 123,
  "user_id": 1,
  "plan": "pro",
  "status": "cancelled",
  "monthly_quota": 999999,
  "used_quota": 450,
  "expires_at": "2024-02-01T12:00:00Z"
}
```

**Lưu ý:**
- ✅ User **VẪN DÙNG** gói đến khi expires_at
- ✅ Status chuyển thành CANCELLED
- ✅ Không deduct credits hoặc refund
- ✅ Khi hết hạn → Tự động downgrade to FREE
- ❌ Không thể cancel FREE plan

### 4. Auto-Renewal Check
**Tự động kiểm tra và expire subscription**

- ✅ Tự động expire khi hết hạn
- ✅ Chuyển về FREE khi truy cập lại
- ✅ Sử dụng `check_and_renew()` để kiểm tra

## 📋 Flow Mua Gói

### Case 1: User chưa có subscription
```
FREE → Purchase PLUS ✅
FREE → Purchase PRO ✅
```

### Case 2: User đang có PLUS
```
PLUS → Purchase PLUS ❌ (Error: Already on PLUS)
PLUS → Purchase PRO ✅ (Upgrade)
PLUS → Cancel → FREE ✅
```

### Case 3: User đang có PRO
```
PRO → Purchase PLUS ❌ (Error: Cannot downgrade)
PRO → Purchase PRO ❌ (Error: Already on PRO)
PRO → Cancel → FREE ✅
```

## 🎯 Use Cases

### Use Case 1: User muốn upgrade
```bash
# Hiện tại đang FREE
POST /api/subscription/purchase {"plan": "plus"}  ✅

# Hiện tại đang PLUS  
POST /api/subscription/purchase {"plan": "pro"}   ✅
```

### Use Case 2: User đang dùng PRO muốn hủy
```bash
# Cancel - User vẫn dùng PRO đến hết hạn
POST /api/subscription/cancel   ✅

# Response: Status = CANCELLED, expires_at vẫn còn
# User tiếp tục dùng PRO features cho đến expires_at
# Khi hết hạn → Tự động về FREE
```

### Use Case 3: Prevent duplicate purchase
```bash
# User đang dùng PLUS (ACTIVE)
POST /api/subscription/purchase {"plan": "plus"}

# Response: 400 Bad Request
# "You are already on the PLUS plan. No need to purchase again."
```

### Use Case 3b: Prevent purchase when CANCELLED but still active
```bash
# User đã cancel PLUS nhưng vẫn còn hạn đến 2024-02-01
POST /api/subscription/purchase {"plan": "plus"}

# Response: 400 Bad Request
# "You cancelled your PLUS subscription, but you can still use it until it expires. No need to purchase again."
```

### Use Case 4: Prevent downgrade
```bash
# User đang dùng PRO
POST /api/subscription/purchase {"plan": "plus"}

# Response: 400 Bad Request  
# "Cannot downgrade from PRO to PLUS. You can only upgrade or cancel your current subscription."
```

## 🔄 Auto-Renewal Logic

Hiện tại, cơ chế auto-renewal hoạt động như sau:

### Khi Subscription Hết Hạn

1. **User truy cập API** → `get_active_subscription()` được gọi
2. **Check expires_at** → Nếu < datetime.utcnow()
3. **Auto-downgrade to FREE** → Tự động tạo subscription FREE mới
4. **Reset quota** → Quota được set về FREE quota

### Custom Auto-Renewal (Để Implement)

Bạn có thể implement true auto-renewal bằng:

```python
# Thêm field auto_renew vào Subscription model
auto_renew = Column(Boolean, default=False)

# Callback khi subscription sắp hết hạn
def should_auto_renew(subscription):
    return (subscription.auto_renew and 
            subscription.expires_at - timedelta(days=7) < datetime.utcnow())
```

## 🛠️ Implementation Details

### Code Changes

**File: `app/services/subscription_service.py`**

1. ✅ Added plan hierarchy check
2. ✅ Prevent purchasing same plan
3. ✅ Prevent downgrade
4. ✅ Added `cancel_subscription()` method
5. ✅ Added `check_and_renew()` method

**File: `app/controllers/subscription_controller.py`**

1. ✅ Added `POST /api/subscription/cancel` endpoint
2. ✅ Updated error handling

## 📊 Subscription Matrix

| Current Plan | Purchase FREE | Purchase PLUS | Purchase PRO | Cancel |
|--------------|---------------|---------------|--------------|--------|
| FREE         | ❌ Same       | ✅ Upgrade     | ✅ Upgrade    | ❌      |
| PLUS         | ❌ Downgrade  | ❌ Same        | ✅ Upgrade    | ✅      |
| PRO          | ❌ Downgrade  | ❌ Downgrade   | ❌ Same       | ✅      |

## 🎓 Best Practices

### 1. Always Check Current Subscription Before Purchase
```python
current = subscription_service.get_active_subscription(user_id)
if current and current.plan == target_plan:
    # Show message: "You are already on this plan"
```

### 2. Show Upgrade Options Based on Current Plan
```python
# Frontend logic
if current_plan == "free":
    show_plans = ["plus", "pro"]
elif current_plan == "plus":
    show_plans = ["pro"]  # Only upgrade
else:
    show_plans = []  # Only cancel option
```

### 3. Handle Errors Properly
```python
try:
    subscription = subscription_service.purchase_plan(user_id, plan)
    return {"success": True, "subscription": subscription}
except ValueError as e:
    return {"success": False, "error": str(e)}
```

## 🚀 Testing

### Test Scenarios

1. **Test Upgrade**
```bash
# 1. User đăng ký FREE
# 2. Purchase PLUS ✅
# 3. Purchase PRO ✅
```

2. **Test Duplicate Purchase**
```bash
# 1. User đã có PLUS
# 2. Try purchase PLUS again ❌
# Expected: Error "already on PLUS"
```

3. **Test Downgrade Prevention**
```bash
# 1. User đã có PRO
# 2. Try purchase PLUS ❌
# Expected: Error "cannot downgrade"
```

4. **Test Cancel**
```bash
# 1. User đã có PRO (expires_at: 2024-02-01)
# 2. Cancel subscription ✅
# Expected: 
#   - Status = CANCELLED
#   - Plan = PRO (vẫn còn)
#   - Expires_at = 2024-02-01 (vẫn dùng đến hết)
# 3. Khi đạt 2024-02-01:
#   - Tự động downgrade to FREE
#   - Status = ACTIVE
#   - Plan = FREE
```

5. **Test Cancel FREE**
```bash
# 1. User đang FREE
# 2. Try cancel ❌
# Expected: Error "cannot cancel FREE"
```

## 📝 Summary

✅ **Prevent duplicate purchase** - Không cho mua lại gói đang dùng
✅ **Prevent downgrade** - Chỉ cho upgrade
✅ **Cancel endpoint** - Hủy và về FREE
✅ **Auto-expire** - Tự động expire khi hết hạn
✅ **Hierarchy** - FREE → PLUS → PRO

Auto-renewal full sẽ cần implement thêm logic recurring payment với MoMo API.

