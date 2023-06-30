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
//public static final int [] allowedLittleFrequencies = {748800,1056000,1420800,1766400} ;
    public static final int [] allowedLittleFrequencies = {940800, 1516800, 1900800} ;

    // 825600 902400 979200 1056000 1209600 1286400 1363200 1459200 1536000 1612800 1689600 1766400 1843200 1920000 1996800 2092800 2169600 2246400 2323200 2400000 2476800 2553600 2649600
 //   public static final int [] allowedBigFrequencies = {1459200, 1843200, 2246400, 2649600 };
    public static final int [] allowedBigFrequencies = {1056000, 1766400, 2400000};

    public static final int maxFrequencyChoices = 9;

}
