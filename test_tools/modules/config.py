import os

version = 9
base =  10
cpu_time = 2 * base 
mem_time = 4 * base
io_time = 6 * base
over_time = 8 * base

test_file_path = "/home/hacksang/Documents/study/博士/项目/横向项目/OPPO/RL_DVFS/RL-Governor-CS-Architecture/test_tools/tests/"

#things = ['fps', 'little', 'big','lclock','bclock','mem']
things = ['fps', 'little', 'big','lclock','bclock','mem']

start_douyin = False
record_battery = False
view = 'com.ss.android.ugc.aweme/com.ss.android.ugc.aweme.detail.ui.DetailActivity#0'
view = "com.smile.gifmaker/com.yxcorp.gifshow.HomeActivity#0"
# view = 'tv.danmaku.bili/com.bilibili.video.videodetail.VideoDetailsActivity#0'
# view = "com.ss.android.ugc.aweme/com.ss.android.ugc.aweme.splash.SplashActivity#0"

ClusterNum = 3
TargetFPS = 120
