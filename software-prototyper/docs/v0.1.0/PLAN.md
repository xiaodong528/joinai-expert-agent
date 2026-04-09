# 大型电商网站（类京东）开发方案完整文档
**技术方案 + API 文档 + Go 后端框架 + Vue 前端结构 + 测试用例**

---

# 一、项目概述

## 1.1 项目名称
**大型电商网站演示系统（类京东）**

## 1.2 建设目标
本项目旨在开发一个具备大型综合电商平台核心业务能力的网站演示系统，前端重点突出丰富的页面功能、良好的交互体验与完整的电商业务流程；后端采用 Go 实现演示级服务，数据库使用 SQLite，以降低部署复杂度并提高演示效率。

系统需支持：

- 用户注册、登录、个人中心
- 商品分类、搜索、筛选、详情浏览
- SKU 规格选择
- 购物车、下单、支付模拟
- 订单管理、物流模拟、评价
- 优惠券、收藏、浏览足迹、消息通知
- 后台商品管理、订单管理、轮播图管理、公告管理、用户管理
- 完整测试方案与测试用例支撑项目验收

## 1.3 技术栈
### 前端
- Vue 3
- JavaScript
- Vue Router
- Pinia
- Axios
- Element Plus
- ECharts
- Vite

### 后端
- Go
- Gin
- GORM
- JWT
- bcrypt

### 数据库
- SQLite

---

# 二、系统总体架构

## 2.1 架构说明
系统采用前后端分离架构：

- 前端通过 RESTful API 与后端通信
- 后端负责业务逻辑、鉴权、订单处理、文件上传等
- SQLite 负责数据存储
- 上传文件保存到本地目录
- 支付、物流采用模拟机制

## 2.2 系统角色
- 游客
- 普通用户
- 管理员

---

# 三、详细 API 文档

本章节为你要求的**第 3 部分：详细 API 文档**。

---

## 3.1 接口设计规范

### 3.1.1 请求规范
- 请求方式：GET / POST / PUT / DELETE
- 请求体格式：`application/json`
- 文件上传：`multipart/form-data`
- 鉴权方式：JWT，放在 Header 中

```http
Authorization: Bearer <token>
```

### 3.1.2 统一响应格式
#### 成功响应
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

#### 失败响应
```json
{
  "code": 4001,
  "message": "参数错误",
  "data": null
}
```

### 3.1.3 常见状态码
| code | 含义 |
|------|------|
| 0 | 成功 |
| 4001 | 参数错误 |
| 4002 | 用户未登录 |
| 4003 | 无权限 |
| 4004 | 数据不存在 |
| 4005 | 业务状态不允许 |
| 5000 | 系统内部错误 |

---

## 3.2 认证模块 API

---

### 3.2.1 用户注册
**POST** `/api/auth/register`

#### 请求参数
```json
{
  "username": "user1",
  "password": "123456",
  "confirm_password": "123456",
  "phone": "13800138000",
  "email": "user1@test.com"
}
```

#### 参数说明
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| confirm_password | string | 是 | 确认密码 |
| phone | string | 否 | 手机号 |
| email | string | 否 | 邮箱 |

#### 成功返回
```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "user_id": 1
  }
}
```

---

### 3.2.2 用户登录
**POST** `/api/auth/login`

#### 请求参数
```json
{
  "username": "user1",
  "password": "123456"
}
```

#### 成功返回
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "jwt-token",
    "user": {
      "id": 1,
      "username": "user1",
      "nickname": "小明",
      "avatar": "/uploads/avatar1.png",
      "role": "user"
    }
  }
}
```

---

### 3.2.3 获取当前用户信息
**GET** `/api/user/profile`

#### 请求头
需要携带 JWT

#### 成功返回
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "user1",
    "nickname": "小明",
    "avatar": "/uploads/avatar1.png",
    "phone": "13800138000",
    "email": "user1@test.com",
    "points": 100,
    "balance": 99.5
  }
}
```

---

### 3.2.4 更新用户资料
**PUT** `/api/user/profile`

#### 请求参数
```json
{
  "nickname": "新昵称",
  "gender": 1,
  "birthday": "2000-01-01",
  "email": "new@test.com"
}
```

---

### 3.2.5 修改密码
**PUT** `/api/user/password`

#### 请求参数
```json
{
  "old_password": "123456",
  "new_password": "654321",
  "confirm_password": "654321"
}
```

---

## 3.3 首页与商品模块 API

---

### 3.3.1 首页数据
**GET** `/api/home/index`

#### 成功返回
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "banners": [
      {
        "id": 1,
        "title": "夏日大促",
        "image_url": "/uploads/banner1.jpg",
        "link_url": "/product/10"
      }
    ],
    "hot_products": [],
    "new_products": [],
    "recommend_products": [],
    "notices": []
  }
}
```

---

### 3.3.2 分类列表
**GET** `/api/categories`

#### 成功返回
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "手机通讯",
      "parent_id": 0,
      "children": [
        {
          "id": 2,
          "name": "智能手机",
          "parent_id": 1,
          "children": []
        }
      ]
    }
  ]
}
```

---

### 3.3.3 商品列表
**GET** `/api/products`

#### 查询参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 关键词 |
| category_id | int | 否 | 分类ID |
| brand_id | int | 否 | 品牌ID |
| min_price | float | 否 | 最低价 |
| max_price | float | 否 | 最高价 |
| sort | string | 否 | 排序：price_asc / price_desc / sales_desc |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

#### 示例请求
```http
GET /api/products?keyword=手机&category_id=2&page=1&page_size=10
```

#### 成功返回
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 10,
        "name": "旗舰手机X1",
        "subtitle": "超清影像",
        "cover_image": "/uploads/p1.jpg",
        "price": 3999,
        "original_price": 4599,
        "stock": 100,
        "sales_count": 2300
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 10
  }
}
```

---

### 3.3.4 商品详情
**GET** `/api/products/:id`

#### 成功返回
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10,
    "name": "旗舰手机X1",
    "subtitle": "超清影像，超长续航",
    "price": 3999,
    "original_price": 4599,
    "stock": 100,
    "cover_image": "/uploads/p1.jpg",
    "images": [
      "/uploads/p1.jpg",
      "/uploads/p2.jpg"
    ],
    "detail_html": "<p>商品详情介绍</p>",
    "skus": [
      {
        "id": 1001,
        "sku_name": "黑色 256G",
        "price": 3999,
        "stock": 20,
        "specs": {
          "颜色": "黑色",
          "版本": "256G"
        }
      }
    ],
    "attributes": {
      "品牌": "某品牌",
      "屏幕尺寸": "6.7英寸"
    }
  }
}
```

---

### 3.3.5 商品评价列表
**GET** `/api/products/:id/reviews`

#### 查询参数
| 参数 | 类型 | 说明 |
|------|------|------|
| page | int | 页码 |
| page_size | int | 每页条数 |
| rating | int | 评分筛选 |

---

## 3.4 购物车模块 API

---

### 3.4.1 获取购物车
**GET** `/api/cart`

