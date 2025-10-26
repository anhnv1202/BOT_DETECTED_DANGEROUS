# API Nhận Diện Vật Thể Nguy Hiểm - Hệ Thống SaaS Production

Hệ thống API FastAPI hoàn chỉnh để phát hiện vật thể nguy hiểm bằng MobileNetV2, tích hợp đầy đủ xác thực, thanh toán MoMo và quản lý gói subscription.

## 🎯 Tính Năng

- **Xác Thực Người Dùng**
  - Đăng ký/đăng nhập bằng Email/Password
  - Đăng nhập bằng Google OAuth
  - Xác thực bằng JWT token

- **Tích Hợp Thanh Toán**
  - Thanh toán MoMo QR code
  - Hệ thống ví credits nội bộ
  - Lịch sử giao dịch

- **Các Gói Subscription**
  - **Free**: 100 lượt/tháng
  - **Plus**: 5,000 lượt/tháng (99,000 VNĐ)
  - **Pro**: Không giới hạn (299,000 VNĐ)

- **API Nhận Diện AI**
  - Phân loại đa nhãn bằng MobileNetV2
  - Bảo vệ bằng xác thực & quota
  - Theo dõi usage và thống kê

## 🏗️ Kiến Trúc

Kiến trúc 3 tầng chuẩn:
- **Controller**: API endpoints (FastAPI routes)
- **Service**: Business logic (Auth, Payment, Subscription, ML)
- **Repository**: Truy cập database (SQLAlchemy ORM)

Database: SQLite (có thể đổi sang PostgreSQL dễ dàng)

## 📦 Cài Đặt

### Chạy Local (Development)

```bash
# Clone repository
git clone <your-repo-url>
cd Model_XDynamic

# Tạo virtual environment
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows Git Bash: source .venv/Scripts/activate
# Linux/Mac: source .venv/bin/activate

# Cài dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Setup file cấu hình
cp .env.example .env
# Sửa file .env với config của bạn (xem phần Cấu Hình bên dưới)

# Chạy server (dễ nhất)
python run.py --reload

# Hoặc dùng uvicorn trực tiếp
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Các lệnh chạy server:**
```bash
# Development (auto-reload khi code thay đổi)
python run.py --reload

# Production (1 worker)
python run.py --host 0.0.0.0 --port 8000

# Production (multiple workers)
python run.py --host 0.0.0.0 --port 8000 --workers 4

# Chạy trên port khác
python run.py --port 3000

# Chỉ khởi tạo database
python run.py --init-db

# Xem tất cả options
python run.py --help
```

Truy cập: http://localhost:8000/docs để xem Swagger UI

### Chạy Bằng Docker

```bash
# Build image
docker build -t dangerous-objects-api:latest .

# Chạy container
docker run --rm -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  dangerous-objects-api:latest
```

## 🔑 Cấu Hình

### Các Bước Cần Thiết

1. **JWT Secret**: Tạo key bảo mật
   ```bash
   openssl rand -hex 32
   ```
   Copy kết quả vào `JWT_SECRET_KEY` trong file `.env`

2. **Google OAuth** (tùy chọn): 
   - Vào [Google Cloud Console](https://console.cloud.google.com/)
   - Tạo OAuth 2.0 credentials
   - Thêm Authorized redirect URI: `http://localhost:8000/api/auth/google/callback`
   - Copy Client ID và Client Secret vào `.env`

