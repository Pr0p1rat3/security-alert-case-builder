import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import tseslint from "typescript-eslint";

export default [
  { ignores: ["dist/**", "node_modules/**"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["src/**/*.{ts,tsx}"],
    plugins: {
      "react-hooks": reactHooks
    },
    languageOptions: {
      globals: {
        document: "readonly",
        fetch: "readonly",
        localStorage: "readonly",
        navigator: "readonly",
        URL: "readonly",
        Blob: "readonly",
        console: "readonly",
        File: "readonly",
        FormData: "readonly"
      }
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "@typescript-eslint/no-explicit-any": "off",
      "react-hooks/set-state-in-effect": "off"
    }
  }
];
