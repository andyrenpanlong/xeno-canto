#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xeno-canto 鸟类数据爬虫
支持按鸟类名称搜索和批量采集数据
使用网页爬取方式，无需API密钥
"""

import requests
import json
import time
import csv
from typing import List, Dict, Optional
from urllib.parse import quote, urlencode, urlparse
import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

class XenoCantoScraper:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key:
            # 使用API方式
            self.base_url = "https://xeno-canto.org/api/3/recordings"
        else:
            # 使用网页爬取方式
            self.search_url = "https://xeno-canto.org/explore"
            
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def search_bird_api(self, bird_name: str, page: int = 1) -> Dict:
        """
        使用API搜索指定鸟类的录音数据（需要API密钥）
        API v3需要使用标签格式查询
        """
        if not self.api_key:
            raise ValueError("API密钥未设置，请使用网页爬取方式")
        
        # 构建查询字符串 - API v3使用标签格式
        # 如果是学名格式（包含空格），使用gen和sp标签
        if ' ' in bird_name and len(bird_name.split()) >= 2:
            parts = bird_name.split()
            query = f"gen:{parts[0]} sp:{parts[1]}"
        else:
            # 否则尝试作为英文名或属名搜索
            query = f"en:{bird_name}"
            
        params = {
            'query': query,
            'page': page,
            'key': self.api_key
        }
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API请求失败: {e}")
            # 如果英文名查询失败，尝试作为属名查询
            if 'en:' in query:
                try:
                    params['query'] = f"gen:{bird_name}"
                    response = self.session.get(self.base_url, params=params)
                    response.raise_for_status()
                    return response.json()
                except:
                    pass
            return {}
    
    def search_bird_web(self, bird_name: str, page: int = 1) -> Dict:
        """
        使用网页爬取方式搜索指定鸟类的录音数据
        
        Args:
            bird_name: 鸟类名称（英文或学名）
            page: 页码，默认为1
            
        Returns:
            包含搜索结果的字典
        """
        params = {
            'query': bird_name,
            'pg': page
        }
        
        try:
            response = self.session.get(self.search_url, params=params)
            response.raise_for_status()
            
            # 解析HTML页面
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找录音数据
            recordings = []
            
            # 查找所有录音条目
            recording_rows = soup.find_all('tr', class_='results-row')
            
            for row in recording_rows:
                recording_data = self._parse_recording_row(row)
                if recording_data:
                    recordings.append(recording_data)
            
            # 获取总页数信息
            pagination = soup.find('div', class_='pagination')
            total_pages = 1
            if pagination:
                page_links = pagination.find_all('a')
                if page_links:
                    try:
                        total_pages = max([int(link.text) for link in page_links if link.text.isdigit()])
                    except:
                        pass
            
            return {
                'recordings': recordings,
                'page': page,
                'numPages': total_pages,
                'numRecordings': len(recordings)
            }
            
        except requests.RequestException as e:
            print(f"网页请求失败: {e}")
            return {}
        except Exception as e:
            print(f"解析失败: {e}")
            return {}
    
    def _parse_recording_row(self, row) -> Optional[Dict]:
        """
        解析单个录音行的数据
        """
        try:
            data = {}
            
            # 获取录音ID和基本信息
            id_cell = row.find('td', class_='results-id')
            if id_cell:
                id_link = id_cell.find('a')
                if id_link and id_link.get('href'):
                    # 从URL中提取ID
                    href = id_link.get('href')
                    id_match = re.search(r'/(\d+)', href)
                    if id_match:
                        data['id'] = id_match.group(1)
                        data['url'] = f"https://xeno-canto.org{href}"
            
            # 获取物种信息
            species_cell = row.find('td', class_='results-species')
            if species_cell:
                species_link = species_cell.find('a')
                if species_link:
                    species_text = species_link.get_text(strip=True)
                    # 解析学名和英文名
                    if ' - ' in species_text:
                        scientific, english = species_text.split(' - ', 1)
                        data['scientific_name'] = scientific.strip()
                        data['en'] = english.strip()
                        
                        # 分离属名和种名
                        if ' ' in scientific:
                            parts = scientific.split()
                            data['gen'] = parts[0]
                            data['sp'] = parts[1] if len(parts) > 1 else ''
            
            # 获取国家信息
            country_cell = row.find('td', class_='results-country')
            if country_cell:
                data['cnt'] = country_cell.get_text(strip=True)
            
            # 获取地点信息
            location_cell = row.find('td', class_='results-location')
            if location_cell:
                data['loc'] = location_cell.get_text(strip=True)
            
            # 获取录音者信息
            recordist_cell = row.find('td', class_='results-recordist')
            if recordist_cell:
                data['rec'] = recordist_cell.get_text(strip=True)
            
            # 获取日期信息
            date_cell = row.find('td', class_='results-date')
            if date_cell:
                data['date'] = date_cell.get_text(strip=True)
            
            # 获取声音类型
            type_cell = row.find('td', class_='results-type')
            if type_cell:
                data['type'] = type_cell.get_text(strip=True)
            
            # 获取质量评级
            quality_cell = row.find('td', class_='results-quality')
            if quality_cell:
                quality_text = quality_cell.get_text(strip=True)
                data['q'] = quality_text
            
            return data if data else None
            
        except Exception as e:
            print(f"解析录音行失败: {e}")
            return None
    
    def search_bird(self, bird_name: str, page: int = 1) -> Dict:
        """
        搜索指定鸟类的录音数据（自动选择API或网页方式）
        """
        if self.api_key:
            return self.search_bird_api(bird_name, page)
        else:
            return self.search_bird_web(bird_name, page)
    
    def get_all_recordings(self, bird_name: str, max_pages: int = 10) -> List[Dict]:
        """
        获取指定鸟类的所有录音数据
        
        Args:
            bird_name: 鸟类名称
            max_pages: 最大页数限制
            
        Returns:
            录音数据列表
        """
        all_recordings = []
        page = 1
        
        print(f"开始采集 '{bird_name}' 的数据...")
        
        while page <= max_pages:
            print(f"正在获取第 {page} 页数据...")
            data = self.search_bird(bird_name, page)
            
            if not data or 'recordings' not in data:
                break
                
            recordings = data['recordings']
            if not recordings:
                break
                
            all_recordings.extend(recordings)
            
            # 检查是否还有更多页面
            if len(recordings) < 500:  # xeno-canto每页最多500条记录
                break
                
            page += 1
            time.sleep(1)  # 避免请求过于频繁
            
        print(f"'{bird_name}' 数据采集完成，共获取 {len(all_recordings)} 条记录")
        return all_recordings    

    def extract_recording_info(self, recording: Dict) -> Dict:
        """
        提取录音的关键信息
        
        Args:
            recording: 原始录音数据
            
        Returns:
            提取后的录音信息
        """
        return {
            'id': recording.get('id'),
            'gen': recording.get('gen'),  # 属名
            'sp': recording.get('sp'),    # 种名
            'ssp': recording.get('ssp'),  # 亚种
            'en': recording.get('en'),    # 英文名
            'rec': recording.get('rec'),  # 录音者
            'cnt': recording.get('cnt'),  # 国家
            'loc': recording.get('loc'),  # 地点
            'lat': recording.get('lat'),  # 纬度
            'lng': recording.get('lng'),  # 经度
            'alt': recording.get('alt'),  # 海拔
            'type': recording.get('type'), # 声音类型
            'sex': recording.get('sex'),   # 性别
            'stage': recording.get('stage'), # 生长阶段
            'method': recording.get('method'), # 录音方法
            'url': recording.get('url'),   # 录音URL
            'file': recording.get('file'), # 文件URL
            'file_name': recording.get('file-name'), # 文件名
            'sono': recording.get('sono'),  # 声谱图
            'osci': recording.get('osci'),  # 波形图
            'lic': recording.get('lic'),    # 许可证
            'q': recording.get('q'),        # 质量评级
            'length': recording.get('length'), # 时长
            'time': recording.get('time'),  # 录音时间
            'date': recording.get('date'),  # 录音日期
            'uploaded': recording.get('uploaded'), # 上传日期
            'also': recording.get('also'),  # 其他物种
            'rmk': recording.get('rmk'),    # 备注
            'bird_seen': recording.get('bird-seen'), # 是否看到鸟
            'animal_seen': recording.get('animal-seen'), # 是否看到动物
            'playback_used': recording.get('playback-used'), # 是否使用回放
            'temp': recording.get('temp'),  # 温度
            'regnr': recording.get('regnr'), # 区域编号
            'auto': recording.get('auto'),  # 自动录音
            'dvc': recording.get('dvc'),    # 设备
            'mic': recording.get('mic'),    # 麦克风
            'smp': recording.get('smp')     # 采样率
        }
    
    def save_to_csv(self, recordings: List[Dict], filename: str):
        """
        将录音数据保存为CSV文件
        
        Args:
            recordings: 录音数据列表
            filename: 输出文件名
        """
        if not recordings:
            print("没有数据需要保存")
            return
            
        # 提取所有录音的信息
        processed_recordings = [self.extract_recording_info(rec) for rec in recordings]
        
        # 获取所有字段名
        fieldnames = set()
        for rec in processed_recordings:
            fieldnames.update(rec.keys())
        fieldnames = sorted(list(fieldnames))
        
        # 写入CSV文件
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_recordings)
            
        print(f"数据已保存到 {filename}")
    
    def save_to_json(self, recordings: List[Dict], filename: str):
        """
        将录音数据保存为JSON文件
        
        Args:
            recordings: 录音数据列表
            filename: 输出文件名
        """
        processed_recordings = [self.extract_recording_info(rec) for rec in recordings]
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(processed_recordings, jsonfile, ensure_ascii=False, indent=2)
            
        print(f"数据已保存到 {filename}")
    
    def batch_search(self, bird_names: List[str], output_dir: str = "bird_data"):
        """
        批量搜索多个鸟类的数据
        
        Args:
            bird_names: 鸟类名称列表
            output_dir: 输出目录
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        all_data = {}
        
        for bird_name in bird_names:
            recordings = self.get_all_recordings(bird_name)
            if recordings:
                all_data[bird_name] = recordings
                
                # 为每个鸟类单独保存文件
                safe_name = bird_name.replace(' ', '_').replace('/', '_')
                csv_filename = os.path.join(output_dir, f"{safe_name}.csv")
                json_filename = os.path.join(output_dir, f"{safe_name}.json")
                
                self.save_to_csv(recordings, csv_filename)
                self.save_to_json(recordings, json_filename)
            
            time.sleep(2)  # 避免请求过于频繁
        
        # 保存汇总数据
        summary_file = os.path.join(output_dir, "summary.json")
        summary = {
            bird_name: len(recordings) 
            for bird_name, recordings in all_data.items()
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            
        print(f"\n批量采集完成！共采集 {len(all_data)} 种鸟类的数据")
        print(f"数据保存在 {output_dir} 目录中")
        
        return all_data
    
    def download_recording(self, recording: Dict, download_dir: str = "recordings") -> bool:
        """
        下载单个录音文件
        
        Args:
            recording: 录音数据字典
            download_dir: 下载目录
            
        Returns:
            下载是否成功
        """
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        # 获取录音文件URL
        file_url = recording.get('file')
        if not file_url:
            print(f"录音 {recording.get('id', 'unknown')} 没有文件URL")
            return False
        
        # 构建文件名
        recording_id = recording.get('id', 'unknown')
        gen = recording.get('gen', '')
        sp = recording.get('sp', '')
        
        # 从URL获取文件扩展名
        parsed_url = urlparse(file_url)
        file_ext = os.path.splitext(parsed_url.path)[1] or '.mp3'
        
        # 创建安全的文件名
        if gen and sp:
            filename = f"{recording_id}_{gen}_{sp}{file_ext}"
        else:
            filename = f"{recording_id}{file_ext}"
        
        # 清理文件名中的非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filepath = os.path.join(download_dir, filename)
        
        # 检查文件是否已存在
        if os.path.exists(filepath):
            print(f"文件已存在: {filename}")
            return True
        
        try:
            print(f"下载录音: {filename}")
            response = self.session.get(file_url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"下载完成: {filename}")
            return True
            
        except Exception as e:
            print(f"下载失败 {filename}: {e}")
            # 删除不完整的文件
            if os.path.exists(filepath):
                os.remove(filepath)
            return False
    
    def download_recordings_batch(self, recordings: List[Dict], download_dir: str = "recordings", max_downloads: int = 10) -> int:
        """
        批量下载录音文件
        
        Args:
            recordings: 录音数据列表
            download_dir: 下载目录
            max_downloads: 最大下载数量（避免下载过多文件）
            
        Returns:
            成功下载的文件数量
        """
        if not recordings:
            print("没有录音数据需要下载")
            return 0
        
        print(f"准备下载 {min(len(recordings), max_downloads)} 个录音文件...")
        
        success_count = 0
        for i, recording in enumerate(recordings[:max_downloads]):
            print(f"进度: {i+1}/{min(len(recordings), max_downloads)}")
            
            if self.download_recording(recording, download_dir):
                success_count += 1
            
            # 添加延时避免请求过于频繁
            time.sleep(1)
        
        print(f"批量下载完成！成功下载 {success_count} 个文件")
        return success_count
    
    def get_recordings_with_download(self, bird_name: str, max_pages: int = 2, max_downloads: int = 5, download_dir: str = None) -> List[Dict]:
        """
        获取录音数据并下载文件
        
        Args:
            bird_name: 鸟类名称
            max_pages: 最大页数
            max_downloads: 最大下载数量
            download_dir: 下载目录，默认为 recordings/{bird_name}
            
        Returns:
            录音数据列表
        """
        # 获取录音数据
        recordings = self.get_all_recordings(bird_name, max_pages)
        
        if not recordings:
            return []
        
        # 设置下载目录
        if download_dir is None:
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', bird_name)
            download_dir = os.path.join("recordings", safe_name)
        
        # 下载录音文件
        self.download_recordings_batch(recordings, download_dir, max_downloads)
        
        return recordings


def main():
    """主函数 - 测试爬虫功能"""
    # 使用API密钥
    api_key = "7e94cbc3decd67738d940c5e4d82fc7c290811ed"
    scraper = XenoCantoScraper(api_key=api_key)
    
    # 测试用的鸟类名称
    test_birds = [
        "Turdus migratorius",  # 美洲知更鸟
        "Passer domesticus",   # 家麻雀
        "Corvus brachyrhynchos", # 美洲乌鸦
        "Cardinalidae",        # 红雀科
        "Robin"                # 知更鸟（通用名）
    ]
    
    print("=== Xeno-canto 鸟类数据爬虫测试 ===\n")
    
    # 单个鸟类测试
    print("1. 单个鸟类数据采集和下载测试:")
    test_bird = "Robin"
    recordings = scraper.get_recordings_with_download(test_bird, max_pages=1, max_downloads=3)
    
    if recordings:
        print(f"成功获取 {len(recordings)} 条 '{test_bird}' 的录音数据")
        
        # 显示第一条记录的详细信息
        if recordings:
            print("\n第一条记录示例:")
            first_record = scraper.extract_recording_info(recordings[0])
            for key, value in first_record.items():
                if value:  # 只显示有值的字段
                    print(f"  {key}: {value}")
                    
        # 保存数据到文件
        scraper.save_to_csv(recordings, f"{test_bird}_with_files.csv")
        scraper.save_to_json(recordings, f"{test_bird}_with_files.json")
    
    print(f"\n{'='*50}")
    
    # 批量采集测试
    print("2. 批量数据采集测试:")
    scraper.batch_search(test_birds[:3])  # 只测试前3个，避免请求过多


if __name__ == "__main__":
    main()
