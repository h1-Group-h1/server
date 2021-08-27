if [ $(which python3)  !=  $(pwd)/server-env/bin/python3 ]; then
  source ./server-env/bin/activate
fi
cd src
python3 -m unittest test_main.py