#### 成功返回
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "product_id": 10,
        "sku_id": 1001,
        "product_name": "旗舰手机X1",
        "sku_name": "黑色 256G",
        "price": 3999,
        "quantity": 1,
        "checked": 1,
        "image": "/uploads/p1.jpg",
        "stock": 20
      }
    ],
    "total_amount": 3999
  }
}
```

---

### 3.4.2 添加购物车
**POST** `/api/cart/add`

#### 请求参数
```json
{
  "product_id": 10,
  "sku_id": 1001,
  "quantity": 2
}
```

---

### 3.4.3 更新购物车数量
**PUT** `/api/cart/:id`

#### 请求参数
```json
{
  "quantity": 3,
  "checked": 1
}
```

---

### 3.4.4 删除购物车项
**DELETE** `/api/cart/:id`

---

### 3.4.5 批量勾选
**PUT** `/api/cart/check`

#### 请求参数
```json
{
  "ids": [1, 2, 3],
  "checked": 1
}
```

---

## 3.5 地址模块 API

---

### 3.5.1 地址列表
**GET** `/api/address/list`

### 3.5.2 新增地址
**POST** `/api/address/create`

#### 请求参数
```json
{
  "receiver_name": "张三",
  "receiver_phone": "13800138000",
  "province": "北京市",
  "city": "北京市",
  "district": "朝阳区",
  "detail_address": "某某路100号",
  "postal_code": "100000",
  "is_default": 1
}
```

### 3.5.3 修改地址
**PUT** `/api/address/:id`

### 3.5.4 删除地址
**DELETE** `/api/address/:id`

### 3.5.5 设为默认
**PUT** `/api/address/:id/default`

---

## 3.6 订单模块 API

---

### 3.6.1 创建订单
**POST** `/api/orders/create`

#### 请求参数
```json
{
  "address_id": 1,
  "cart_ids": [1, 2],
  "coupon_id": 3,
  "remark": "请尽快发货"
}
```

#### 成功返回
```json
{
  "code": 0,
  "message": "下单成功",
  "data": {
    "order_id": 10,
    "order_no": "ORD202501010001",
    "pay_amount": 3999
  }
}
```

---

### 3.6.2 订单列表
**GET** `/api/orders`

#### 查询参数
| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | 订单状态 |
| page | int | 页码 |
| page_size | int | 每页条数 |

---

### 3.6.3 订单详情
**GET** `/api/orders/:id`

---

### 3.6.4 取消订单
**POST** `/api/orders/:id/cancel`

---

### 3.6.5 模拟支付
**POST** `/api/orders/:id/pay`

#### 请求参数
```json
{
  "payment_type": "alipay"
}
```

#### 成功返回
```json
{
  "code": 0,
  "message": "支付成功",
  "data": {
    "order_id": 10,
    "status": "pending_shipment"
  }
}
```

---

### 3.6.6 确认收货
**POST** `/api/orders/:id/confirm`

---

## 3.7 优惠券模块 API

### 3.7.1 优惠券列表
**GET** `/api/coupons`

### 3.7.2 领取优惠券
**POST** `/api/coupons/receive`

#### 请求参数
```json
{
  "coupon_id": 1
}
```

### 3.7.3 我的优惠券
**GET** `/api/user/coupons`

---

## 3.8 收藏与足迹 API

### 3.8.1 收藏/取消收藏
**POST** `/api/favorites/toggle`

```json
{
  "product_id": 10
}
```

### 3.8.2 收藏列表
**GET** `/api/favorites`

### 3.8.3 浏览足迹
**GET** `/api/history`

### 3.8.4 清空足迹
**DELETE** `/api/history`

---

## 3.9 评价模块 API

### 3.9.1 提交评价
**POST** `/api/reviews`

#### 请求参数
```json
{
  "order_id": 10,
  "order_item_id": 100,
  "product_id": 10,
  "rating": 5,
  "content": "商品很好，物流很快",
  "images": ["/uploads/review1.jpg"],
  "is_anonymous": 0
}
```

### 3.9.2 我的评价
**GET** `/api/reviews/user`

---

## 3.10 上传接口

### 3.10.1 图片上传
**POST** `/api/upload/image`

- 请求类型：`multipart/form-data`
- 字段名：`file`

#### 成功返回
```json
{
  "code": 0,
  "message": "上传成功",
  "data": {
    "url": "/uploads/20250101/test.jpg"
  }
}
```

---

## 3.11 后台管理 API

---

### 3.11.1 管理员登录
**POST** `/api/admin/login`

### 3.11.2 后台数据看板
**GET** `/api/admin/dashboard`

返回：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "today_order_count": 20,
    "today_sales_amount": 29999,
    "user_count": 500,
    "product_count": 200
  }
}
```

### 3.11.3 商品管理
- `GET /api/admin/products`
- `POST /api/admin/products`
- `PUT /api/admin/products/:id`
- `DELETE /api/admin/products/:id`

#### 新增商品请求示例
```json
{
  "category_id": 2,
  "brand_id": 1,
  "name": "旗舰手机X1",
  "subtitle": "新品首发",
  "price": 3999,
  "original_price": 4599,
  "stock": 100,
  "cover_image": "/uploads/p1.jpg",
  "detail_html": "<p>详情</p>",
  "skus": [
    {
      "sku_name": "黑色 256G",
      "price": 3999,
      "stock": 20,
      "specs_json": "{\"颜色\":\"黑色\",\"版本\":\"256G\"}"
    }
  ]
}
```

### 3.11.4 订单管理
- `GET /api/admin/orders`
- `POST /api/admin/orders/:id/ship`

### 3.11.5 Banner 管理
- `GET /api/admin/banners`
- `POST /api/admin/banners`
- `PUT /api/admin/banners/:id`
- `DELETE /api/admin/banners/:id`

### 3.11.6 公告管理
- `GET /api/admin/notices`
- `POST /api/admin/notices`
- `PUT /api/admin/notices/:id`
- `DELETE /api/admin/notices/:id`

---

# 四、Go 后端项目目录与基础代码框架

本章节为你要求的**第 4 部分：Go 后端项目目录和基础代码框架**。

---

## 4.1 后端项目目录结构

```bash
ecommerce-go/
├── cmd/
│   └── server/
│       └── main.go
├── config/
│   └── config.yaml
├── internal/
│   ├── api/
│   │   ├── auth_handler.go
│   │   ├── product_handler.go
│   │   ├── cart_handler.go
│   │   ├── order_handler.go
│   │   ├── user_handler.go
│   │   ├── address_handler.go
│   │   ├── admin_handler.go
│   │   └── upload_handler.go
│   ├── bootstrap/
│   │   ├── db.go
│   │   ├── router.go
│   │   └── config.go
│   ├── middleware/
│   │   ├── jwt.go
│   │   ├── auth.go
│   │   └── cors.go
│   ├── model/
│   │   ├── user.go
│   │   ├── category.go
│   │   ├── product.go
│   │   ├── cart.go
│   │   ├── order.go
│   │   ├── coupon.go
│   │   └── common.go
│   ├── repository/
│   │   ├── user_repo.go
│   │   ├── product_repo.go
│   │   ├── cart_repo.go
│   │   └── order_repo.go
│   ├── service/
│   │   ├── auth_service.go
│   │   ├── product_service.go
│   │   ├── cart_service.go
│   │   ├── order_service.go
│   │   └── user_service.go
│   ├── dto/
│   │   ├── auth_dto.go
│   │   ├── product_dto.go
│   │   ├── order_dto.go
│   │   └── common.go
│   └── utils/
│       ├── jwt.go
│       ├── password.go
│       ├── response.go
│       ├── order_no.go
│       └── file.go
├── uploads/
├── data/
│   └── ecommerce.db
├── go.mod
└── go.sum
```

