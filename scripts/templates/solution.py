# LeetCode ${problem_id}. ${problem_title}
import json
import os

class Solution:
    def ${method_name}(self, nums: list[int], target: int) -> list[int]:
        # TODO: 实现解题逻辑
        return []

if __name__ == '__main__':
    s = Solution()
    json_path = os.path.join(os.path.dirname(__file__), '..', 'testcases.json')
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            cases = json.load(f)
        for case in cases:
            assert s.${method_name}(*case['input']) == case['output']
        print("Python: All tests passed!")
