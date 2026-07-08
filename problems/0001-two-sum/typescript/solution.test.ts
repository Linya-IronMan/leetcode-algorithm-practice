import { describe, it, expect } from 'vitest';
import { twoSum } from './solution';
import cases from '../testcases.json';

describe('Two Sum', () => {
    it.each(cases)('case %#', (c) => {
        const args = c.input as unknown as Parameters<typeof twoSum>;
        expect(twoSum(...args)).toEqual(c.output);
    });
});
