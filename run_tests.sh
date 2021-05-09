if [ $(which python3)  !=  $(pwd)/server-env/bin/python3 ]; then
  source ./server-env/bin/activate
fi

python3 src/test/master_test.py
