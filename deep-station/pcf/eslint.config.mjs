import eslintjs from "@eslint/js";
import microsoftPowerApps from "@microsoft/eslint-plugin-power-apps";
import globals from "globals";
import typescriptEslint from "typescript-eslint";

/** @type {import('eslint').Linter.Config[]} */
export default [
  { ignores: ["**/generated", "out/**", "harness/**", "node_modules/**"] },
  eslintjs.configs.recommended,
  ...typescriptEslint.configs.recommended,
  {
    plugins: { "@microsoft/power-apps": microsoftPowerApps },
    languageOptions: { globals: { ...globals.browser, ComponentFramework: true } },
    rules: { "@microsoft/power-apps/avoid-unpub-api": "warn" },
  },
];
