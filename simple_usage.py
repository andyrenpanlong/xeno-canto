#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的使用示例 - 方便集成
"""

from xeno_canto_scraper import XenoCantoScraper

# 你的API密钥
API_KEY = "7e94cbc3decd67738d940c5e4d82fc7c290811ed"

def quick_download(bird_name, num_files=5):
    """
    快速下载指定鸟类的录音
    
    Args:
        bird_name: 鸟类名称（英文名或学名）
        num_files: 要下载的文件数量
    """
    scraper = XenoCantoScraper(api_key=API_KEY)
    
    print(f"正在下载 '{bird_name}' 的 {num_files} 个录音文件...")
    
    # 获取数据并下载
    recordings = scraper.get_recordings_with_download(
        bird_name=bird_name,
        max_pages=2,
        max_downloads=num_files
    )
    
    if recordings:
        print(f"成功！下载了 {bird_name} 的录音文件")
        return recordings
    else:
        print(f"未找到 {bird_name} 的录音数据")
        return []

def search_only(bird_name, max_results=50):
    """
    只搜索数据，不下载文件
    
    Args:
        bird_name: 鸟类名称
        max_results: 最大结果数量
    """
    scraper = XenoCantoScraper(api_key=API_KEY)
    
    recordings = scraper.get_all_recordings(bird_name, max_pages=3)
    
    if recordings:
        # 保存为CSV和JSON
        safe_name = bird_name.replace(' ', '_')
        scraper.save_to_csv(recordings[:max_results], f"{safe_name}_data.csv")
        scraper.save_to_json(recordings[:max_results], f"{safe_name}_data.json")
        
        print(f"找到 {len(recordings)} 条 '{bird_name}' 的数据")
        print(f"已保存前 {min(len(recordings), max_results)} 条到文件")
        
        return recordings[:max_results]
    else:
        print(f"未找到 '{bird_name}' 的数据")
        return []

if __name__ == "__main__":
    # 示例1: 快速下载
    print("=== 示例1: 快速下载录音 ===")
    quick_download("Robin", 3)
    
    print("\n" + "="*50 + "\n")
    
    # 示例2: 只获取数据
    print("=== 示例2: 只获取数据 ===")
    search_only("Passer domesticus", 20)
    
    print("\n" + "="*50 + "\n")
    
    # 示例3: 批量处理
    print("=== 示例3: 批量处理 ===")
    birds = ["Cardinal", "Blue Jay", "Sparrow"]
    
    for bird in birds:
        print(f"\n处理: {bird}")
        recordings = search_only(bird, 10)
        if recordings:
            print(f"  获得 {len(recordings)} 条数据")