3. **Thanh Toán MoMo**:
   - Đăng ký tài khoản business tại [MoMo Business](https://business.momo.vn/)
   - Liên hệ MoMo để lấy Partner Code, Access Key, Secret Key
   - Để test: Dùng credentials môi trường test của MoMo
   - **Quan trọng**: IPN URL phải là domain công khai (dùng ngrok nếu test local)
     ```bash
     # Ví dụ dùng ngrok
     ngrok http 8000
     # Copy HTTPS URL vào MOMO_IPN_URL trong .env
     ```

Cập nhật tất cả thông tin vào file `.env` (copy từ `.env.example`)

## 📡 API Endpoints

### Xác Thực (Authentication)
- `POST /api/auth/register` - Đăng ký bằng email/password
- `POST /api/auth/login` - Đăng nhập bằng email/password
- `POST /api/auth/google` - Đăng nhập bằng Google OAuth
- `GET /api/auth/me` - Lấy thông tin user hiện tại (cần auth)

### Thanh Toán (Payment)
- `POST /api/payment/topup` - Tạo link thanh toán MoMo (cần auth)
- `POST /api/payment/momo/ipn` - Webhook callback từ MoMo (internal)

### Gói Subscription
- `GET /api/subscription/current` - Lấy gói đang dùng (cần auth)
- `POST /api/subscription/purchase` - Mua gói Plus/Pro (cần auth)

### Nhận Diện AI (Prediction)
- `POST /api/v1/predict` - Nhận diện vật thể nguy hiểm (cần auth + quota)

### Public
- `GET /` - Thông tin API
- `GET /health` - Health check
- `GET /docs` - Swagger UI (tài liệu tương tác)

## 🧪 Hướng Dẫn Test API

### Bước 1: Đăng Ký User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"matkhau123","name":"Nguyen Van A"}'
```

**Response:**
```json
{"access_token":"eyJhbGci...","token_type":"bearer"}
```

Lưu `access_token` để dùng cho các bước sau.

### Bước 2: Kiểm Tra Gói Đang Dùng
```bash
curl -X GET "http://localhost:8000/api/subscription/current" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** Gói FREE với 100 lượt/tháng

### Bước 3: Nạp Tiền Vào Ví
```bash
curl -X POST "http://localhost:8000/api/payment/topup" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":100000}'
```

**Response:** Nhận được `pay_url` - mở link trong browser để quét MoMo QR.

Sau khi thanh toán thành công, tiền sẽ tự động cộng vào ví.

### Bước 4: Mua Gói Plus/Pro
```bash
curl -X POST "http://localhost:8000/api/subscription/purchase" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan":"plus"}'
```

Hệ thống sẽ trừ 99,000 VNĐ từ ví và nâng cấp lên gói Plus (5,000 lượt/tháng).

### Bước 5: Nhận Diện Ảnh
```bash
curl -X POST "http://localhost:8000/api/v1/predict?threshold=0.5" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/anh_cua_ban.jpg"
```

**Response:**
```json
{
  "classes": ["0", "1", "2", "3"],
  "probabilities": [0.12, 0.85, 0.23, 0.05],
  "active": ["1"],
  "quota_remaining": 4999
}
```

## 🚀 Deploy Production

### Triển Khai Lên AWS ECS/Fargate
1. Push image lên Amazon ECR
2. Tạo Task Definition (1 vCPU, 2GB RAM)
3. Tạo Service với Application Load Balancer
4. Cấu hình biến môi trường từ `.env`
5. Bật auto-scaling theo CPU/Memory

### Triển Khai Lên Google Cloud Run
```bash
# Build và push image
gcloud builds submit --tag gcr.io/PROJECT_ID/dangerous-objects-api

# Deploy
gcloud run deploy dangerous-objects-api \
  --image gcr.io/PROJECT_ID/dangerous-objects-api \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1
```

### Triển Khai Lên Heroku
```bash
heroku create ten-app-cua-ban
heroku stack:set container
git push heroku main
```

### Triển Khai Lên DigitalOcean Droplet (Chi Tiết)

#### 1. Tạo Droplet
- Vào DigitalOcean → Create → Droplets
- **Image**: Ubuntu 22.04 LTS
- **Plan**: Basic 2GB RAM, 1 vCPU ($12/tháng) hoặc 4GB RAM ($24/tháng)
- **Datacenter**: Singapore (gần VN)
- **Authentication**: SSH Key
- **Hostname**: `dangerous-objects-api`

#### 2. Kết Nối và Setup Server

```bash
# SSH vào server
ssh root@YOUR_DROPLET_IP

# Update system
apt update && apt upgrade -y

# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Cài Docker Compose
apt install docker-compose -y

# Tạo user non-root (best practice security)
adduser deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# Switch sang user deploy
su - deploy
```

#### 3. Upload Code Lên Server

**Cách 1: Dùng Git (Khuyến nghị)**
```bash
# Trên server (đã login user deploy)
cd ~
git clone https://github.com/your-username/Model_XDynamic.git
cd Model_XDynamic
```

**Cách 2: Upload từ máy local bằng SCP**
```bash
# Trên máy local (Linux/Mac/Git Bash)
cd /path/to/Model_XDynamic
scp -r ./* deploy@YOUR_DROPLET_IP:~/Model_XDynamic/

# Windows PowerShell
scp -r * deploy@YOUR_DROPLET_IP:~/Model_XDynamic/
```

#### 4. Cấu Hình Environment

```bash
# Tạo file .env
cd ~/Model_XDynamic
nano .env
```

Paste nội dung (nhớ thay YOUR_* bằng giá trị thực):
```bash
APP_NAME="Dangerous Objects AI API"
APP_VERSION="2.0.0"
DEBUG=false

DATABASE_URL="sqlite:///./app.db"

# Tạo JWT secret: python3 -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY="YOUR_64_CHAR_RANDOM_STRING"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080

GOOGLE_CLIENT_ID=""
GOOGLE_CLIENT_SECRET=""
GOOGLE_REDIRECT_URI="https://your-domain.com/api/auth/google/callback"

MOMO_PARTNER_CODE="YOUR_MOMO_PARTNER_CODE"
MOMO_ACCESS_KEY="YOUR_MOMO_ACCESS_KEY"
MOMO_SECRET_KEY="YOUR_MOMO_SECRET_KEY"
MOMO_ENDPOINT="https://payment.momo.vn/v2/gateway/api/create"
MOMO_REDIRECT_URL="https://your-domain.com/payment/success"
MOMO_IPN_URL="https://your-domain.com/api/payment/momo/ipn"

MODEL_PATH="mobilenetv2_dangerous_objects.pth"
MODEL_IMG_SIZE=224

PLAN_FREE_MONTHLY_QUOTA=100
PLAN_PLUS_MONTHLY_QUOTA=5000
PLAN_PRO_MONTHLY_QUOTA=999999
PLAN_PLUS_PRICE=99000
PLAN_PRO_PRICE=299000
```

Lưu: `Ctrl+O` → Enter → `Ctrl+X`

#### 5. Tạo Docker Compose File

```bash
# Tạo docker-compose.yml
nano docker-compose.yml
```

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: dangerous-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    env_file:
      - .env
    environment:
      - PYTHONUNBUFFERED=1
```

Lưu file: `Ctrl+O` → Enter → `Ctrl+X`

#### 6. Build và Chạy

```bash
# Build và chạy container
docker-compose up -d

# Xem logs
docker-compose logs -f

# Kiểm tra container
docker ps

# Test API (trong server)
curl http://localhost:8000/health
```

#### 7. Setup Nginx Reverse Proxy

```bash
# Cài Nginx
sudo apt install nginx -y

# Tạo config file
sudo nano /etc/nginx/sites-available/dangerous-api
```

Paste config này:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/dangerous-api /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### 8. Setup SSL/HTTPS với Let's Encrypt

```bash
# Cài Certbot
sudo apt install certbot python3-certbot-nginx -y

# Tự động setup SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Làm theo hướng dẫn:
# - Nhập email
# - Agree to terms: Y
# - Redirect HTTP to HTTPS: 2 (Yes)

# Test auto-renewal
sudo certbot renew --dry-run
```

#### 9. Setup Firewall (UFW)

```bash
# Enable firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Check status
sudo ufw status verbose
```

#### 10. Setup Domain DNS

Tại nhà cung cấp domain (GoDaddy, Cloudflare, etc.):
- **Type**: A Record
- **Name**: `@` (hoặc subdomain như `api`)
- **Value**: `YOUR_DROPLET_IP`
- **TTL**: 3600

Đợi 5-30 phút để DNS propagate.

#### 11. Test Production API

```bash
# Health check
curl https://your-domain.com/health

# Đăng ký user
curl -X POST "https://your-domain.com/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'

# Xem Swagger docs
# https://your-domain.com/docs
```

---

### 🔄 Update Code Trên Production

```bash
# SSH vào server
ssh deploy@YOUR_DROPLET_IP
cd ~/Model_XDynamic

# Pull code mới từ Git
git pull origin main

# Rebuild và restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Xem logs
docker-compose logs -f
```

---

### 📊 Monitoring & Logs

```bash
# Xem logs realtime
docker-compose logs -f

# Xem logs 100 dòng cuối
docker-compose logs --tail=100

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Kiểm tra CPU/RAM
htop

# Kiểm tra disk space
df -h

# Docker resource usage
docker stats
```

---

### 🔧 Các Lệnh Hữu Ích

```bash
# Restart API
docker-compose restart

# Stop API
docker-compose down

# Xem tất cả containers
docker ps -a

# Xóa container cũ
docker system prune -a

# Backup database
docker exec dangerous-api cp /app/app.db /app/data/backup_$(date +%Y%m%d).db

# Tải backup về máy local
scp deploy@YOUR_DROPLET_IP:~/Model_XDynamic/data/backup_*.db ./

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx status
sudo systemctl status nginx

# Reload Nginx config (không downtime)
sudo nginx -s reload
```

---

### 🚨 Troubleshooting

**API không start:**
```bash
docker-compose logs api
docker ps -a
```

**Port 8000 bị chiếm:**
```bash
sudo lsof -i :8000
sudo kill -9 PID
```

**Nginx lỗi:**
```bash
sudo nginx -t
sudo systemctl status nginx
sudo tail -50 /var/log/nginx/error.log
```

**MoMo IPN không hoạt động:**
- Đảm bảo domain có SSL (HTTPS)
- Test IPN endpoint: `curl https://your-domain.com/api/payment/momo/ipn`
- Check firewall: `sudo ufw status`
- Check Nginx logs: `sudo tail -f /var/log/nginx/access.log`

**Hết disk space:**
```bash
df -h
docker system prune -a -f
sudo apt autoremove -y
sudo apt clean
```

---

### 💡 Production Tips

**1. Setup Auto-Backup Database:**
```bash
# Tạo script backup
nano ~/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec dangerous-api cp /app/app.db /app/data/backup_$DATE.db
# Xóa backup cũ hơn 7 ngày
find ~/Model_XDynamic/data/backup_*.db -mtime +7 -delete
```

```bash
chmod +x ~/backup.sh

# Add vào crontab (chạy mỗi ngày 2h sáng)
crontab -e
# Thêm dòng: 0 2 * * * /home/deploy/backup.sh
```

**2. Setup Monitoring với Netdata:**
```bash
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
# Truy cập: http://YOUR_IP:19999
```

**3. Rate Limiting ở Nginx:**
```bash
sudo nano /etc/nginx/sites-available/dangerous-api
```

Thêm trước block `server`:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    # ... existing config ...
    
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        limit_req_status 429;
        # ... existing proxy config ...
    }
}
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

