DROP DATABASE Snooper;
CREATE DATABASE Snooper;
USE Snooper;

CREATE TABLE users(
my_id int auto_increment,
email varchar(250) NOT NULL,
password varchar(250) NOT NULL,
name varchar(250) NOT NULL,
company_name varchar(250),
date_created DATETIME DEFAULT current_timestamp,
primary key (my_id)
);

CREATE TABLE apps(
id int auto_increment,
user_id int,
app_name varchar(50),
PRIMARY KEY (id),
FOREIGN KEY (user_id) REFERENCES users(my_id)
);
