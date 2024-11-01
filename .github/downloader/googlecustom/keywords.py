import json
import yaml
import os
from collections import defaultdict
from datetime import datetime

def extract_search_history(directory):
    # 使用字典来存储关键词和查询列表
    search_history = {}
    
    # 用于跟踪每个查询的累计结果
    query_items_count = {}
    
    # 遍历目录中的所有JSON文件
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                
                try:
                    # 从文件名中提取关键词
                    filename_parts = file.split('_')
                    if len(filename_parts) >= 3:
                        keyword = filename_parts[2].split('.')[0]
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # 如果关键词不存在，初始化一个空列表
                        if keyword not in search_history:
                            search_history[keyword] = []
                            
                        # 处理每个页面的数据
                        for page_data in data:
                            query = page_data.get('query')
                            timestamp = page_data.get('timestamp')
                            
                            # 初始化查询的计数器
                            if query not in query_items_count:
                                query_items_count[query] = 0
                            
                            # 从 queries.request[0].totalResults 中提取结果数量
                            total_results = None
                            if 'response' in page_data:
                                queries = page_data['response'].get('queries', {})
                                request = queries.get('request', [{}])[0]
                                total_results = request.get('totalResults')
                                
                                # 累计 items 数量
                                items = page_data['response'].get('items', [])
                                query_items_count[query] += len(items)
                            
                            # 创建或更新查询记录
                            query_record = {
                                'query': query,
                                'engines': [{
                                    'name': 'google',
                                    'total_results': total_results,
                                    'searched_results': query_items_count[query],  # 使用累计值
                                    'last_search_date': timestamp
                                }],
                                'last_search': timestamp
                            }
                            
                            # 检查是否已存在相同的查询
                            existing_query = next(
                                (item for item in search_history[keyword] if item['query'] == query),
                                None
                            )
                            
                            if existing_query:
                                # 更新现有记录，保持累计的搜索结果数
                                existing_query.update(query_record)
                            else:
                                # 添加新记录
                                search_history[keyword].append(query_record)
                                
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    
    return search_history

def save_to_yaml(data, output_file):
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

def main():
    # 包含搜索结果的目录
    search_dir = '.github/downloader/googlecustom'
    
    # 输出文件
    output_file = '.github/downloader/googlecustom/keywords.yml'
    
    # 提取搜索历史
    history = extract_search_history(search_dir)
    
    # 保存结果
    save_to_yaml(history, output_file)
    
    # 打印统计信息
    print(f"Processed search history for {len(history)} keywords")
    total_queries = sum(len(queries) for queries in history.values())
    print(f"Total unique queries: {total_queries}")

if __name__ == "__main__":
    main()