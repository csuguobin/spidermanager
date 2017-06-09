upstream phantomjsserver {
    {{ serverlist }}
}

server {
    listen       20000;
    location / {
        proxy_pass   http://phantomjsserver;
    }
}