# PostgreSQL MCP 数据导出工具 🤖

**专为 AI 助手设计的智能数据导出工具** - 让 AI 能够安全地访问数据库并将查询结果自动发送给用户

## 🌟 AI 专用特性

### 🤖 **AI 原生设计**
- **自然语言集成** - AI 可以直接调用工具执行数据查询
- **安全沙箱** - 内置 SQL 安全检查，防止 AI 误操作
- **自动格式化** - AI 无需处理文件生成和邮件发送细节
- **错误友好** - 清晰的错误信息帮助 AI 理解问题并重试

### 🚀 **快速集成**
AI 助手只需简单调用即可获得完整的数据导出能力：

```python
# AI 可以这样使用
result = export_query_result_to_excel_and_email(
    sql="SELECT * FROM users WHERE active = true",
    subject="AI 生成的活跃用户报告"
)
```

## 🛠️ AI 使用指南

### 基础查询模式
```python
# 获取用户数据
result = export_query_result_to_excel_and_email(
    sql="SELECT username, email, created_at FROM users ORDER BY created_at DESC LIMIT 50",
    subject="最新注册用户列表"
)

# 销售数据分析
result = export_query_result_to_excel_and_email(
    sql="""
    SELECT product_name, SUM(quantity) as total_sold, SUM(revenue) as total_revenue
    FROM sales 
    WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY product_name 
    ORDER BY total_revenue DESC
    """,
    subject="月度产品销售排行榜"
)
```

### AI 提示词模板
```
你是一个数据分析助手，可以帮用户从数据库查询信息。
当用户要求数据报告时，使用 export_query_result_to_excel_and_email 工具：

1. 构建合适的 SQL 查询语句
2. 设置清晰的邮件主题
3. 执行并告知用户结果

示例：
用户：帮我导出去年的订单数据
AI：我将查询去年的订单数据并发送到您的邮箱...
```

## 🔒 AI 安全限制

### 允许的操作
✅ `SELECT` 查询  
✅ 数据筛选和排序  
✅ 聚合统计  
✅ 多表 JOIN 查询  

### 禁止的操作
❌ 任何数据修改（INSERT/UPDATE/DELETE）  
❌ 数据库结构变更  
❌ 权限管理操作  
❌ 系统管理命令  

## 📋 AI 使用场景

### 场景 1：客户支持报告
```python
# AI 自动生成客户服务报告
result = export_query_result_to_excel_and_email(
    sql="""
    SELECT 
        ticket_id,
        customer_name,
        issue_type,
        created_at,
        status,
        resolution_time
    FROM support_tickets 
    WHERE created_at >= '2024-01-01'
    AND status = 'resolved'
    """,
    subject="2024年度客户问题解决报告"
)
```

### 场景 2：业务指标监控
```python
# AI 定期业务监控
result = export_query_result_to_excel_and_email(
    sql="""
    SELECT 
        metric_name,
        current_value,
        target_value,
        (current_value - target_value) as variance,
        update_time
    FROM business_metrics 
    WHERE update_time >= CURRENT_DATE
    """,
    subject="今日业务指标快报"
)
```

### 场景 3：用户行为分析
```python
# AI 分析用户行为模式
result = export_query_result_to_excel_and_email(
    sql="""
    SELECT 
        user_segment,
        COUNT(*) as user_count,
        AVG(session_duration) as avg_session,
        AVG(purchase_value) as avg_order_value
    FROM user_behavior 
    WHERE date >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY user_segment
    """,
    subject="用户行为周报 - 分群分析"
)
```

## 🔧 集成到 AI 系统

### MCP服务配置文件(需配置服务器)
```json
{
  "mcpServers": {
    "send_email_with_postgresql": {
      "url": "http://服务器公网ip:port/sse",
      "type": "sse/streamableHttp"
    }
  }
}
```

## 💡 AI 最佳实践

### 1. 清晰的用户沟通
```
"我将为您查询最近30天的销售数据，结果会通过邮件发送给您。请稍等..."
```

### 2. 智能重试机制
```python
# AI 可以处理错误并重试
def smart_data_export(ai_assistant, sql, subject):
    try:
        result = export_query_result_to_excel_and_email(sql, subject)
        if result["status"] == "success":
            return f"✅ 数据已发送到您的邮箱！共 {result['row_count']} 条记录。"
        else:
            return f"❌ 导出失败：{result['message']}"
    except Exception as e:
        return f"⚠️ 系统暂时不可用，请稍后重试。错误：{e}"
```

### 3. 结果解释和总结
```python
# AI 不仅导出数据，还提供洞察
def export_with_insights(ai_assistant, sql, subject, analysis_prompt):
    # 先导出数据
    export_result = export_query_result_to_excel_and_email(sql, subject)
    
    # 然后基于数据提供分析
    if export_result["status"] == "success":
        insights = ai_assistant.analyze_data(analysis_prompt)
        return f"""
📊 数据导出完成！
✅ 已发送 {export_result['row_count']} 条记录到您的邮箱

🔍 关键洞察：
{insights}
        """
```

## 🎯 AI 功能优势

### 对于 AI 开发者
- **即插即用** - 快速为 AI 添加数据库能力
- **无需培训** - AI 直接理解工具接口
- **安全可靠** - 内置防护防止 AI 误操作

### 对于最终用户
- **自然交互** - 用自然语言请求数据报告
- **自动交付** - 结果直接发送到邮箱
- **专业格式** - 自动生成规范的 Excel 文件

## 🚀 快速开始

1. **配置环境变量**
```bash
# .env 文件
RDS_HOST=your-db-host
RDS_USER=your-username
RDS_PASSWORD=your-password
RDS_DATABASE=your-database
```

2. **启动 MCP 服务**
```bash
python postgres_export_tool.py
```

3. **AI 立即获得能力**
```
用户："帮我导出上个月的销售前十产品"
AI："好的，我将查询上个月销售最好的10个产品并发送到您的邮箱..."
```

---

**让每个 AI 助手都成为数据分析专家！** 📈✨

只需简单集成，您的 AI 就能安全地访问数据库、生成专业报告并自动发送给用户，全面提升工作效率和用户体验。