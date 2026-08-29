#!/usr/bin/env python3
import csv
import json
import sys
from collections import Counter


def analyze_csv(filepath: str) -> dict:
    """
    分析指定的 CSV 文件并返回统计摘要。
    返回包括每个列的类型、缺失值、主要统计信息（数值型/分类型）。
    """
    # 打开 CSV 文件并使用 DictReader 读取每一行为字典
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # 如果没有有效行，返回错误信息
    if not rows:
        return {"error": "CSV file is empty or has no data rows"}

    columns = list(rows[0].keys())  # 所有字段名
    total_rows = len(rows)  # 行总数

    column_stats = {}
    for col in columns:
        # 提取非空数据用于统计分析
        values = [row[col] for row in rows if row[col].strip()]
        non_empty = len(values)  # 非空数据条数
        missing = total_rows - non_empty  # 缺失值数量

        # 尝试将值转为数值型（支持数值型统计）
        numeric_values = []
        for v in values:
            try:
                numeric_values.append(float(v))
            except ValueError:
                pass  # 非法数值则跳过

        # 若超半数可转为数值类型，则按数值型处理
        if len(numeric_values) > len(values) * 0.5:
            sorted_nums = sorted(numeric_values)
            column_stats[col] = {
                "type": "numeric",
                "count": non_empty,
                "missing": missing,
                "min": round(sorted_nums[0], 2),
                "max": round(sorted_nums[-1], 2),
                "mean": round(sum(sorted_nums) / len(sorted_nums), 2),
                "median": round(sorted_nums[len(sorted_nums) // 2], 2),
            }
        else:
            # 作为分类型列处理，统计唯一值、前5高频值等
            freq = Counter(values).most_common(5)
            column_stats[col] = {
                "type": "categorical",
                "count": non_empty,
                "missing": missing,
                "unique_values": len(set(values)),
                "top_values": [{"value": v, "count": c} for v, c in freq],
            }

    # 汇总并返回全表统计结果
    return {
        "file": filepath,
        "total_rows": total_rows,
        "total_columns": len(columns),
        "columns": columns,
        "column_stats": column_stats,
    }


if __name__ == "__main__":
    try:
        # 检查参数，调用分析主函数
        if len(sys.argv) > 1:
            result = analyze_csv(sys.argv[1])
        else:
            # 缺少文件路径参数
            print(json.dumps({"error": "Please provide a CSV file path"}))
            sys.exit(1)

        # 输出分析结果（美化格式，支持中文内容）
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except FileNotFoundError:
        # 文件不存在时的异常处理
        print(json.dumps({"error": f"File not found: {sys.argv[1]}"}))
        sys.exit(1)
    except Exception as e:
        # 其他异常的统一处理
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