---

## 4.2 main.go

```go
package main

import (
	"log"

	"ecommerce-go/internal/bootstrap"
)

func main() {
	bootstrap.InitConfig()
	bootstrap.InitDB()

	r := bootstrap.SetupRouter()

	log.Println("server started at :8080")
	if err := r.Run(":8080"); err != nil {
		log.Fatal(err)
	}
}
```

---

## 4.3 数据库初始化 db.go

```go
package bootstrap

import (
	"log"

	"ecommerce-go/internal/model"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var DB *gorm.DB

func InitDB() {
	db, err := gorm.Open(sqlite.Open("data/ecommerce.db"), &gorm.Config{})
	if err != nil {
		log.Fatal("failed to connect database:", err)
	}

	err = db.AutoMigrate(
		&model.User{},
		&model.UserAddress{},
		&model.Category{},
		&model.Brand{},
		&model.Product{},
		&model.ProductImage{},
		&model.ProductSKU{},
		&model.Cart{},
		&model.Order{},
		&model.OrderItem{},
		&model.Payment{},
		&model.Coupon{},
		&model.UserCoupon{},
		&model.Favorite{},
		&model.BrowsingHistory{},
		&model.Review{},
		&model.Notice{},
		&model.Banner{},
		&model.Message{},
	)
	if err != nil {
		log.Fatal("auto migrate failed:", err)
	}

	DB = db
}
```

---

## 4.4 路由初始化 router.go

```go
package bootstrap

import (
	"ecommerce-go/internal/api"
	"ecommerce-go/internal/middleware"

	"github.com/gin-gonic/gin"
)

func SetupRouter() *gin.Engine {
	r := gin.Default()

	r.Use(middleware.CORS())

	r.Static("/uploads", "./uploads")

	apiGroup := r.Group("/api")
	{
		apiGroup.POST("/auth/register", api.Register)
		apiGroup.POST("/auth/login", api.Login)

		apiGroup.GET("/home/index", api.HomeIndex)
		apiGroup.GET("/categories", api.GetCategories)
		apiGroup.GET("/products", api.GetProducts)
		apiGroup.GET("/products/:id", api.GetProductDetail)
		apiGroup.GET("/products/:id/reviews", api.GetProductReviews)

		authGroup := apiGroup.Group("/")
		authGroup.Use(middleware.JWTAuth())
		{
			authGroup.GET("/user/profile", api.GetProfile)
			authGroup.PUT("/user/profile", api.UpdateProfile)

			authGroup.GET("/cart", api.GetCart)
			authGroup.POST("/cart/add", api.AddCart)
			authGroup.PUT("/cart/:id", api.UpdateCart)
			authGroup.DELETE("/cart/:id", api.DeleteCart)

			authGroup.GET("/address/list", api.GetAddressList)
			authGroup.POST("/address/create", api.CreateAddress)

			authGroup.POST("/orders/create", api.CreateOrder)
			authGroup.GET("/orders", api.GetOrders)
			authGroup.GET("/orders/:id", api.GetOrderDetail)
			authGroup.POST("/orders/:id/pay", api.PayOrder)
			authGroup.POST("/orders/:id/cancel", api.CancelOrder)
			authGroup.POST("/orders/:id/confirm", api.ConfirmOrder)

			authGroup.POST("/favorites/toggle", api.ToggleFavorite)
			authGroup.GET("/favorites", api.GetFavorites)

			authGroup.POST("/reviews", api.CreateReview)

			authGroup.POST("/upload/image", api.UploadImage)
		}

		adminGroup := apiGroup.Group("/admin")
		adminGroup.POST("/login", api.AdminLogin)
		adminGroup.Use(middleware.JWTAuth(), middleware.AdminOnly())
		{
			adminGroup.GET("/dashboard", api.AdminDashboard)
			adminGroup.GET("/products", api.AdminGetProducts)
			adminGroup.POST("/products", api.AdminCreateProduct)
			adminGroup.PUT("/products/:id", api.AdminUpdateProduct)
			adminGroup.DELETE("/products/:id", api.AdminDeleteProduct)

			adminGroup.GET("/orders", api.AdminGetOrders)
			adminGroup.POST("/orders/:id/ship", api.AdminShipOrder)
		}
	}

	return r
}
```

---

## 4.5 用户模型 user.go

```go
package model

import "time"

type User struct {
	ID           uint      `gorm:"primaryKey" json:"id"`
	Username     string    `gorm:"unique;not null" json:"username"`
	PasswordHash string    `gorm:"not null" json:"-"`
	Nickname     string    `json:"nickname"`
	Avatar       string    `json:"avatar"`
	Phone        string    `gorm:"unique" json:"phone"`
	Email        string    `gorm:"unique" json:"email"`
	Gender       int       `json:"gender"`
	Birthday     string    `json:"birthday"`
	Status       int       `json:"status"`
	Role         string    `json:"role"`
	Points       int       `json:"points"`
	Balance      float64   `json:"balance"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

type UserAddress struct {
	ID            uint      `gorm:"primaryKey" json:"id"`
	UserID        uint      `json:"user_id"`
	ReceiverName  string    `json:"receiver_name"`
	ReceiverPhone string    `json:"receiver_phone"`
	Province      string    `json:"province"`
	City          string    `json:"city"`
	District      string    `json:"district"`
	DetailAddress string    `json:"detail_address"`
	PostalCode    string    `json:"postal_code"`
	IsDefault     int       `json:"is_default"`
	CreatedAt     time.Time `json:"created_at"`
	UpdatedAt     time.Time `json:"updated_at"`
}
```

---

## 4.6 商品模型 product.go

```go
package model

import "time"

type Category struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	ParentID  uint      `json:"parent_id"`
	Name      string    `json:"name"`
	Icon      string    `json:"icon"`
	SortOrder int       `json:"sort_order"`
	Level     int       `json:"level"`
	Status    int       `json:"status"`
	CreatedAt time.Time `json:"created_at"`
}

type Brand struct {
	ID          uint      `gorm:"primaryKey" json:"id"`
	Name        string    `json:"name"`
	Logo        string    `json:"logo"`
	Description string    `json:"description"`
	Status      int       `json:"status"`
	CreatedAt   time.Time `json:"created_at"`
}

