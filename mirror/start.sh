start_time=1
while test '1'='1'
do
echo '正在进行第'${start_time}'次开服……'
echo 'The server has been started for '${start_time}' times...'
sudo python3 MCDReforged.py
start_time=$[$start_time+1]
done