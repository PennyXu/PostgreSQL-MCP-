from mcp.server.fastmcp import FastMCP
import os
import pandas as pd
import psycopg2
import psycopg2.extras
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import traceback
import logging
import tempfile
import atexit
import smtplib
import shutil
from dotenv import load_dotenv

# ========== 日志配置 ==========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== 临时目录管理 ==========
TEMP_DIR = "./temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# 清理临时文件（程序退出时）
def cleanup_temp():
    try:
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
            logger.info("✅ 临时目录已清理")
    except Exception as e:
        logger.warning(f"❌ 清理临时目录失败: {e}")

atexit.register(cleanup_temp)

load_dotenv()
# ========== 数据库连接 ==========
def get_db_connection():
    return psycopg2.connect(
         host=os.getenv("RDS_HOST"),
         port=int(os.getenv("RDS_PORT", 5432)),
         user=os.getenv("RDS_USER"),
         password=os.getenv("RDS_PASSWORD"),
         dbname=os.getenv("RDS_DATABASE")
     )

# ========== 安全检查 ==========
def is_safe_sql(sql, action):
    sql_upper = sql.upper().strip()
    forbidden = [
        'DROP', 'CREATE DATABASE', 'GRANT', 'REVOKE', 'ALTER USER', 'FLUSH', 'SHUTDOWN',
        'COPY', 'TRUNCATE', 'DELETE', 'UPDATE', 'INSERT'
    ]
    for kw in forbidden:
        if kw in sql_upper:
            return False, f"禁止关键字: {kw}"
    if action == "select" and not sql_upper.startswith("SELECT"):
        return False, "只允许 SELECT"
    return True, "OK"

# ========== Excel 导出与邮件发送 ==========
def export_to_excel_and_email(sql: str, subject: str = None):
    try:
        # 1. 执行查询
        conn = get_db_connection()
        df = pd.read_sql(sql, conn)
        conn.close()

        if df.empty:
            return {
                "status": "failed",
                "message": "查询返回空数据集，无法生成文件。",
                "file_path": None,
                "email_sent": False
            }

        logger.info(f"✅ 查询成功，共 {len(df)} 行数据")

        # 2. 生成 Excel 文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"rds_query_result_{timestamp}.xlsx"
        filepath = os.path.join(TEMP_DIR, excel_filename)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='查询结果', index=False)

        logger.info(f"✅ Excel 文件已保存: {filepath}")

        # 3. 发送邮件
        sender = '发送人邮箱'
        receiver = '收件人邮箱'
        password = '发件人smtp密码'
        smtp_server = 'smtp.126.com' #根据发件人邮箱修改smtp_server
        smtp_port = 465

        if not subject:
            subject = f"【RDS】查询结果 - {timestamp}"

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject

        body = f"""
        <html>
          <body>
            <h2>📊 PostgreSQL 查询结果已导出</h2>
            <p>查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>数据已附在邮件中，请查收。</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html', 'utf-8'))

        with open(filepath, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{excel_filename}"'
        )
        msg.attach(part)

        try:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
            server.quit()
            email_sent = True
            logger.info("✅ 邮件发送成功！")
        except Exception as e:
            email_sent = False
            logger.error(f"❌ 邮件发送失败: {e}")
            traceback.print_exc()

        return {
            "status": "success",
            "message": f"查询成功，Excel 已生成并发送至 {receiver}。",
            "file_path": filepath,
            "email_sent": email_sent,
            "row_count": len(df),
            "timestamp": timestamp
        }

    except Exception as e:
        logger.error(f"❌ 导出或发送失败: {e}")
        traceback.print_exc()
        return {
            "status": "failed",
            "message": str(e),
            "file_path": None,
            "email_sent": False
        }

# ========== 初始化 MCP ==========
mcp = FastMCP("PostgreSQL Export Tool")

@mcp.tool()
def export_query_result_to_excel_and_email(
    sql: str,
    subject: str = None
) -> dict:
    """
    从 PostgreSQL 执行 SQL 查询，导出为 Excel 并发送邮件。

    Args:
        sql (str): SQL 查询语句（必须以 SELECT 开头）
        subject (str, optional): 邮件主题（默认自动生成）

    Returns:
        dict: 包含状态、消息、文件路径、邮件发送状态等信息
    """
    # 安全检查
    safe, msg = is_safe_sql(sql, "select")
    if not safe:
        return {"error": msg, "status": "failed"}

    return export_to_excel_and_email(sql, subject)

# ========== 函数计算入口 ==========
def handler(event, context):
    return mcp.handle_http(event, context)

# ========== 启动服务 ==========
if __name__ == '__main__':
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8001 
    mcp.run(transport='sse')
