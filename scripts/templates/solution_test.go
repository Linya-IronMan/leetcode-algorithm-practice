package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func Test${method_name_cap}(t *testing.T) {
	data, err := os.ReadFile(filepath.Join("..", "testcases.json"))
	if err != nil {
		t.Fatal(err)
	}

	var cases []struct {
		Input  []json.RawMessage `json:"input"`
		Output json.RawMessage   `json:"output"`
	}
	if err := json.Unmarshal(data, &cases); err != nil {
		t.Fatal(err)
	}

	for i, tc := range cases {
		// TODO: 根据题目的输入输出类型修改以下变量类型和反序列化逻辑
		var nums []int
		var target int
		var want []int

		json.Unmarshal(tc.Input[0], &nums)
		json.Unmarshal(tc.Input[1], &target)
		json.Unmarshal(tc.Output, &want)

		got := ${method_name}(nums, target)
		if !reflect.DeepEqual(got, want) {
			t.Errorf("case %d: got %v, want %v", i, got, want)
		}
	}
}
