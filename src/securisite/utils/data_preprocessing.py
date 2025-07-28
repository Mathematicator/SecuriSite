"""
Data preprocessing utilities for SecuriSite-IA
Fixes JSON format issues and prepares data for agent analysis
"""

import json
import os
from pathlib import Path

def fix_json_format_single_line(input_path, output_path=None):
    """
    Fixes the single-line JSON format to pretty-printed format for better debugging
    """
    if output_path is None:
        output_path = input_path.replace('.json', '_fixed.json')
    
    try:
        # Load the JSON data (works even if single line)
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Write pretty-formatted JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
        
        print(f"✅ Fixed JSON format: {input_path} -> {output_path}")
        return {"status": "success", "output_path": output_path, "original_size": os.path.getsize(input_path)}