type Product struct {
	ID            uint      `gorm:"primaryKey" json:"id"`
	CategoryID    uint      `json:"category_id"`
	BrandID       uint      `json:"brand_id"`
	Name          string    `json:"name"`
	Subtitle      string    `json:"subtitle"`
	CoverImage    string    `json:"cover_image"`
	Price         float64   `json:"price"`
	OriginalPrice float64   `json:"original_price"`
	Stock         int       `json:"stock"`
	SalesCount    int       `json:"sales_count"`
	Status        int       `json:"status"`
	IsHot         int       `json:"is_hot"`
	IsNew         int       `json:"is_new"`
	IsRecommend   int       `json:"is_recommend"`
	DetailHTML    string    `json:"detail_html"`
	CreatedAt     time.Time `json:"created_at"`
	UpdatedAt     time.Time `json:"updated_at"`
}

type ProductImage struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	ProductID uint      `json:"product_id"`
	ImageURL  string    `json:"image_url"`
	SortOrder int       `json:"sort_order"`
	CreatedAt time.Time `json:"created_at"`
}

type ProductSKU struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	ProductID uint      `json:"product_id"`
	SKUCode   string    `gorm:"unique" json:"sku_code"`
	SKUName   string    `json:"sku_name"`
	SpecsJSON string    `json:"specs_json"`
	Price     float64   `json:"price"`
	Stock     int       `json:"stock"`
	Image     string    `json:"image"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}
```

---

## 4.7 订单模型 order.go

```go
package model

import "time"

type Cart struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	UserID    uint      `json:"user_id"`
	ProductID uint      `json:"product_id"`
	SKUID     uint      `json:"sku_id"`
	Quantity  int       `json:"quantity"`
	Checked   int       `json:"checked"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type Order struct {
	ID              uint      `gorm:"primaryKey" json:"id"`
	OrderNo         string    `gorm:"unique" json:"order_no"`
	UserID          uint      `json:"user_id"`
	Status          string    `json:"status"`
	TotalAmount     float64   `json:"total_amount"`
	DiscountAmount  float64   `json:"discount_amount"`
	FreightAmount   float64   `json:"freight_amount"`
	PayAmount       float64   `json:"pay_amount"`
	PaymentType     string    `json:"payment_type"`
	PaymentStatus   string    `json:"payment_status"`
	AddressSnapshot string    `json:"address_snapshot"`
	Remark          string    `json:"remark"`
	CouponID        *uint     `json:"coupon_id"`
	CreatedAt       time.Time `json:"created_at"`
	PaidAt          *time.Time `json:"paid_at"`
	ShippedAt       *time.Time `json:"shipped_at"`
	FinishedAt      *time.Time `json:"finished_at"`
	CancelledAt     *time.Time `json:"cancelled_at"`
}

type OrderItem struct {
	ID           uint      `gorm:"primaryKey" json:"id"`
	OrderID      uint      `json:"order_id"`
	ProductID    uint      `json:"product_id"`
	SKUID        uint      `json:"sku_id"`
	ProductName  string    `json:"product_name"`
	SKUName      string    `json:"sku_name"`
	ProductImage string    `json:"product_image"`
	Price        float64   `json:"price"`
	Quantity     int       `json:"quantity"`
	TotalAmount  float64   `json:"total_amount"`
	CreatedAt    time.Time `json:"created_at"`
}

type Payment struct {
	ID          uint      `gorm:"primaryKey" json:"id"`
	OrderID     uint      `json:"order_id"`
	PaymentNo   string    `gorm:"unique" json:"payment_no"`
	PaymentType string    `json:"payment_type"`
	Amount      float64   `json:"amount"`
	Status      string    `json:"status"`
	PaidAt      *time.Time `json:"paid_at"`
	CreatedAt   time.Time `json:"created_at"`
}
```

---

## 4.8 响应工具 response.go

```go
package utils

import "github.com/gin-gonic/gin"

func Success(c *gin.Context, data interface{}) {
	c.JSON(200, gin.H{
		"code":    0,
		"message": "success",
		"data":    data,
	})
}

func Error(c *gin.Context, code int, msg string) {
	c.JSON(200, gin.H{
		"code":    code,
		"message": msg,
		"data":    nil,
	})
}
```

---

## 4.9 JWT 工具 jwt.go

```go
package utils

import (
	"time"

	"github.com/golang-jwt/jwt/v5"
)

var jwtSecret = []byte("ecommerce-demo-secret")

type CustomClaims struct {
	UserID uint   `json:"user_id"`
	Role   string `json:"role"`
	jwt.RegisteredClaims
}

func GenerateToken(userID uint, role string) (string, error) {
	claims := CustomClaims{
		UserID: userID,
		Role:   role,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(7 * 24 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}
```

---

## 4.10 JWT 中间件 jwt.go

```go
package middleware

import (
	"strings"

	"ecommerce-go/internal/utils"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

func JWTAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			utils.Error(c, 4002, "未登录")
			c.Abort()
			return
		}

		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			utils.Error(c, 4002, "认证信息格式错误")
			c.Abort()
			return
		}

		token, err := jwt.ParseWithClaims(parts[1], &utils.CustomClaims{}, func(token *jwt.Token) (interface{}, error) {
			return []byte("ecommerce-demo-secret"), nil
		})

		if err != nil || !token.Valid {
			utils.Error(c, 4002, "token无效")
			c.Abort()
			return
		}

		claims := token.Claims.(*utils.CustomClaims)
		c.Set("user_id", claims.UserID)
		c.Set("role", claims.Role)
		c.Next()
	}
}
```

---

## 4.11 管理员中间件 auth.go

```go
package middleware

import (
	"ecommerce-go/internal/utils"
	"github.com/gin-gonic/gin"
)

func AdminOnly() gin.HandlerFunc {
	return func(c *gin.Context) {
		role, exists := c.Get("role")
		if !exists || role != "admin" {
			utils.Error(c, 4003, "无权限")
			c.Abort()
			return
		}
		c.Next()
	}
}
```

---

## 4.12 登录处理 auth_handler.go

```go
package api

import (
	"ecommerce-go/internal/bootstrap"
	"ecommerce-go/internal/model"
	"ecommerce-go/internal/utils"

	"github.com/gin-gonic/gin"
	"golang.org/x/crypto/bcrypt"
)

