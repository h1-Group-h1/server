test_path() {
    if [ $1 = 'POST' ]; then
        curl -X $1 -d $3 https://com-ra-api.co.uk/$2
    fi
        
    curl -X $1 https://com-ra-api.co.uk/$2
}

test_path 'GET' 
test_path 'GET'
test_path 'POST' 'add_user' "{'email': 'st', 'name': 'st', 'stp'}"

