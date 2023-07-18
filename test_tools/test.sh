echo hacksang | sudo -S python testline_stress.py | grep duration -A 10

echo hacksang | sudo -S python baseline_stress.py | grep duration -A 10

echo hacksang | sudo -S python testline_test.py | grep duration -A 10

echo hacksang | sudo -S python baseline_test.py | grep duration -A 10
