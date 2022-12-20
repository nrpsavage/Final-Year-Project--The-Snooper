// Code used to connect to the databse, will be put into the index.js class to tidy up application.

const mysql = require('mysql');
const con = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'mysql123456',
});

con.connect((error) => {
  if(error) throw error;
  console.log('Connection established sucessfully');
});


  con.connect(function(err){
    if(err) throw err;
    con.query("SELECT * FROM cvs_list, assets WHERE name LIKE '%asset%';", function (err,result){
      if (err) throw err;
      console.log(result);
    })
  });

