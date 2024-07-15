import smtplib
import pandas as pd
import numpy as np
import base64
import io
import matplotlib.pyplot as plt
from email.header import Header
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openpyxl import load_workbook
from sqlalchemy import create_engine

# 配置 matplotlib 中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 邮箱授权码（需要替换为你的实际授权码）
password = "jkkwsybxgpggjcah"

def get_image_for_plt():
    """
    获取 matplotlib 中的图表并编码为 base64
    """
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()

def send_email(receiver, subject, content):
    """
    通过 QQ 邮箱发送邮件
    :param receiver: 收件人邮箱账号
    :param subject: 邮件主题
    :param content: 邮件内容
    """
    smtp_server = 'smtp.qq.com'
    port = 465
    sender = "1752106450@qq.com"
    msg = MIMEMultipart()
    msg['From'] = formataddr((Header(sender, 'utf-8').encode(), sender))
    msg['To'] = formataddr((Header(receiver, 'utf-8').encode(), receiver))
    msg['Subject'] = Header(subject, 'utf-8').encode()
    html_content = f"""  
    <html>  
    <body>  
    <p>{content}</p>  
    <img src="data:image/png;base64,{get_image_for_plt()}" alt="chart" />  
    </body>  
    </html>  
    """
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    server = smtplib.SMTP_SSL(smtp_server, port)
    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()

#
df_data=pd.read_sql_table(
    "car",
    create_engine("mysql+pymysql://root:123456@localhost/tongcheng"),
)

# # 加载 Excel 文件
# file_path = '58同城.xlsx'
# book = load_workbook(file_path)
# sheet = book.active

# 将数据从 openpyxl 转换为 pandas DataFrame
data = df_data.values
columns =["编号","汽车名称","表显里程","图片"] # 获取第一行作为列名
df = pd.DataFrame(data, columns=columns)

# 数据清洗：去掉价格中的符号，并转换为数值类型
df['表显里程'] = df['表显里程'].replace('[万公里,]', '', regex=True).astype(float)

# 数据统计
total_rows = df.shape[0]  # 总行数
unique_products = df['汽车名称'].nunique()  # 商品名的唯一数量
average_price = df['表显里程'].mean()  # 平均价格
price_range = (df['表显里程'].min(), df['表显里程'].max())  # 里程范围

# 输出统计结果
print(f"总行数：{total_rows}")
print(f"不同汽车数量：{unique_products}")
print(f"平均表显里程：{average_price:.2f}")
print(f"里程范围：{price_range}")

# 绘制直方图
plt.figure(figsize=(10, 6))
plt.hist(df['表显里程'], bins=20, color='yellow', edgecolor='blue')
plt.xlabel('表显里程（万公里）')
plt.ylabel('汽车数量')
plt.title('汽车表显里程分布')
plt.grid(True)

# 在图表上添加统计结果文本框
stats_text = (
    f"总行数：{total_rows}\n"
    f"不同汽车数量：{unique_products}\n"
    f"平均里程：{average_price:.2f} 万公里\n"
    f"表显里程范围：{price_range[0]} - {price_range[1]} 万公里"
)
plt.gca().text(0.95, 0.95, stats_text, fontsize=10, verticalalignment='top', horizontalalignment='right',
               bbox=dict(facecolor='red', alpha=0.6), transform=plt.gca().transAxes)

plt.show()

# 分析结论
content = f"""
总行数：{total_rows}
不同汽车数量：{unique_products}
平均表显里程：{average_price:.2f} 万公里
表显里程范围：{price_range[0]} - {price_range[1]} 万公里


"""
#
# 发送邮件

send_email("1752106450@qq.com", "wcb/汽车里程数据分析", content)
