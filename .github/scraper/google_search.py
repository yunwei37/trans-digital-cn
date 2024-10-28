import os
import json
import requests
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print(f"Current working directory: {os.getcwd()}")
print(f"Environment variables loaded: GOOGLE_API_KEY={os.getenv('GOOGLE_API_KEY')}, GOOGLE_SEARCH_ENGINE_ID={os.getenv('GOOGLE_SEARCH_ENGINE_ID')}")

class GoogleSearchAPI:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        print(f"API Key: {self.api_key}")
        print(f"Search Engine ID: {self.search_engine_id}")
        if not self.api_key or not self.search_engine_id:
            raise ValueError("需要设置 GOOGLE_API_KEY 和 GOOGLE_SEARCH_ENGINE_ID 环境变量")
        
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, 
               query: str, 
               total_results: int = 100,
               language: str = 'lang_zh',
               country: str = 'countryCN') -> List[Dict]:
        """
        执行Google自定义搜索，支持分页获取大量结果
        
        Args:
            query: 搜索关键词
            total_results: 需要获取的总结果数
            language: 语言限制 (默认中文)
            country: 国家限制 (默认中国)
        """
        all_results = []
        results_per_page = 10  # Google API 每页最多10条
        total_pages = (total_results + results_per_page - 1) // results_per_page

        print(f"开始搜索: {query}")
        print(f"计划获取: {total_results} 条结果")

        for page in range(total_pages):
            print(f"搜索进度: {page + 1}/{total_pages}")
            start_index = page * results_per_page + 1
            
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': results_per_page,
                'start': start_index,
                'lr': language,
                'cr': country
            }

            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                if 'items' in data:
                    for item in data['items']:
                        result = {
                            'title': item.get('title'),
                            'link': item.get('link'),
                            'snippet': item.get('snippet'),
                            'pagemap': item.get('pagemap', {})
                        }
                        all_results.append(result)
                        
                        # 实时打印每条结果
                        print(f"\n标题: {result['title']}")
                        print(f"链接: {result['link']}")
                        print(f"摘要: {result['snippet']}")
                        print("-" * 80)

                # API 限制：每秒最多一次请求
                time.sleep(1)

                # 如果没有更多结果，提前退出
                if 'queries' in data and 'nextPage' not in data['queries']:
                    print(f"没有更多结果，已获取 {len(all_results)} 条")
                    break

            except requests.exceptions.RequestException as e:
                print(f"搜索出错: {e}")
                break

        print(f"\n搜索完成！共获取 {len(all_results)} 条结果")
        return all_results

def save_results(results: List[Dict], filename: str):
    """保存搜索结果到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"结果已保存到: {filename}")

def main():
    search_client = GoogleSearchAPI()
    
    # 示例：搜索并获取1000条结果
    query = "跨性别"
    results = search_client.search(
        query=query,
        total_results=50,
        language='lang_zh',
        country='countryCN'
    )
    
    # 保存结果到文件
    save_results(results, f".github/scraper/search_results_{query[:10]}.json")

if __name__ == "__main__":
    main()
