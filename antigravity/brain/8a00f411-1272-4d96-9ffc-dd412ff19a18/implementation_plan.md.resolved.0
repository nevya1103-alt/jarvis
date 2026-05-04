# Implementation Plan: UI/UX Improvements

This plan outlines the steps to add the requested Light/Dark Theme toggle and the Gold Coin loading animations to the crypto dashboard.

## Proposed Changes

### 1. Light/Dark Theme Toggle
We will introduce a new light theme by utilizing CSS variables.
- Add `.light-theme` class to `:root` in `style.css` which overrides the default dark colors with lighter equivalents (e.g., white cards, dark text).
- Add a floating toggle button (`🌗`) to `index.html` at the top right, next to the Watchlist button.
- Add JavaScript logic in `index.html` to toggle the `.light-theme` class on the `document.documentElement` and save the user's preference in `localStorage`.

### 2. Animated Gold Coin Loader
We will replace the boring "Loading..." text with animated spinning gold coins.
- Create CSS keyframes (`coinSpin`) in `style.css` to create a 3D spinning effect for a coin element.
- Design the `.gold-coin` CSS class to look like a gold coin with a `$` symbol inside.
- In `index.html`, replace the "Loading..." text inside the Overview cards with these animated coins.
- Add an initial "Loading" row inside the main top 50 table (`#crypto-table-body`) displaying the spinning coins. 
- *Note:* Because your `script.py` directly overwrites the HTML of these elements once the data is fetched, the coins will automatically disappear when the real data arrives!

### File Modifications

#### [MODIFY] `style.css`
- Add `:root.light-theme` variables.
- Add styling for `.theme-toggle-btn`.
- Add `.gold-coin` class and `@keyframes coinSpin`.

#### [MODIFY] `index.html`
- Insert the `<button>` for the Theme Toggle.
- Replace `Loading...` text in `#avg-price`, `#highest-change`, and `#lowest-change` with the gold coin HTML.
- Add a temporary loading row inside `#crypto-table-body`.
- Add a small JavaScript block to handle the theme switching logic.

## User Review Required
Please review the plan. The transition to light mode will automatically invert text and card backgrounds. Are you okay with the theme toggle button floating at the top right next to the Watchlist? Once approved, I will proceed with the code changes.
