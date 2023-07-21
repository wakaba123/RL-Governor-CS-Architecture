package com.example.networktrans;

public class Config {
    public static final String BinaryServerPosition = "/data/local/tmp/server";
    public static final String SERVER_IP = "127.0.0.1";
    public static final int SERVER_PORT = 8888;
    public static final String view = "com.smile.gifmaker/com.yxcorp.gifshow.HomeActivity#0";
    public static final int ModelInputNum = 5;
    public static final int ModelActionNum = 9;
    public static final int TargetFPS = 60;
    public static final String ModelName = "model_oppo_a36.tflite";

    public static final int ClusterNum = 2;
    public static final int [] allowedLittleFrequencies = {940800, 1516800, 1900800} ;
    public static final int [] allowedBigFrequencies = {1056000, 1766400, 2400000};
    public static final int maxFrequencyChoices = 9;

}
