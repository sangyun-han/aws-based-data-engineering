# download & unzip logstash
wget https://artifacts.elastic.co/downloads/logstash/logstash-7.16.2-linux-x86_64.tar.gz
tar -zxvf logstash-7.16.2-linux-x86_64.tar.gz

# download & unzip filebeat
wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.16.2-linux-x86_64.tar.gz
tar -zxvf filebeat-7.16.2-linux-x86_64.tar.gz

# run logstash
cd logstash-7.16.2/ 
./bin/logstash -f config/logstash-sample.conf

# run filebeat
cd filebeat-7.16.2-linux-x86_64/
./filebeat run -e

git clone https://github.com/sangyun-han/aws-based-data-engineering
cp aws-based-data-engineering/week-1/logstash/logstash-config-* logstash-7.16.2/config/

./logstash-7.16.2/bin/logstash -f config/logstash-config-generator.conf
./logstash-7.16.2/bin/logstash -f config/logstash-config-file.conf
./logstash-7.16.2/bin/logstash -f config/logstash-config-filter.conf

#######

cd ~/aws-based-data-engineering/week-1/logstash
~/logstash-7.16.2/bin/logstash -f logstash-config-filebeat.conf

cd ~/aws-based-data-engineering/week-1/filebeat
chmod go-w filebeat.yml
~/filebeat-7.16.2-linux-x86_64/filebeat run -e filebeat.yml


for ((i=0; ;i+=1 )); do echo $i >> input.file;sleep 1; done
######

sudo apt update
sudo apt install openjdk-11-jdk

wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
sudo apt-get update && sudo apt-get install logstash