**4. Đổi Sang PostgreSQL:**
```bash
# Thêm vào docker-compose.yml
nano docker-compose.yml
```

```yaml
  postgres:
    image: postgres:15-alpine
    container_name: dangerous-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: apiuser
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: dangerous_objects
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

Sửa `.env`:
```bash
DATABASE_URL="postgresql://apiuser:your_secure_password@postgres:5432/dangerous_objects"
```

```bash
docker-compose up -d
```

### Quan Trọng Khi Deploy Production
- ✅ Đổi sang PostgreSQL thay vì SQLite (sửa `DATABASE_URL`)
- ✅ Dùng `JWT_SECRET_KEY` mạnh (64+ ký tự random)
- ✅ Cấu hình CORS `allow_origins` đúng domain
- ✅ Bắt buộc dùng HTTPS (Let's Encrypt/CloudFlare)
- ✅ Setup monitoring (Sentry, DataDog, CloudWatch)
- ✅ Thêm rate limiting ở load balancer
- ✅ Dùng file `.env` riêng cho từng môi trường (dev/staging/prod)

## 📊 Cấu Trúc Database

- **users**: Tài khoản người dùng (email, password hash, credits, google_id)
- **subscriptions**: Gói đang dùng (plan, quota, used_quota, expires_at)
- **transactions**: Lịch sử giao dịch (nạp tiền, mua gói, refund)
- **usage_logs**: Theo dõi API usage (endpoint, response time, timestamp)

## 🔒 Bảo Mật

- ✅ Password mã hóa bằng bcrypt
- ✅ JWT tokens cho xác thực stateless
- ✅ Verify chữ ký MoMo để chống fake IPN
- ✅ Chống SQL injection (dùng SQLAlchemy ORM)
- ✅ CORS đã cấu hình
- ✅ Khuyến nghị dùng HTTPS cho production

## 📝 Giải Thích Code

### Cấu Trúc Thư Mục

```
app/
├── config.py              # Cấu hình (JWT, MoMo, Database, Plans)
├── database.py            # Kết nối SQLite/PostgreSQL
├── main.py               # FastAPI app chính, đăng ký routes
├── models/               # SQLAlchemy ORM models (User, Subscription, Transaction, UsageLog)
├── schemas/              # Pydantic schemas (validate request/response)
├── repositories/         # Truy cập database (CRUD operations)
├── services/            # Business logic
│   ├── auth_service.py       # Đăng ký, đăng nhập, JWT, Google OAuth
│   ├── payment_service.py    # Tạo QR MoMo, xử lý IPN callback
│   ├── subscription_service.py # Quản lý gói, check quota, mua gói
│   └── ml_inference_service.py # Load model AI, predict
└── controllers/          # API endpoints (routes)
```

### Luồng Hoạt Động

1. **User đăng ký** → `auth_service.register()` → Tạo user + gói FREE
2. **User nạp tiền** → `payment_service.create_topup_payment()` → Tạo QR MoMo
3. **MoMo callback** → `payment_service.process_ipn()` → Cộng tiền vào ví
4. **User mua gói** → `subscription_service.purchase_plan()` → Trừ tiền, tạo subscription mới
5. **User gọi API** → Check quota → ML inference → Tăng usage counter → Trả kết quả

## 🤝 Liên Hệ & Hỗ Trợ

**Hỗ trợ tích hợp MoMo:**
- Hotline: **1900 636 652**
- Email: **merchant.care@momo.vn**
- Docs: https://developers.momo.vn/v3/vi/docs/payment/onboarding/overall/

**Issues API:**
- Mở issue trên GitHub hoặc liên hệ developer

---

## 📖 Ghi Chú Quan Trọng

- Model weights file phải tên `mobilenetv2_dangerous_objects.pth` và đặt ở root project
- Class names hiện tại là `["0", "1", "2", "3"]` - bạn có thể đổi tên trong `app/config.py`
- Mặc định gói FREE có 100 lượt/tháng, không reset tự động (cần cronjob riêng nếu muốn)
- IPN URL của MoMo **phải là HTTPS** và accessible từ internet
- Để test local: dùng **ngrok** để expose port 8000 ra ngoài

**License:** MIT
