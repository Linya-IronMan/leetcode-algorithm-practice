import { describe, it, expect } from 'vitest';
import { isPalindrome } from './solution';
import cases from '../testcases.json';

describe('Palindrome Number', () => {
    it.each(cases)('case %#', (c) => {
        const args = c.input as unknown as Parameters<typeof isPalindrome>;
        expect(isPalindrome(...args)).toEqual(c.output);
    });
});