type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func Register(c *gin.Context) {
	var req struct {
		Username        string `json:"username"`
		Password        string `json:"password"`
		ConfirmPassword string `json:"confirm_password"`
		Phone           string `json:"phone"`
		Email           string `json:"email"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.Error(c, 4001, "参数错误")
		return
	}
	if req.Password != req.ConfirmPassword {
		utils.Error(c, 4001, "两次密码不一致")
		return
	}

	hash, _ := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	user := model.User{
		Username:     req.Username,
		PasswordHash: string(hash),
		Phone:        req.Phone,
		Email:        req.Email,
		Role:         "user",
		Status:       1,
	}
	if err := bootstrap.DB.Create(&user).Error; err != nil {
		utils.Error(c, 5000, "注册失败")
		return
	}
	utils.Success(c, gin.H{"user_id": user.ID})
}

func Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.Error(c, 4001, "参数错误")
		return
	}

	var user model.User
	if err := bootstrap.DB.Where("username = ?", req.Username).First(&user).Error; err != nil {
		utils.Error(c, 4004, "用户不存在")
		return
	}

	if user.Status == 0 {
		utils.Error(c, 4005, "账号已禁用")
		return
	}

	if err := bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(req.Password)); err != nil {
		utils.Error(c, 4001, "密码错误")
		return
	}

	token, _ := utils.GenerateToken(user.ID, user.Role)
	utils.Success(c, gin.H{
		"token": token,
		"user": gin.H{
			"id":       user.ID,
			"username": user.Username,
			"nickname": user.Nickname,
			"avatar":   user.Avatar,
			"role":     user.Role,
		},
	})
}

func AdminLogin(c *gin.Context) {
	Login(c)
}
```

---

## 4.13 商品列表示例 product_handler.go

```go
package api

import (
	"strconv"

	"ecommerce-go/internal/bootstrap"
	"ecommerce-go/internal/model"
	"ecommerce-go/internal/utils"

	"github.com/gin-gonic/gin"
)

func GetProducts(c *gin.Context) {
	var products []model.Product
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "10"))
	offset := (page - 1) * pageSize

	db := bootstrap.DB.Model(&model.Product{}).Where("status = ?", 1)

	if keyword := c.Query("keyword"); keyword != "" {
		db = db.Where("name LIKE ?", "%"+keyword+"%")
	}
	if categoryID := c.Query("category_id"); categoryID != "" {
		db = db.Where("category_id = ?", categoryID)
	}

	var total int64
	db.Count(&total)
	db.Offset(offset).Limit(pageSize).Find(&products)

	utils.Success(c, gin.H{
		"list":      products,
		"total":     total,
		"page":      page,
		"page_size": pageSize,
	})
}
```

---

## 4.14 创建订单示例 order_handler.go

```go
package api

import (
	"encoding/json"
	"fmt"
	"time"

	"ecommerce-go/internal/bootstrap"
	"ecommerce-go/internal/model"
	"ecommerce-go/internal/utils"

	"github.com/gin-gonic/gin"
)

type CreateOrderRequest struct {
	AddressID uint   `json:"address_id"`
	CartIDs   []uint `json:"cart_ids"`
	CouponID  *uint  `json:"coupon_id"`
	Remark    string `json:"remark"`
}

func CreateOrder(c *gin.Context) {
	userID := c.GetUint("user_id")
	var req CreateOrderRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.Error(c, 4001, "参数错误")
		return
	}

	var address model.UserAddress
	if err := bootstrap.DB.Where("id = ? AND user_id = ?", req.AddressID, userID).First(&address).Error; err != nil {
		utils.Error(c, 4004, "地址不存在")
		return
	}

	var carts []model.Cart
	if err := bootstrap.DB.Where("user_id = ? AND id IN ?", userID, req.CartIDs).Find(&carts).Error; err != nil || len(carts) == 0 {
		utils.Error(c, 4004, "购物车数据不存在")
		return
	}

	var total float64 = 0
	var items []model.OrderItem

	for _, cart := range carts {
		var sku model.ProductSKU
		var product model.Product
		bootstrap.DB.First(&sku, cart.SKUID)
		bootstrap.DB.First(&product, cart.ProductID)

		if sku.Stock < cart.Quantity {
			utils.Error(c, 4005, fmt.Sprintf("商品库存不足: %s", product.Name))
			return
		}

		itemTotal := sku.Price * float64(cart.Quantity)
		total += itemTotal

		items = append(items, model.OrderItem{
			ProductID:    product.ID,
			SKUID:        sku.ID,
			ProductName:  product.Name,
			SKUName:      sku.SKUName,
			ProductImage: product.CoverImage,
			Price:        sku.Price,
			Quantity:     cart.Quantity,
			TotalAmount:  itemTotal,
		})
	}

	addressJSON, _ := json.Marshal(address)
	order := model.Order{
		OrderNo:         fmt.Sprintf("ORD%d", time.Now().UnixNano()),
		UserID:          userID,
		Status:          "pending_payment",
		TotalAmount:     total,
		DiscountAmount:  0,
		FreightAmount:   0,
		PayAmount:       total,
		PaymentStatus:   "unpaid",
		AddressSnapshot: string(addressJSON),
		Remark:          req.Remark,
		CouponID:        req.CouponID,
	}

	tx := bootstrap.DB.Begin()
	if err := tx.Create(&order).Error; err != nil {
		tx.Rollback()
		utils.Error(c, 5000, "创建订单失败")
		return
	}

	for i := range items {
		items[i].OrderID = order.ID
		if err := tx.Create(&items[i]).Error; err != nil {
			tx.Rollback()
			utils.Error(c, 5000, "创建订单明细失败")
			return
		}
	}

	for _, cart := range carts {
		tx.Delete(&cart)
	}

	tx.Commit()

	utils.Success(c, gin.H{
		"order_id":  order.ID,
		"order_no":  order.OrderNo,
		"pay_amount": order.PayAmount,
	})
}
```

---

# 五、Vue 前端项目页面结构与路由方案

本章节为你要求的**第 5 部分：前端 Vue 项目页面结构和路由方案**。

---

## 5.1 前端项目目录结构

```bash
ecommerce-web/
├── public/
├── src/
│   ├── api/
│   │   ├── auth.js
│   │   ├── product.js
│   │   ├── cart.js
│   │   ├── order.js
│   │   ├── user.js
│   │   ├── admin.js
│   │   └── upload.js
│   ├── assets/
│   │   ├── images/
│   │   ├── icons/
│   │   └── styles/
│   ├── components/
│   │   ├── common/
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppFooter.vue
│   │   │   ├── ProductCard.vue
│   │   │   ├── EmptyState.vue
│   │   │   └── Pagination.vue
│   │   ├── home/
│   │   │   ├── BannerSwiper.vue
│   │   │   ├── FlashSale.vue
│   │   │   ├── CategoryNav.vue
│   │   │   └── FloorSection.vue
│   │   ├── product/
│   │   │   ├── ProductGallery.vue
│   │   │   ├── SkuSelector.vue
│   │   │   ├── ProductDetailTabs.vue
│   │   │   └── ReviewList.vue
│   │   ├── cart/
│   │   │   └── CartItem.vue
│   │   └── admin/
│   │       ├── AdminSidebar.vue
│   │       ├── AdminHeader.vue
│   │       └── DashboardCard.vue
│   ├── layout/
│   │   ├── FrontLayout.vue
│   │   └── AdminLayout.vue
│   ├── router/
│   │   └── index.js
│   ├── stores/
│   │   ├── user.js
│   │   ├── cart.js
│   │   └── app.js
│   ├── utils/
│   │   ├── request.js
│   │   ├── auth.js
│   │   ├── format.js
│   │   └── validators.js
│   ├── views/
│   │   ├── front/
│   │   │   ├── Home.vue
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Search.vue
│   │   │   ├── Category.vue
│   │   │   ├── ProductDetail.vue
│   │   │   ├── Cart.vue
│   │   │   ├── Checkout.vue
│   │   │   ├── Payment.vue
│   │   │   ├── PaymentResult.vue
│   │   │   ├── HelpCenter.vue
│   │   │   └── user/
│   │   │       ├── UserCenter.vue
│   │   │       ├── Profile.vue
│   │   │       ├── Orders.vue
│   │   │       ├── OrderDetail.vue
│   │   │       ├── Address.vue
│   │   │       ├── Favorites.vue
│   │   │       ├── History.vue
│   │   │       ├── Coupons.vue
│   │   │       ├── Reviews.vue
│   │   │       └── Messages.vue
│   │   ├── admin/
│   │   │   ├── AdminLogin.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── Users.vue
│   │   │   ├── Products.vue
│   │   │   ├── ProductEdit.vue
│   │   │   ├── Categories.vue
│   │   │   ├── Orders.vue
│   │   │   ├── Coupons.vue
│   │   │   ├── Banners.vue
│   │   │   ├── Notices.vue
│   │   │   └── Settings.vue
│   │   ├── NotFound.vue
│   │   └── Forbidden.vue
│   ├── App.vue
│   └── main.js
├── package.json
└── vite.config.js
```

---

## 5.2 Vue Router 路由设计

### 5.2.1 路由文件 index.js
```js
import { createRouter, createWebHistory } from 'vue-router'
import FrontLayout from '@/layout/FrontLayout.vue'
import AdminLayout from '@/layout/AdminLayout.vue'

const routes = [
  {
    path: '/',
    component: FrontLayout,
    children: [
      { path: '', name: 'Home', component: () => import('@/views/front/Home.vue') },
      { path: 'login', name: 'Login', component: () => import('@/views/front/Login.vue') },
      { path: 'register', name: 'Register', component: () => import('@/views/front/Register.vue') },
      { path: 'search', name: 'Search', component: () => import('@/views/front/Search.vue') },
      { path: 'category/:id?', name: 'Category', component: () => import('@/views/front/Category.vue') },
      { path: 'product/:id', name: 'ProductDetail', component: () => import('@/views/front/ProductDetail.vue') },
      { path: 'cart', name: 'Cart', component: () => import('@/views/front/Cart.vue') },
      { path: 'checkout', name: 'Checkout', component: () => import('@/views/front/Checkout.vue') },
      { path: 'payment/:id', name: 'Payment', component: () => import('@/views/front/Payment.vue') },
      { path: 'payment-result', name: 'PaymentResult', component: () => import('@/views/front/PaymentResult.vue') },
      { path: 'help', name: 'HelpCenter', component: () => import('@/views/front/HelpCenter.vue') },

      { path: 'user', name: 'UserCenter', component: () => import('@/views/front/user/UserCenter.vue') },
      { path: 'user/profile', name: 'Profile', component: () => import('@/views/front/user/Profile.vue') },
      { path: 'user/orders', name: 'UserOrders', component: () => import('@/views/front/user/Orders.vue') },
      { path: 'user/orders/:id', name: 'OrderDetail', component: () => import('@/views/front/user/OrderDetail.vue') },
      { path: 'user/address', name: 'Address', component: () => import('@/views/front/user/Address.vue') },
      { path: 'user/favorites', name: 'Favorites', component: () => import('@/views/front/user/Favorites.vue') },
      { path: 'user/history', name: 'History', component: () => import('@/views/front/user/History.vue') },
      { path: 'user/coupons', name: 'Coupons', component: () => import('@/views/front/user/Coupons.vue') },
      { path: 'user/reviews', name: 'Reviews', component: () => import('@/views/front/user/Reviews.vue') },
      { path: 'user/messages', name: 'Messages', component: () => import('@/views/front/user/Messages.vue') }
    ]
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/admin/AdminLogin.vue')
  },
  {
    path: '/admin',
    component: AdminLayout,
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'users', name: 'AdminUsers', component: () => import('@/views/admin/Users.vue') },
      { path: 'products', name: 'AdminProducts', component: () => import('@/views/admin/Products.vue') },
      { path: 'products/edit/:id?', name: 'ProductEdit', component: () => import('@/views/admin/ProductEdit.vue') },
      { path: 'categories', name: 'AdminCategories', component: () => import('@/views/admin/Categories.vue') },
      { path: 'orders', name: 'AdminOrders', component: () => import('@/views/admin/Orders.vue') },
      { path: 'coupons', name: 'AdminCoupons', component: () => import('@/views/admin/Coupons.vue') },
      { path: 'banners', name: 'AdminBanners', component: () => import('@/views/admin/Banners.vue') },
      { path: 'notices', name: 'AdminNotices', component: () => import('@/views/admin/Notices.vue') },
      { path: 'settings', name: 'AdminSettings', component: () => import('@/views/admin/Settings.vue') }
    ]
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/Forbidden.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const adminToken = localStorage.getItem('admin_token')

  if (to.path.startsWith('/user') || ['/cart', '/checkout'].includes(to.path)) {
    if (!token) return next('/login')
  }

  if (to.path.startsWith('/admin') && to.path !== '/admin/login') {
    if (!adminToken) return next('/admin/login')
  }

  next()
})

export default router
```

---

## 5.3 前端 API 请求封装

### request.js
```js
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://localhost:8080/api',
  timeout: 10000
})

request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  const adminToken = localStorage.getItem('admin_token')

  if (config.url.startsWith('/admin')) {
    if (adminToken) {
      config.headers.Authorization = `Bearer ${adminToken}`
    }
  } else {
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 0) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(res)
    }
    return res
  },
  error => {
    ElMessage.error(error.message || '网络异常')
    return Promise.reject(error)
  }
)

export default request
```

---

## 5.4 前端模块划分建议

### 5.4.1 公共布局
- `FrontLayout.vue`
  - 顶部导航
  - 搜索栏
  - Footer
- `AdminLayout.vue`
  - 侧边菜单
  - 面包屑
  - 顶部用户信息

### 5.4.2 状态管理
#### user.js
- token
- userInfo
- login/logout
- fetchProfile

#### cart.js
- cartList
- cartCount
- totalAmount
- addCart
- loadCart

#### app.js
- categoryList
- bannerList
- notices

---

## 5.5 页面功能说明

### 首页 Home.vue
- 轮播图
- 楼层商品
- 秒杀模块
- 推荐商品
- 分类导航
- 公告信息

### 商品详情 ProductDetail.vue
- 图片画廊
- SKU 选择器
- 加购物车
- 立即购买
- 商品详情 tabs
- 评价列表

### 购物车 Cart.vue
- 购物车项列表
- 全选/反选
- 删除
- 数量修改
- 金额计算

### 结算页 Checkout.vue
- 地址选择
- 优惠券选择
- 商品确认
- 金额汇总
- 提交订单

### 用户中心
- 订单列表
- 收藏
- 足迹
- 消息
- 地址管理
- 评价管理

### 后台商品管理
- 商品列表
- 条件搜索
- 上架/下架
- 新增商品
- SKU 管理
- 图片上传

---

# 六、完整测试用例表格版（Excel 风格）

本章节为你要求的**第 7 部分：完整测试用例表格版**。

为了方便你后续复制到 Word/Excel，我采用标准表格化格式：

字段包括：

- 用例编号
- 功能模块
- 用例名称
- 前置条件
- 测试步骤
- 预期结果
- 优先级

---

## 6.1 用户注册模块测试用例

| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| REG-001 | 用户注册 | 正常注册成功 | 无 | 输入合法用户名、密码、手机号、邮箱并提交 | 注册成功，跳转登录页或自动登录 | 高 |
| REG-002 | 用户注册 | 用户名重复注册 | 数据库已存在 user1 | 输入已存在用户名注册 | 提示用户名已存在 | 高 |
| REG-003 | 用户注册 | 手机号重复 | 数据库已存在手机号 | 输入已存在手机号注册 | 提示手机号已存在 | 中 |
| REG-004 | 用户注册 | 邮箱重复 | 数据库已存在邮箱 | 输入已存在邮箱注册 | 提示邮箱已存在 | 中 |
| REG-005 | 用户注册 | 密码过短 | 无 | 输入长度不足的密码 | 前端/后端提示密码不合法 | 高 |
| REG-006 | 用户注册 | 两次密码不一致 | 无 | 输入不同密码和确认密码 | 提示两次密码不一致 | 高 |
| REG-007 | 用户注册 | 手机号格式错误 | 无 | 输入非法手机号 | 提示手机号格式错误 | 中 |
| REG-008 | 用户注册 | 邮箱格式错误 | 无 | 输入非法邮箱 | 提示邮箱格式错误 | 中 |
| REG-009 | 用户注册 | 必填字段为空 | 无 | 不输入用户名或密码提交 | 提示必填项不能为空 | 高 |

---

## 6.2 用户登录模块测试用例

| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| LOG-001 | 用户登录 | 正常登录 | 用户已注册 | 输入正确账号密码登录 | 登录成功，返回 token，进入首页 | 高 |
| LOG-002 | 用户登录 | 用户不存在 | 无 | 输入不存在用户名 | 提示用户不存在 | 高 |
| LOG-003 | 用户登录 | 密码错误 | 用户存在 | 输入错误密码 | 提示密码错误 | 高 |
| LOG-004 | 用户登录 | 被禁用用户登录 | 用户状态为禁用 | 输入正确账号密码 | 提示账号已禁用 | 高 |
| LOG-005 | 用户登录 | 空账号登录 | 无 | 不输入账号密码提交 | 提示参数错误 | 中 |

---

## 6.3 首页模块测试用例

| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| HOME-001 | 首页 | Banner 正常显示 | 已配置 Banner | 打开首页 | Banner 成功显示 | 高 |
| HOME-002 | 首页 | 分类导航显示 | 已存在分类数据 | 打开首页 | 分类列表正常展示 | 高 |
| HOME-003 | 首页 | 热门商品显示 | 已配置热销商品 | 打开首页 | 热门商品区域正常展示 | 中 |
| HOME-004 | 首页 | 新品推荐显示 | 已配置新品 | 打开首页 | 新品区域正常展示 | 中 |
| HOME-005 | 首页 | 点击 Banner 跳转 | 已配置 link_url | 点击 Banner | 跳转目标页面 | 中 |

---

## 6.4 商品列表与搜索测试用例

| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| PRO-001 | 商品列表 | 默认分页加载 | 商品数据存在 | 访问商品列表页 | 返回第一页数据 | 高 |
| PRO-002 | 商品列表 | 分类筛选 | 存在多个分类商品 | 按分类筛选 | 只显示对应分类商品 | 高 |
| PRO-003 | 商品列表 | 品牌筛选 | 存在多个品牌商品 | 按品牌筛选 | 数据正确 | 中 |
| PRO-004 | 商品列表 | 价格区间筛选 | 商品有不同价格 | 设置价格范围 | 返回对应区间商品 | 中 |
| PRO-005 | 商品列表 | 按价格升序排序 | 商品数据存在 | 选择价格升序 | 列表顺序正确 | 中 |
| PRO-006 | 搜索 | 关键词搜索 | 商品名称包含关键词 | 输入关键词搜索 | 返回匹配商品 | 高 |
| PRO-007 | 搜索 | 无搜索结果 | 不存在匹配关键词 | 输入无效关键词 | 显示空态页和推荐商品 | 中 |

---

## 6.5 商品详情测试用例

| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| DETAIL-001 | 商品详情 | 基础信息显示 | 商品存在 | 进入商品详情页 | 名称、价格、库存等展示正确 | 高 |
| DETAIL-002 | 商品详情 | 图片切换 | 商品有多张图片 | 点击缩略图 | 主图切换正常 | 中 |
| DETAIL-003 | 商品详情 | SKU 切换价格 | 商品有多个 SKU | 切换不同规格 | 价格/库存联动更新 | 高 |
| DETAIL-004 | 商品详情 | 库存不足限制购买 | SKU 库存为 0 | 选择无库存 SKU | 加购/购买按钮置灰或提示 | 高 |
| DETAIL-005 | 商品详情 | 收藏商品 | 用户已登录 | 点击收藏按钮 | 收藏成功，状态变化 | 中 |
| DETAIL-006 | 商品详情 | 加入购物车 | 用户已登录 | 选择 SKU 和数量加入购物车 | 成功加入购物车 | 高 |

---

## 6.6 购物车测试用例

| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| CART-001 | 购物车 | 添加商品到购物车 | 用户已登录 | 商品详情页点击加入购物车 | 购物车新增商品 | 高 |
| CART-002 | 购物车 | 相同 SKU 数量累加 | 购物车已有该 SKU | 再次加入相同 SKU | 数量累加 | 高 |
| CART-003 | 购物车 | 修改数量 | 购物车中有商品 | 修改数量为 3 | 数量更新成功，总价更新 | 高 |
| CART-004 | 购物车 | 数量小于1限制 | 购物车中有商品 | 数量改为 0 | 系统拦截并提示 | 高 |
| CART-005 | 购物车 | 删除单个商品 | 购物车中有商品 | 点击删除 | 商品移除成功 | 高 |
| CART-006 | 购物车 | 全选功能 | 购物车中多个商品 | 点击全选 | 所有商品被勾选 | 中 |
| CART-007 | 购物车 | 总价计算 | 多商品不同价格 | 勾选多个商品 | 总价计算正确 | 高 |

---

## 6.7 地址管理测试用例

| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| ADDR-001 | 地址管理 | 新增地址成功 | 用户已登录 | 输入完整地址信息保存 | 地址保存成功 | 高 |
| ADDR-002 | 地址管理 | 编辑地址 | 存在地址 | 修改收货人后保存 | 修改成功 | 中 |
| ADDR-003 | 地址管理 | 删除地址 | 存在地址 | 删除指定地址 | 删除成功 | 中 |
| ADDR-004 | 地址管理 | 设置默认地址 | 存在多个地址 | 设某条地址为默认 | 默认地址唯一 | 高 |
| ADDR-005 | 地址管理 | 手机号格式错误 | 用户已登录 | 输入非法手机号保存 | 提示手机号错误 | 中 |

---

## 6.8 下单与支付测试用例

| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| ORD-001 | 订单 | 正常创建订单 | 已登录，购物车有商品，存在地址 | 选择地址并提交订单 | 订单创建成功 | 高 |
| ORD-002 | 订单 | 无地址下单 | 购物车有商品 | 不选择地址提交 | 提示请选择收货地址 | 高 |
| ORD-003 | 订单 | 优惠券抵扣 | 存在可用优惠券 | 选择优惠券下单 | 抵扣金额正确 | 中 |
| ORD-004 | 订单 | 库存不足时下单 | 商品库存不足 | 提交订单 | 下单失败并提示库存不足 | 高 |
| PAY-001 | 支付 | 模拟支付成功 | 存在待支付订单 | 进入支付页点击支付 | 支付成功，订单状态更新 | 高 |
| PAY-002 | 支付 | 已支付订单重复支付 | 订单已支付 | 再次进入支付 | 提示订单已支付 | 高 |
| PAY-003 | 支付 | 已取消订单支付 | 订单已取消 | 点击支付 | 提示不可支付 | 高 |

---

## 6.9 订单状态流转测试用例

| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| FLOW-001 | 订单流转 | 待支付取消订单 | 订单待支付 | 点击取消订单 | 状态变更为 cancelled | 高 |
| FLOW-002 | 订单流转 | 待支付付款 | 待支付订单 | 模拟支付 | 状态变更为 pending_shipment | 高 |
| FLOW-003 | 订单流转 | 后台发货 | 待发货订单 | 管理员点击发货 | 状态变更为 pending_receipt | 高 |
| FLOW-004 | 订单流转 | 用户确认收货 | 待收货订单 | 用户确认收货 | 状态变更为 completed | 高 |
| FLOW-005 | 订单流转 | 非法状态发货 | 订单已取消 | 后台点击发货 | 提示状态不允许 | 高 |

---

## 6.10 收藏与足迹测试用例

| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| FAV-001 | 收藏 | 收藏商品 | 用户登录 | 点击收藏 | 收藏成功 | 中 |
| FAV-002 | 收藏 | 取消收藏 | 已收藏商品 | 再次点击收藏 | 取消成功 | 中 |
| HIS-001 | 足迹 | 浏览生成足迹 | 用户已登录 | 访问商品详情 | 足迹记录新增 | 中 |
| HIS-002 | 足迹 | 清空足迹 | 足迹存在 | 点击清空 | 足迹被清空 | 低 |

---

## 6.11 评价测试用例

| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| REV-001 | 评价 | 已完成订单评价 | 订单已完成 | 填写评价提交 | 评价成功 | 高 |
| REV-002 | 评价 | 未完成订单评价 | 订单未完成 | 提交评价 | 提示不可评价 | 高 |
| REV-003 | 评价 | 匿名评价 | 已完成订单 | 勾选匿名后提交 | 前台显示匿名 | 中 |
| REV-004 | 评价 | 上传评价图片 | 已完成订单 | 上传图片并提交 | 图片保存成功 | 中 |
| REV-005 | 评价 | 评分范围校验 | 已完成订单 | 提交超范围评分 | 提示评分不合法 | 中 |

---

## 6.12 后台管理测试用例

### 6.12.1 管理员登录与权限
| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| ADM-001 | 后台登录 | 管理员登录成功 | 管理员存在 | 输入正确账号密码 | 登录成功进入后台 | 高 |
| ADM-002 | 后台权限 | 普通用户访问后台 | 普通用户 token | 请求后台接口 | 返回无权限 | 高 |

### 6.12.2 商品管理
| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| ADM-PRO-001 | 商品管理 | 新增商品 | 管理员登录 | 填写商品信息并提交 | 新增成功 | 高 |
| ADM-PRO-002 | 商品管理 | 编辑商品 | 存在商品 | 修改价格并保存 | 修改成功 | 高 |
| ADM-PRO-003 | 商品管理 | 删除商品 | 存在商品 | 删除商品 | 删除成功或逻辑下架成功 | 高 |
| ADM-PRO-004 | 商品管理 | SKU 保存正确 | 商品支持规格 | 增加 SKU 保存 | SKU 数据正确入库 | 高 |

### 6.12.3 订单管理
| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| ADM-ORD-001 | 订单管理 | 查看订单列表 | 管理员登录 | 打开订单页 | 列表正常显示 | 高 |
| ADM-ORD-002 | 订单管理 | 模拟发货 | 订单待发货 | 点击发货 | 发货成功 | 高 |
| ADM-ORD-003 | 订单管理 | 非法状态订单发货 | 订单已取消 | 点击发货 | 提示不可发货 | 高 |

### 6.12.4 Banner / 公告管理
| 用例编号 | 功能模块 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|---|---|
| ADM-BAN-001 | Banner管理 | 新增 Banner | 管理员登录 | 上传图片并提交 | 新增成功 | 中 |
| ADM-BAN-002 | Banner管理 | 删除 Banner | 已存在 Banner | 删除操作 | 删除成功 | 低 |
| ADM-NOT-001 | 公告管理 | 新增公告 | 管理员登录 | 输入标题内容保存 | 新增成功 | 中 |

---

## 6.13 接口测试检查表

| 编号 | 检查项 | 内容 | 预期 |
|---|---|---|---|
| API-001 | 参数校验 | 缺少必填参数 | 返回参数错误 |
| API-002 | 鉴权校验 | 未登录访问用户接口 | 返回未登录 |
| API-003 | 权限校验 | 普通用户访问后台接口 | 返回无权限 |
| API-004 | 数据不存在 | 查询不存在商品 | 返回数据不存在 |
| API-005 | 异常处理 | 服务内部错误 | 返回统一错误信息 |

---

## 6.14 性能测试用例表

| 用例编号 | 场景 | 并发数 | 持续时间 | 预期结果 |
|---|---|---:|---|---|
| PERF-001 | 首页接口压测 | 50 | 3分钟 | 平均响应 < 500ms |
| PERF-002 | 商品列表接口压测 | 100 | 5分钟 | 错误率 < 1% |
| PERF-003 | 登录接口压测 | 30 | 3分钟 | 服务稳定 |
| PERF-004 | 下单接口压测 | 20 | 3分钟 | 无严重错误 |

---

## 6.15 安全测试用例表

| 用例编号 | 安全项 | 测试步骤 | 预期结果 |
|---|---|---|---|
| SEC-001 | SQL注入 | 在搜索参数中输入注入语句 | 不可注入成功 |
| SEC-002 | XSS | 在评价内容输入脚本标签 | 页面渲染安全，无弹窗执行 |
| SEC-003 | 越权访问 | 使用普通用户访问管理员接口 | 被拒绝 |
| SEC-004 | 非法上传 | 上传 exe 文件 | 上传被拦截 |
| SEC-005 | 弱口令 | 使用简单口令注册/登录 | 有风险提示或后续增强策略 |

---

# 七、前后端联调建议

## 7.1 联调顺序
建议按以下顺序联调：

1. 登录注册
2. 首页接口
3. 商品列表、详情
4. 购物车
5. 地址管理
6. 下单
7. 支付
8. 订单中心
9. 收藏、评价
10. 后台管理

## 7.2 Mock 策略
前端开发初期可使用 mock 数据，待后端接口完成后切换为真实 API。

---

# 八、部署与运行说明

## 8.1 后端运行
```bash
go mod tidy
go run cmd/server/main.go
```

## 8.2 前端运行
```bash
npm install
npm run dev
```

## 8.3 默认端口
- 前端：`5173`
- 后端：`8080`

---
