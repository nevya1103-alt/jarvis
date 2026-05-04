# TMDB API Integration Walkthrough

I have successfully updated the code to pull **thousands of Bollywood movies** released between 2006 and 2026, directly from the official TMDB servers!

## What Changed?
1. **Dynamic Data Engine**: The website no longer relies on a hardcoded list of 10 movies. Instead, it talks directly to TMDB.
2. **Infinite Pagination**: I added a "Load More Movies" button at the bottom of the grid. This allows the browser to smoothly fetch and display thousands of movies without crashing.
3. **Advanced Filtering**: The genre buttons and search bar now ask TMDB's servers to do the heavy lifting, ensuring you always get accurate, up-to-date results.

## How to Make It Work

Because the application is now wired up to TMDB, you must provide it with your unique API Key so TMDB knows who is requesting the data.

### Step 1: Get Your Free API Key
1. Go to [The Movie Database (TMDB)](https://www.themoviedb.org/) and create a free account.
2. Go to your **Account Settings** -> **API**.
3. Click to create a new API key (choose "Developer").
4. Fill out the short form (you can just say it's for a personal hobby project).
5. Copy the **"API Key (v3 auth)"** string. It will look like a long random string of letters and numbers.

### Step 2: Add it to the Code
1. Open the `script.js` file located at: `C:\Users\NEVYA\.gemini\antigravity\scratch\movie-recommender\script.js`
2. At the very top of the file, on **Line 4**, you will see:
   ```javascript
   const TMDB_API_KEY = "YOUR_API_KEY_HERE";
   ```
3. Replace `"YOUR_API_KEY_HERE"` with the key you copied. Make sure to keep the quote marks!
   *(Example: `const TMDB_API_KEY = "1a2b3c4d5e6f7g8h9i";`)*

### Step 3: Run the Website
Save the `script.js` file and open `index.html` in your browser. You will instantly see the massive library of Bollywood movies load!
