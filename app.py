import os
from dotenv import load_dotenv
import google.generativeai as genai

# 配置gemini api
################################################
load_dotenv()

def create_gemini():
    # 从环境变量获取API密钥
    api_key = os.environ.get("GEMINI_API_KEY")  
    # 配置Gemini
    if api_key:
        genai.configure(api_key=api_key)
        return True
    else:
        raise ValueError("未找到API密钥，请设置环境变量API_KEY")



# 读取rss源
def fetch_feed(url, log_file):
    feed = None
    response = None
    headers = {}
    try:
        ua = UserAgent()
        headers['User-Agent'] = ua.random.strip()
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            feed = feedparser.parse(response.text)
            return {'feed': feed, 'status': 'success'}
        else:
            with open(log_file, 'a') as f:
                f.write(f"Fetch error: {response.status_code}\n")
            return {'feed': None, 'status': response.status_code}
    except requests.RequestException as e:
        with open(log_file, 'a') as f:
            f.write(f"Fetch error: {e}\n")
        return {'feed': None, 'status': 'failed'}
    
# 从rss源中提取文章
def extract_articles(feed):

# 截断本地内存
def truncate_entries(entries, max_entries):
    if len(entries) > max_entries:
        entries = entries[:max_entries]
    return entries


# 清理每一篇文章的content，用于交给gemini总结
def clean_html(html_content):
    """
    This function is used to clean the HTML content.
    It will remove all the <script>, <style>, <img>, <a>, <video>, <audio>, <iframe>, <input> tags.
    Returns:
        Cleaned text for summarization
    """
    soup = BeautifulSoup(html_content, "html.parser")

    for script in soup.find_all("script"):
        script.decompose()

    for style in soup.find_all("style"):
        style.decompose()

    for img in soup.find_all("img"):
        img.decompose()

    for a in soup.find_all("a"):
        a.decompose()

    for video in soup.find_all("video"):
        video.decompose()

    for audio in soup.find_all("audio"):
        audio.decompose()
    
    for iframe in soup.find_all("iframe"):
        iframe.decompose()
    
    for input in soup.find_all("input"):
        input.decompose()

    return soup.get_text()



# 清洗html文档
def clean_html():



# 把html文档传递给chatgpt，让他总结
model = genai.GenerativeModel("gemini-1.5-flash")

def gemini_summary(query, language, keyword_length, summary_length):
    
    # 根据语言设置提示词
    if language == "zh":
        prompt = f"""请用中文总结这篇文章:
        1. 先提取出{keyword_length}个关键词,在同一行输出
        2. 然后换行
        3. 用中文在{summary_length}字内写一个包含所有要点的总结
        4. 按顺序分要点输出
        5. 必须按照以下格式输出: '<br><br>总结:'
        
        文章内容:
        {query}
        """
    else:
        prompt = f"""Please summarize this article in {language}:
        1. First extract {keyword_length} keywords, output in one line
        2. Then line break
        3. Write a summary containing all points in {summary_length} words
        4. Output points in order
        5. Must follow this format: '<br><br>Summary:'
        
        Article content:
        {query}
        """
    
    try:
        # 生成响应
        response = model.generate_content(prompt)
        
        # 返回生成的文本
        return response.text
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return ""