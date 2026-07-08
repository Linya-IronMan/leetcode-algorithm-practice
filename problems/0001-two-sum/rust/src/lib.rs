use std::collections::HashMap;

pub struct Solution;

impl Solution {
    pub fn twoSum(nums: Vec<i32>, target: i32) -> Vec<i32> {
        let mut map = HashMap::new();
        for (i, &num) in nums.iter().enumerate() {
            let complement = target - num;
            if let Some(&index) = map.get(&complement) {
                return vec![index as i32, i as i32];
            }
            map.insert(num, i);
        }
        vec![]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde::Deserialize;

    #[derive(Deserialize)]
    struct TestCase {
        input: (Vec<i32>, i32),
        output: Vec<i32>,
    }

    #[test]
    fn test_all() {
        let content = std::fs::read_to_string("../testcases.json")
            .expect("Failed to read testcases.json");
        let cases: Vec<TestCase> = serde_json::from_str(&content)
            .expect("Failed to parse testcases.json");
        for case in cases {
            // TODO: 根据题目的输入参数和返回类型修改这里的解包与 assert
            assert_eq!(Solution::twoSum(case.input.0, case.input.1), case.output);
        }
    }
}
