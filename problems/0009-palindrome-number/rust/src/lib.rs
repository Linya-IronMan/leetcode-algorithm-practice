pub struct Solution;

impl Solution {
    /// 判断一个整数是否是回文数。
    ///
    /// # 参数
    /// * `x` - 待判断的整数
    ///
    /// # 返回值
    /// 如果是回文数返回 `true`，否则返回 `false`
    pub fn is_palindrome(x: i32) -> bool {
        // TODO: 请在此处实现您的解题逻辑
        todo!()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde::Deserialize;

    #[derive(Deserialize)]
    struct TestCase {
        input: Vec<i32>,
        output: bool,
    }

    #[test]
    fn test_all() {
        let content =
            std::fs::read_to_string("../testcases.json").expect("Failed to read testcases.json");
        let cases: Vec<TestCase> =
            serde_json::from_str(&content).expect("Failed to parse testcases.json");
        for case in cases {
            assert_eq!(Solution::is_palindrome(case.input[0]), case.output);
        }
    }
}
