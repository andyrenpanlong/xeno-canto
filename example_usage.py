#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xeno-canto 爬虫使用示例
"""

from xeno_canto_scraper import XenoCantoScraper

def search_specific_bird():
    """搜索特定鸟类的示例"""
    api_key = "7e94cbc3decd67738d940c5e4d82fc7c290811ed"
    scraper = XenoCantoScraper(api_key=api_key)
    
    # 搜索知更鸟
    bird_name = "Robin"
    print(f"搜索 '{bird_name}' 的录音数据...")
    
    recordings = scraper.get_all_recordings(bird_name, max_pages=3)
    
    if recordings:
        print(f"找到 {len(recordings)} 条录音")
        
        # 保存数据
        scraper.save_to_csv(recordings, f"{bird_name}_recordings.csv")
        scraper.save_to_json(recordings, f"{bird_name}_recordings.json")
        
        # 显示一些统计信息
        countries = set(rec.get('cnt', '') for rec in recordings if rec.get('cnt'))
        print(f"录音来自 {len(countries)} 个国家: {', '.join(sorted(countries))}")
        
        types = set(rec.get('type', '') for rec in recordings if rec.get('type'))
        print(f"声音类型: {', '.join(sorted(types))}")

def search_multiple_birds():
    """批量搜索多种鸟类的示例"""
    api_key = "7e94cbc3decd67738d940c5e4d82fc7c290811ed"
    scraper = XenoCantoScraper(api_key=api_key)
    
    # 常见鸟类列表
    bird_list = [
        "Passer domesticus",    # 家麻雀
        "Turdus migratorius",   # 美洲知更鸟
        "Corvus brachyrhynchos", # 美洲乌鸦
        "Sturnus vulgaris",     # 欧洲椋鸟
        "Hirundo rustica"       # 家燕
    ]
    
    print("批量搜索鸟类数据...")
    results = scraper.batch_search(bird_list, output_dir="bird_collection")
    
    # 显示结果摘要
    print("\n=== 采集结果摘要 ===")
    for bird_name, recordings in results.items():
        print(f"{bird_name}: {len(recordings)} 条录音")

def search_by_country():
    """按国家搜索的示例"""
    scraper = XenoCantoScraper()
    
    # 搜索中国的鸟类录音
    print("搜索中国的鸟类录音...")
    
    # 使用 cnt:china 参数搜索
    params_url = f"{scraper.base_url}?query=cnt:china"
    response = scraper.session.get(params_url)
    
    if response.status_code == 200:
        data = response.json()
        recordings = data.get('recordings', [])
        print(f"找到 {len(recordings)} 条中国的鸟类录音")
        
        if recordings:
            # 统计物种
            species = set()
            for rec in recordings:
                if rec.get('gen') and rec.get('sp'):
                    species.add(f"{rec['gen']} {rec['sp']}")
            
            print(f"涉及 {len(species)} 个物种")
            print("前10个物种:")
            for i, sp in enumerate(sorted(species)[:10]):
                print(f"  {i+1}. {sp}")

if __name__ == "__main__":
    print("=== Xeno-canto 爬虫使用示例 ===\n")
    
    # 选择要运行的示例
    print("选择要运行的示例:")
    print("1. 搜索特定鸟类")
    print("2. 批量搜索多种鸟类")
    print("3. 按国家搜索")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == "1":
        search_specific_bird()
    elif choice == "2":
        search_multiple_birds()
    elif choice == "3":
        search_by_country()
    else:
        print("无效选择，运行默认示例...")
        search_specific_bird()
