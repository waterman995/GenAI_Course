# 导入aiohttp库，用于异步HTTP请求
import aiohttp
# 导入asyncio库，用于异步编程
import asyncio
# 导入pandas库，用于数据处理和分析
import pandas as pd
# 从bs4库中导入BeautifulSoup类，用于解析HTML文档
from bs4 import BeautifulSoup

# 定义目标URL，确保这是CVPR 2024论文的正确URL
url = 'https://openaccess.thecvf.com/CVPR2024?day=2024-06-19'

# 定义请求头，模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 异步函数fetch，用于发送GET请求并返回响应文本
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()  # 返回响应的文本内容

# 主异步函数，负责整体流程控制
async def main():
    # 创建一个带有请求头的异步HTTP会话
    async with aiohttp.ClientSession(headers=headers) as session:
        # 获取目标网页的HTML内容
        html = await fetch(session, url)
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'lxml')
        # 查找所有论文标题的标签
        papers = soup.find_all('dt', class_='ptitle')
        if not papers:
            print("未找到论文。请检查类名或网站结构。")
        # 初始化数据列表，用于存储论文信息
        data = []
        # 创建任务列表，用于并发获取每篇论文的详细信息
        tasks = []
        for paper in papers:
            a_tag = paper.find('a')  # 查找论文标题的链接标签
            if a_tag:
                title = a_tag.text.strip()  # 获取论文标题
                link = a_tag['href']  # 获取论文链接
                paper_url = f'https://openaccess.thecvf.com{link}'  # 构造完整的论文URL
                # 将获取论文详细信息的任务添加到任务列表中
                tasks.append(fetch_paper_details(session, paper_url, title))
                
        # 并发执行所有任务，并获取结果
        data = await asyncio.gather(*tasks)

        return data  # 返回所有论文的信息

# 异步函数fetch_paper_details，用于获取论文的详细信息
async def fetch_paper_details(session, paper_url, title):
    paper_html = await fetch(session, paper_url)  # 获取论文页面的HTML
    paper_soup = BeautifulSoup(paper_html, 'lxml')  # 解析HTML
    # 获取作者信息
    authors = [meta['content'] for meta in paper_soup.find_all('meta', {'name': 'citation_author'})]
    # 获取摘要信息
    abstract_div = paper_soup.find('div', id='abstract')
    abstract = abstract_div.text.strip() if abstract_div else 'N/A'
    # 获取PDF下载链接
    pdf_url_meta = paper_soup.find('meta', {'name': 'citation_pdf_url'})
    pdf_url = pdf_url_meta['content'] if pdf_url_meta else 'N/A'
    # 返回包含论文详细信息的字典
    return {
        'title': title,  # 论文标题
        'authors': ', '.join(authors),  # 作者列表
        'abstract': abstract,  # 摘要
        'pdf_url': pdf_url  # PDF下载链接
    }

# 主程序入口
if __name__ == "__main__":
    # 运行主异步函数
    data = asyncio.run(main())
    # 将数据转换为DataFrame
    df = pd.DataFrame(data)
    # 获取用户输入的保存路径
    save_path = input("请输入要保存数据集的路径（例如，'papers.csv'）：")
    # 将DataFrame保存为CSV文件
    df.to_csv(save_path, index=False)
    print(f"数据已成功抓取并保存到 {save_path}。")
