export function twoSum(nums: number[], target: number): number[] {
	let map = new Map<number, number>();
	for (let i = 0; i < nums.length; i++) {
		const n1 = nums[i];
		const n2 = target - n1;
		if (map.get(n2) === undefined) map.set(n1, i);
		else return [map.get(n2)!, i];
	}
	return [];
}
