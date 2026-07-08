#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LeetCode 本地多语言刷题仓库管理脚本。
支持新建题目模板和一键运行各语言测试。
"""

import argparse
import os
import re
import sys
import shutil
import json
import subprocess
from pathlib import Path

# 支持的语言映射
LANG_MAPPING = {
    "py": "python",
    "go": "go",
    "ts": "typescript",
    "rs": "rust",
    "c": "c",
    "cpp": "cpp",
    "java": "java"
}

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "scripts" / "templates"
PROBLEMS_DIR = BASE_DIR / "problems"

def get_problem_dir(problem_id: int) -> Path:
    """根据题目 ID 寻找已存在的题目目录，如果不存在则返回预期的路径（补零）"""
    prefix = f"{problem_id:04d}-"
    if PROBLEMS_DIR.exists():
        for path in PROBLEMS_DIR.iterdir():
            if path.is_dir() and path.name.startswith(prefix):
                return path
    return None

def update_cargo_toml(problem_dir_name: str):
    """向根目录 Cargo.toml 追加 Rust 工作空间成员"""
    cargo_path = BASE_DIR / "Cargo.toml"
    if not cargo_path.exists():
        return

    member_line = f'    "problems/{problem_dir_name}/rust",'
    content = cargo_path.read_text(encoding="utf-8")
    
    # 判断是否已经存在
    if member_line.strip() in content:
        return

    # 使用简单正则在 members = [ 下插入
    pattern = r'(members\s*=\s*\[)'
    match = re.search(pattern, content)
    if match:
        idx = match.end()
        new_content = content[:idx] + "\n" + member_line + content[idx:]
        cargo_path.write_text(new_content, encoding="utf-8")
        print(f"Cargo.toml: Added {member_line.strip()} to workspace members.")

def create_problem(args):
    """新建题目"""
    problem_id = args.id
    title = args.title.strip().lower().replace(" ", "-")
    method = args.method
    
    # 格式化文件夹名
    problem_dir_name = f"{problem_id:04d}-{title}"
    problem_dir = PROBLEMS_DIR / problem_dir_name
    
    if problem_dir.exists():
        print(f"Error: 题目目录已存在: {problem_dir}")
        sys.exit(1)
        
    problem_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 生成 README.md
    readme_template = TEMPLATES_DIR / "problem_readme.md"
    if readme_template.exists():
        content = readme_template.read_text(encoding="utf-8")
        content = content.replace("${problem_id}", str(problem_id))
        content = content.replace("${problem_title}", title.replace("-", " ").title())
        content = content.replace("${problem_slug}", title)
        content = content.replace("${problem_difficulty}", "Medium") # 默认 Medium
        content = content.replace("${problem_description}", "<!-- 在此粘贴 LeetCode 题目描述 -->")
        content = content.replace("${problem_thinking}", "")
        (problem_dir / "README.md").write_text(content, encoding="utf-8")
        print(f"Created: {problem_dir / 'README.md'}")

    # 2. 生成 testcases.json
    testcases_template = TEMPLATES_DIR / "testcases.json"
    if testcases_template.exists():
        shutil.copy(testcases_template, problem_dir / "testcases.json")
        print(f"Created: {problem_dir / 'testcases.json'}")

    # 3. 生成各语言模板
    langs = args.langs.split(",")
    for lang in langs:
        lang = lang.strip().lower()
        if lang not in LANG_MAPPING:
            print(f"Warning: 不支持的语言 {lang}，跳过")
            continue
            
        lang_dir_name = LANG_MAPPING[lang]
        lang_dir = problem_dir / lang_dir_name
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        # 预设占位符替换
        replacements = {
            "${problem_id}": str(problem_id),
            "${problem_id_str}": f"{problem_id:04d}",
            "${problem_title}": title.replace("-", " ").title(),
            "${method_name}": method,
            "${method_name_cap}": method[0].upper() + method[1:] if method else "",
            "${args}": "nums, target" if method == "twoSum" else "args",
            "${return_type}": "int[]" if lang == "java" else ("Vec<i32>" if lang == "rs" else ("number[]" if lang == "ts" else "[]")),
            "${zero_value}": "new int[0]" if lang == "java" else ("vec![]" if lang == "rs" else ("[]" if lang == "ts" else "nil"))
        }

        def replace_placeholders(tmpl_path: Path, target_path: Path):
            if not tmpl_path.exists():
                return
            txt = tmpl_path.read_text(encoding="utf-8")
            for k, v in replacements.items():
                txt = txt.replace(k, v)
            target_path.write_text(txt, encoding="utf-8")
            print(f"Created: {target_path}")

        if lang == "py":
            replace_placeholders(TEMPLATES_DIR / "solution.py", lang_dir / "solution.py")
        elif lang == "go":
            replace_placeholders(TEMPLATES_DIR / "solution.go", lang_dir / "solution.go")
            replace_placeholders(TEMPLATES_DIR / "solution_test.go", lang_dir / "solution_test.go")
        elif lang == "ts":
            replace_placeholders(TEMPLATES_DIR / "solution.ts.tmpl", lang_dir / "solution.ts")
            replace_placeholders(TEMPLATES_DIR / "solution.test.ts.tmpl", lang_dir / "solution.test.ts")
        elif lang == "rs":
            # Rust 额外需要创建 Cargo.toml 和 src/lib.rs
            (lang_dir / "src").mkdir(exist_ok=True)
            replace_placeholders(TEMPLATES_DIR / "rust" / "Cargo.toml.tmpl", lang_dir / "Cargo.toml")
            replace_placeholders(TEMPLATES_DIR / "rust" / "lib.rs.tmpl", lang_dir / "src" / "lib.rs")
            update_cargo_toml(problem_dir_name)
        elif lang == "c":
            replace_placeholders(TEMPLATES_DIR / "solution.c", lang_dir / "solution.c")
        elif lang == "cpp":
            replace_placeholders(TEMPLATES_DIR / "solution.cpp", lang_dir / "solution.cpp")
        elif lang == "java":
            replace_placeholders(TEMPLATES_DIR / "Solution.java.tmpl", lang_dir / "Solution.java")

    print(f"\n🎉 成功创建题目 {problem_id:04d}-{title} 模板！")

def is_lang_available(lang: str) -> bool:
    """检查某种语言的运行时或编译器是否真正可用"""
    required_cmds = {
        "go": ["go"],
        "ts": ["npx"],
        "rs": ["cargo"],
        "c": ["gcc"],
        "cpp": ["g++"],
        "java": ["java"]
    }
    if lang not in required_cmds:
        return True
    
    for cmd in required_cmds[lang]:
        if not shutil.which(cmd):
            return False
        
        # 特殊处理 macOS java 桩可执行文件
        if lang == "java":
            try:
                res = subprocess.run([cmd, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if res.returncode != 0:
                    return False
            except Exception:
                return False
    return True

def to_cpp_val(val):
    if isinstance(val, list):
        items = [to_cpp_val(x) for x in val]
        if len(val) > 0 and isinstance(val[0], list):
            return f"vector<vector<int>>({{{', '.join(items)}}})"
        return f"vector<int>({{{', '.join(items)}}})"
    elif isinstance(val, str):
        return f'"{val}"'
    elif isinstance(val, bool):
        return "true" if val else "false"
    else:
        return str(val)

def to_java_val(val):
    if isinstance(val, list):
        items = [to_java_val(x) for x in val]
        return f"new int[]{{ {', '.join(items)} }}"
    elif isinstance(val, str):
        return f'"{val}"'
    elif isinstance(val, bool):
        return "true" if val else "false"
    else:
        return str(val)

def generate_assertions(lang, cases, method_name):
    """根据 JSON 用例生成 C/C++/Java 的硬编码 assert 校验语句"""
    lines = []
    if lang == "cpp":
        for i, case in enumerate(cases):
            decl_lines = []
            call_args = []
            for arg_idx, arg in enumerate(case['input']):
                var_name = f"arg_{i}_{arg_idx}"
                if isinstance(arg, list):
                    val = to_cpp_val(arg)
                    # 假定两数之和等题目里 list 映射为 vector<int>
                    # 如果更复杂的结构，我们暂时都将其转换为 vector<int>，或使用 auto
                    decl_lines.append(f"        vector<int> {var_name} = {val};")
                    call_args.append(var_name)
                else:
                    val = to_cpp_val(arg)
                    decl_lines.append(f"        int {var_name} = {val};")
                    call_args.append(var_name)
            
            expected = to_cpp_val(case['output'])
            decl_str = "\n".join(decl_lines)
            lines.append(f"    {{\n"
                         f"{decl_str}\n"
                         f"        assert(s.{method_name}({', '.join(call_args)}) == {expected});\n"
                         f"    }}")
    elif lang == "java":
        for case in cases:
            java_args = [to_java_val(arg) for arg in case['input']]
            expected = to_java_val(case['output'])
            if isinstance(case['output'], list):
                lines.append(f"        assert Arrays.equals(s.{method_name}({', '.join(java_args)}), {expected}) : \"Test case failed\";")
            else:
                lines.append(f"        assert s.{method_name}({', '.join(java_args)}) == {expected} : \"Test case failed\";")
    elif lang == "c":
        for case in cases:
            if len(case['input']) == 2 and isinstance(case['input'][0], list):
                arr = ", ".join(str(x) for x in case['input'][0])
                target = case['input'][1]
                ans = case['output']
                lines.append(f"    {{\n"
                             f"        int nums[] = {{{arr}}};\n"
                             f"        int returnSize;\n"
                             f"        int* res = {method_name}(nums, {len(case['input'][0])}, {target}, &returnSize);\n"
                             f"        assert(returnSize == {len(ans)});\n"
                             f"        assert(res[0] == {ans[0]} && res[1] == {ans[1]});\n"
                             f"        free(res);\n"
                             f"    }}")
            else:
                lines.append(f"    // 警告: C 语言暂不支持此用例的自动转译，请手动编写自测。")
    return "\n".join(lines)

def extract_method_name(lang, test_dir):
    """根据源文件特征自动提取方法名"""
    filename = "Solution.java" if lang == "java" else f"solution.{lang}"
    filepath = test_dir / filename
    if not filepath.exists():
        return "twoSum"
    
    content = filepath.read_text(encoding="utf-8")
    if lang == "cpp":
        match = re.search(r'\b[a-zA-Z0-9_<>]+\s+([a-zA-Z0-9_]+)\s*\(', content)
        if match:
            name = match.group(1)
            if name not in ["main", "Solution", "vector", "string", "assert"]:
                return name
    elif lang == "java":
        match = re.search(r'public\s+[a-zA-Z0-9_<>\[\]]+\s+([a-zA-Z0-9_]+)\s*\(', content)
        if match:
            return match.group(1)
    elif lang == "c":
        match = re.search(r'\b[a-zA-Z0-9_*]+\s+([a-zA-Z0-9_]+)\s*\(', content)
        if match:
            name = match.group(1)
            if name not in ["main", "assert", "malloc", "free", "printf"]:
                return name
    return "twoSum"

def run_compile_test_with_injection(lang, test_dir, problem_dir, compile_run_fn):
    """如果源文件包含 // {{TEST_CASES}} 且 testcases.json 存在，执行插桩替换编译运行"""
    src_file_name = "Solution.java" if lang == "java" else f"solution.{lang}"
    src_file = test_dir / src_file_name
    testcases_file = problem_dir / "testcases.json"
    
    if not src_file.exists():
        print(f"Error: 未找到源文件 {src_file}")
        sys.exit(1)
        
    content = src_file.read_text(encoding="utf-8")
    
    if "// {{TEST_CASES}}" in content and testcases_file.exists():
        try:
            cases = json.loads(testcases_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error: 解析 testcases.json 失败: {e}")
            sys.exit(1)
            
        method_name = extract_method_name(lang, test_dir)
        assertions = generate_assertions(lang, cases, method_name)
        new_content = content.replace("// {{TEST_CASES}}", assertions)
        
        # 写临时源文件进行编译
        temp_src_name = "Solution_temp.java" if lang == "java" else f"solution_temp.{lang}"
        temp_src_file = test_dir / temp_src_name
        temp_src_file.write_text(new_content, encoding="utf-8")
        
        try:
            compile_run_fn(temp_src_file)
        finally:
            if temp_src_file.exists():
                temp_src_file.unlink()
    else:
        # 直接运行
        compile_run_fn(src_file)

def run_test(args):
    """运行测试"""
    problem_id = args.id
    lang = args.lang
    
    problem_dir = get_problem_dir(problem_id)
    if not problem_dir:
        print(f"Error: 未找到 ID 为 {problem_id} 的题目目录")
        sys.exit(1)
        
    print(f"🔍 匹配到题目目录: {problem_dir.name}")
    
    # 如果指定了语言，只测该语言；否则测试所有已存在的语言
    langs_to_test = []
    if lang:
        if lang not in LANG_MAPPING:
            print(f"Error: 不支持的语言: {lang}")
            sys.exit(1)
        langs_to_test = [lang]
    else:
        # 扫描目录下有哪些语言的文件夹
        for l, dir_name in LANG_MAPPING.items():
            if (problem_dir / dir_name).exists():
                langs_to_test.append(l)

    if not langs_to_test:
        print("Error: 题目目录下没有检测到任何已实现的语言代码")
        sys.exit(1)

    for l in langs_to_test:
        dir_name = LANG_MAPPING[l]
        test_dir = problem_dir / dir_name

        # 检查运行时是否可用
        if not is_lang_available(l):
            if lang:  # 显式指定的语言不存在
                print(f"Error: 未检测到运行 [{dir_name.upper()}] 所需的命令行工具或运行时环境")
                sys.exit(1)
            else:  # 自动遍历时跳过
                print(f"\n⚠️  未检测到可用环境，跳过 [{dir_name.upper()}] 测试。")
                continue

        print(f"\n=== 🚀 正在运行 [{dir_name.upper()}] 测试 ===")
        
        try:
            if l == "py":
                py_file = test_dir / "solution.py"
                subprocess.run([sys.executable, str(py_file)], check=True)
            elif l == "go":
                subprocess.run(["go", "test", f"./{test_dir.relative_to(BASE_DIR)}/..."], check=True)
            elif l == "ts":
                subprocess.run(["npx", "vitest", "run", str(test_dir)], check=True)
            elif l == "rs":
                pkg_name = f"leetcode-{problem_id:04d}"
                subprocess.run(["cargo", "test", "-p", pkg_name], check=True)
            elif l == "c":
                def compile_run_c(src):
                    out_exe = test_dir / "sol_c"
                    subprocess.run(["gcc", "-O2", str(src), "-o", str(out_exe)], check=True)
                    try:
                        subprocess.run([str(out_exe)], check=True)
                    finally:
                        if out_exe.exists():
                            out_exe.unlink()
                run_compile_test_with_injection(l, test_dir, problem_dir, compile_run_c)
            elif l == "cpp":
                def compile_run_cpp(src):
                    out_exe = test_dir / "sol_cpp"
                    subprocess.run(["g++", "-std=c++17", "-O2", str(src), "-o", str(out_exe)], check=True)
                    try:
                        subprocess.run([str(out_exe)], check=True)
                    finally:
                        if out_exe.exists():
                            out_exe.unlink()
                run_compile_test_with_injection(l, test_dir, problem_dir, compile_run_cpp)
            elif l == "java":
                def compile_run_java(src):
                    subprocess.run(["java", "-ea", str(src)], check=True)
                run_compile_test_with_injection(l, test_dir, problem_dir, compile_run_java)
                
            print(f"✅ [{dir_name.upper()}] 测试运行成功！")
        except subprocess.CalledProcessError as e:
            print(f"❌ [{dir_name.upper()}] 测试运行失败，错误代码: {e.returncode}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="LeetCode 本地刷题工具")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # new 命令
    parser_new = subparsers.add_parser("new", help="新建题目模板")
    parser_new.add_argument("id", type=int, help="题目 ID")
    parser_new.add_argument("--title", required=True, help="题目英文标题")
    parser_new.add_argument("--method", default="twoSum", help="初始解题方法签名名称 (默认: twoSum)")
    parser_new.add_argument("--langs", default="ts,rs", 
                            help="要生成的语言列表，用逗号分隔 (默认: ts,rs)")
    
    # test 命令
    parser_test = subparsers.add_parser("test", help="运行题目测试")
    parser_test.add_argument("id", type=int, help="题目 ID")
    parser_test.add_argument("--lang", choices=list(LANG_MAPPING.keys()), help="指定运行哪种语言的测试 (默认运行所有)")
    
    args = parser.parse_args()
    
    if args.command == "new":
        create_problem(args)
    elif args.command == "test":
        run_test(args)

if __name__ == "__main__":
    main()
