# ktaabot

ktaabot adalah game sebagai bot telegram yang tujuannya adalah mencari kata dalam sebuat grid 4x4 berisi karakter-karakter acak. Kata tersebut memenuhi:

- panjang kata min 3 huruf/karakter
- kata merupakan jalur dalam grid
- jalur kata dapat dihubungkan secara horizontal, vertikal, atau diagonal
- tidak ada huruf yang "meloncat" dalam grid

contoh:

~~~
a a a a
a k a a
a t a a
n a a m
~~~

Untuk grid diatas "kata" dan "tak" merupakan kata yang sesuai, sedangkan "nama" bukan merupakan jawaban yang diperlukan.

## Inisiasi database

ktaabot menggunakan sqlite3 sebagai engine database. Dalam folder "data" tersedia

- schema.sql : definisi tabel dan contoh grid game
- words.txt : daftar kata bahasa indonesia yang dipakai untuk membentuk grid
- game_data.db : file ini diperlukan script dan dapat dibuat dari schema.sql

Eksekusi perintah berikut dalam folder "data" untuk menginisiasi database yang diperlukan.

~~~
cat schema.sql | sqlite3 game_data.db
~~~



