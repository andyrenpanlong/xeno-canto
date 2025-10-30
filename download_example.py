#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xeno-canto 录音文件下载示例
"""

from xeno_canto_scraper import XenoCantoScraper
import os

def download_specific_bird():
    """下载特定鸟类录音的示例"""
    # 使用你的API密钥
    api_key = "7e94cbc3decd67738d940c5e4d82fc7c290811ed"
    scraper = XenoCantoScraper(api_key=api_key)
    
    # 选择要下载的鸟类
    bird_name = "Turdus migratorius"  # 美洲知更鸟
    print(f"开始下载 '{bird_name}' 的录音...")
    
    # 获取数据并下载录音文件（限制下载5个文件）
    recordings = scraper.get_recordings_with_download(
        bird_name=bird_name,
        max_pages=1,
        max_downloads=5,
        download_dir=f"recordings/{bird_name.replace(' ', '_')}"
    )
    
    if recordings:
        print(f"\n下载完成！获取了 {len(recordings)} 条录音数据")
        
        # 显示下载的文件信息
        download_dir = f"recordings/{bird_name.replace(' ', '_')}"
        if os.path.exists(download_dir):
            files = os.listdir(download_dir)
            print(f"下载的文件 ({len(files)} 个):")
            for file in files:
                file_path = os.path.join(download_dir, file)
                file_size = os.path.getsize(file_path) / 1024 / 1024  # MB
                print(f"  - {file} ({file_size:.2f} MB)")

def download_multiple_species():
    """下载多个物种录音的示例"""
    api_key = "7e94cbc3decd67738d940c5e4d82fc7c290811ed"
    scraper = XenoCantoScraper(api_key=api_key)
    
    # 要下载的鸟类列表
    bird_list = [
        "Passer domesticus",    # 家麻雀
        "Corvus brachyrhynchos", # 美洲乌鸦
        "Hirundo rustica"       # 家燕
    ]
    
    print("开始批量下载多个物种的录音...")
    
    for bird_name in bird_list:
        print(f"\n处理: {bird_name}")
        
        # 每个物种下载2-3个录音文件
        recordings = scraper.get_recordings_with_download(
            bird_name=bird_name,
            max_pages=1,
            max_downloads=3,
            download_dir=f"recordings/{bird_name.replace(' ', '_')}"
        )
        
        if recordings:
            print(f"  完成 {bird_name}: {len(recordings)} 条数据")
        else:
            print(f"  未找到 {bird_name} 的数据")

def download_high_quality_only():
    """只下载高质量录音的示例"""
    api_key = "7e94cbc3decd67738d940c5e4d82fc7c290811ed"
    scraper = XenoCantoScraper(api_key=api_key)
    
    bird_name = "Robin"
    print(f"搜索 '{bird_name}' 的高质量录音...")
    
    # 获取所有录音数据
    all_recordings = scraper.get_all_recordings(bird_name, max_pages=2)
    
    if all_recordings:
        # 筛选高质量录音（A级和B级）
        high_quality = [
            rec for rec in all_recordings 
            if rec.get('q') in ['A', 'B']
        ]
        
        print(f"找到 {len(high_quality)} 条高质量录音（共 {len(all_recordings)} 条）")
        
        if high_quality:
            # 下载高质量录音
            download_dir = f"recordings/high_quality_{bird_name}"
            success_count = scraper.download_recordings_batch(
                high_quality[:5],  # 最多下载5个
                download_dir=download_dir,
                max_downloads=5
            )
            
            print(f"成功下载 {success_count} 个高质量录音文件")

def show_download_info():
    """显示下载信息和统计"""
    recordings_dir = "recordings"
    
    if not os.path.exists(recordings_dir):
        print("还没有下载任何录音文件")
        return
    
    print("=== 下载统计 ===")
    
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk(recordings_dir):
        if files:
            species_name = os.path.basename(root)
            species_files = len(files)
            species_size = sum(
                os.path.getsize(os.path.join(root, f)) 
                for f in files
            ) / 1024 / 1024  # MB
            
            print(f"{species_name}: {species_files} 文件, {species_size:.2f} MB")
            total_files += species_files
            total_size += species_size
    
    print(f"\n总计: {total_files} 文件, {total_size:.2f} MB")

if __name__ == "__main__":
    print("=== Xeno-canto 录音下载示例 ===\n")
    
    print("选择要运行的示例:")
    print("1. 下载特定鸟类录音")
    print("2. 批量下载多个物种")
    print("3. 只下载高质量录音")
    print("4. 显示下载统计")
    
    choice = input("请输入选择 (1-4): ").strip()
    
    if choice == "1":
        download_specific_bird()
    elif choice == "2":
        download_multiple_species()
    elif choice == "3":
        download_high_quality_only()
    elif choice == "4":
        show_download_info()
    else:
        print("无效选择，运行默认示例...")
        download_specific_bird()
