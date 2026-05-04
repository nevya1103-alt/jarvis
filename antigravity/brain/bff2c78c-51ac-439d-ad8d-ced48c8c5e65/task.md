# TMDB Integration Tasks

- [x] Application Logic Updates (`script.js`)
  - [x] Remove hardcoded mock `moviesData`.
  - [x] Add `TMDB_API_KEY` placeholder.
  - [x] Implement `fetchMoviesFromTMDB()` using `/discover/movie` endpoint.
  - [x] Configure parameters for Bollywood (Hindi, IN) from 2006 to 2026.
  - [x] Map TMDB response to existing `movie-card` UI.
  - [x] Implement pagination ("Load More" button) to handle thousands of movies.
  - [x] Update search functionality to use TMDB `/search/movie` endpoint.
  - [x] Update genre filtering to use TMDB genre IDs.
- [x] UI Updates (`index.html`)
  - [x] Add a "Load More" button at the bottom of the grid.
- [x] Verification
  - [x] Ensure the app degrades gracefully or shows a clear error if the API key is missing.
