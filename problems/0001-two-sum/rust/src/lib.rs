use std::collections::HashMap;

pub struct Solution;

impl Solution {
    pub fn two_sum(nums: Vec<i32>, target: i32) -> Vec<i32> {
        let mut map: HashMap<i32, i32> = HashMap::new();
        for (i, item) in nums.iter().enumerate() {
            let n1 = item;
            let n2 = target - n1;
            if let Some(i3) = map.get(&n2) {
                return vec![*i3 as i32, i as i32];
            } else {
                map.insert(*item, i as i32);
            }
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
        let content =
            std::fs::read_to_string("../testcases.json").expect("Failed to read testcases.json");
        let cases: Vec<TestCase> =
            serde_json::from_str(&content).expect("Failed to parse testcases.json");
        for case in cases {
            // TODO: 根据题目的输入参数和返回类型修改这里的解包与 assert
            assert_eq!(Solution::two_sum(case.input.0, case.input.1), case.output);
        }
    }
}
