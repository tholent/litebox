// Copyright 2026 Chris Wells
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// ESLint checks the script inside litebox.html (through eslint-plugin-html) and the test harnesses.
import js from '@eslint/js';
import html from 'eslint-plugin-html';
import globals from 'globals';

export default [
  { ignores: ['tests/out/**', 'node_modules/**'] },
  js.configs.recommended,
  {
    files: ['**/*.html', 'tests/*.js'],
    plugins: { html },
    languageOptions: { ecmaVersion: 'latest', sourceType: 'script', globals: { ...globals.browser } },
    // litebox often ignores a failed browser call on purpose: `catch (e) { fall back }`.
    rules: { 'no-unused-vars': ['error', { caughtErrors: 'none' }] },
  },
  {
    files: ['eslint.config.mjs'],
    languageOptions: { globals: { ...globals.node } },
  },
];
