-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS gmap;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE gmap (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  k TEXT UNIQUE NOT NULL,
  v TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  local_ip TEXT,
  port INTEGER,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
