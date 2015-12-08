--initial users table implementation
CREATE TABLE IF NOT EXISTS users(
id serial PRIMARY KEY,
email varchar(50) NOT NULL,
password varchar(50) NOT NULL,
dob date NOT NULL,
gender char(1) NOT NULL,
interested_in char(1) NOT NULL,
status boolean NOT NULL DEFAULT true,
created_at date NOT NULL DEFAULT CURRENT_DATE,
CONSTRAINT email UNIQUE(email)
);
