import requests
from bs4 import BeautifulSoup
import time

def get_ssq_history(limit=30):
    """
    抓取双色球历史开奖数据
    :param limit: 需要抓取的期数
    :return: 包含字典的列表，每个字典是一期数据
    """
    results = []
    page = 1
    
    while len(results) < limit:
        url = f"http://kaijiang.zhcw.com/zhcw/html/ssq/list_{page}.html"
        print(f"正在抓取第 {page} 页: {url}")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='wqhgt')
            
            if not table:
                print("未找到数据表格，停止抓取。")
                break
                
            # 跳过表头（前两行）
            rows = table.find_all('tr')[2:]
            
            if not rows:
                print("当前页面没有数据，停止抓取。")
                break
                
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 3:
                    continue
                
                date = cols[0].text.strip()
                issue = cols[1].text.strip()
                
                # 提取红球和蓝球
                # 红球 class="rr"
                red_balls = [em.text.strip() for em in cols[2].find_all('em', class_='rr')]
                # 蓝球是最后一个 em，且通常没有 class="rr" (或者在红球之后)
                # 这里我们直接找所有的 em，然后根据红球数量来区分，或者直接看 class
                all_ems = cols[2].find_all('em')
                blue_ball = ""
                if all_ems:
                    # 假设最后一个是蓝球
                    blue_ball = all_ems[-1].text.strip()
                    
                    # 再次确认红球是否正确
                    if len(red_balls) != 6:
                         # 如果 class 方法失败，尝试前6个是红球
                         red_balls = [em.text.strip() for em in all_ems[:6]]
                
                if not red_balls or not blue_ball:
                    continue
                    
                results.append({
                    "date": date,
                    "issue": issue,
                    "red_balls": red_balls,
                    "blue_ball": blue_ball
                })
                
                if len(results) >= limit:
                    break
            
            page += 1
            # 礼貌性延迟
            time.sleep(1)
            
        except Exception as e:
            print(f"抓取页面 {page} 失败: {e}")
            break
            
    return results

if __name__ == "__main__":
    # 测试代码
    data = get_ssq_history(5)
    for item in data:
        print(item)
